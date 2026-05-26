import os
import subprocess
import time

import pytest
import requests
from testcontainers.core.container import DockerContainer

pytestmark = pytest.mark.integration

IMAGE_TAG = "capabilities-test:latest"
POLICY_IMAGE_TAG = "capabilities-test-policies:local"


def _build_policy_image(repo_root: str) -> None:
    """Build a scratch policy bundle image for the runtime stage."""
    policies_dir = os.path.join(repo_root, "tests/fixtures/policies")
    subprocess.run(
        [
            "docker",
            "build",
            "-f",
            os.path.join(policies_dir, "Dockerfile"),
            "-t",
            POLICY_IMAGE_TAG,
            policies_dir,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
    )


@pytest.fixture(scope="session", autouse=True)
def build_container_image():
    """Build the Docker image once per test session."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    policy_image = os.environ.get("POLICY_IMAGE", POLICY_IMAGE_TAG)
    if policy_image == POLICY_IMAGE_TAG:
        _build_policy_image(repo_root)
    subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"POLICY_IMAGE={policy_image}",
            "--target",
            "runtime",
            "-t",
            IMAGE_TAG,
            ".",
        ],
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
    container.with_env("JWT_PUBLIC_KEY", "DEFAULT_PUBLIC_KEY")
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



