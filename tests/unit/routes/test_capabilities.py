import pytest

from tests.conftest import encode_test_access_token

pytestmark = pytest.mark.unit


def test_unauthorized_without_token(client):
    response = client.get("/api/v1/capabilities/ui")

    assert response.status_code == 401


def test_unknown_namespace_returns_not_found(client, rsa_keypair):
    token = encode_test_access_token(rsa_keypair["private"], roles=["admin"])
    response = client.get(
        "/api/v1/capabilities/unknown",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


def test_multiple_roles_without_active_role_returns_bad_request(client, rsa_keypair):
    token = encode_test_access_token(rsa_keypair["private"], roles=["admin", "clinician"])
    response = client.get(
        "/api/v1/capabilities/ui",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert response.json["error"] in ("invalid_request", "bad_request")
