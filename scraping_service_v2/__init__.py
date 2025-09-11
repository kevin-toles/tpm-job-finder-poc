"""
Scraping Service v2 - Independent microservice for job data collection.

This service provides a modular, extensible architecture for job scraping
with support for both API-based connectors and browser-based scrapers.
"""

__version__ = "2.0.0"
__author__ = "TPM Job Finder Team"

from .core import (
    BaseJobSource,
    JobPosting,
    HealthStatus,
    FetchParams,
    ServiceRegistry,
    ScrapingOrchestrator,
    registry
)
from .scrapers import (
    BaseScraper,
    IndeedScraper,
    LinkedInScraper,
    ZipRecruiterScraper,
    GreenhouseScraper
)

__all__ = [
    "BaseJobSource",
    "JobPosting", 
    "HealthStatus",
    "FetchParams",
    "ServiceRegistry",
    "ScrapingOrchestrator",
    "registry",
    "BaseScraper",
    "IndeedScraper",
    "LinkedInScraper",
    "ZipRecruiterScraper",
    "GreenhouseScraper"
]
