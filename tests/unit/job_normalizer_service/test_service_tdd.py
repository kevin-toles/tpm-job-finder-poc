"""Comprehensive TDD Test Suite for Job Normalizer Service

This test suite defines the complete service contract requirements for the
JobNormalizerService following TDD methodology (RED-GREEN-REFACTOR).

Test Categories:
1. Service Lifecycle Management
2. Job Parsing and Validation
3. Field Normalization
4. Deduplication Logic
5. Batch Processing
6. Error Handling
7. Statistics and Monitoring
8. Configuration Management
9. Performance Requirements
10. Health Monitoring
"""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from unittest.mock import AsyncMock, Mock, patch

# Service contract imports
from tpm_job_finder_poc.shared.contracts.job_normalizer_service import (
    IJobNormalizerService,
    JobNormalizationConfig,
    NormalizationResult,
    NormalizationStatistics,
    ServiceNotStartedError,
    NormalizationError,
    ServiceError
)

# Schema imports
from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting

# Service implementation import (will be implemented in GREEN phase)
from tpm_job_finder_poc.job_normalizer_service.service import JobNormalizerService
from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig


class TestJobNormalizerServiceLifecycle:
    """Test service lifecycle management (start/stop/health)."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        config = JobNormalizerServiceConfig()
        return JobNormalizerService(config)
    
    @pytest.mark.asyncio
    async def test_service_starts_successfully(self, service):
        """Test that service starts without errors."""
        # Arrange
        assert not service.is_running()
        
        # Act
        await service.start()
        
        # Assert
        assert service.is_running()
    
    @pytest.mark.asyncio
    async def test_service_stops_successfully(self, service):
        """Test that service stops without errors."""
        # Arrange
        await service.start()
        assert service.is_running()
        
        # Act
        await service.stop()
        
        # Assert
        assert not service.is_running()
    
    @pytest.mark.asyncio
    async def test_multiple_starts_are_idempotent(self, service):
        """Test that multiple start calls don't cause issues."""
        # Act
        await service.start()
        await service.start()  # Second start should be safe
        
        # Assert
        assert service.is_running()
    
    @pytest.mark.asyncio
    async def test_multiple_stops_are_idempotent(self, service):
        """Test that multiple stop calls don't cause issues."""
        # Arrange
        await service.start()
        
        # Act
        await service.stop()
        await service.stop()  # Second stop should be safe
        
        # Assert
        assert not service.is_running()
    
    @pytest.mark.asyncio
    async def test_service_not_started_error(self, service):
        """Test that operations fail when service not started."""
        # Arrange
        raw_job = {
            'id': 'test123',
            'title': 'Software Engineer',
            'company': 'Test Corp',
            'url': 'https://example.com/job/123',
            'date_posted': datetime.now(timezone.utc).isoformat()
        }
        
        # Act & Assert
        with pytest.raises(ServiceNotStartedError):
            await service.normalize_jobs([raw_job], "test")
        
        with pytest.raises(ServiceNotStartedError):
            await service.parse_job(raw_job, "test")
        
        with pytest.raises(ServiceNotStartedError):
            await service.get_statistics()


