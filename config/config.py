import os
from dotenv import load_dotenv

load_dotenv()

class Config:
	ENV = os.getenv("ENV", "DEV")
	DEBUG = os.getenv("DEBUG", "false").lower() == "true"
	DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cache.db")
	SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
	# Feature flags for job source connectors
	ENABLE_GREENHOUSE = os.getenv("ENABLE_GREENHOUSE", "true").lower() == "true"
	ENABLE_LEVER = os.getenv("ENABLE_LEVER", "true").lower() == "true"
	ENABLE_REMOTEOK = os.getenv("ENABLE_REMOTEOK", "true").lower() == "true"
	# Add more config variables as needed

config = Config()