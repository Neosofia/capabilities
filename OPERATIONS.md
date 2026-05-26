# Operations

## Local Development

1. Sync dependencies:

   ```bash
   uv sync
   ```

2. Run the test suite:

   ```bash
   uv run --dev -m pytest -q
   ```

3. Start the service locally:

   ```bash
   uv run --dev -m gunicorn -c src/gunicorn.py src.app:app
   ```

4. Check health:

   ```bash
   curl http://localhost:8019/health
   ```

5. Request entitlement evaluation:

   ```bash
   curl -H "Authorization: Bearer <token>" -H "X-Active-Role: admin" http://localhost:8019/api/v1/capabilities/ui
   ```

## Docker Build & Run

Build the runtime image from the capabilities repository. Production images copy the UI policy bundle from **`cdp-ui-policies`** at build time (pinned in the Dockerfile, same pattern as authentication + `sql-template`):

```bash
docker build --target runtime -t capabilities:test .
```

Publish a local policy bundle for prod-like testing:

```bash
docker build -f policies/Dockerfile -t cdp-ui-policies:local policies   # from CDP repo
```

Run the container:

```bash
docker run -d --rm -p 8019:8019 \
  -e ENV=development \
  -e JWT_PUBLIC_KEY="$(base64 < public.pem)" \
  --name capabilities-dev capabilities:test
```

Local CDP development volume-mounts `cdp/policies/` over `/app/policies` instead (see CDP `docker-compose.dev.yml`).

## Railway

Production deploys pull the CI-built image from GHCR (`ghcr.io/neosofia/capabilities:vX.Y.Z` and `:latest`). Railway does **not** receive webhooks when GHCR images are published — redeploy explicitly after each release.

**Manual redeploy (immediate):** Railway → capabilities service → **Redeploy**, with image `ghcr.io/neosofia/capabilities:vX.Y.Z` (or `:latest` after the release workflow has run).

**Automated redeploy (optional):** add repo secrets/variables and the `deploy-railway` job in `service-build-push.yml` will run `railway redeploy` after a green build:

| Name | Type | Value |
|------|------|-------|
| `RAILWAY_TOKEN` | secret | Project token from Railway → Project Settings → Tokens |
| `RAILWAY_SERVICE_ID` | variable | Service UUID from Railway service settings |
