import pytest
import jwt
import time
from flask.testing import FlaskClient

def create_token(roles, private_key, audience="capabilities"):
    now = int(time.time())
    return jwt.encode(
        {
            "sub": "user_123",
            "iss": "https://test.neosofia.com",
            "aud": audience,
            "roles": roles,
            "iat": now,
            "exp": now + 3600
        },
        private_key,
        algorithm="RS256"
    )

@pytest.mark.integration
def test_admin_can_see_admin_menu(client: FlaskClient, rsa_keypair):
    token = create_token(["admin"], rsa_keypair["private"])
    response = client.get("/api/v1/capabilities", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json
    assert data["ui:menu:admin"] is True
    assert data["ui:menu:debug"] is True

@pytest.mark.integration
def test_clinician_cannot_see_admin_menu(client: FlaskClient, rsa_keypair):
    token = create_token(["clinician"], rsa_keypair["private"])
    response = client.get("/api/v1/capabilities", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json
    assert data["ui:menu:admin"] is False
    assert data["ui:menu:debug"] is False

@pytest.mark.integration
def test_unauthorized_without_token(client: FlaskClient):
    response = client.get("/api/v1/capabilities")
    assert response.status_code == 401

@pytest.mark.integration
def test_multiple_roles_requires_active_role(client: FlaskClient, rsa_keypair):
    token = create_token(["admin", "clinician"], rsa_keypair["private"])
    response = client.get("/api/v1/capabilities", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    assert response.json["error"] in ("invalid_request", "bad_request")
    
    # Now provide active role
    response = client.get(
        "/api/v1/capabilities", 
        headers={"Authorization": f"Bearer {token}", "X-Active-Role": "admin"}
    )
    assert response.status_code == 200
    assert response.json["ui:menu:admin"] is True

    # Switch active role
    response = client.get(
        "/api/v1/capabilities", 
        headers={"Authorization": f"Bearer {token}", "X-Active-Role": "clinician"}
    )
    assert response.status_code == 200
    assert response.json["ui:menu:admin"] is False

@pytest.mark.integration
def test_accepts_authenticated_audience(client: FlaskClient, rsa_keypair):
    token = create_token(["admin"], rsa_keypair["private"], audience=["authentication", "capabilities"])
    response = client.get("/api/v1/capabilities", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json["ui:menu:admin"] is True

