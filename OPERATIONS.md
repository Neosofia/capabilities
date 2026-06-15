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
   curl -H "Authorization: Bearer <token>" -H "X-Active-Role: operator" http://localhost:8019/api/v1/capabilities/ui
   ```

## Docker Build & Run

Build the runtime image from the capabilities repository. Production images copy the UI policy bundle from **`cdp-policies`** at build time via build arg **`POLICIES_IMAGE`** (default in the Dockerfile, same pattern as authentication + `sql-template`):

```bash
docker build --target runtime -t capabilities:test .
# Or pin explicitly:
docker build --target runtime --build-arg POLICIES_IMAGE=ghcr.io/neosofia/cdp-policies:v0.2.0 -t capabilities:test .
```

Publish a local policy bundle for prod-like testing:

```bash
docker build -f policies/Dockerfile -t cdp-policies:local policies   # from CDP repo
```

Run the container:

```bash
docker run -d --rm -p 8019:8019 \
  -e ENV=development \
  -e JWT_PUBLIC_KEY="$(base64 < public.pem)" \
  --name capabilities-dev capabilities:test
```

Local CDP development builds `cdp-policies:local` and passes `POLICIES_IMAGE` at image build; compose may volume-mount `cdp/policies/capabilities/` over `/app/policies` for hot-reload (see CDP `docker-compose.local.yml` and `docker-compose.dev.yml`). Runtime config belongs in `.capabilities.env`, not inline in compose.

## Public cloud deployment

Shared guidance — why local JWKS differs from cloud, two traffic planes, JWT audience coupling, healthcheck probes, operational gotchas, and a Railway staging example — lives in the infrastructure repo:

**→ [public-cloud/OPERATIONS.md](https://github.com/Neosofia/infrastructure/blob/main/public-cloud/OPERATIONS.md)**

### Capabilities-specific notes

- **CI / deploy:** Railway watches `main`; waits for **`service-ci`** before deploy. Runtime image pulls UI policies from `ghcr.io/neosofia/cdp-policies:vX.Y.Z` at build time.
- **Local JWKS:** `JWT_JWKS_URI=http://authentication:8014/.well-known/jwks.json` (see CDP `.capabilities.env.sample`).
- **Cloud JWKS audience:** `JWT_AUDIENCE=capabilities`; authentication must list `capabilities` in `JWT_WEB_AUDIENCE`.
- **Healthcheck:** `/health` exempt from Talisman HTTPS redirect since **v0.5.8+**.
- **CORS preflight cache:** OPTIONS responses include `Access-Control-Max-Age: 86400` (24 h; Chrome caps at 2 h) so browsers cache cross-origin preflights.
- **Verify:**

```bash
curl -s https://<capabilities-host>/health
curl -s https://<capabilities-host>/api/v1/capabilities
curl -s -H "Authorization: Bearer <token>" -H "X-Active-Role: operator" \
  https://<capabilities-host>/api/v1/capabilities/ui
```

