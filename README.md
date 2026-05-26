# Capabilities Service

Lightweight capabilities service for UI entitlement evaluation using Cedar.

Product deployments inject a policy bundle at runtime (for example, CDP mounts `cdp/policies/` locally, or production copies from the `cdp-ui-policies` image at build time). The bundle must include:

- `schema.cedar.json`
- `entitlements.json` — maps API keys to Cedar resources/actions, grouped by namespace
- one or more `*.cedar` policy files

## Design

This service is the platform **UI control plane**. It evaluates coarse `{ key: boolean }` entitlements for authenticated principals — menu visibility today; licensing and feature toggles in the future — using the same API contract.

**In scope:** generic evaluation engine, namespace-scoped HTTP API, manifest-driven entitlement keys, Cedar policy loading from an injected bundle.

**Out of scope:** product-specific menu or feature definitions (owned by the deploying product, e.g. CDP `policies/`), and complex request-scoped authorization (owned by each backend service's Cedar policies at the API boundary).

For the architectural decision and roadmap, see [CDP ADR 0012](https://github.com/Neosofia/cdp/blob/main/architecture/adrs/0012-ui-capabilities-control-plane.md).

Production images copy the bundle from **`cdp-ui-policies`** at build time (pinned in the Dockerfile) — the same pattern authentication uses for `sql-template`.

## Quickstart

```bash
uv sync
uv run --dev -m pytest -q
python -m gunicorn -c src/gunicorn.py src.app:app
```

## Endpoints

- `GET /health`
- `GET /api/v1/capabilities` — list capability namespaces from the loaded policy bundle
- `GET /api/v1/capabilities/{namespace}` — evaluate entitlements for the authenticated principal in that namespace (for example, `/api/v1/capabilities/ui`)

The machine-readable contract lives in `openapi.json`.

## Environment Variables

| Variable | Type | Default | Effect |
|---|---|---|---|
| `JWT_AUDIENCE` | string | `capabilities` | Audience to expect on JWT.  |
| `ENV` | string | `development` | Controls development/test behavior such as HTTPS enforcement. |
| `LOG_LEVEL` | string | `info` | Minimum structured log severity. |
| `PORT` | integer | `8019` | HTTP listener port. |
| `TRUSTED_PROXY_HOPS` | integer | `0` | Number of trusted reverse proxies for `ProxyFix`. |
| `CAPABILITIES_POLICIES_DIR` | path | `policies` | Directory containing Cedar policy files, `schema.cedar.json`, and `entitlements.json`. |
| `CAPABILITIES_POLICY_CACHE_TTL` | integer | `60` | Seconds to cache the loaded policy bundle in process. |
| `MAX_CONTENT_LENGTH` | integer | `16384` | Maximum accepted request body size in bytes. |
| `RATELIMIT_STORAGE_URI` | string | `memory://` | Rate-limit backend. Use Redis in multi-replica deployments. |
| `HEALTH_RATE_LIMIT` | string | `600 per minute` | Health endpoint rate limit. |
| `WEB_CONCURRENCY` | integer | `2` | Gunicorn worker count. |
| `GUNICORN_THREADS` | integer | `2` | Gunicorn thread count per worker. |
| `GUNICORN_TIMEOUT` | integer | `30` | Gunicorn worker timeout in seconds. |
| `GUNICORN_KEEPALIVE` | integer | `5` | Gunicorn keepalive in seconds. |
| `JWT_JWKS_URI` | string | | JWKS URI for token validation. |

## Testing

```bash
uv run --dev -m pytest -q
```
