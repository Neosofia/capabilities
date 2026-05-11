import os
import subprocess
import time

import pytest
import requests
from testcontainers.core.container import DockerContainer

pytestmark = pytest.mark.integration

IMAGE_TAG = "service-template-test:latest"


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
    container.with_env("PORT", "7018")
    container.with_exposed_ports(7018)

    with container as c:
        port = c.get_exposed_port(7018)
        host = c.get_container_host_ip()
        url = f"http://{host}:{port}/health"

        start = time.time()
        while time.time() - start < 30:
            try:
                if requests.get(url, timeout=1).status_code == 200:
                    break
            except requests.exceptions.RequestException:
                time.sleep(0.5)
        else:
            pytest.fail("Container did not become ready in time.")

        yield f"http://{host}:{port}"


def test_container_health(app_container):
    """Container starts and the health endpoint returns 200."""
    res = requests.get(f"{app_container}/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}



