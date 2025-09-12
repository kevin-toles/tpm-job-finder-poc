"""
Base interfaces for all job sources in the scraping service.

Provides abstract base classes that define the contract for both
API connectors and browser-based scrapers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
import asyncio


class SourceType(Enum):
    """Types of job sources."""
    API_CONNECTOR = "api_connector"
    BROWSER_SCRAPER = "browser_scraper"


class HealthStatus(Enum):
    """Health check status for job sources."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class JobPosting:
    """Standardized job posting structure."""
    id: str
    source: str
    company: str
    title: str
    location: Optional[str] = None
    salary: Optional[str] = None
    url: Optional[str] = None
    date_posted: Optional[datetime] = None
    description: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "source": self.source,
            "company": self.company,
            "title": self.title,
            "location": self.location,
            "salary": self.salary,
            "url": self.url,
            "date_posted": self.date_posted.isoformat() if self.date_posted else None,
            "description": self.description,
            "raw_data": self.raw_data
        }


@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: float
    details: Optional[Dict[str, Any]] = None


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    backoff_factor: float = 2.0
    max_retries: int = 3


@dataclass
@dataclass
class FetchParams:
    """Parameters for job fetching operations."""
    keywords: Optional[List[str]] = None
    location: Optional[str] = None
    company_ids: Optional[List[str]] = None
    date_range: Optional[int] = 7  # days
    limit: Optional[int] = None
    offset: Optional[int] = 0
    filters: Optional[Dict[str, Any]] = None
    extra_params: Optional[Dict[str, Any]] = None  # For backward compatibility


class BaseJobSource(ABC):
    """
    Abstract base class for all job sources.
    
    Defines the contract that both API connectors and browser scrapers
    must implement to be part of the scraping service ecosystem.
    """
    
    def __init__(self, name: str, source_type: SourceType):
        self.name = name
        self.source_type = source_type
        self.enabled = True
        self._rate_limiter = None
        
    @abstractmethod
    async def fetch_jobs(self, params: FetchParams) -> List[JobPosting]:
        """
        Fetch jobs from this source.
        
        Args:
            params: Parameters for the job fetch operation
            
        Returns:
            List of standardized JobPosting objects
            
        Raises:
            SourceUnavailableError: When the source is temporarily unavailable
            AuthenticationError: When authentication fails
            RateLimitError: When rate limits are exceeded
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthCheckResult:
        """
        Perform a health check on this source.
        
        Returns:
            HealthCheckResult with current source status
        """
        pass
    
    @abstractmethod
    def get_rate_limits(self) -> RateLimitConfig:
        """
        Get the rate limiting configuration for this source.
        
        Returns:
            RateLimitConfig specifying the limits
        """
        pass
    
    @abstractmethod
    def get_supported_params(self) -> Dict[str, Any]:
        """
        Get the parameters supported by this source.
        
        Returns:
            Dictionary describing supported parameters and their types
        """
        pass
    
    async def initialize(self) -> bool:
        """
        Initialize the job source.
        
        Returns:
            True if initialization was successful
        """
        return True
    
    async def cleanup(self) -> None:
        """Clean up resources used by this source."""
        pass
    
    def is_enabled(self) -> bool:
        """Check if this source is enabled."""
        return self.enabled
    
    def enable(self) -> None:
        """Enable this source."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable this source."""
        self.enabled = False


class SourceUnavailableError(Exception):
    """Raised when a job source is temporarily unavailable."""
    pass


class AuthenticationError(Exception):
    """Raised when authentication with a job source fails."""
    pass


class RateLimitError(Exception):
    """Raised when rate limits are exceeded."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        super().__init__(message)
        self.retry_after = retry_after


class ConfigurationError(Exception):
    """Raised when there are configuration issues."""
    pass
