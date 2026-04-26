# =============================================================================
# Project Management Configuration
# =============================================================================
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "project_management"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://emergency_admin:emergency_secure_pass_2025@localhost:5432/emergency_project"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
