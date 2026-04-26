# =============================================================================
# Gateway Configuration
# =============================================================================
from __future__ import annotations

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "gateway"
    environment: str = "development"
    log_level: str = "INFO"

    # Backend service URLs
    auth_service_url: str = "http://auth:8001"
    messaging_service_url: str = "http://messaging:8002"
    events_service_url: str = "http://events:8003"
    prediction_service_url: str = "http://prediction:8004"
    dsl_service_url: str = "http://dsl-engine:8005"
    project_service_url: str = "http://project-management:8006"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