class TestJobParsingAndValidation:
    """Test job parsing, validation, and conversion to JobPosting objects."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_parse_valid_job_success(self, started_service):
        """Test parsing a valid job succeeds."""
        # Arrange
        raw_job = {
            'id': 'test123',
            'title': 'Software Engineer',
            'company': 'Test Corp',
            'url': 'https://example.com/job/123',
            'date_posted': datetime.now(timezone.utc).isoformat(),
            'location': 'San Francisco, CA',
            'salary': '$100,000'
        }
        
        # Act
        job = await started_service.parse_job(raw_job, "indeed")
        
        # Assert
        assert isinstance(job, JobPosting)
        assert job.id == 'test123'
        assert job.title == 'Software Engineer'
        assert job.company == 'Test Corp'
        assert job.source == 'indeed'
        assert job.location == 'San Francisco, CA'
        assert job.salary == '$100,000'
        assert str(job.url) == 'https://example.com/job/123'
    
    @pytest.mark.asyncio
    async def test_parse_job_with_minimal_required_fields(self, started_service):
        """Test parsing job with only required fields."""
        # Arrange
        raw_job = {
            'id': 'test456',
            'title': 'Product Manager',
            'company': 'Minimal Corp',
            'url': 'https://example.com/job/456',
            'date_posted': datetime.now(timezone.utc).isoformat()
        }
        
        # Act
        job = await started_service.parse_job(raw_job, "linkedin")
        
        # Assert
        assert job.id == 'test456'
        assert job.source == 'linkedin'
        assert job.location is None
        assert job.salary is None
    
    @pytest.mark.asyncio
    async def test_parse_job_missing_required_field_fails(self, started_service):
        """Test that parsing fails when required fields are missing."""
        # Arrange
        raw_job = {
            'title': 'Software Engineer',
            'company': 'Test Corp',
            # Missing 'id', 'url', 'date_posted'
        }
        
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            await started_service.parse_job(raw_job, "test")
    
    @pytest.mark.asyncio
    async def test_parse_job_invalid_url_fails(self, started_service):
        """Test that parsing fails with invalid URL."""
        # Arrange
        raw_job = {
            'id': 'test789',
            'title': 'Software Engineer',
            'company': 'Test Corp',
            'url': 'not-a-valid-url',
            'date_posted': datetime.now(timezone.utc).isoformat()
        }
        
        # Act & Assert
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            await started_service.parse_job(raw_job, "test")
    
    @pytest.mark.asyncio
    async def test_validate_job_success(self, started_service):
        """Test job validation returns True for valid data."""
        # Arrange
        valid_job = {
            'id': 'test123',
            'title': 'Software Engineer',
            'company': 'Test Corp',
            'url': 'https://example.com/job/123',
            'date_posted': datetime.now(timezone.utc).isoformat()
        }
        
        # Act
        is_valid = await started_service.validate_job(valid_job, "test")
        
        # Assert
        assert is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_job_failure(self, started_service):
        """Test job validation returns False for invalid data."""
        # Arrange
        invalid_job = {
            'title': 'Software Engineer',
            # Missing required fields
        }
        
        # Act
        is_valid = await started_service.validate_job(invalid_job, "test")
        
        # Assert
        assert is_valid is False


class TestFieldNormalization:
    """Test field-level normalization functionality."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_normalize_job_title(self, started_service):
        """Test job title normalization."""
        # Arrange
        job = JobPosting(
            id="test1",
            source="test",
            company="Test Corp",
            title="sr. software engineer",
            url="https://example.com/1",
            date_posted=datetime.now(timezone.utc)
        )
        
        # Act
        normalized_job = await started_service.normalize_job_fields(job)
        
        # Assert
        assert normalized_job.title == "Senior Software Engineer"
    
    @pytest.mark.asyncio
    async def test_normalize_job_salary(self, started_service):
        """Test salary normalization."""
        # Arrange
        job = JobPosting(
            id="test2",
            source="test",
            company="Test Corp",
            title="Engineer",
            url="https://example.com/2",
            date_posted=datetime.now(timezone.utc),
            salary="$100k-$150k"
        )
        
        # Act
        normalized_job = await started_service.normalize_job_fields(job)
        
        # Assert
        assert "$100,000" in normalized_job.salary
        assert "$150,000" in normalized_job.salary
    
    @pytest.mark.asyncio
    async def test_normalize_job_location(self, started_service):
        """Test location normalization."""
        # Arrange
        job = JobPosting(
            id="test3",
            source="test",
            company="Test Corp",
            title="Engineer",
            url="https://example.com/3",
            date_posted=datetime.now(timezone.utc),
            location="SF, CA"
        )
        
        # Act
        normalized_job = await started_service.normalize_job_fields(job)
        
        # Assert
        assert "San Francisco" in normalized_job.location
    
    @pytest.mark.asyncio
    async def test_normalize_preserves_other_fields(self, started_service):
        """Test that normalization preserves unchanged fields."""
        # Arrange
        job = JobPosting(
            id="test4",
            source="test",
            company="Test Corp",
            title="Engineer",
            url="https://example.com/4",
            date_posted=datetime.now(timezone.utc),
            description="A great job opportunity"
        )
        
        # Act
        normalized_job = await started_service.normalize_job_fields(job)
        
        # Assert
        assert normalized_job.id == job.id
        assert normalized_job.source == job.source
        assert normalized_job.company == job.company
        assert normalized_job.url == job.url
        assert normalized_job.date_posted == job.date_posted
        assert normalized_job.description == job.description


