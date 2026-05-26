from flask import Blueprint, abort, jsonify, current_app
from authentication_in_the_middle.decorators import with_authentication
from authorization_in_the_middle.flask_identity import extract_jwt_principal_uid, extract_jwt_principal_entity
from src.bootstrap.config import settings
from src.bootstrap.extensions import limiter
from src.services.entitlements_manifest import EntitlementDefinition, EntitlementsManifest

bp = Blueprint("capabilities", __name__, url_prefix="/api/v1/capabilities")


@bp.get("")
@limiter.limit(settings.health_rate_limit)
def list_capability_namespaces():
    manifest: EntitlementsManifest = current_app.extensions["entitlement_manifest"]
    return jsonify({"namespaces": manifest.namespace_names})


@bp.get("/<namespace>")
@limiter.limit(settings.health_rate_limit)
@with_authentication(audience=settings.jwt_audience)
def get_capabilities(namespace: str):
    manifest: EntitlementsManifest = current_app.extensions["entitlement_manifest"]
    definitions = manifest.namespaces.get(namespace)
    if definitions is None:
        abort(404)

    principal_entity = extract_jwt_principal_entity(namespace)
    principal_id = extract_jwt_principal_uid(namespace)

    entities = [principal_entity]
    evaluator = current_app.extensions["cedar_evaluator"]

    def check(defn: EntitlementDefinition) -> bool:
        return evaluator.is_authorized(
            principal=principal_id,
            action=f'Action::"{defn.action}"',
            resource=defn.resource,
            context={},
            entities=entities,
        )

    return jsonify({defn.key: check(defn) for defn in definitions})


def init_routes(app, cedar_evaluator, entitlement_manifest):
    app.extensions["cedar_evaluator"] = cedar_evaluator
    app.extensions["entitlement_manifest"] = entitlement_manifest
    app.register_blueprint(bp)
