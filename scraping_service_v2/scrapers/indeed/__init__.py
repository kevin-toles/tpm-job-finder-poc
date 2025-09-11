"""
Indeed scraper module.

Exports the main Indeed scraper class and configuration.
"""

from .scraper import IndeedScraper
from .config import IndeedConfig, get_indeed_config

__all__ = [
    "IndeedScraper",
    "IndeedConfig",
    "get_indeed_config"
]
