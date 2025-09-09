"""
Config & Secrets Manager Utility
Centralizes environment variables, tokens, and feature toggles for all runtime services.
For POC: loads from .env file using python-dotenv.
For MVP: ready to migrate to AWS/GCP managed secret store.
"""
import os
from dotenv import load_dotenv

# Load .env file at startup
load_dotenv()

class ConfigManager:
    """
    Centralized config and secrets manager.
    Usage:
        ConfigManager.get('API_KEY')
        ConfigManager.is_feature_enabled('NEW_FEATURE')
    """
    @staticmethod
    def get(key: str, default=None):
        return os.getenv(key, default)

    @staticmethod
    def is_feature_enabled(feature_name: str) -> bool:
        value = os.getenv(feature_name)
        if value is None:
            return False
        return value.lower() in ('1', 'true', 'yes', 'on')

    @staticmethod
    def all():
        return dict(os.environ)

# Example usage:
# API_KEY = ConfigManager.get('API_KEY')
# if ConfigManager.is_feature_enabled('EXPERIMENTAL_MODE'):
#     ...
