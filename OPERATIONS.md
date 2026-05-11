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
   PYTHONPATH=. uv run --dev -m gunicorn -c src/gunicorn.py src.app:app
   ```

4. Check health:

   ```bash
   curl http://localhost:8019/health
   ```

5. Request entitlement evaluation:

   ```bash
   curl -H "Authorization: Bearer <token>" -H "X-Active-Role: admin" http://localhost:8019/api/v1/entitlements
   ```

## Docker Build & Run

In this monorepo, build from the repository root:

```bash
docker build -f authorization/Dockerfile --target runtime -t authorization-service:test .
```

Run the container locally with development settings:

```bash
docker run -d --rm -p 8019:8019 -e ENV=development --env-file .env.example --name authorization-service-dev authorization-service:test
```
