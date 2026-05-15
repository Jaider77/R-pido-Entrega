"""
Configuration settings for notifications service
"""

import json
from typing import Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = (
        "postgresql://notif_user:notif_password@db-notificaciones:5432/notificaciones_db"
    )

    # Redis
    redis_url: str = "redis://redis-cache:6379/2"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq-broker:5672/"

    # Authentication Service
    auth_service_url: str = "http://auth-service:8000"

    # Service
    service_name: str = "notificaciones"
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

    # Email configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@rapido-entrega.com"

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
