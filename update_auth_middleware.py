import re
from pathlib import Path

file_path = "/home/byoung/projects/neosofia/sdk/python/authentication-middleware/src/authentication_in_the_middle/decorators.py"
content = Path(file_path).read_text()

import_pattern = "from flask import g, jsonify, make_response, request"
new_import = """from flask import g, jsonify, make_response, request
import re
from werkzeug.exceptions import BadRequest, Forbidden"""

content = content.replace(import_pattern, new_import)

decorator_def = "def with_authentication(public_key: str | None, issuer: str, audience: str, algorithms: list[str] | None = None, jwks_uri: str | None = None) -> Callable:"
new_decorator_def = "def with_authentication(public_key: str | None, issuer: str, audience: str, algorithms: list[str] | None = None, jwks_uri: str | None = None, enforce_active_role: bool = True) -> Callable:\n    SLUG_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')"

content = content.replace(decorator_def, new_decorator_def)


auth_logic = """
                claims = pyjwt.decode(
                    token,
                    key=signing_key,
                    algorithms=algorithms,
                    issuer=issuer,
                    audience=audience,
                    options={"require": ["exp", "iat", "iss", "sub", "aud"]}
                )
                g.jwt_claims = claims
"""

new_auth_logic = """
                claims = pyjwt.decode(
                    token,
                    key=signing_key,
                    algorithms=algorithms,
                    issuer=issuer,
                    audience=audience,
                    options={"require": ["exp", "iat", "iss", "sub", "aud"]}
                )
                
                if enforce_active_role:
                    auth_roles = claims.get("neosofia:roles", claims.get("roles", []))
                    if not isinstance(auth_roles, list):
                        auth_roles = []
                        
                    requested_role = request.headers.get("X-Active-Role")
                    
                    if requested_role:
                        if not SLUG_PATTERN.match(requested_role):
                            return make_response(jsonify({"error": "bad_request", "detail": "Invalid role format"}), 400)
                        if requested_role not in auth_roles:
                            return make_response(jsonify({"error": "forbidden", "detail": "Active role not authorized for this session"}), 403)
                        active_roles = [requested_role]
                    else:
                        if len(auth_roles) > 1:
                            return make_response(jsonify({"error": "bad_request", "detail": "Multiple roles present but X-Active-Role header is missing"}), 400)
                        active_roles = auth_roles
                        
                    # Inject resolved roles back into claims so downstream authz picks it up correctly
                    claims["neosofia:roles"] = active_roles

                g.jwt_claims = claims
"""
content = content.replace(auth_logic, new_auth_logic)

Path(file_path).write_text(content)
