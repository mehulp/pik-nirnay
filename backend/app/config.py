"""Application configuration.

Settings are loaded from environment variables / a local .env file so that
provider credentials and deployment-specific values never live in source
control (see CLAUDE.md, Security and Safety).
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Pik Nirnay"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://pik_nirnay:pik_nirnay@localhost:5432/pik_nirnay"

    default_language: str = "mr"
    supported_languages: list[str] = ["mr", "en"]

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
