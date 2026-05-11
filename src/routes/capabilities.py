from flask import Blueprint, jsonify, current_app
from authentication_in_the_middle.decorators import with_authentication
from authorization_in_the_middle.flask_identity import extract_jwt_principal_uid, extract_jwt_principal_entity
from src.bootstrap.config import settings
from src.bootstrap.extensions import limiter

bp = Blueprint("capabilities", __name__, url_prefix="/api/v1/capabilities")

@bp.get("")
@limiter.limit(settings.health_rate_limit)
@with_authentication()
def get_capabilities():
    # Enforces X-Active-Role via with_authentication, returns entity dict
    principal_entity = extract_jwt_principal_entity("ui")
    principal_id = extract_jwt_principal_uid("ui")
    
    entities = [principal_entity]
    evaluator = current_app.extensions["cedar_evaluator"]
    
    def check(resource_uid):
        return evaluator.is_authorized(
            principal=principal_id,
            action='Action::"View"',
            resource=resource_uid,
            context={},
            entities=entities
        )
        
    return jsonify({
        "ui:menu:admin": check('ui::Menu::"admin"'),
        "ui:menu:debug": check('ui::Menu::"debug"')
    })

def init_routes(app, cedar_evaluator):
    app.extensions["cedar_evaluator"] = cedar_evaluator
    app.register_blueprint(bp)
