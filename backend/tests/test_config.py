from typing import List
from app.core.config import Settings

class TestSettings(Settings):
    model_config = {"env_file": "tests/test.env", "env_file_encoding": "utf-8", "case_sensitive": True}
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

# Create test settings instance
test_settings = TestSettings() 