class TestDeduplication:
    """Test job deduplication logic."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_deduplicate_identical_urls(self, started_service):
        """Test deduplication removes jobs with identical URLs."""
        # Arrange
        job1 = JobPosting(
            id="1", source="test", company="Corp A", title="Engineer",
            url="https://example.com/job/1", date_posted=datetime.now(timezone.utc)
        )
        job2 = JobPosting(
            id="2", source="test", company="Corp A", title="Engineer",
            url="https://example.com/job/1", date_posted=datetime.now(timezone.utc)  # Same URL
        )
        
        # Act
        unique_jobs = await started_service.deduplicate_jobs([job1, job2])
        
        # Assert
        assert len(unique_jobs) == 1
        assert unique_jobs[0].url == job1.url
    
    @pytest.mark.asyncio
    async def test_deduplicate_same_company_title(self, started_service):
        """Test deduplication removes jobs with same company and title."""
        # Arrange
        job1 = JobPosting(
            id="1", source="test", company="Corp A", title="Software Engineer",
            url="https://example.com/job/1", date_posted=datetime.now(timezone.utc)
        )
        job2 = JobPosting(
            id="2", source="test", company="Corp A", title="Software Engineer",
            url="https://example.com/job/2", date_posted=datetime.now(timezone.utc)
        )
        
        # Act
        unique_jobs = await started_service.deduplicate_jobs([job1, job2])
        
        # Assert
        assert len(unique_jobs) == 1
    
    @pytest.mark.asyncio
    async def test_deduplicate_preserves_unique_jobs(self, started_service):
        """Test that unique jobs are preserved during deduplication."""
        # Arrange
        job1 = JobPosting(
            id="1", source="test", company="Corp A", title="Engineer",
            url="https://example.com/job/1", date_posted=datetime.now(timezone.utc)
        )
        job2 = JobPosting(
            id="2", source="test", company="Corp B", title="Manager",
            url="https://example.com/job/2", date_posted=datetime.now(timezone.utc)
        )
        
        # Act
        unique_jobs = await started_service.deduplicate_jobs([job1, job2])
        
        # Assert
        assert len(unique_jobs) == 2
    
    @pytest.mark.asyncio
    async def test_deduplicate_empty_list(self, started_service):
        """Test deduplication handles empty list."""
        # Act
        unique_jobs = await started_service.deduplicate_jobs([])
        
        # Assert
        assert unique_jobs == []


class TestBatchProcessing:
    """Test batch job normalization functionality."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_normalize_jobs_batch_success(self, started_service):
        """Test successful batch normalization."""
        # Arrange
        raw_jobs = [
            {
                'id': 'job1',
                'title': 'sr. engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat(),
                'salary': '$100k'
            },
            {
                'id': 'job2',
                'title': 'product mgr',
                'company': 'Corp B',
                'url': 'https://example.com/job/2',
                'date_posted': datetime.now(timezone.utc).isoformat(),
                'location': 'NYC'
            }
        ]
        
        # Act
        result = await started_service.normalize_jobs(raw_jobs, "indeed")
        
        # Assert
        assert isinstance(result, NormalizationResult)
        assert result.total_input_jobs == 2
        assert result.successful_normalizations == 2
        assert result.failed_normalizations == 0
        assert len(result.normalized_jobs) == 2
        assert result.processing_time_seconds > 0
        assert result.jobs_per_second > 0
    
    @pytest.mark.asyncio
    async def test_normalize_jobs_with_duplicates(self, started_service):
        """Test batch normalization removes duplicates."""
        # Arrange
        raw_jobs = [
            {
                'id': 'job1',
                'title': 'Engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat()
            },
            {
                'id': 'job2',
                'title': 'Engineer',
                'company': 'Corp A',  # Same company and title
                'url': 'https://example.com/job/2',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Act
        result = await started_service.normalize_jobs(raw_jobs, "linkedin")
        
        # Assert
        assert result.total_input_jobs == 2
        assert result.duplicates_removed == 1
        assert len(result.normalized_jobs) == 1
    
    @pytest.mark.asyncio
    async def test_normalize_jobs_with_invalid_data(self, started_service):
        """Test batch normalization handles invalid jobs."""
        # Arrange
        raw_jobs = [
            {
                'id': 'job1',
                'title': 'Valid Engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat()
            },
            {
                # Missing required fields
                'title': 'Invalid Job',
                'company': 'Corp B'
            }
        ]
        
        # Act
        result = await started_service.normalize_jobs(raw_jobs, "test")
        
        # Assert
        assert result.total_input_jobs == 2
        assert result.successful_normalizations == 1
        assert result.failed_normalizations == 1
        assert result.validation_errors == 1
        assert len(result.normalized_jobs) == 1
        assert len(result.validation_error_details) == 1
    
    @pytest.mark.asyncio
    async def test_normalize_jobs_empty_list(self, started_service):
        """Test batch normalization handles empty input."""
        # Act
        result = await started_service.normalize_jobs([], "test")
        
        # Assert
        assert result.total_input_jobs == 0
        assert result.successful_normalizations == 0
        assert len(result.normalized_jobs) == 0


class TestConfiguration:
    """Test service configuration management."""
    
    @pytest.mark.asyncio
    async def test_custom_configuration_applied(self):
        """Test that custom configuration is applied."""
        # Arrange
        config = JobNormalizerServiceConfig(
            enable_deduplication=False,
            enable_field_normalization=False
        )
        service = JobNormalizerService(config)
        await service.start()
        
        try:
            # Act
            raw_jobs = [
                {
                    'id': 'job1',
                    'title': 'sr. engineer',  # Should not be normalized
                    'company': 'Corp A',
                    'url': 'https://example.com/job/1',
                    'date_posted': datetime.now(timezone.utc).isoformat()
                }
            ]
            
            result = await service.normalize_jobs(raw_jobs, "test")
            
            # Assert
            assert len(result.normalized_jobs) == 1
            # Title should not be normalized due to config
            assert result.normalized_jobs[0].title == 'sr. engineer'
        
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_override_configuration_in_operation(self):
        """Test that configuration can be overridden per operation."""
        # Arrange
        service_config = JobNormalizerServiceConfig(enable_deduplication=True)
        service = JobNormalizerService(service_config)
        await service.start()
        
        try:
            operation_config = JobNormalizationConfig(enable_deduplication=False)
            
            raw_jobs = [
                {
                    'id': 'job1',
                    'title': 'Engineer',
                    'company': 'Corp A',
                    'url': 'https://example.com/job/1',
                    'date_posted': datetime.now(timezone.utc).isoformat()
                },
                {
                    'id': 'job2',
                    'title': 'Engineer',
                    'company': 'Corp A',  # Duplicate
                    'url': 'https://example.com/job/2',
                    'date_posted': datetime.now(timezone.utc).isoformat()
                }
            ]
            
            # Act
            result = await service.normalize_jobs(raw_jobs, "test", operation_config)
            
            # Assert
            # Duplicates should not be removed due to override config
            assert len(result.normalized_jobs) == 2
            assert result.duplicates_removed == 0
        
        finally:
            await service.stop()


class TestErrorHandling:
    """Test comprehensive error handling scenarios."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_normalization_error_handling(self, started_service):
        """Test handling of normalization errors."""
        # This test will be implemented based on specific error conditions
        # that arise during the GREEN phase implementation
        pass
    
    @pytest.mark.asyncio
    async def test_service_error_on_invalid_state(self, started_service):
        """Test service errors are raised appropriately."""
        # This test will be expanded based on specific error conditions
        pass


class TestStatisticsAndMonitoring:
    """Test service statistics and monitoring functionality."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_initial_statistics(self, started_service):
        """Test initial statistics are zero."""
        # Act
        stats = await started_service.get_statistics()
        
        # Assert
        assert isinstance(stats, NormalizationStatistics)
        assert stats.total_jobs_processed == 0
        assert stats.total_successful_normalizations == 0
        assert stats.total_failed_normalizations == 0
        assert stats.total_duplicates_removed == 0
        assert stats.average_processing_time == 0.0
        assert stats.average_throughput == 0.0
    
    @pytest.mark.asyncio
    async def test_statistics_updated_after_processing(self, started_service):
        """Test statistics are updated after job processing."""
        # Arrange
        raw_jobs = [
            {
                'id': 'job1',
                'title': 'Engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Act
        await started_service.normalize_jobs(raw_jobs, "test")
        stats = await started_service.get_statistics()
        
        # Assert
        assert stats.total_jobs_processed == 1
        assert stats.total_successful_normalizations == 1
        assert stats.jobs_by_source["test"] == 1
        assert stats.average_processing_time > 0
        assert stats.first_processing_time is not None
        assert stats.last_processing_time is not None
    
    @pytest.mark.asyncio
    async def test_statistics_accumulate_over_multiple_operations(self, started_service):
        """Test statistics accumulate over multiple operations."""
        # Arrange
        raw_jobs1 = [
            {
                'id': 'job1',
                'title': 'Engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
        ]
        raw_jobs2 = [
            {
                'id': 'job2',
                'title': 'Manager',
                'company': 'Corp B',
                'url': 'https://example.com/job/2',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
        ]
        
        # Act
        await started_service.normalize_jobs(raw_jobs1, "indeed")
        await started_service.normalize_jobs(raw_jobs2, "linkedin")
        stats = await started_service.get_statistics()
        
        # Assert
        assert stats.total_jobs_processed == 2
        assert stats.total_successful_normalizations == 2
        assert stats.jobs_by_source["indeed"] == 1
        assert stats.jobs_by_source["linkedin"] == 1
    
    @pytest.mark.asyncio
    async def test_reset_statistics(self, started_service):
        """Test statistics can be reset."""
        # Arrange
        raw_jobs = [
            {
                'id': 'job1',
                'title': 'Engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
        ]
        await started_service.normalize_jobs(raw_jobs, "test")
        
        # Act
        await started_service.reset_statistics()
        stats = await started_service.get_statistics()
        
        # Assert
        assert stats.total_jobs_processed == 0
        assert stats.total_successful_normalizations == 0
        assert len(stats.jobs_by_source) == 0


class TestHealthMonitoring:
    """Test service health monitoring functionality."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_health_status_when_running(self, started_service):
        """Test health status when service is running."""
        # Act
        health = await started_service.get_health_status()
        
        # Assert
        assert isinstance(health, dict)
        assert health["status"] == "healthy"
        assert health["is_running"] is True
        assert "uptime_seconds" in health
        assert "memory_usage" in health
        assert "last_operation_time" in health
        assert "total_operations" in health
        assert "error_rate" in health
    
    @pytest.mark.asyncio
    async def test_health_status_includes_performance_metrics(self, started_service):
        """Test health status includes performance metrics."""
        # Arrange - perform some operations first
        raw_jobs = [
            {
                'id': 'job1',
                'title': 'Engineer',
                'company': 'Corp A',
                'url': 'https://example.com/job/1',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
        ]
        await started_service.normalize_jobs(raw_jobs, "test")
        
        # Act
        health = await started_service.get_health_status()
        
        # Assert
        assert health["total_operations"] > 0
        assert health["average_response_time"] > 0
        assert health["last_operation_time"] is not None


class TestPerformanceRequirements:
    """Test performance requirements and benchmarks."""
    
    @pytest.fixture
    async def started_service(self):
        """Create and start service for testing."""
        config = JobNormalizerServiceConfig()
        service = JobNormalizerService(config)
        await service.start()
        yield service
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_large_batch_processing_performance(self, started_service):
        """Test processing large batches meets performance requirements."""
        # Arrange - create 100 jobs
        raw_jobs = []
        for i in range(100):
            raw_jobs.append({
                'id': f'job{i}',
                'title': f'Engineer {i}',
                'company': f'Corp {i}',
                'url': f'https://example.com/job/{i}',
                'date_posted': datetime.now(timezone.utc).isoformat()
            })
        
        # Act
        result = await started_service.normalize_jobs(raw_jobs, "performance_test")
        
        # Assert
        assert result.total_input_jobs == 100
        assert result.processing_time_seconds < 10.0  # Should process 100 jobs in under 10 seconds
        assert result.jobs_per_second > 10  # Should process at least 10 jobs per second
    
    @pytest.mark.asyncio
    async def test_concurrent_operations_performance(self, started_service):
        """Test concurrent operations don't significantly degrade performance."""
        # Arrange
        raw_jobs = [
            {
                'id': f'job{i}',
                'title': f'Engineer {i}',
                'company': f'Corp {i}',
                'url': f'https://example.com/job/{i}',
                'date_posted': datetime.now(timezone.utc).isoformat()
            }
            for i in range(10)
        ]
        
        # Act - run multiple operations concurrently
        tasks = [
            started_service.normalize_jobs(raw_jobs, f"source{i}")
            for i in range(3)
        ]
        results = await asyncio.gather(*tasks)
        
        # Assert
        assert len(results) == 3
        for result in results:
            assert result.successful_normalizations == 10
            assert result.processing_time_seconds < 5.0  # Each operation should complete quickly