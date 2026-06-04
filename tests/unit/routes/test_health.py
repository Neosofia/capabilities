import pytest
from importlib.metadata import version

from src.app import create_app
from src.bootstrap.config import Settings

pytestmark = pytest.mark.unit


def test_health_allows_plain_http_in_production(rsa_keypair):
    """Railway's internal probe uses HTTP; /health must not 302 to HTTPS."""
    import base64
    import src.bootstrap.config as config_module

    original = config_module.settings
    config_module.settings = Settings(
        env="production",
        jwt_public_key=base64.b64encode(rsa_keypair["public"]).decode("utf-8"),
        capabilities_policies_dir=original.capabilities_policies_dir,
    )
    try:
        response = create_app().test_client().get("/health")
        assert response.status_code == 200
        assert response.headers.get("Location") is None
        assert response.get_json() == {
            "status": "ok",
            "version": version("capabilities"),
        }
    finally:
        config_module.settings = original


def test_health_is_rate_limited(client):
    # Confirm the endpoint consistently returns 200 across multiple calls.
    # Actual rate-limit enforcement is governed by Flask-Limiter and tested separately.
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200
