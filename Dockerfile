# Reference multi-stage Dockerfile for the Python capabilities service.
# Build this from the service directory:
#   docker build --target test .
#   docker build --target runtime -t capabilities:test .

# cedarpy 4.8.1 needs the glibc manylinux wheel for attribute-based policy evaluation.
ARG PYTHON_IMAGE=python:3.14-slim@sha256:2409290aa375de35f6492db84c700067d5c4c2aacfaf770c155d7528fb68bcf1

FROM ${PYTHON_IMAGE} AS build-base

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./pyproject.toml
COPY uv.lock ./uv.lock

FROM build-base AS prod-deps
RUN uv sync --frozen --no-dev --no-editable --no-install-project

FROM build-base AS test-deps
RUN uv sync --frozen --all-groups --no-editable --no-install-project

FROM test-deps AS test

COPY src ./src
COPY tests ./tests
COPY policies ./policies
COPY openapi.json ./openapi.json

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app"

RUN python -m pytest -q

FROM ${PYTHON_IMAGE} AS runtime

RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app

WORKDIR /app

COPY --from=prod-deps /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

COPY src ./src
COPY policies ./policies
COPY openapi.json ./openapi.json

EXPOSE 8018

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8019/health', timeout=3).raise_for_status()" || exit 1

USER app

CMD ["/bin/sh", "-c", "python -m gunicorn -c src/gunicorn.py src.app:app"]
