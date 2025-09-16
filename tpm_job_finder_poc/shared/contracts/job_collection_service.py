"""
Contracts for the Job Collection Service.

Defines interfaces for collecting, aggregating, and managing job postings
from multiple sources including API-based aggregators and browser scrapers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Protocol
import asyncio


class JobSourceType(Enum):
    """Types of job sources."""
    API_AGGREGATOR = "api_aggregator"
    BROWSER_SCRAPER = "browser_scraper"


class JobType(Enum):
    """Job classification types."""
    ENTRY_LEVEL = "entry_level"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    MANAGEMENT = "management"


@dataclass
class JobPosting:
    """Standardized job posting data structure."""
    id: str
    source: str
    title: str
    company: str
    location: Optional[str] = None
    url: Optional[str] = None
    date_posted: Optional[datetime] = None
    job_type: Optional[JobType] = None
    remote_friendly: bool = False
    tpm_keywords_found: int = 0
    raw_data: Optional[Dict[str, Any]] = None
    aggregated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "id": self.id,
            "source": self.source,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "url": self.url,
            "date_posted": self.date_posted.isoformat() if self.date_posted else None,
            "job_type": self.job_type.value if self.job_type else None,
            "remote_friendly": self.remote_friendly,
            "tpm_keywords_found": self.tpm_keywords_found,
            "raw_data": self.raw_data,
            "aggregated_at": self.aggregated_at.isoformat() if self.aggregated_at else None
        }


@dataclass
class JobQuery:
    """Parameters for job collection queries."""
    keywords: Optional[List[str]] = None
    location: Optional[str] = None
    max_jobs_per_source: int = 50
    sources: Optional[List[str]] = None
    include_remote: bool = True
    date_range_days: int = 7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "keywords": self.keywords,
            "location": self.location,
            "max_jobs_per_source": self.max_jobs_per_source,
            "sources": self.sources,
            "include_remote": self.include_remote,
            "date_range_days": self.date_range_days
        }


@dataclass
class CollectionResult:
    """Result from job collection operation."""
    jobs: List[JobPosting]
    total_jobs: int
    raw_jobs: int
    duplicates_removed: int
    sources_queried: List[str]
    successful_sources: List[str]
    failed_sources: List[str]
    collection_time: datetime
    duration_seconds: float
    errors: Dict[str, str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "jobs": [job.to_dict() for job in self.jobs],
            "total_jobs": self.total_jobs,
            "raw_jobs": self.raw_jobs,
            "duplicates_removed": self.duplicates_removed,
            "sources_queried": self.sources_queried,
            "successful_sources": self.successful_sources,
            "failed_sources": self.failed_sources,
            "collection_time": self.collection_time.isoformat(),
            "duration_seconds": self.duration_seconds,
            "errors": self.errors
        }


@dataclass
class SourceStatus:
    """Status information for a job source."""
    name: str
    type: JobSourceType
    enabled: bool
    healthy: bool
    last_check: Optional[datetime] = None
    error_message: Optional[str] = None
    jobs_collected_today: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "type": self.type.value,
            "enabled": self.enabled,
            "healthy": self.healthy,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_message": self.error_message,
            "jobs_collected_today": self.jobs_collected_today
        }


class IJobCollectionService(ABC):
    """Interface for job collection service operations."""
    
    @abstractmethod
    async def collect_jobs(self, query: JobQuery) -> CollectionResult:
        """
        Collect jobs from configured sources based on query parameters.
        
        Args:
            query: Job collection query parameters
            
        Returns:
            CollectionResult with jobs and metadata
            
        Raises:
            JobCollectionError: When job collection fails
            ValidationError: When query parameters are invalid
        """
        pass
    
    @abstractmethod
    async def run_daily_aggregation(self, query: JobQuery) -> CollectionResult:
        """
        Run complete daily job aggregation process.
        
        Args:
            query: Job collection query parameters
            
        Returns:
            CollectionResult with aggregated and processed jobs
            
        Raises:
            JobCollectionError: When aggregation fails
        """
        pass
    
    @abstractmethod
    async def get_source_statuses(self) -> List[SourceStatus]:
        """
        Get status information for all configured job sources.
        
        Returns:
            List of SourceStatus objects
        """
        pass
    
    @abstractmethod
    async def enable_source(self, source_name: str) -> bool:
        """
        Enable a specific job source.
        
        Args:
            source_name: Name of the source to enable
            
        Returns:
            True if source was enabled successfully
            
        Raises:
            SourceNotFoundError: When source doesn't exist
        """
        pass
    
    @abstractmethod
    async def disable_source(self, source_name: str) -> bool:
        """
        Disable a specific job source.
        
        Args:
            source_name: Name of the source to disable
            
        Returns:
            True if source was disabled successfully
            
        Raises:
            SourceNotFoundError: When source doesn't exist
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the job collection service.
        
        Returns:
            Health check status and details
        """
        pass
    
    @abstractmethod
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics and metrics.
        
        Returns:
            Dictionary with collection statistics
        """
        pass


class IJobStorage(Protocol):
    """Interface for job storage operations."""
    
    async def store_job(self, job: JobPosting) -> bool:
        """Store a single job posting."""
        ...
    
    async def store_jobs(self, jobs: List[JobPosting]) -> int:
        """Store multiple job postings."""
        ...
    
    async def get_job(self, job_id: str) -> Optional[JobPosting]:
        """Retrieve a job posting by ID."""
        ...
    
    async def search_jobs(self, query: JobQuery) -> List[JobPosting]:
        """Search stored job postings."""
        ...
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job posting."""
        ...
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        ...


class IJobEnricher(Protocol):
    """Interface for job enrichment operations."""
    
    def classify_job_type(self, title: str) -> JobType:
        """Classify job type based on title."""
        ...
    
    def detect_remote_work(self, location: str) -> bool:
        """Detect if job supports remote work."""
        ...
    
    def count_tpm_keywords(self, title: str, description: str = "") -> int:
        """Count TPM-related keywords in job posting."""
        ...
    
    def enrich_job(self, job: JobPosting) -> JobPosting:
        """Apply all enrichment to a job posting."""
        ...


# Custom exceptions
class JobCollectionError(Exception):
    """Base exception for job collection operations."""
    pass


class SourceNotFoundError(JobCollectionError):
    """Raised when a requested job source is not found."""
    pass


class ValidationError(JobCollectionError):
    """Raised when query parameters are invalid."""
    pass


class JobCollectionTimeoutError(JobCollectionError):
    """Raised when job collection times out."""
    pass


class DuplicateJobError(JobCollectionError):
    """Raised when attempting to store duplicate jobs."""
    pass