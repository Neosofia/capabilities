import base64
import json
import os
from pathlib import Path

os.environ.setdefault("VALID_ACTORS", "operator,clinician,patient")

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jsonschema import validate
from jsonschema.validators import _RefResolver

from src.bootstrap.config import Settings

# Generate keys at module load time so they exist before ANY test imports
_PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_PUBLIC_KEY = _PRIVATE_KEY.public_key()

_PRIVATE_PEM = _PRIVATE_KEY.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption(),
)

_PUBLIC_PEM = _PUBLIC_KEY.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# Inject explicit test settings before the app (and its routes) are imported.
# Route modules bind `settings` at import time, so this must precede `create_app`.
import src.bootstrap.config as config_module

config_module.settings = Settings(
    env="test",
    jwt_public_key=base64.b64encode(_PUBLIC_PEM).decode("utf-8"),
    capabilities_policies_dir=Path(__file__).parent / "fixtures" / "policies",
    valid_actors="operator,clinician,patient",
)

from src.app import create_app  # noqa: E402


def encode_test_access_token(
    private_key,
    *,
    actors: list[str],
    audience: str | list[str] = "capabilities",
    sub: str = "user_123",
) -> str:
    import jwt
    import time

    now = int(time.time())
    payload: dict = {
        "sub": sub,
        "iss": "https://test.neosofia.com",
        "aud": audience,
        "neosofia:actors": actors,
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(payload, private_key, algorithm="RS256")


@pytest.fixture(scope="session")
def rsa_keypair():
    return {"private": _PRIVATE_PEM, "public": _PUBLIC_PEM}


@pytest.fixture
def app():
    application = create_app({"TESTING": True})
    return application


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def api_spec():
    spec_path = Path(__file__).parent.parent / "openapi.json"
    with open(spec_path) as f:
        return json.load(f)


@pytest.fixture
def validate_response():
    def _validate(spec, endpoint, method, status_code, data):
        try:
            schema = spec["paths"][endpoint][method]["responses"][str(status_code)]["content"]["application/json"]["schema"]
        except KeyError:
            return
        resolver = _RefResolver.from_schema(spec)
        validate(instance=data, schema=schema, resolver=resolver)

    return _validate
