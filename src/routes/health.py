from flask import Blueprint, jsonify, Response
from src.bootstrap.config import settings
from src.bootstrap.extensions import limiter, talisman

bp = Blueprint("health", __name__)

@bp.get("/health")
@talisman(force_https=False)
@limiter.limit(settings.health_rate_limit)
def health() -> Response:
    return jsonify({"status": "ok"})
