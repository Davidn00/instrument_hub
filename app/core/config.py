from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InstrumentHub"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    # Optional email notifications. Keep credentials outside source control.
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None
    alert_email_to: str | None = None
    smtp_starttls: bool = True

    api_v1_prefix: str = "/api/v1"

    database_url: str = (
        "postgresql+asyncpg://instrumenthub:instrumenthub@localhost:5432/instrumenthub"
    )

    database_echo: bool = False

    websocket_max_connections: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
