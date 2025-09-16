"""
Shared Contracts Package

This package contains interface contracts and shared models for all microservices
in the TPM Job Finder POC application. These contracts define the boundaries
between services and ensure consistent APIs across the system.
"""

# Version information for contracts
__version__ = "1.0.0"

# Import all contracts for easy access
from .scraping_service import (
    IScrapingService,
    ScrapingConfig,
    ScrapingQuery,
    ScrapingResult,
    ScrapingStatistics,
    SourceHealth,
    ServiceNotStartedError,
    SourceNotFoundError,
    ScrapingTimeoutError,
    ServiceError,
    ConfigurationError
)

__all__ = [
    "IScrapingService",
    "ScrapingConfig",
    "ScrapingQuery", 
    "ScrapingResult",
    "ScrapingStatistics",
    "SourceHealth",
    "ServiceNotStartedError",
    "SourceNotFoundError",
    "ScrapingTimeoutError",
    "ServiceError",
    "ConfigurationError"
]