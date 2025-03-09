import os
from pathlib import Path
from dotenv import load_dotenv

# Print current working directory
print(f"Current working directory: {os.getcwd()}")

# Try to load .env file
env_path = Path(".env")
load_result = load_dotenv(dotenv_path=env_path)
print(f"Load result: {load_result}")

# Check if we have required environment variables
required_vars = ["SECRET_KEY", "DATABASE_URL", "TEST_DATABASE_URL"]
for var in required_vars:
    print(f"{var}: {os.getenv(var, 'NOT FOUND')}")

# Try to load from absolute path
abs_env_path = Path(__file__).parent / ".env"
print(f"Absolute path: {abs_env_path}")
load_result = load_dotenv(dotenv_path=abs_env_path)
print(f"Load result from absolute path: {load_result}")

# Check again after absolute path load
for var in required_vars:
    print(f"{var}: {os.getenv(var, 'NOT FOUND')}") 