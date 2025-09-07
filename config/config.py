import os
from dotenv import load_dotenv

load_dotenv()

class Config:
	ENV = os.getenv("ENV", "DEV")
	DEBUG = os.getenv("DEBUG", "false").lower() == "true"
	DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cache.db")
	SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
	# Add more config variables as needed

config = Config()