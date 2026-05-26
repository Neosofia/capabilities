import pytest

from tests.conftest import encode_test_access_token

pytestmark = pytest.mark.integration


def test_list_capability_namespaces(client, api_spec, validate_response):
    response = client.get("/api/v1/capabilities")

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities", "get", 200, response.get_json())
    assert response.json == {"namespaces": ["ui"]}


def test_admin_can_see_admin_menu(client, rsa_keypair, api_spec, validate_response):
    token = encode_test_access_token(rsa_keypair["private"], roles=["admin"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities/{namespace}", "get", 200, response.get_json())
    data = response.json
    assert data["ui:menu:admin"] is True
    assert data["ui:menu:debug"] is True
    assert data["ui:menu:patient"] is False
    assert data["ui:menu:clinician"] is False


def test_clinician_can_see_clinician_menu(client, rsa_keypair, api_spec, validate_response):
    token = encode_test_access_token(rsa_keypair["private"], roles=["clinician"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities/{namespace}", "get", 200, response.get_json())
    data = response.json
    assert data["ui:menu:admin"] is False
    assert data["ui:menu:debug"] is False
    assert data["ui:menu:patient"] is False
    assert data["ui:menu:clinician"] is True


def test_patient_can_see_patient_menu(client, rsa_keypair, api_spec, validate_response):
    token = encode_test_access_token(rsa_keypair["private"], roles=["patient"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities/{namespace}", "get", 200, response.get_json())
    data = response.json
    assert data["ui:menu:admin"] is False
    assert data["ui:menu:debug"] is False
    assert data["ui:menu:patient"] is True
    assert data["ui:menu:clinician"] is False


def test_accepts_authenticated_audience(client, rsa_keypair):
    token = encode_test_access_token(
        rsa_keypair["private"],
        roles=["admin"],
        audience=["authentication", "capabilities"],
    )
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["ui:menu:admin"] is True


def test_multiple_roles_with_active_role(client, rsa_keypair):
    token = encode_test_access_token(rsa_keypair["private"], roles=["admin", "clinician"])

    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}", "X-Active-Role": "admin"},
    )
    assert response.status_code == 200
    assert response.json["ui:menu:admin"] is True

    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}", "X-Active-Role": "clinician"},
    )
    assert response.status_code == 200
    assert response.json["ui:menu:admin"] is False
    assert response.json["ui:menu:clinician"] is True
