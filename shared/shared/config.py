# =============================================================================
# Shared Configuration Loader
# =============================================================================
from __future__ import annotations

import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class BaseServiceConfig(BaseSettings):
    """Base configuration shared by all microservices."""

    # Service identity
    service_name: str = "unknown"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # Database
    database_url: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"

    # JWT
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_config() -> BaseServiceConfig:
    """Get cached configuration instance."""
    return BaseServiceConfig()
