# =============================================================================
# Auth Service Configuration
# =============================================================================
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "auth"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://emergency_admin:emergency_secure_pass_2025@localhost:5432/emergency_auth"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    rsa_key_size: int = 2048

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
