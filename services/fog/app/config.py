# =============================================================================
# Fog Node Configuration
# =============================================================================
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "fog"
    environment: str = "development"
    node_id: str = "fog-1"
    node_role: str = "primary"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    messaging_service_url: str = "http://messaging:8002"
    dsl_service_url: str = "http://dsl-engine:8005"
    prediction_service_url: str = "http://prediction:8004"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
