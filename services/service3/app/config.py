"""
Configuration settings for service3
"""

import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "postgresql://service3_user:service3_password@db-service3:5432/service3_db"

    # Redis
    redis_url: str = "redis://redis-cache:6379/3"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq-broker:5672/"

    # Authentication Service
    auth_service_url: str = "http://auth-service:8000"

    # Service
    service_name: str = "service3"
    service_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # CORS
    allowed_origins: Any = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:80",
    ]

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
