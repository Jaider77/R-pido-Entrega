"""
Configuration settings for authentication service
"""

import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "postgresql://auth_user:auth_password@db-auth:5432/auth_db"

    # Redis
    redis_url: str = "redis://redis-cache:6379/0"

    # JWT
    jwt_secret: str = "your-super-secret-key-change-in-production-12345"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24

    # Service
    service_name: str = "authentication"
    service_port: int = 8000
    debug: bool = False
    log_level: str = "INFO"

    # CORS
    allowed_origins: Any = ["http://localhost:3000", "http://localhost:80"]

    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

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
