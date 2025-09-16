"""Job Normalizer Service Implementation.

This module implements the JobNormalizerService class that provides
job normalization, validation, and deduplication functionality.
"""

import asyncio
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import traceback

from pydantic import ValidationError

from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig
from tpm_job_finder_poc.shared.contracts.job_normalizer_service import (
    IJobNormalizerService,
    JobNormalizationConfig,
    NormalizationResult,
    NormalizationStatistics,
    ServiceNotStartedError,
    NormalizationError,
    ServiceError
)
from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting

# Import existing normalizer functions
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_job, dedupe_jobs
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job


logger = logging.getLogger(__name__)


class JobNormalizerService(IJobNormalizerService):
    """Implementation of the Job Normalizer Service.
    
    This service provides comprehensive job normalization functionality including:
    - Job parsing and validation
    - Field normalization (titles, salaries, locations)
    - Deduplication
    - Batch processing
    - Statistics tracking
    - Health monitoring
    """
    
    def __init__(self, config: JobNormalizerServiceConfig):
        """Initialize the service with configuration.
        
        Args:
            config: Service configuration settings
        """
        self._config = config
        self._is_running = False
        self._start_time: Optional[datetime] = None
        self._executor: Optional[ThreadPoolExecutor] = None
        
        # Statistics tracking
        self._stats = NormalizationStatistics(
            total_jobs_processed=0,
            total_successful_normalizations=0,
            total_failed_normalizations=0,
            total_duplicates_removed=0,
            jobs_by_source={},
            average_processing_time=0.0,
            average_throughput=0.0,
            first_processing_time=None,
            last_processing_time=None
        )
        
        # Performance tracking
        self._processing_times: List[float] = []
        self._operation_count = 0
        self._total_response_time = 0.0
        
        logger.info(f"JobNormalizerService initialized with config: {config}")
    
    async def start(self) -> None:
        """Start the service and initialize resources."""
        if self._is_running:
            logger.warning("Service already running, ignoring start request")
            return
        
        try:
            # Initialize thread pool for parallel processing
            if self._config.async_batch_processing:
                self._executor = ThreadPoolExecutor(
                    max_workers=self._config.worker_pool_size,
                    thread_name_prefix="job_normalizer"
                )
            
            self._start_time = datetime.now(timezone.utc)
            self._is_running = True
            
            logger.info("JobNormalizerService started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start JobNormalizerService: {e}")
            raise ServiceError(f"Failed to start service: {e}") from e
    
    async def stop(self) -> None:
        """Stop the service and cleanup resources."""
        if not self._is_running:
            logger.warning("Service not running, ignoring stop request")
            return
        
        try:
            # Shutdown thread pool
            if self._executor:
                self._executor.shutdown(wait=True)
                self._executor = None
            
            self._is_running = False
            self._start_time = None
            
            logger.info("JobNormalizerService stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping JobNormalizerService: {e}")
            raise ServiceError(f"Failed to stop service: {e}") from e
    
    def is_running(self) -> bool:
        """Check if the service is currently running."""
        return self._is_running
    
    async def normalize_jobs(
        self,
        raw_jobs: List[Dict[str, Any]],
        source: str,
        config: Optional[JobNormalizationConfig] = None
    ) -> NormalizationResult:
        """Normalize a batch of raw job data.
        
        Args:
            raw_jobs: List of raw job dictionaries
            source: Source identifier for the jobs
            config: Optional operation-specific configuration
            
        Returns:
            NormalizationResult with processing details and normalized jobs
            
        Raises:
            ServiceNotStartedError: If service is not running
            NormalizationError: If normalization fails
        """
        if not self._is_running:
            raise ServiceNotStartedError("Service must be started before processing jobs")
        
        start_time = time.time()
        operation_config = config or JobNormalizationConfig()
        
        try:
            logger.info(f"Starting normalization of {len(raw_jobs)} jobs from source '{source}'")
            
            # Validate batch size
            if len(raw_jobs) > self._config.max_batch_size:
                raise NormalizationError(
                    f"Batch size {len(raw_jobs)} exceeds maximum allowed {self._config.max_batch_size}"
                )
            
            # Initialize result tracking
            total_input_jobs = len(raw_jobs)
            successful_normalizations = 0
            failed_normalizations = 0
            validation_errors = 0
            validation_error_details = []
            normalized_jobs = []
            
            # Parse and validate jobs
            for i, raw_job in enumerate(raw_jobs):
                try:
                    job = await self.parse_job(raw_job, source)
                    
                    # Apply field normalization if enabled
                    if (operation_config.enable_field_normalization and 
                        self._config.enable_field_normalization):
                        job = await self.normalize_job_fields(job)
                    
                    normalized_jobs.append(job)
                    successful_normalizations += 1
                    
                except ValidationError as e:
                    validation_errors += 1
                    failed_normalizations += 1
                    error_msg = f"Job at index {i}: {str(e)}"
                    validation_error_details.append(error_msg)
                    logger.warning(f"Validation error for job {i}: {e}")
                    
                except Exception as e:
                    failed_normalizations += 1
                    error_msg = f"Job at index {i}: Processing error - {str(e)}"
                    validation_error_details.append(error_msg)
                    logger.error(f"Processing error for job {i}: {e}")
            
            # Apply deduplication if enabled
            duplicates_removed = 0
            if (operation_config.enable_deduplication and 
                self._config.enable_deduplication):
                original_count = len(normalized_jobs)
                normalized_jobs = await self.deduplicate_jobs(normalized_jobs)
                duplicates_removed = original_count - len(normalized_jobs)
            
            # Calculate performance metrics
            processing_time = time.time() - start_time
            jobs_per_second = len(normalized_jobs) / processing_time if processing_time > 0 else 0
            
            # Calculate quality metrics
            data_quality_score = 1.0 if total_input_jobs == 0 else successful_normalizations / total_input_jobs
            completeness_score = 1.0 if total_input_jobs == 0 else (
                sum(1 for job in normalized_jobs if job.description is not None) / 
                len(normalized_jobs) if normalized_jobs else 0.0
            )
            
            # Convert validation error details to proper format
            validation_error_dict_details = []
            for error_msg in validation_error_details:
                validation_error_dict_details.append({
                    "error": error_msg,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
            
            # Update statistics
            if self._config.enable_statistics:
                await self._update_statistics(
                    total_input_jobs, successful_normalizations, 
                    failed_normalizations, duplicates_removed, 
                    source, processing_time
                )
            
            # Create result
            result = NormalizationResult(
                total_input_jobs=total_input_jobs,
                successful_normalizations=successful_normalizations,
                failed_normalizations=failed_normalizations,
                validation_errors=validation_errors,
                duplicates_removed=duplicates_removed,
                normalized_jobs=normalized_jobs,
                processing_time_seconds=processing_time,
                jobs_per_second=jobs_per_second,
                validation_error_details=validation_error_dict_details,
                data_quality_score=data_quality_score,
                completeness_score=completeness_score
            )
            
            logger.info(
                f"Normalization completed: {successful_normalizations} successful, "
                f"{failed_normalizations} failed, {duplicates_removed} duplicates removed, "
                f"processing time: {processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Normalization failed after {processing_time:.2f}s: {e}")
            if isinstance(e, (ServiceNotStartedError, NormalizationError)):
                raise
            raise NormalizationError(f"Normalization failed: {e}") from e
    
    async def parse_job(self, raw_job: Dict[str, Any], source: str) -> JobPosting:
        """Parse a raw job dictionary into a JobPosting object.
        
        Args:
            raw_job: Raw job dictionary
            source: Source identifier
            
        Returns:
            Parsed and validated JobPosting object
            
        Raises:
            ServiceNotStartedError: If service is not running
            ValidationError: If job data is invalid
        """
        if not self._is_running:
            raise ServiceNotStartedError("Service must be started before parsing jobs")
        
        try:
            # Use existing parser logic with source parameter
            job = parse_job(raw_job, source)
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to parse job from source '{source}': {e}")
            raise
    
    async def validate_job(self, raw_job: Dict[str, Any], source: str) -> bool:
        """Validate a raw job dictionary.
        
        Args:
            raw_job: Raw job dictionary to validate
            source: Source identifier
            
        Returns:
            True if job is valid, False otherwise
            
        Raises:
            ServiceNotStartedError: If service is not running
        """
        if not self._is_running:
            raise ServiceNotStartedError("Service must be started before validating jobs")
        
        try:
            await self.parse_job(raw_job, source)
            return True
        except (ValidationError, ValueError):
            return False
        except Exception:
            return False
    
    async def normalize_job_fields(self, job: JobPosting) -> JobPosting:
        """Normalize fields of a JobPosting object.
        
        Args:
            job: JobPosting object to normalize
            
        Returns:
            JobPosting with normalized fields
        """
        try:
            # Use existing normalizer logic
            normalized_job = normalize_job(job)
            return normalized_job
            
        except Exception as e:
            logger.error(f"Failed to normalize job fields for job {job.id}: {e}")
            # Return original job if normalization fails
            return job
    
    async def deduplicate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Remove duplicate jobs from a list.
        
        Args:
            jobs: List of JobPosting objects
            
        Returns:
            List of unique JobPosting objects
        """
        try:
            # Use existing deduplication logic
            unique_jobs = dedupe_jobs(jobs)
            return unique_jobs
            
        except Exception as e:
            logger.error(f"Failed to deduplicate jobs: {e}")
            # Return original list if deduplication fails
            return jobs
    
    async def get_statistics(self) -> NormalizationStatistics:
        """Get current processing statistics.
        
        Returns:
            Current NormalizationStatistics
            
        Raises:
            ServiceNotStartedError: If service is not running
        """
        if not self._is_running:
            raise ServiceNotStartedError("Service must be started before accessing statistics")
        
        return self._stats.model_copy()
    
    async def reset_statistics(self) -> None:
        """Reset all processing statistics.
        
        Raises:
            ServiceNotStartedError: If service is not running
        """
        if not self._is_running:
            raise ServiceNotStartedError("Service must be started before resetting statistics")
        
        self._stats = NormalizationStatistics(
            total_jobs_processed=0,
            total_successful_normalizations=0,
            total_failed_normalizations=0,
            total_duplicates_removed=0,
            jobs_by_source={},
            average_processing_time=0.0,
            average_throughput=0.0,
            first_processing_time=None,
            last_processing_time=None
        )
        
        self._processing_times.clear()
        self._operation_count = 0
        self._total_response_time = 0.0
        
        logger.info("Statistics reset successfully")
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get current service health status.
        
        Returns:
            Dictionary containing health status information
        """
        try:
            current_time = datetime.now(timezone.utc)
            
            # Calculate uptime
            uptime_seconds = 0
            if self._start_time:
                uptime_seconds = (current_time - self._start_time).total_seconds()
            
            # Calculate error rate
            error_rate = 0.0
            if self._stats.total_jobs_processed > 0:
                error_rate = (
                    self._stats.total_failed_normalizations / 
                    self._stats.total_jobs_processed
                )
            
            # Calculate average response time
            average_response_time = 0.0
            if self._operation_count > 0:
                average_response_time = self._total_response_time / self._operation_count
            
            health_status = {
                "status": "healthy" if self._is_running else "unhealthy",
                "is_running": self._is_running,
                "uptime_seconds": uptime_seconds,
                "memory_usage": "N/A",  # Could implement actual memory tracking
                "last_operation_time": self._stats.last_processing_time,
                "total_operations": self._operation_count,
                "error_rate": error_rate,
                "average_response_time": average_response_time
            }
            
            if not self._is_running:
                health_status["error"] = "Service not started"
            
            return health_status
            
        except Exception as e:
            logger.error(f"Failed to get health status: {e}")
            return {
                "status": "unhealthy",
                "is_running": False,
                "error": f"Health check failed: {e}"
            }
    
    async def _update_statistics(
        self,
        input_jobs: int,
        successful: int,
        failed: int,
        duplicates_removed: int,
        source: str,
        processing_time: float
    ) -> None:
        """Update internal statistics tracking.
        
        Args:
            input_jobs: Number of input jobs processed
            successful: Number of successful normalizations
            failed: Number of failed normalizations
            duplicates_removed: Number of duplicates removed
            source: Source identifier
            processing_time: Processing time in seconds
        """
        current_time = datetime.now(timezone.utc)
        
        # Update totals
        self._stats.total_jobs_processed += input_jobs
        self._stats.total_successful_normalizations += successful
        self._stats.total_failed_normalizations += failed
        self._stats.total_duplicates_removed += duplicates_removed
        
        # Update source tracking
        if source not in self._stats.jobs_by_source:
            self._stats.jobs_by_source[source] = 0
        self._stats.jobs_by_source[source] += input_jobs
        
        # Update timing statistics
        self._processing_times.append(processing_time)
        if len(self._processing_times) > 1000:  # Keep only recent times
            self._processing_times = self._processing_times[-1000:]
        
        self._stats.average_processing_time = sum(self._processing_times) / len(self._processing_times)
        
        # Update throughput
        if processing_time > 0:
            self._stats.average_throughput = successful / processing_time
        
        # Update timestamps
        if self._stats.first_processing_time is None:
            self._stats.first_processing_time = current_time
        self._stats.last_processing_time = current_time
        
        # Update operation tracking
        self._operation_count += 1
        self._total_response_time += processing_time