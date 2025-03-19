import os
from pathlib import Path
from typing import List, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "IMLS Library Pulse"
    API_V1_STR: str = "/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api.log"

    # CORS
    CORS_ORIGINS: List[str] = []

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v or not v.strip():
                return []
            try:
                # Try to parse as JSON
                import json
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, treat as comma-separated
                return [origin.strip() for origin in v.split(",") if origin and origin.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Frontend URL for email links
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Email settings
    EMAILS_ENABLED: bool = os.getenv("EMAILS_ENABLED", "False").lower() == "true"
    EMAILS_FROM_EMAIL: str = os.getenv("EMAILS_FROM_EMAIL", "noreply@librarypulse.com")
    EMAILS_FROM_NAME: str = os.getenv("EMAILS_FROM_NAME", "Library Pulse")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_TLS: bool = os.getenv("SMTP_TLS", "True").lower() == "true"

    # Database
    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: PostgresDsn = None  # type: ignore

    # Data Settings
    IMLS_DATA_BASE_URL: str = "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"
    DATA_STORAGE_PATH: Path = Path("./data")

    @field_validator("DATA_STORAGE_PATH", mode="before")
    def validate_data_path(cls, v: Union[str, Path]) -> Path:
        if isinstance(v, str):
            path = Path(v)
        else:
            path = v
        
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)
        return path

    # Redis Settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "100/minute")
    RATE_LIMIT_LOGIN: str = os.getenv("RATE_LIMIT_LOGIN", "5/minute")
    RATE_LIMIT_REGISTER: str = os.getenv("RATE_LIMIT_REGISTER", "3/hour")
    RATE_LIMIT_PASSWORD_RESET: str = os.getenv("RATE_LIMIT_PASSWORD_RESET", "3/hour")
    RATE_LIMIT_EMAIL_VERIFY: str = os.getenv("RATE_LIMIT_EMAIL_VERIFY", "5/minute")


# Create global settings instance
settings = Settings() 