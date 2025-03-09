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

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[AnyHttpUrl]:
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Security
    SECRET_KEY: str

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


# Create global settings instance
settings = Settings() 