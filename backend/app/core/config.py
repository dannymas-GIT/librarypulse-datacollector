import os
from pathlib import Path
from typing import List, Union, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    PRODUCTION: bool = False
    PROJECT_NAME: str = "Library Lens"
    PROJECT_DESCRIPTION: str = "API for collecting and analyzing public library data through Library Lens"
    VERSION: str = "1.1.0"
    API_V1_STR: str = "/api/v1"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/api.log"

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list."""
        return [i.strip() for i in self.CORS_ORIGINS.split(",")]

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Frontend URL for email links
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Email settings
    EMAILS_ENABLED: bool = False
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    TEST_DATABASE_URL: str = "sqlite:///./test.db"

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
    REDIS_URL: str = "redis://localhost:6379/0"
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_REGISTER: str = "3/minute"
    RATE_LIMIT_PASSWORD_RESET: str = "3/minute"
    RATE_LIMIT_EMAIL_VERIFY: str = "3/minute"

    # Admin
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin"  # Change in production

    @field_validator("ENVIRONMENT", mode="after")
    def set_production(cls, v: str, info) -> str:
        if v and v.lower() == "production":
            info.data["PRODUCTION"] = True
        return v


# Create global settings instance
settings = Settings() 