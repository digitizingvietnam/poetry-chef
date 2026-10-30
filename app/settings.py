"""
settings.py

Centralised application configuration.

All values are read from environment variables, or from a `.env` file in the
project root (see `.env.example` for the full list). No secrets are hardcoded.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Poetry Chef backend."""

    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    chat_model: str = Field("gpt-4o-mini", alias="CHAT_MODEL")
    data_dir: Path = Field(Path("data"), alias="DATA_DIR")
    allowed_origins: list[str] = Field(["*"], alias="ALLOWED_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("data_dir", mode="before")
    @classmethod
    def _expand_path(cls, value: str | Path) -> Path:
        return Path(value).expanduser().resolve()


@lru_cache()
def get_settings() -> Settings:
    """Return the process-wide settings instance."""
    return Settings()
