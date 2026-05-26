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

Production deploys from the **capabilities** GitHub repo (Railway watches `main`). Railway waits for the **`service-ci`** check suite to pass before deploying.

After each green `main` push, Railway builds the Dockerfile (runtime stage), pulling the UI policy bundle from `ghcr.io/neosofia/cdp-ui-policies:v0.1.0`.

**Verify a deploy landed:**

```bash
curl -s https://capabilities-production.up.railway.app/api/v1/capabilities
# → {"namespaces":["ui"]}
```

Required Railway variables:

| Variable | Example |
|----------|---------|
| `JWT_JWKS_URI` | `https://authentication.staging.neosofia.tech/.well-known/jwks.json` |
| `JWT_AUDIENCE` | `capabilities` |
| `FRONTEND_URL` | `https://staging.neosofia.tech` |
