"""Configuration classes for Job Normalizer Service.

This module defines configuration classes that control service behavior,
validation rules, and processing parameters.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator


class JobNormalizerServiceConfig(BaseModel):
    """Configuration for the Job Normalizer Service.
    
    This class defines service-level configuration that affects overall
    service behavior, resource limits, and default processing parameters.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra='forbid',
        use_enum_values=True
    )
    
    # Core service settings
    enable_deduplication: bool = Field(
        default=True,
        description="Enable automatic deduplication of jobs"
    )
    
    enable_field_normalization: bool = Field(
        default=True,
        description="Enable normalization of job fields (titles, salaries, etc.)"
    )
    
    enable_statistics: bool = Field(
        default=True,
        description="Enable collection of processing statistics"
    )
    
    # Processing limits
    max_batch_size: int = Field(
        default=1000,
        ge=1,
        description="Maximum number of jobs to process in a single batch"
    )
    
    processing_timeout_seconds: int = Field(
        default=300,
        ge=1,
        description="Maximum time allowed for processing a batch of jobs"
    )
    
    # Deduplication settings
    duplicate_detection_similarity_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for duplicate detection (0.0 to 1.0)"
    )
    
    # Normalization settings
    normalize_titles: bool = Field(
        default=True,
        description="Enable normalization of job titles"
    )
    
    normalize_salaries: bool = Field(
        default=True,
        description="Enable normalization of salary information"
    )
    
    normalize_locations: bool = Field(
        default=True,
        description="Enable normalization of location information"
    )
    
    # Data preservation
    preserve_original_data: bool = Field(
        default=True,
        description="Preserve original job data for comparison"
    )
    
    # Service health and monitoring
    health_check_interval_seconds: int = Field(
        default=60,
        ge=1,
        description="Interval for internal health checks"
    )
    
    # Performance tuning
    async_batch_processing: bool = Field(
        default=True,
        description="Enable asynchronous batch processing for better performance"
    )
    
    worker_pool_size: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of worker threads for parallel processing"
    )
    
    @field_validator('max_batch_size')
    @classmethod
    def validate_max_batch_size(cls, v):
        """Validate max_batch_size is reasonable."""
        if v > 10000:
            raise ValueError("max_batch_size cannot exceed 10,000 for performance reasons")
        return v
    
    @field_validator('processing_timeout_seconds')
    @classmethod
    def validate_processing_timeout(cls, v):
        """Validate processing timeout is reasonable."""
        if v > 3600:  # 1 hour
            raise ValueError("processing_timeout_seconds cannot exceed 3600 (1 hour)")
        return v