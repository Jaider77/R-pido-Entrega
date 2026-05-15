"""
Configuration settings for routes service
"""

import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "postgresql://rutas_user:rutas_password@db-rutas:5432/rutas_db"

    # Redis
    redis_url: str = "redis://redis-cache:6379/1"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq-broker:5672/"

    # Authentication Service
    auth_service_url: str = "http://auth-service:8000"

    # Service
    service_name: str = "rutas"
    service_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # CORS
    allowed_origins: Any = ["http://localhost:3000", "http://localhost:80"]

    # Geolocation
    default_zoom_level: int = 12
    map_provider: str = "openstreetmap"

    @field_validator("allowed_origins", mode="before")
    def parse_allowed_origins(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return [item.strip() for item in value.split(",") if item.strip()]
        return value

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)


settings = Settings()
