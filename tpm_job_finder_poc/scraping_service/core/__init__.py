"""
Core components for the scraping service.

Contains base classes, orchestrator, and service registry components.
"""

from .base_job_source import (
    BaseJobSource,
    JobPosting,
    HealthCheckResult, 
    HealthStatus,
    RateLimitConfig,
    FetchParams,
    SourceType,
    SourceUnavailableError,
    AuthenticationError,
    RateLimitError,
    ConfigurationError
)
from .service_registry import ServiceRegistry, registry
from .orchestrator import ScrapingOrchestrator

__all__ = [
    "BaseJobSource",
    "JobPosting",
    "HealthCheckResult",
    "HealthStatus", 
    "RateLimitConfig",
    "FetchParams",
    "SourceType",
    "SourceUnavailableError",
    "AuthenticationError",
    "RateLimitError",
    "ConfigurationError",
    "ServiceRegistry",
    "registry",
    "ScrapingOrchestrator"
]
