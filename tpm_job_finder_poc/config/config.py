import os
from dotenv import load_dotenv

load_dotenv()

class Config:
	ENV = os.getenv("ENV", "DEV")
	DEBUG = os.getenv("DEBUG", "false").lower() == "true"
	DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cache.db")
	SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
	# Feature flags for job source connectors
	
	@classmethod
	def get(cls, key: str, default=None):
		"""Get configuration value by key"""
		return getattr(cls, key, default)
	ENABLE_GREENHOUSE = os.getenv("ENABLE_GREENHOUSE", "true").lower() == "true"
	ENABLE_LEVER = os.getenv("ENABLE_LEVER", "true").lower() == "true"
	ENABLE_REMOTEOK = os.getenv("ENABLE_REMOTEOK", "true").lower() == "true"
	# Add more config variables as needed

config = Config()

# Stub for legacy tests
class ConfigManager:
	@classmethod
	def get(cls, key, default=None):
		return os.getenv(key, default)
	@classmethod
	def is_feature_enabled(cls, feature):
		return os.getenv(feature, "false").lower() == "true"
	@classmethod
	def all(cls):
		return dict(os.environ)