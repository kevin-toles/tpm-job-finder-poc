"""Scraping Service Contract Interface

This module defines the interface contract for the Scraping Service,
establishing the standard API for browser-based job data collection operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from enum import Enum

from tpm_job_finder_poc.scraping_service.core.base_job_source import JobPosting, SourceType


class ScrapingConfig(BaseModel):
    """Configuration for scraping operations."""
    
    # Browser Settings
    headless: bool = True
    timeout_seconds: int = 30
    max_retries: int = 3
    user_agent_rotation: bool = True
    
    # Anti-Detection Settings
    enable_anti_detection: bool = True
    delay_min_seconds: float = 1.0
    delay_max_seconds: float = 3.0
    viewport_randomization: bool = True
    javascript_protection: bool = True
    
    # Resource Management
    max_browser_instances: int = 5
    browser_instance_timeout: int = 300
    browser_memory_limit_mb: int = 1024
    cleanup_interval_seconds: int = 60
    
    # Rate Limiting (requests per minute)
    indeed_rate_limit: int = 10
    linkedin_rate_limit: int = 5
    ziprecruiter_rate_limit: int = 10
    greenhouse_rate_limit: int = 15
    
    # Performance Settings
    enable_parallel_processing: bool = True
    max_concurrent_scrapers: int = 3
    batch_size: int = 50
    
    # Error Handling
    fail_on_source_error: bool = False
    log_scraping_errors: bool = True
    skip_failed_sources: bool = True
    
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    @field_validator('delay_min_seconds', 'delay_max_seconds')
    @classmethod
    def validate_delays(cls, v):
        """Validate delay times are positive."""
        if v < 0:
            raise ValueError("delay times must be positive")
        return v
    
    @field_validator('timeout_seconds', 'max_retries')
    @classmethod
    def validate_positive_ints(cls, v):
        """Validate positive integer values."""
        if v <= 0:
            raise ValueError("value must be positive")
        return v


class ScrapingQuery(BaseModel):
    """Query parameters for scraping operations."""
    
    # Search Parameters
    keywords: List[str]
    location: Optional[str] = None
    company_names: Optional[List[str]] = None
    
    # Filters
    date_posted: Optional[Literal["today", "3days", "week", "2weeks", "month"]] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[Literal["full-time", "part-time", "contract", "internship"]] = None
    experience_level: Optional[Literal["entry", "mid", "senior", "executive"]] = None
    
    # Limits
    max_results: int = 50
    offset: int = 0
    
    # Source Selection
    sources: Optional[List[str]] = None  # If None, use all available sources
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )
    
    @field_validator('max_results')
    @classmethod
    def validate_max_results(cls, v):
        """Validate max_results is reasonable."""
        if v <= 0 or v > 1000:
            raise ValueError("max_results must be between 1 and 1000")
        return v
    
    @field_validator('keywords')
    @classmethod
    def validate_keywords(cls, v):
        """Validate keywords list is not empty."""
        if not v or all(not keyword.strip() for keyword in v):
            raise ValueError("keywords must contain at least one non-empty string")
        return [keyword.strip() for keyword in v if keyword.strip()]


class SourceHealth(BaseModel):
    """Health status for a scraping source."""
    
    source_name: str
    status: Literal["healthy", "degraded", "unhealthy", "unknown"]
    response_time_ms: float
    success_rate: float  # 0.0 to 1.0
    last_check: datetime
    error_message: Optional[str] = None
    last_successful_scrape: Optional[datetime] = None
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class ScrapingResult(BaseModel):
    """Result of scraping operation."""
    
    # Results
    jobs: List[JobPosting]
    
    # Query Information
    query: ScrapingQuery
    
    # Processing Statistics
    total_jobs_found: int
    jobs_after_deduplication: int
    duplicates_removed: int
    sources_queried: int
    successful_sources: int
    failed_sources: int
    
    # Performance Metrics
    processing_time_seconds: float
    average_response_time_ms: float
    
    # Source Results
    source_results: Dict[str, Dict[str, Any]]  # source_name -> {jobs: int, status: str, error: str}
    
    # Error Details
    errors: Dict[str, str]  # source_name -> error_message
    
    # Timestamp
    scraped_at: datetime
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class ScrapingStatistics(BaseModel):
    """Service-level scraping statistics."""
    
    # Lifetime Counts
    total_queries_processed: int = 0
    total_jobs_scraped: int = 0
    total_successful_scrapes: int = 0
    total_failed_scrapes: int = 0
    total_duplicates_removed: int = 0
    
    # Performance Metrics
    average_query_time: float = 0.0
    average_jobs_per_query: float = 0.0
    peak_throughput: float = 0.0  # jobs per minute
    
    # Source Statistics
    jobs_by_source: Dict[str, int] = {}
    errors_by_source: Dict[str, int] = {}
    success_rate_by_source: Dict[str, float] = {}
    
    # Browser Statistics
    total_browser_instances_created: int = 0
    average_browser_memory_usage_mb: float = 0.0
    browser_crashes: int = 0
    
    # Time Tracking
    first_scrape_time: Optional[datetime] = None
    last_scrape_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class IScrapingService(ABC):
    """Interface for Scraping Service.
    
    Defines the contract for browser-based job data collection operations.
    Implementations must provide lifecycle management, comprehensive error 
    handling, and detailed statistics tracking.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the scraping service.
        
        Initialize browser instances, validate configuration, register scrapers,
        and prepare for processing. Should be idempotent.
        
        Raises:
            ServiceError: If service fails to start properly
            ConfigurationError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the scraping service.
        
        Clean up browser instances, finalize any pending operations, and shut 
        down gracefully. Should be idempotent.
        
        Raises:
            ServiceError: If service fails to stop properly
        """
        pass
    
    @abstractmethod
    async def scrape_jobs(
        self, 
        query: ScrapingQuery,
        config: Optional[ScrapingConfig] = None
    ) -> ScrapingResult:
        """Scrape jobs based on query parameters.
        
        Execute browser-based scraping across multiple sources with the
        specified query parameters. Returns comprehensive results with statistics.
        
        Args:
            query: Scraping query with search parameters and source selection
            config: Optional configuration overrides for this operation
            
        Returns:
            ScrapingResult containing found jobs and processing statistics
            
        Raises:
            ServiceNotStartedError: If service is not started
            ValidationError: If query parameters are invalid
            ScrapingTimeoutError: If scraping operation times out
            ServiceError: If scraping fails across all sources
        """
        pass
    
    @abstractmethod
    async def get_available_sources(self) -> List[str]:
        """Get list of available scraping sources.
        
        Returns names of all registered and enabled scraping sources.
        
        Returns:
            List of source names (e.g., ["indeed", "linkedin", "ziprecruiter"])
            
        Raises:
            ServiceNotStartedError: If service is not started
        """
        pass
    
    @abstractmethod
    async def check_source_health(self, source_name: Optional[str] = None) -> Dict[str, SourceHealth]:
        """Check health status of scraping sources.
        
        Perform health checks on specified source or all sources if none specified.
        Returns detailed health information including response times and error rates.
        
        Args:
            source_name: Optional specific source to check (if None, check all)
            
        Returns:
            Dictionary mapping source names to SourceHealth objects
            
        Raises:
            ServiceNotStartedError: If service is not started
            SourceNotFoundError: If specified source doesn't exist
        """
        pass
    
    @abstractmethod
    async def enable_source(self, source_name: str) -> bool:
        """Enable a scraping source.
        
        Enable the specified scraping source for use in operations.
        
        Args:
            source_name: Name of the source to enable
            
        Returns:
            True if source was enabled successfully
            
        Raises:
            ServiceNotStartedError: If service is not started
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    @abstractmethod
    async def disable_source(self, source_name: str) -> bool:
        """Disable a scraping source.
        
        Disable the specified scraping source from use in operations.
        
        Args:
            source_name: Name of the source to disable
            
        Returns:
            True if source was disabled successfully
            
        Raises:
            ServiceNotStartedError: If service is not started
            SourceNotFoundError: If source doesn't exist
        """
        pass
    
    @abstractmethod
    async def get_source_capabilities(self, source_name: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """Get capabilities and supported parameters for sources.
        
        Returns information about what parameters and features each source supports.
        
        Args:
            source_name: Optional specific source (if None, return all sources)
            
        Returns:
            Dictionary mapping source names to capability information
            
        Raises:
            ServiceNotStartedError: If service is not started
            SourceNotFoundError: If specified source doesn't exist
        """
        pass
    
    @abstractmethod
    async def validate_query(self, query: ScrapingQuery) -> Dict[str, Any]:
        """Validate scraping query without executing it.
        
        Check if query parameters are valid and supported by selected sources.
        
        Args:
            query: Scraping query to validate
            
        Returns:
            Dictionary with validation results and any warnings
            
        Raises:
            ServiceNotStartedError: If service is not started
            ValidationError: If query is invalid
        """
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current service health status.
        
        Returns comprehensive health information including service state,
        browser instance status, recent performance metrics, and error rates.
        
        Returns:
            Dictionary containing health status information
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> ScrapingStatistics:
        """Get comprehensive service statistics.
        
        Returns detailed statistics about scraping operations including
        processing counts, performance metrics, source statistics, and error tracking.
        
        Returns:
            ScrapingStatistics object with comprehensive metrics
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """Check if service is currently running.
        
        Returns:
            True if service is started and ready for operations
        """
        pass
    
    @abstractmethod
    async def reset_statistics(self) -> None:
        """Reset all service statistics.
        
        Clear all accumulated statistics and metrics. Useful for testing
        or when starting fresh monitoring periods.
        
        Raises:
            ServiceNotStartedError: If service is not started
        """
        pass


class ServiceNotStartedError(Exception):
    """Raised when service operation is attempted before starting service."""
    pass


class SourceNotFoundError(Exception):
    """Raised when specified scraping source doesn't exist."""
    pass


class ScrapingTimeoutError(Exception):
    """Raised when scraping operation times out."""
    pass


class ServiceError(Exception):
    """Raised when service operations fail."""
    pass


class ConfigurationError(Exception):
    """Raised when service configuration is invalid."""
    pass