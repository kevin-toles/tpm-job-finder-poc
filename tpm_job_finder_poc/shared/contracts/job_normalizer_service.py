"""Job Normalizer Service Contract Interface

This module defines the interface contract for the Job Normalizer Service,
establishing the standard API for job data normalization and validation operations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator

from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting


class JobNormalizationConfig(BaseModel):
    """Configuration for job normalization operations."""
    
    # Processing Options
    enable_deduplication: bool = True
    enable_field_normalization: bool = True
    enable_validation: bool = True
    preserve_original_data: bool = True
    
    # Normalization Settings
    normalize_titles: bool = True
    normalize_salaries: bool = True
    normalize_locations: bool = True
    
    # Deduplication Settings
    deduplication_strategy: str = "multi_level"  # "url_only", "content_hash", "multi_level"
    duplicate_detection_method: Literal["exact", "fuzzy", "smart"] = "fuzzy"
    similarity_threshold: float = 0.8
    case_sensitive_dedup: bool = False
    
    # Validation Settings
    strict_validation: bool = True
    allow_partial_data: bool = False
    require_descriptions: bool = False
    
    # Performance Settings
    batch_size: int = 1000
    enable_parallel_processing: bool = True
    max_workers: int = 4
    
    # Error Handling
    fail_on_validation_error: bool = False
    log_validation_errors: bool = True
    skip_invalid_jobs: bool = True
    
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid"
    )
    
    @field_validator('similarity_threshold')
    @classmethod
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        return v
    
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
        extra="forbid"
    )


class NormalizationResult(BaseModel):
    """Result of job normalization operation."""
    
    # Processed Jobs
    normalized_jobs: List[JobPosting]
    
    # Processing Statistics
    total_input_jobs: int
    successful_normalizations: int
    failed_normalizations: int
    duplicates_removed: int
    validation_errors: int
    
    # Processing Metrics
    processing_time_seconds: float
    jobs_per_second: float
    
    # Error Details
    validation_error_details: List[Dict[str, Any]]
    
    # Quality Metrics
    data_quality_score: float  # 0.0 to 1.0
    completeness_score: float  # 0.0 to 1.0
    
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True
    )


class NormalizationStatistics(BaseModel):
    """Service-level normalization statistics."""
    
    # Lifetime Counts
    total_jobs_processed: int = 0
    total_successful_normalizations: int = 0
    total_failed_normalizations: int = 0
    total_duplicates_removed: int = 0
    total_validation_errors: int = 0
    
    # Performance Metrics
    average_processing_time: float = 0.0
    average_throughput: float = 0.0  # jobs per second
    peak_throughput: float = 0.0
    
    # Quality Metrics
    average_data_quality_score: float = 0.0
    average_completeness_score: float = 0.0
    
    # Source Statistics
    jobs_by_source: Dict[str, int] = {}
    errors_by_source: Dict[str, int] = {}
    
    # Field Statistics
    normalized_fields_count: Dict[str, int] = {}
    validation_errors_by_field: Dict[str, int] = {}
    
    # Time Tracking
    first_processing_time: Optional[datetime] = None
    last_processing_time: Optional[datetime] = None
    
    model_config = ConfigDict(
        validate_assignment=True
    )


class IJobNormalizerService(ABC):
    """Interface for Job Normalizer Service.
    
    Defines the contract for job data normalization, validation, and deduplication
    operations. Implementations must provide lifecycle management, comprehensive
    error handling, and detailed statistics tracking.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """Start the job normalizer service.
        
        Initialize resources, validate configuration, and prepare for processing.
        Should be idempotent - multiple calls should not cause issues.
        
        Raises:
            ServiceError: If service fails to start properly
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the job normalizer service.
        
        Clean up resources, finalize any pending operations, and shut down gracefully.
        Should be idempotent - multiple calls should not cause issues.
        
        Raises:
            ServiceError: If service fails to stop properly
        """
        pass
    
    @abstractmethod
    async def normalize_jobs(
        self, 
        raw_jobs: List[Dict[str, Any]], 
        source: str,
        config: Optional[JobNormalizationConfig] = None
    ) -> NormalizationResult:
        """Normalize a batch of raw job data.
        
        Process raw job data through parsing, validation, normalization, and
        deduplication pipeline. Returns comprehensive results with statistics.
        
        Args:
            raw_jobs: List of raw job data dictionaries
            source: Source identifier for the jobs (e.g., "indeed", "linkedin")
            config: Optional configuration overrides for this operation
            
        Returns:
            NormalizationResult containing processed jobs and statistics
            
        Raises:
            ServiceNotStartedError: If service is not started
            ValidationError: If input data is invalid (when strict_validation=True)
            ServiceError: If processing fails
        """
        pass
    
    @abstractmethod
    async def parse_job(
        self, 
        raw_job: Dict[str, Any], 
        source: str
    ) -> JobPosting:
        """Parse and validate a single raw job.
        
        Convert raw job data into validated JobPosting object with proper
        type validation and business rule checking.
        
        Args:
            raw_job: Raw job data dictionary
            source: Source identifier for the job
            
        Returns:
            Validated JobPosting object
            
        Raises:
            ValidationError: If job data is invalid
            ServiceNotStartedError: If service is not started
        """
        pass
    
    @abstractmethod
    async def normalize_job_fields(self, job: JobPosting) -> JobPosting:
        """Normalize fields of a single job posting.
        
        Apply field-level normalization to title, salary, location, and other
        fields according to configured normalization rules.
        
        Args:
            job: JobPosting to normalize
            
        Returns:
            New JobPosting with normalized fields
            
        Raises:
            ServiceNotStartedError: If service is not started
            NormalizationError: If normalization fails
        """
        pass
    
    @abstractmethod
    async def deduplicate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate jobs from a list.
        
        Apply configured deduplication strategy to identify and remove
        duplicate job postings while preserving the best quality entries.
        
        Args:
            jobs: List of JobPosting objects to deduplicate
            
        Returns:
            List of unique JobPosting objects
            
        Raises:
            ServiceNotStartedError: If service is not started
        """
        pass
    
    @abstractmethod
    async def validate_job(self, raw_job: Dict[str, Any], source: str) -> bool:
        """Validate raw job data without parsing.
        
        Check if raw job data would pass validation without creating
        a JobPosting object. Useful for pre-filtering invalid data.
        
        Args:
            raw_job: Raw job data dictionary
            source: Source identifier for the job
            
        Returns:
            True if job data is valid, False otherwise
            
        Raises:
            ServiceNotStartedError: If service is not started
        """
        pass
    
    @abstractmethod
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current service health status.
        
        Returns comprehensive health information including service state,
        recent performance metrics, error rates, and system resources.
        
        Returns:
            Dictionary containing health status information
        """
        pass
    
    @abstractmethod
    async def get_statistics(self) -> NormalizationStatistics:
        """Get comprehensive service statistics.
        
        Returns detailed statistics about normalization operations including
        processing counts, performance metrics, quality scores, and error tracking.
        
        Returns:
            NormalizationStatistics object with comprehensive metrics
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


class NormalizationError(Exception):
    """Raised when job normalization fails."""
    pass


class ServiceError(Exception):
    """Raised when service operations fail."""
    pass