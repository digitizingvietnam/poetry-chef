"""
deps.py

FastAPI dependency providers.

The Poetry Chef service is built once per process and shared across requests.
"""

from __future__ import annotations

from functools import lru_cache

from .service import PoetryChefService
from .settings import Settings, get_settings


@lru_cache()
def get_service() -> PoetryChefService:
    """Return the shared PoetryChefService instance."""
    return PoetryChefService(get_settings())


def get_app_settings() -> Settings:
    """Return the application settings."""
    return get_settings()
