import pytest

from tests.conftest import encode_test_access_token

pytestmark = pytest.mark.integration


def test_list_capability_namespaces(client, api_spec, validate_response):
    response = client.get("/api/v1/capabilities")

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities", "get", 200, response.get_json())
    assert response.json == {"namespaces": ["ui"]}


def test_operator_can_see_operator_menu(client, rsa_keypair, api_spec, validate_response):
    token = encode_test_access_token(rsa_keypair["private"], actors=["operator"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities/{namespace}", "get", 200, response.get_json())
    data = response.json
    assert data["ui:menu:operator"] is True
    assert data["ui:menu:debug"] is True
    assert data["ui:menu:patient"] is False
    assert data["ui:menu:clinician"] is False


def test_clinician_can_see_clinician_menu(client, rsa_keypair, api_spec, validate_response):
    token = encode_test_access_token(rsa_keypair["private"], actors=["clinician"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities/{namespace}", "get", 200, response.get_json())
    data = response.json
    assert data["ui:menu:operator"] is False
    assert data["ui:menu:debug"] is False
    assert data["ui:menu:patient"] is False
    assert data["ui:menu:clinician"] is True


def test_patient_can_see_patient_menu(client, rsa_keypair, api_spec, validate_response):
    token = encode_test_access_token(rsa_keypair["private"], actors=["patient"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    validate_response(api_spec, "/api/v1/capabilities/{namespace}", "get", 200, response.get_json())
    data = response.json
    assert data["ui:menu:operator"] is False
    assert data["ui:menu:debug"] is False
    assert data["ui:menu:patient"] is True
    assert data["ui:menu:clinician"] is False


def test_accepts_authenticated_audience(client, rsa_keypair):
    token = encode_test_access_token(
        rsa_keypair["private"],
        actors=["operator"],
        audience=["authentication", "capabilities"],
    )
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json["ui:menu:operator"] is True


def test_multiple_actors_with_active_actor(client, rsa_keypair):
    token = encode_test_access_token(rsa_keypair["private"], actors=["operator", "clinician"])

    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}", "X-Active-Actor": "operator"},
    )
    assert response.status_code == 200
    assert response.json["ui:menu:operator"] is True

    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}", "X-Active-Actor": "clinician"},
    )
    assert response.status_code == 200
    assert response.json["ui:menu:operator"] is False
    assert response.json["ui:menu:clinician"] is True
