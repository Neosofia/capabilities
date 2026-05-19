# Capabilities Service

Lightweight capabilities service for UI entitlement evaluation using Cedar.

## Quickstart

```bash
uv sync
uv run --dev -m pytest -q
python -m gunicorn -c src/gunicorn.py src.app:app
```

## Endpoints

- `GET /health`
- `GET /api/v1/entitlements`

The machine-readable contract lives in `openapi.json`.

## Environment Variables

| Variable | Type | Default | Effect |
|---|---|---|---|
| `JWT_AUDIENCE` | string | `capabilities` | Audience to expect on JWT.  |
| `ENV` | string | `development` | Controls development/test behavior such as HTTPS enforcement. |
| `LOG_LEVEL` | string | `info` | Minimum structured log severity. |
| `PORT` | integer | `8019` | HTTP listener port. |
| `TRUSTED_PROXY_HOPS` | integer | `0` | Number of trusted reverse proxies for `ProxyFix`. |
| `CAPABILITIES_POLICIES_DIR` | path | `policies` | Directory containing Cedar policy files and schema. |
| `CAPABILITIES_POLICY_CACHE_TTL` | integer | `60` | Seconds to cache the loaded policy bundle in process. |
| `MAX_CONTENT_LENGTH` | integer | `16384` | Maximum accepted request body size in bytes. |
| `RATELIMIT_STORAGE_URI` | string | `memory://` | Rate-limit backend. Use Redis in multi-replica deployments. |
| `HEALTH_RATE_LIMIT` | string | `600 per minute` | Health endpoint rate limit. |
| `WEB_CONCURRENCY` | integer | `2` | Gunicorn worker count. |
| `GUNICORN_THREADS` | integer | `2` | Gunicorn thread count per worker. |
| `GUNICORN_TIMEOUT` | integer | `30` | Gunicorn worker timeout in seconds. |
| `GUNICORN_KEEPALIVE` | integer | `5` | Gunicorn keepalive in seconds. |
| `JWT_JWKS_URI` | string | | JWKS URI for token validation. |
| `JWT_ISSUER` | string | | Expected JWT issuer. |

## Testing

```bash
uv run --dev -m pytest -q
```
