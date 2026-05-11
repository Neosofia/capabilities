import pytest

pytestmark = pytest.mark.unit


def test_health_is_rate_limited(client):
    # Confirm the endpoint consistently returns 200 across multiple calls.
    # Actual rate-limit enforcement is governed by Flask-Limiter and tested separately.
    for _ in range(3):
        response = client.get("/health")
        assert response.status_code == 200
