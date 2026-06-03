import os
import subprocess
import time

import pytest
import requests
from testcontainers.core.container import DockerContainer

pytestmark = [pytest.mark.integration, pytest.mark.slow]

IMAGE_TAG = "capabilities-test:latest"
SERVICE_PORT = 8019


@pytest.fixture(scope="session", autouse=True)
def build_container_image():
    """Build the Docker image once per test session."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    subprocess.run(
        ["docker", "build", "--target", "runtime", "-t", IMAGE_TAG, "."],
        cwd=repo_root,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    yield


@pytest.fixture(scope="module")
def app_container():
    """Spin up the built image and wait for the health endpoint to respond."""
    container = DockerContainer(IMAGE_TAG)
    container.with_env("ENV", "test")
    container.with_env("PORT", str(SERVICE_PORT))
    container.with_env("VALID_ACTORS", "operator,clinician,patient")
    container.with_env("JWT_PUBLIC_KEY", "DEFAULT_PUBLIC_KEY")
    container.with_exposed_ports(SERVICE_PORT)

    with container as c:
        port = c.get_exposed_port(SERVICE_PORT)
        host = c.get_container_host_ip()
        base_url = f"http://{host}:{port}"
        health_url = f"{base_url}/health"

        start = time.time()
        ready = False
        while time.time() - start < 60:
            try:
                res = requests.get(health_url, timeout=1)
                if res.status_code == 200:
                    ready = True
                    break
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        if not ready:
            logs = c.get_wrapped_container().logs(tail=50)
            pytest.fail(
                "Container did not become ready in time.\n" + logs.decode("utf-8", errors="replace")
            )

        yield base_url


def test_container_health(app_container):
    """Container starts and the health endpoint returns 200."""
    res = requests.get(f"{app_container}/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}
