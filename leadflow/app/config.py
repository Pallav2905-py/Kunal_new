"""
LeadFlow — Application Configuration
Loads from .env file. Never hardcode secrets.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "LeadFlow"
    app_version: str = "1.0.0"
    app_env: str = "development"
    log_level: str = "INFO"

    # Database
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "leadflow"

    # JWT
    jwt_secret_key: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    # Whisper
    whisper_model_size: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # File uploads
    upload_dir: str = "uploads/recordings"
    max_upload_size_mb: int = 100

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    @property
    def upload_path(self) -> Path:
        return Path(self.upload_dir)

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


def _find_env_file() -> Path | None:
    """Walk up directory tree looking for .env file."""
    current = Path(__file__).parent
    for _ in range(5):
        candidate = current / ".env"
        if candidate.exists():
            return candidate
        current = current.parent
    return None


def get_settings() -> Settings:
    env_file = _find_env_file()
    if env_file:
        return Settings(_env_file=str(env_file))
    return Settings()


# Global singleton
settings = get_settings()
