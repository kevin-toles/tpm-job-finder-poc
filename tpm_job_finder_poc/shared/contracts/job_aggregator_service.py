"""
Contracts for the Job Aggregator Service.

Defines interfaces for collecting jobs from multiple sources including
API-based aggregators and browser scrapers with deduplication and enrichment.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Protocol
import asyncio


class SourceType(Enum):
    """Types of job sources."""
    API_AGGREGATOR = "api_aggregator"
    BROWSER_SCRAPER = "browser_scraper"


class HealthStatus(Enum):
    """Source health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class SearchParams:
    """Search parameters for job aggregation."""
    keywords: Optional[str] = None
    location: Optional[str] = None
    remote_only: bool = False
    job_type: Optional[str] = None
    company: Optional[str] = None
    max_age_days: int = 7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "keywords": self.keywords,
            "location": self.location,
            "remote_only": self.remote_only,
            "job_type": self.job_type,
            "company": self.company,
            "max_age_days": self.max_age_days
        }


@dataclass
class AggregatedJob:
    """Standardized aggregated job posting."""
    id: str
    source: str
    source_type: SourceType
    title: str
    company: str
    location: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None
    salary: Optional[str] = None
    job_type: Optional[str] = None
    remote_friendly: bool = False
    tpm_keywords_found: int = 0
    date_posted: Optional[datetime] = None
    raw_data: Optional[Dict[str, Any]] = None
    aggregated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "source": self.source,
            "source_type": self.source_type.value,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "description": self.description,
            "salary": self.salary,
            "job_type": self.job_type,
            "remote_friendly": self.remote_friendly,
            "tpm_keywords_found": self.tpm_keywords_found,
            "date_posted": self.date_posted.isoformat() if self.date_posted else None,
            "raw_data": self.raw_data,
            "aggregated_at": self.aggregated_at.isoformat() if self.aggregated_at else None
        }


@dataclass
class SourceStatus:
    """Status information for a job source."""
    name: str
    type: SourceType
    status: HealthStatus
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None
    jobs_collected: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "type": self.type.value,
            "status": self.status.value,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_error": self.last_error,
            "jobs_collected": self.jobs_collected
        }


@dataclass
class AggregationResult:
    """Result of job aggregation operation."""
    jobs: List[AggregatedJob]
    total_collected: int
    total_deduplicated: int
    sources_used: List[str]
    duration_seconds: float
    errors: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "jobs": [job.to_dict() for job in self.jobs],
            "total_collected": self.total_collected,
            "total_deduplicated": self.total_deduplicated,
            "sources_used": self.sources_used,
            "duration_seconds": self.duration_seconds,
            "errors": self.errors or []
        }


# Exception classes
class JobAggregatorError(Exception):
    """Base exception for job aggregator errors."""
    pass


class SourceUnavailableError(JobAggregatorError):
    """Raised when a job source is unavailable."""
    pass


class RateLimitError(JobAggregatorError):
    """Raised when rate limits are exceeded."""
    pass


class ValidationError(JobAggregatorError):
    """Raised when input validation fails."""
    pass


# Service interface
class IJobAggregatorService(Protocol):
    """Interface for job aggregator service operations."""
    
    async def aggregate_jobs(self, 
                           search_params: SearchParams,
                           max_jobs_per_source: int = 50) -> AggregationResult:
        """
        Aggregate jobs from all configured sources.
        
        Args:
            search_params: Search criteria for job collection
            max_jobs_per_source: Maximum jobs to collect per source
            
        Returns:
            AggregationResult with collected and processed jobs
            
        Raises:
            ValidationError: If search parameters are invalid
            JobAggregatorError: If aggregation fails
        """
        ...
    
    async def get_source_statuses(self) -> List[SourceStatus]:
        """
        Get health status of all configured sources.
        
        Returns:
            List of source status information
        """
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform service health check.
        
        Returns:
            Health status information
        """
        ...
    
    def get_enabled_sources(self) -> Dict[str, List[str]]:
        """
        Get list of enabled sources by type.
        
        Returns:
            Dictionary mapping source types to source names
        """
        ...


# Storage interface
class IJobAggregatorStorage(Protocol):
    """Interface for job aggregator storage operations."""
    
    async def store_aggregation_result(self, result: AggregationResult) -> None:
        """Store aggregation result."""
        ...
    
    async def get_recent_aggregations(self, limit: int = 10) -> List[AggregationResult]:
        """Get recent aggregation results."""
        ...
    
    async def get_aggregation_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics."""
        ...