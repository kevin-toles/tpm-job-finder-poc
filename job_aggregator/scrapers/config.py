"""Configuration for job scrapers."""

from dataclasses import dataclass
from typing import Dict, Optional
import json
import os

@dataclass
class ScraperConfig:
    """Configuration for a single scraper."""
    enabled: bool
    requests_per_minute: int = 10
    cache_enabled: bool = True
    cache_max_age: int = 3600  # 1 hour in seconds
    proxy_enabled: bool = False
    browser_simulation_enabled: bool = True
    captcha_service_enabled: bool = False
    captcha_service_url: Optional[str] = None
    captcha_api_key: Optional[str] = None

class JobScraperConfig:
    """Configuration manager for all job scrapers."""
    
    DEFAULT_CONFIG = {
        "linkedin": {
            "enabled": True,
            "requests_per_minute": 10,
            "cache_enabled": True,
            "cache_max_age": 3600,
            "proxy_enabled": False,
            "browser_simulation_enabled": True,
            "captcha_service_enabled": False
        },
        "indeed": {
            "enabled": True,
            "requests_per_minute": 10,
            "cache_enabled": True,
            "cache_max_age": 3600,
            "proxy_enabled": False,
            "browser_simulation_enabled": True,
            "captcha_service_enabled": False
        },
        "ziprecruiter": {
            "enabled": True,
            "requests_per_minute": 10,
            "cache_enabled": True,
            "cache_max_age": 3600,
            "proxy_enabled": False,
            "browser_simulation_enabled": True,
            "captcha_service_enabled": False
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize scraper configuration.
        
        Args:
            config_file: Optional path to JSON config file
        """
        self.config_file = config_file
        self.config: Dict[str, ScraperConfig] = {}
        self._load_config()
        
    def _load_config(self):
        """Load configuration from file or use defaults."""
        config_data = self.DEFAULT_CONFIG.copy()
        
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Update only existing scraper configs
                    for scraper in self.DEFAULT_CONFIG:
                        if scraper in file_config:
                            config_data[scraper].update(file_config[scraper])
            except Exception as e:
                print(f"Error loading config file: {str(e)}")
                
        # Convert dict to ScraperConfig objects
        for scraper, settings in config_data.items():
            self.config[scraper] = ScraperConfig(**settings)
            
    def save_config(self):
        """Save current configuration to file."""
        if not self.config_file:
            return
            
        try:
            # Convert ScraperConfig objects to dict
            config_data = {
                scraper: {
                    "enabled": cfg.enabled,
                    "requests_per_minute": cfg.requests_per_minute,
                    "cache_enabled": cfg.cache_enabled,
                    "cache_max_age": cfg.cache_max_age,
                    "proxy_enabled": cfg.proxy_enabled,
                    "browser_simulation_enabled": cfg.browser_simulation_enabled,
                    "captcha_service_enabled": cfg.captcha_service_enabled,
                    "captcha_service_url": cfg.captcha_service_url,
                    "captcha_api_key": cfg.captcha_api_key
                }
                for scraper, cfg in self.config.items()
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
        except Exception as e:
            print(f"Error saving config file: {str(e)}")
            
    def is_enabled(self, scraper: str) -> bool:
        """Check if a scraper is enabled.
        
        Args:
            scraper: Name of the scraper to check
            
        Returns:
            True if scraper is enabled, False otherwise
        """
        return self.config.get(scraper, ScraperConfig(enabled=False)).enabled
        
    def get_config(self, scraper: str) -> Optional[ScraperConfig]:
        """Get configuration for a specific scraper.
        
        Args:
            scraper: Name of the scraper
            
        Returns:
            ScraperConfig if found, None otherwise
        """
        return self.config.get(scraper)
        
    def enable_scraper(self, scraper: str, save: bool = True):
        """Enable a specific scraper.
        
        Args:
            scraper: Name of the scraper to enable
            save: Whether to save config to file
        """
        if scraper in self.config:
            self.config[scraper].enabled = True
            if save and self.config_file:
                self.save_config()
                
    def disable_scraper(self, scraper: str, save: bool = True):
        """Disable a specific scraper.
        
        Args:
            scraper: Name of the scraper to disable
            save: Whether to save config to file
        """
        if scraper in self.config:
            self.config[scraper].enabled = False
            if save and self.config_file:
                self.save_config()
                
    def get_enabled_scrapers(self) -> Dict[str, ScraperConfig]:
        """Get all enabled scrapers and their configurations.
        
        Returns:
            Dict of enabled scraper names to their configurations
        """
        return {
            name: cfg 
            for name, cfg in self.config.items() 
            if cfg.enabled
        }
