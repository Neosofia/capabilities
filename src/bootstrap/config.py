import base64
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Operational settings
    service_name: str = "capabilities"
    env: str = "production"
    log_level: str = "info"
    port: int = 8019
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
    jwt_audience: str | list[str] = Field(default="capabilities")

    # Rate limit settings
    rate_limit_storage_uri: str = "memory://"
    health_rate_limit: str = "600 per minute"

    # Gunicorn settings
    web_concurrency: int = Field(default=2, ge=1)
    gunicorn_threads: int = Field(default=2, ge=1)
    gunicorn_timeout: int = Field(default=30, ge=1)
    
    # CORS settings
    frontend_url: str = Field(default="http://localhost:5173")
    gunicorn_keepalive: int = Field(default=5, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    @field_validator("jwt_audience", mode="before")
    def normalize_jwt_audience(cls, value: str | list[str] | None) -> list[str] | None:
        if value is None:
            return None
        if isinstance(value, str):
            return [entry.strip() for entry in value.split(",") if entry.strip()]
        return [entry.strip() for entry in value if isinstance(entry, str) and entry.strip()]

    @field_validator("jwt_public_key", mode="before")
    def decode_jwt_public_key(cls, value: str | None) -> str | None:
        if not value or value == "DEFAULT_PUBLIC_KEY":
            return value
        if "BEGIN PUBLIC KEY" in value:
            return value
        try:
            return base64.b64decode(value).decode("utf-8")
        except Exception as exc:
            raise ValueError(f"Failed to decode base64 jwt_public_key: {exc}") from exc


settings = Settings()  # type: ignore[call-arg]