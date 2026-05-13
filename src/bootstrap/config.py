import base64
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Operational settings
    service_name: str = "capabilities"
    env: str = "production"
    log_level: str = "info"
    port: int = 8018
    trusted_proxy_hops: int = Field(default=1, ge=0)

    # Input validation settings
    max_content_length: int = Field(default=16_384, gt=0)

    # Authorization settings
    capabilities_policies_dir: Path = Field(default=Path("policies"))
    capabilities_policy_cache_ttl: int = Field(default=60, ge=0)
    
    # JWT authentication settings
    jwt_public_key: str | None = Field(default=None)
    jwt_jwks_uri: str | None = Field(default=None)
    jwt_issuer: str = Field(default="https://neosofia.com")
    jwt_audience: str = Field(default="api.neosofia.com")

    # Rate limit settings
    rate_limit_storage_uri: str = "memory://"
    health_rate_limit: str = "600 per minute"

    # Gunicorn settings
    web_concurrency: int = Field(default=2, ge=1)
    gunicorn_threads: int = Field(default=2, ge=1)
    gunicorn_timeout: int = Field(default=30, ge=1)
    gunicorn_keepalive: int = Field(default=5, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    def model_post_init(self, __context: object) -> None:
        # Decode Base64 PEM keys passed in via environment variables
        if self.jwt_public_key and self.jwt_public_key != "DEFAULT_PUBLIC_KEY":
            try:
                decoded = base64.b64decode(self.jwt_public_key).decode("utf-8")
                object.__setattr__(self, "jwt_public_key", decoded)
            except Exception as e:
                # If it's already a PEM string (not base64), or we provided a JWKS URI, just continue
                if "BEGIN PUBLIC KEY" not in self.jwt_public_key:
                    raise ValueError(f"Failed to decode base64 jwt_public_key: {e}")


settings = Settings()  # type: ignore[call-arg]