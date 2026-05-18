from typing import Any
import traceback
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_talisman import Talisman
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from authorization_in_the_middle import CedarEvaluator, FilesystemPolicySetSource
from src.bootstrap.config import settings
from src.bootstrap.extensions import limiter
from src.bootstrap.logging_config import log_event, setup_logging
from src.routes import health
from src.routes.capabilities import init_routes

def _http_error_name(status_code: int) -> str:
    return {400: "invalid_request", 404: "not_found", 405: "method_not_allowed", 413: "payload_too_large"}.get(status_code, "http_error")


def create_app(config: dict[str, Any] | None = None) -> Flask:
    setup_logging(settings.service_name, settings.log_level)
    app = Flask(__name__)
    CORS(app, origins=[settings.frontend_url], supports_credentials=True)
    if config:
        app.config.update(config)
    app.config.setdefault("MAX_CONTENT_LENGTH", settings.max_content_length)
    app.config.setdefault("JWT_PUBLIC_KEY", settings.jwt_public_key)
    app.config.setdefault("JWT_ISSUER", settings.jwt_issuer)
    app.config.setdefault("JWT_AUDIENCE", settings.jwt_audience)
    app.config.setdefault("SERVICE_NAME", settings.service_name)
    if hasattr(settings, "jwt_jwks_uri"):
        app.config.setdefault("JWT_JWKS_URI", settings.jwt_jwks_uri)

    if not settings.jwt_public_key and not settings.jwt_jwks_uri:
        raise RuntimeError(
            "Capabilities service requires JWT_PUBLIC_KEY or JWT_JWKS_URI to be configured. "
            "Set one in the environment before startup."
        )

    is_dev = settings.env.lower() in ("development", "test")
    if not is_dev and settings.trusted_proxy_hops > 0:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=settings.trusted_proxy_hops, x_proto=settings.trusted_proxy_hops, x_host=settings.trusted_proxy_hops, x_prefix=settings.trusted_proxy_hops)

    Talisman(app, force_https=not is_dev, strict_transport_security=not is_dev, strict_transport_security_max_age=31536000, strict_transport_security_include_subdomains=True, content_security_policy={"default-src": ["'none'"], "frame-ancestors": ["'none'"]}, referrer_policy="strict-origin-when-cross-origin")
    limiter.init_app(app)

    policy_source = FilesystemPolicySetSource(settings.capabilities_policies_dir, cache_ttl=settings.capabilities_policy_cache_ttl)
    evaluator = CedarEvaluator(policy_source=policy_source)

    app.register_blueprint(health.bp)
    init_routes(app, evaluator)

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        return jsonify({"error": _http_error_name(exc.code or 500)}), exc.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception):
        log_event("request.unhandled_error", route=request.path, error_type=type(exc).__name__)
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500

    log_event("service.startup", env=settings.env, port=settings.port, policies_dir=str(settings.capabilities_policies_dir))
    return app


app = create_app()
