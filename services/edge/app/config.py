# =============================================================================
# Edge Node Configuration
# =============================================================================
from __future__ import annotations
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    service_name: str = "edge"
    environment: str = "development"
    node_id: str = "edge-1"
    zone: str = "zone-alpha"
    sensors: str = "temperature,smoke,motion"
    redis_url: str = "redis://localhost:6379/0"
    kafka_bootstrap_servers: str = "localhost:9092"
    fog_node_url: str = "http://fog-node-1:8020"
    simulation_interval: int = 5

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
