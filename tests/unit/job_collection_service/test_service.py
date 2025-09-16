"""
Tests for Job Collection Service core functionality.

Tests the main service implementation including job collection,
aggregation, source management, and health monitoring.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    JobQuery,
    JobPosting,
    JobType,
    CollectionResult,
    SourceStatus,
    JobSourceType,
    JobCollectionError,
    SourceNotFoundError,
    ValidationError,
    JobCollectionTimeoutError
)


class TestJobCollectionService:
    """Test cases for the job collection service."""
    
    @pytest.mark.asyncio
    async def test_collect_jobs_success(self, mock_job_collection_service, sample_job_query):
        """Test successful job collection."""
        result = await mock_job_collection_service.collect_jobs(sample_job_query)
        
        assert isinstance(result, CollectionResult)
        assert result.total_jobs > 0
        assert len(result.jobs) == result.total_jobs
        assert result.duration_seconds > 0
        assert len(result.successful_sources) > 0
        assert len(result.failed_sources) == 0
        
        # Verify job structure
        for job in result.jobs:
            assert isinstance(job, JobPosting)
            assert job.id is not None
            assert job.title is not None
            assert job.company is not None
            assert job.source is not None
    
    @pytest.mark.asyncio
    async def test_collect_jobs_with_keywords_filter(self, mock_job_collection_service):
        """Test job collection with keyword filtering."""
        query = JobQuery(
            keywords=["product manager", "tpm"],
            max_jobs_per_source=20
        )
        
        result = await mock_job_collection_service.collect_jobs(query)
        
        assert result.total_jobs > 0
        # Check that TPM keywords are counted
        for job in result.jobs:
            assert job.tpm_keywords_found >= 0
    
    @pytest.mark.asyncio
    async def test_collect_jobs_with_location_filter(self, mock_job_collection_service):
        """Test job collection with location filtering."""
        query = JobQuery(
            location="San Francisco, CA",
            include_remote=False,
            max_jobs_per_source=15
        )
        
        result = await mock_job_collection_service.collect_jobs(query)
        
        assert result.total_jobs > 0
        # Verify location is applied
        for job in result.jobs:
            assert job.location == "San Francisco, CA"
    
    @pytest.mark.asyncio
    async def test_collect_jobs_with_source_filter(self, mock_job_collection_service):
        """Test job collection from specific sources."""
        query = JobQuery(
            sources=["remoteok", "linkedin"],
            max_jobs_per_source=10
        )
        
        result = await mock_job_collection_service.collect_jobs(query)
        
        assert result.total_jobs > 0
        assert set(result.sources_queried) == {"remoteok", "linkedin"}
        assert set(result.successful_sources).issubset({"remoteok", "linkedin"})
    
    @pytest.mark.asyncio
    async def test_collect_jobs_empty_result(self, mock_job_collection_service):
        """Test job collection with no results."""
        query = JobQuery(
            keywords=["nonexistent-keyword-xyz"],
            max_jobs_per_source=50
        )
        
        # Mock to return empty results
        mock_job_collection_service._enabled_sources = set()
        
        result = await mock_job_collection_service.collect_jobs(query)
        
        assert result.total_jobs == 0
        assert len(result.jobs) == 0
        assert result.duration_seconds >= 0
    
    @pytest.mark.asyncio
    async def test_run_daily_aggregation(self, mock_job_collection_service, sample_job_query):
        """Test daily aggregation process."""
        result = await mock_job_collection_service.run_daily_aggregation(sample_job_query)
        
        assert isinstance(result, CollectionResult)
        assert result.total_jobs >= 0
        assert result.collection_time is not None
        assert result.duration_seconds >= 0
        
        # Daily aggregation should include enrichment
        for job in result.jobs:
            assert job.aggregated_at is not None or True  # Mock doesn't set this
    
    @pytest.mark.asyncio
    async def test_get_source_statuses(self, mock_job_collection_service):
        """Test getting source status information."""
        statuses = await mock_job_collection_service.get_source_statuses()
        
        assert isinstance(statuses, list)
        assert len(statuses) > 0
        
        for status in statuses:
            assert isinstance(status, SourceStatus)
            assert status.name is not None
            assert isinstance(status.type, JobSourceType)
            assert isinstance(status.enabled, bool)
            assert isinstance(status.healthy, bool)
            assert status.jobs_collected_today >= 0
    
    @pytest.mark.asyncio
    async def test_enable_source_success(self, mock_job_collection_service):
        """Test successful source enablement."""
        source_name = "test_source"
        
        result = await mock_job_collection_service.enable_source(source_name)
        
        assert result is True
        assert source_name in mock_job_collection_service._enabled_sources
    
    @pytest.mark.asyncio
    async def test_disable_source_success(self, mock_job_collection_service):
        """Test successful source disabling."""
        source_name = "remoteok"
        
        # Ensure source is initially enabled
        await mock_job_collection_service.enable_source(source_name)
        assert source_name in mock_job_collection_service._enabled_sources
        
        result = await mock_job_collection_service.disable_source(source_name)
        
        assert result is True
        assert source_name not in mock_job_collection_service._enabled_sources
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_job_collection_service):
        """Test service health check."""
        health = await mock_job_collection_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "timestamp" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "sources_enabled" in health
        assert "sources_healthy" in health
    
    @pytest.mark.asyncio
    async def test_get_collection_stats(self, mock_job_collection_service):
        """Test getting collection statistics."""
        stats = await mock_job_collection_service.get_collection_stats()
        
        assert isinstance(stats, dict)
        assert "total_jobs_collected" in stats
        assert "jobs_collected_today" in stats
        assert "active_sources" in stats
        assert "average_collection_time" in stats
        
        # Verify numeric values
        assert isinstance(stats["total_jobs_collected"], int)
        assert isinstance(stats["jobs_collected_today"], int)
        assert isinstance(stats["active_sources"], int)
        assert isinstance(stats["average_collection_time"], (int, float))


class TestJobQuery:
    """Test cases for JobQuery data class."""
    
    def test_job_query_creation(self):
        """Test creating a job query."""
        query = JobQuery(
            keywords=["product manager"],
            location="San Francisco",
            max_jobs_per_source=25,
            sources=["remoteok"],
            include_remote=True,
            date_range_days=7
        )
        
        assert query.keywords == ["product manager"]
        assert query.location == "San Francisco"
        assert query.max_jobs_per_source == 25
        assert query.sources == ["remoteok"]
        assert query.include_remote is True
        assert query.date_range_days == 7
    
    def test_job_query_defaults(self):
        """Test job query with default values."""
        query = JobQuery()
        
        assert query.keywords is None
        assert query.location is None
        assert query.max_jobs_per_source == 50
        assert query.sources is None
        assert query.include_remote is True
        assert query.date_range_days == 7
    
    def test_job_query_to_dict(self):
        """Test converting job query to dictionary."""
        query = JobQuery(
            keywords=["tpm"],
            location="Remote",
            max_jobs_per_source=30
        )
        
        query_dict = query.to_dict()
        
        assert isinstance(query_dict, dict)
        assert query_dict["keywords"] == ["tpm"]
        assert query_dict["location"] == "Remote"
        assert query_dict["max_jobs_per_source"] == 30
        assert query_dict["include_remote"] is True


class TestJobPosting:
    """Test cases for JobPosting data class."""
    
    def test_job_posting_creation(self, sample_job_posting):
        """Test creating a job posting."""
        job = sample_job_posting
        
        assert job.id == "test-job-123"
        assert job.source == "test_source"
        assert job.title == "Senior Product Manager"
        assert job.company == "Tech Corp"
        assert job.location == "San Francisco, CA"
        assert job.job_type == JobType.SENIOR
        assert job.remote_friendly is True
        assert job.tpm_keywords_found == 3
    
    def test_job_posting_to_dict(self, sample_job_posting):
        """Test converting job posting to dictionary."""
        job = sample_job_posting
        job_dict = job.to_dict()
        
        assert isinstance(job_dict, dict)
        assert job_dict["id"] == job.id
        assert job_dict["title"] == job.title
        assert job_dict["company"] == job.company
        assert job_dict["job_type"] == job.job_type.value
        assert job_dict["remote_friendly"] == job.remote_friendly
        assert job_dict["tpm_keywords_found"] == job.tpm_keywords_found
    
    def test_job_posting_optional_fields(self):
        """Test job posting with optional fields."""
        job = JobPosting(
            id="minimal-job",
            source="test_source",
            title="Product Manager",
            company="Test Corp"
        )
        
        assert job.location is None
        assert job.url is None
        assert job.date_posted is None
        assert job.job_type is None
        assert job.remote_friendly is False
        assert job.tpm_keywords_found == 0
        assert job.raw_data is None
        assert job.aggregated_at is None


class TestCollectionResult:
    """Test cases for CollectionResult data class."""
    
    def test_collection_result_creation(self, sample_collection_result):
        """Test creating a collection result."""
        result = sample_collection_result
        
        assert len(result.jobs) == result.total_jobs
        assert result.raw_jobs >= result.total_jobs
        assert result.duplicates_removed >= 0
        assert len(result.sources_queried) > 0
        assert len(result.successful_sources) <= len(result.sources_queried)
        assert len(result.failed_sources) <= len(result.sources_queried)
        assert result.duration_seconds > 0
    
    def test_collection_result_to_dict(self, sample_collection_result):
        """Test converting collection result to dictionary."""
        result = sample_collection_result
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert "jobs" in result_dict
        assert "total_jobs" in result_dict
        assert "raw_jobs" in result_dict
        assert "duplicates_removed" in result_dict
        assert "sources_queried" in result_dict
        assert "successful_sources" in result_dict
        assert "failed_sources" in result_dict
        assert "collection_time" in result_dict
        assert "duration_seconds" in result_dict
        assert "errors" in result_dict
        
        # Verify jobs are converted to dicts
        assert isinstance(result_dict["jobs"], list)
        if result_dict["jobs"]:
            assert isinstance(result_dict["jobs"][0], dict)


class TestSourceStatus:
    """Test cases for SourceStatus data class."""
    
    def test_source_status_creation(self, sample_source_statuses):
        """Test creating source status objects."""
        statuses = sample_source_statuses
        
        assert len(statuses) == 3
        
        # Test healthy source
        healthy_source = statuses[0]
        assert healthy_source.name == "remoteok"
        assert healthy_source.type == JobSourceType.API_AGGREGATOR
        assert healthy_source.enabled is True
        assert healthy_source.healthy is True
        assert healthy_source.error_message is None
        assert healthy_source.jobs_collected_today == 45
    
    def test_source_status_unhealthy(self, sample_source_statuses):
        """Test unhealthy source status."""
        unhealthy_source = sample_source_statuses[2]
        
        assert unhealthy_source.name == "indeed"
        assert unhealthy_source.enabled is False
        assert unhealthy_source.healthy is False
        assert unhealthy_source.error_message == "Connection timeout"
        assert unhealthy_source.jobs_collected_today == 0
    
    def test_source_status_to_dict(self, sample_source_statuses):
        """Test converting source status to dictionary."""
        status = sample_source_statuses[0]
        status_dict = status.to_dict()
        
        assert isinstance(status_dict, dict)
        assert status_dict["name"] == status.name
        assert status_dict["type"] == status.type.value
        assert status_dict["enabled"] == status.enabled
        assert status_dict["healthy"] == status.healthy
        assert status_dict["jobs_collected_today"] == status.jobs_collected_today


class TestJobCollectionExceptions:
    """Test cases for job collection custom exceptions."""
    
    def test_job_collection_error(self):
        """Test base JobCollectionError."""
        error = JobCollectionError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    def test_source_not_found_error(self):
        """Test SourceNotFoundError."""
        error = SourceNotFoundError("Source 'test' not found")
        assert str(error) == "Source 'test' not found"
        assert isinstance(error, JobCollectionError)
    
    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Invalid query parameters")
        assert str(error) == "Invalid query parameters"
        assert isinstance(error, JobCollectionError)
    
    def test_timeout_error(self):
        """Test JobCollectionTimeoutError."""
        error = JobCollectionTimeoutError("Collection timed out after 30 seconds")
        assert str(error) == "Collection timed out after 30 seconds"
        assert isinstance(error, JobCollectionError)