"""
Config & Secrets Manager for TPM Job Finder POC
Centralizes environment variable and .env file loading for all services.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
ENV_PATH = Path(__file__).parent.parent.parent / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)

class Config:
    @staticmethod
    def get(key: str, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def require(key: str):
        value = os.environ.get(key)
        if value is None:
            raise RuntimeError(f"Missing required config: {key}")
        return value

# Example usage:
# api_key = Config.get("OPENAI_API_KEY")
# db_url = Config.get("DB_URL", "sqlite:///dedupe_cache.db")
