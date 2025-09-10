"""Core configuration settings for the scraper service."""

from typing import Dict, Any
from pydantic import BaseSettings, Field
import json
from pathlib import Path

class ScraperConfig(BaseSettings):
    """Configuration for individual scrapers."""
    enabled: bool = True
    requests_per_minute: int = Field(10, ge=1)
    cache_enabled: bool = True
    cache_max_age: int = Field(3600, ge=0)
    proxy_enabled: bool = False
    browser_simulation_enabled: bool = True
    captcha_service_enabled: bool = False
    max_retries: int = Field(3, ge=0)

class Settings(BaseSettings):
    """Global settings for the scraper service."""
    config_path: str = Field("/app/config/scraper_config.json", env="CONFIG_PATH")
    scrapers: Dict[str, ScraperConfig] = {}

    class Config:
        env_prefix = "SCRAPER_"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_config()

    def load_config(self):
        """Load scraper configurations from JSON file."""
        config_path = Path(self.config_path)
        if config_path.exists():
            with open(config_path) as f:
                config_data = json.load(f)
                self.scrapers = {
                    source: ScraperConfig(**config)
                    for source, config in config_data.items()
                }

    def get_scraper_config(self, source: str) -> ScraperConfig:
        """Get configuration for a specific scraper."""
        if source not in self.scrapers:
            self.scrapers[source] = ScraperConfig()
        return self.scrapers[source]
