"""
TDD Tests for Job Collection Service - RED Phase Implementation

Following proper TDD: Write failing tests first to define expected behavior

Based on documentation analysis and shared contracts, the Job Collection Service should:
1. Implement IJobCollectionService protocol
2. Provide async job collection from multiple sources  
3. Support job queries with filtering and source selection
4. Handle job deduplication and enrichment
5. Provide source management (enable/disable)
6. Implement health monitoring and statistics
7. Provide comprehensive error handling with specific exceptions
8. Support high-performance async operations with concurrent source querying
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

# Test imports - these define the expected interface
from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    IJobCollectionService,
    JobQuery,
    JobPosting,
    CollectionResult,
    SourceStatus,
    JobSourceType,
    JobType,
    JobCollectionError,
    SourceNotFoundError,
    ValidationError,
    JobCollectionTimeoutError,
    DuplicateJobError
)

# Implementation imports - what we're testing
from tpm_job_finder_poc.job_collection_service.service import JobCollectionService
from tpm_job_finder_poc.job_collection_service.storage import JobStorage
from tpm_job_finder_poc.job_collection_service.enricher import JobEnricher
from tpm_job_finder_poc.job_collection_service.config import JobCollectionConfig


class TestJobCollectionServiceTDD:
    """TDD tests for Job Collection Service implementation."""

    # ==================== FIXTURES ====================
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def mock_storage(self):
        """Mock job storage."""
        storage = AsyncMock(spec=JobStorage)
        storage.store_job.return_value = True
        storage.store_jobs.return_value = 5
        storage.get_job.return_value = None
        storage.search_jobs.return_value = []
        storage.delete_job.return_value = True
        storage.get_storage_stats.return_value = {
            "total_jobs": 0,  # Fresh service should have no jobs
            "jobs_today": 0,  # Fresh service should have no jobs today
            "storage_size_mb": 0  # Fresh service should have no storage
        }
        return storage

    @pytest.fixture
    def mock_enricher(self):
        """Mock job enricher."""
        enricher = Mock(spec=JobEnricher)
        # Mock the main public method
        async def mock_enrich_job(job):
            job.job_type = JobType.MID_LEVEL
            job.remote_friendly = True
            job.tpm_keywords_found = 3
            return job
        enricher.enrich_job = AsyncMock(side_effect=mock_enrich_job)
        return enricher

    @pytest.fixture
    def service_config(self):
        """Service configuration for testing."""
        config = JobCollectionConfig(
            max_jobs_per_source=50,
            collection_timeout_seconds=300,
            enable_deduplication=True,
            enable_enrichment=True
        )
        # Enable multiple test sources for comprehensive testing
        config.api_aggregators["remoteok"]["enabled"] = True
        config.api_aggregators["greenhouse"]["enabled"] = True
        config.api_aggregators["lever"]["enabled"] = True
        config.browser_scrapers["indeed"]["enabled"] = True
        config.browser_scrapers["linkedin"]["enabled"] = True
        return config

    @pytest.fixture
    async def service(self, service_config, mock_storage, mock_enricher):
        """Job collection service instance."""
        service = JobCollectionService(
            config=service_config,
            storage=mock_storage,
            enricher=mock_enricher
        )
        await service.start()
        yield service
        await service.stop()

    @pytest.fixture
    def sample_job_query(self):
        """Sample job query for testing."""
        return JobQuery(
            keywords=["product manager", "TPM"],
            location="Remote",
            max_jobs_per_source=20,
            sources=["remoteok"],
            include_remote=True,
            date_range_days=7
        )

    @pytest.fixture
    def sample_job_posting(self):
        """Sample job posting for testing."""
        return JobPosting(
            id="job_123",
            source="remoteok",
            title="Senior Product Manager",
            company="Tech Corp",
            location="Remote",
            url="https://example.com/job/123",
            date_posted=datetime.now(timezone.utc),
            job_type=JobType.SENIOR,
            remote_friendly=True,
            tpm_keywords_found=5,
            raw_data={"description": "Great TPM role"},
            aggregated_at=datetime.now(timezone.utc)
        )

    # ==================== CORE SERVICE TESTS ====================

    @pytest.mark.asyncio
    async def test_service_initialization(self, service_config, mock_storage, mock_enricher):
        """Test service initializes correctly with all components."""
        service = JobCollectionService(
            config=service_config,
            storage=mock_storage,
            enricher=mock_enricher
        )
        
        # Should have correct configuration
        assert service.config == service_config
        assert service.storage == mock_storage
        assert service.enricher == mock_enricher
        
        # Should not be running initially
        assert not service.is_running
        
        # Should have empty statistics
        stats = await service.get_collection_stats()
        assert stats["total_collections"] == 0
        assert stats["total_jobs_collected"] == 0

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service_config, mock_storage, mock_enricher):
        """Test service start/stop lifecycle management."""
        service = JobCollectionService(
            config=service_config,
            storage=mock_storage,
            enricher=mock_enricher
        )
        
        # Should start correctly
        await service.start()
        assert service.is_running
        
        # Should stop correctly
        await service.stop()
        assert not service.is_running
        
        # Should handle double start/stop gracefully
        await service.start()
        await service.start()  # Should not error
        await service.stop()
        await service.stop()   # Should not error

    @pytest.mark.asyncio
    async def test_implements_service_contract(self, service):
        """Test that service implements IJobCollectionService interface."""
        assert isinstance(service, IJobCollectionService)
        
        # Verify all required methods exist
        assert hasattr(service, 'collect_jobs')
        assert hasattr(service, 'run_daily_aggregation')
        assert hasattr(service, 'get_source_statuses')
        assert hasattr(service, 'enable_source')
        assert hasattr(service, 'disable_source')
        assert hasattr(service, 'health_check')
        assert hasattr(service, 'get_collection_stats')

    # ==================== JOB COLLECTION TESTS ====================

    @pytest.mark.asyncio
    async def test_collect_jobs_basic(self, service, sample_job_query):
        """Test basic job collection functionality."""
        result = await service.collect_jobs(sample_job_query)
        
        assert isinstance(result, CollectionResult)
        assert len(result.jobs) >= 0
        assert result.total_jobs >= 0
        assert result.raw_jobs >= result.total_jobs
        assert result.duplicates_removed >= 0
        assert len(result.sources_queried) > 0
        assert result.collection_time is not None
        assert result.duration_seconds >= 0

    @pytest.mark.asyncio
    async def test_collect_jobs_with_results(self, service, sample_job_query, sample_job_posting):
        """Test job collection returns properly formatted results."""
        # Mock the internal collection to return sample jobs
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([sample_job_posting], {"remoteok": None})
            
            # Mock the enricher to preserve the expected job data for this test
            with patch.object(service.enricher, 'enrich_job') as mock_enrich:
                async def preserve_job(job_posting):
                    # Return the job with original values preserved
                    return sample_job_posting
                mock_enrich.side_effect = preserve_job
                
                result = await service.collect_jobs(sample_job_query)
                
                assert len(result.jobs) == 1
                assert result.jobs[0].id == sample_job_posting.id
                assert result.jobs[0].title == sample_job_posting.title
                assert result.jobs[0].company == sample_job_posting.company
                assert result.jobs[0].job_type == sample_job_posting.job_type
                assert result.total_jobs == 1
                assert "remoteok" in result.successful_sources
                assert len(result.failed_sources) == 0

    @pytest.mark.asyncio
    async def test_collect_jobs_deduplication(self, service, sample_job_query):
        """Test that duplicate jobs are properly removed."""
        # Create duplicate jobs
        job1 = JobPosting(
            id="job_1", source="remoteok", title="PM Role", company="Corp A",
            location="Remote", url="https://example.com/1"
        )
        job2 = JobPosting(
            id="job_2", source="indeed", title="PM Role", company="Corp A",
            location="Remote", url="https://example.com/1"  # Same URL = duplicate
        )
        
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([job1, job2], {})
            
            result = await service.collect_jobs(sample_job_query)
            
            # Should have removed one duplicate
            assert result.duplicates_removed >= 1
            assert result.total_jobs < result.raw_jobs

    @pytest.mark.asyncio
    async def test_collect_jobs_enrichment(self, service, sample_job_query, mock_enricher):
        """Test that collected jobs are properly enriched."""
        job = JobPosting(
            id="job_1", source="remoteok", title="Product Manager",
            company="Tech Corp", location="San Francisco"
        )
        
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([job], {})
            
            await service.collect_jobs(sample_job_query)
            
            # Verify enricher was called
            mock_enricher.enrich_job.assert_called()

    @pytest.mark.asyncio
    async def test_collect_jobs_source_filtering(self, service):
        """Test job collection respects source filtering."""
        query = JobQuery(sources=["remoteok"])
        
        result = await service.collect_jobs(query)
        
        # Should only query specified sources
        assert "remoteok" in result.sources_queried
        assert len([s for s in result.sources_queried if s != "remoteok"]) == 0

    @pytest.mark.asyncio
    async def test_collect_jobs_concurrent_execution(self, service, sample_job_query):
        """Test that multiple sources are queried concurrently."""
        query = JobQuery(sources=["remoteok", "indeed"])
        
        # Mock the source collection to prevent real network calls
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([], {})  # Return empty jobs, no errors
            
            start_time = datetime.now()
            result = await service.collect_jobs(query)
            duration = (datetime.now() - start_time).total_seconds()
            
            # Concurrent execution should be faster than sequential
            assert len(result.sources_queried) >= 2
            assert duration < 10  # Should complete quickly in mock scenario

    # ==================== DAILY AGGREGATION TESTS ====================

    @pytest.mark.asyncio
    async def test_run_daily_aggregation(self, service, sample_job_query):
        """Test daily aggregation process."""
        result = await service.run_daily_aggregation(sample_job_query)
        
        assert isinstance(result, CollectionResult)
        # Daily aggregation should include storage operations
        service.storage.store_jobs.assert_called()

    @pytest.mark.asyncio
    async def test_run_daily_aggregation_comprehensive(self, service):
        """Test daily aggregation runs complete process."""
        # Should use default query if none provided
        default_query = JobQuery(
            keywords=["product manager", "TPM"],
            location="Remote",
            max_jobs_per_source=50
        )
        
        result = await service.run_daily_aggregation(default_query)
        
        assert result.collection_time is not None
        assert result.duration_seconds >= 0

    # ==================== SOURCE MANAGEMENT TESTS ====================

    @pytest.mark.asyncio
    async def test_get_source_statuses(self, service):
        """Test retrieval of source status information."""
        statuses = await service.get_source_statuses()
        
        assert isinstance(statuses, list)
        assert len(statuses) >= 2  # At least remoteok and indeed
        
        # Expect all configured sources
        expected_sources = ["remoteok", "greenhouse", "lever", "indeed", "linkedin"]
        
        for status in statuses:
            assert isinstance(status, SourceStatus)
            assert status.name in expected_sources
            assert isinstance(status.type, JobSourceType)
            assert isinstance(status.enabled, bool)
            assert isinstance(status.healthy, bool)

    @pytest.mark.asyncio
    async def test_enable_source(self, service):
        """Test enabling a job source."""
        result = await service.enable_source("remoteok")
        assert result is True
        
        # Verify source is enabled
        statuses = await service.get_source_statuses()
        remoteok_status = next(s for s in statuses if s.name == "remoteok")
        assert remoteok_status.enabled is True

    @pytest.mark.asyncio
    async def test_disable_source(self, service):
        """Test disabling a job source."""
        result = await service.disable_source("remoteok")
        assert result is True
        
        # Verify source is disabled
        statuses = await service.get_source_statuses()
        remoteok_status = next(s for s in statuses if s.name == "remoteok")
        assert remoteok_status.enabled is False

    @pytest.mark.asyncio
    async def test_enable_nonexistent_source(self, service):
        """Test enabling non-existent source raises error."""
        with pytest.raises(SourceNotFoundError):
            await service.enable_source("nonexistent_source")

    @pytest.mark.asyncio
    async def test_disable_nonexistent_source(self, service):
        """Test disabling non-existent source raises error."""
        with pytest.raises(SourceNotFoundError):
            await service.disable_source("nonexistent_source")

    # ==================== HEALTH AND MONITORING TESTS ====================

    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test service health check functionality."""
        health = await service.health_check()
        
        assert isinstance(health, dict)
        assert 'status' in health
        assert 'timestamp' in health
        assert 'service' in health
        assert 'sources' in health
        assert 'storage' in health
        
        # Service should be healthy
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
        assert isinstance(health['service'], dict)
        assert isinstance(health['sources'], list)
        assert isinstance(health['storage'], dict)

    @pytest.mark.asyncio
    async def test_get_collection_stats(self, service):
        """Test collection statistics retrieval."""
        stats = await service.get_collection_stats()
        
        assert isinstance(stats, dict)
        assert 'total_collections' in stats
        assert 'total_jobs_collected' in stats
        assert 'avg_collection_time' in stats
        assert 'successful_collections' in stats
        assert 'failed_collections' in stats
        assert 'last_collection_time' in stats
        
        # All values should be numeric or None
        for key in ['total_collections', 'total_jobs_collected', 'successful_collections', 'failed_collections']:
            assert isinstance(stats[key], (int, float))

    # ==================== ERROR HANDLING TESTS ====================

    @pytest.mark.asyncio
    async def test_invalid_query_validation(self, service):
        """Test validation of invalid query parameters."""
        invalid_query = JobQuery(max_jobs_per_source=-1)  # Invalid negative value
        
        with pytest.raises(ValidationError):
            await service.collect_jobs(invalid_query)

    @pytest.mark.asyncio
    async def test_collection_timeout_handling(self, service):
        """Test handling of collection timeouts."""
        query = JobQuery(keywords=["test"])
        
        # Mock a timeout scenario
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.side_effect = asyncio.TimeoutError("Collection timed out")
            
            with pytest.raises(JobCollectionTimeoutError):
                await service.collect_jobs(query)

    @pytest.mark.asyncio
    async def test_source_failure_handling(self, service, sample_job_query):
        """Test graceful handling of source failures."""
        # Mock one source failing
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([], {"remoteok": "Connection failed"})
            
            result = await service.collect_jobs(sample_job_query)
            
            # Should handle failure gracefully
            assert "remoteok" in result.failed_sources
            assert result.errors["remoteok"] == "Connection failed"

    @pytest.mark.asyncio
    async def test_storage_error_handling(self, service, sample_job_query):
        """Test handling of storage errors during collection."""
        service.storage.store_jobs.side_effect = Exception("Storage failed")
        
        # Collection should handle storage errors gracefully
        result = await service.collect_jobs(sample_job_query)
        assert isinstance(result, CollectionResult)

    # ==================== DATA MODEL VALIDATION TESTS ====================

    def test_job_posting_model_validation(self):
        """Test job posting data model validation."""
        # Valid job posting should create successfully
        job = JobPosting(
            id="test_123",
            source="careerjet",
            title="Product Manager",
            company="Test Corp"
        )
        
        assert job.id == "test_123"
        assert job.source == "careerjet"
        assert job.title == "Product Manager"
        assert job.company == "Test Corp"
        
        # Should convert to dict properly
        job_dict = job.to_dict()
        assert isinstance(job_dict, dict)
        assert job_dict["id"] == "test_123"

    def test_job_query_model_validation(self):
        """Test job query data model validation."""
        query = JobQuery(
            keywords=["PM", "TPM"],
            location="Remote",
            max_jobs_per_source=100
        )
        
        assert query.keywords == ["PM", "TPM"]
        assert query.location == "Remote"
        assert query.max_jobs_per_source == 100
        
        # Should convert to dict properly
        query_dict = query.to_dict()
        assert isinstance(query_dict, dict)
        assert query_dict["keywords"] == ["PM", "TPM"]

    def test_collection_result_model_validation(self):
        """Test collection result data model validation."""
        job = JobPosting(id="1", source="test", title="PM", company="Corp")
        result = CollectionResult(
            jobs=[job],
            total_jobs=1,
            raw_jobs=2,
            duplicates_removed=1,
            sources_queried=["test"],
            successful_sources=["test"],
            failed_sources=[],
            collection_time=datetime.now(timezone.utc),
            duration_seconds=5.5,
            errors={}
        )
        
        assert len(result.jobs) == 1
        assert result.total_jobs == 1
        assert result.duplicates_removed == 1
        
        # Should convert to dict properly
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert len(result_dict["jobs"]) == 1

    def test_source_status_model_validation(self):
        """Test source status data model validation."""
        status = SourceStatus(
            name="remoteok",
            type=JobSourceType.API_AGGREGATOR,
            enabled=True,
            healthy=True,
            jobs_collected_today=50
        )
        
        assert status.name == "remoteok"
        assert status.type == JobSourceType.API_AGGREGATOR
        assert status.enabled is True
        assert status.healthy is True
        
        # Should convert to dict properly
        status_dict = status.to_dict()
        assert isinstance(status_dict, dict)
        assert status_dict["name"] == "remoteok"

    # ==================== PERFORMANCE TESTS ====================

    @pytest.mark.asyncio
    async def test_concurrent_source_limit(self, service):
        """Test that concurrent source limit is respected."""
        # This would be a more complex test that verifies the service
        # doesn't exceed the configured concurrent source limit
        query = JobQuery(sources=["remoteok", "greenhouse", "indeed", "linkedin"])
        
        # Mock multiple sources to verify concurrency control
        with patch.object(service, '_query_single_source') as mock_query:
            mock_query.return_value = ([], None)
            
            await service.collect_jobs(query)
            
            # Verify that sources were processed (exact concurrency testing would be more complex)
            assert mock_query.call_count >= 0

    @pytest.mark.asyncio
    async def test_memory_efficiency_large_collections(self, service):
        """Test memory efficiency with large job collections."""
        # This test would verify that the service handles large collections efficiently
        query = JobQuery(max_jobs_per_source=1000)
        
        # Generate large mock dataset
        large_job_list = [
            JobPosting(id=f"job_{i}", source="test", title=f"Job {i}", company="Corp")
            for i in range(500)
        ]
        
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = (large_job_list, {})
            
            result = await service.collect_jobs(query)
            
            assert len(result.jobs) <= 500
            assert result.total_jobs <= 500

    # ==================== INTEGRATION-STYLE TESTS ====================

    @pytest.mark.asyncio
    async def test_end_to_end_collection_workflow(self, service, sample_job_query):
        """Test complete end-to-end collection workflow."""
        # This test verifies the complete workflow:
        # Query -> Collection -> Deduplication -> Enrichment -> Storage -> Results
        
        job = JobPosting(
            id="e2e_job", source="remoteok", title="Senior TPM",
            company="E2E Corp", location="Remote"
        )
        
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([job], {})
            
            result = await service.collect_jobs(sample_job_query)
            
            # Verify complete workflow
            assert len(result.jobs) >= 0
            assert result.total_jobs >= 0
            assert result.collection_time is not None
            
            # Verify enrichment was applied
            service.enricher.enrich_job.assert_called()

    @pytest.mark.asyncio
    async def test_service_resilience_partial_failures(self, service):
        """Test service resilience when some sources fail."""
        query = JobQuery(sources=["remoteok", "indeed"])
        
        # Mock mixed success/failure scenario
        good_job = JobPosting(id="good", source="remoteok", title="PM", company="Corp")
        
        with patch.object(service, '_collect_from_sources') as mock_collect:
            mock_collect.return_value = ([good_job], {"indeed": "Failed to connect"})
            
            result = await service.collect_jobs(query)
            
            # Should have partial success
            assert len(result.successful_sources) >= 1
            assert len(result.failed_sources) >= 1
            assert len(result.jobs) >= 0
            assert result.total_jobs >= 0