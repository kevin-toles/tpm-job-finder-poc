"""
TDD Tests for Job Aggregator Service - RED Phase
Following proper TDD: Write failing tests first to define expected behavior

Based on documentation analysis and shared contracts, the Job Aggregator Service should:
1. Implement IJobAggregatorService protocol
2. Coordinate multi-source job collection (API + browser scrapers)
3. Provide deduplication across sources
4. Enrich job data with metadata
5. Handle errors gracefully with proper exceptions
6. Support health monitoring and source status tracking
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime, timezone

# Test imports - these define the expected interface
from tpm_job_finder_poc.job_aggregator.service import JobAggregatorService
from tpm_job_finder_poc.shared.contracts.job_aggregator_service import (
    SearchParams,
    AggregatedJob,
    AggregationResult,
    SourceStatus,
    SourceType,
    HealthStatus,
    JobAggregatorError,
    SourceUnavailableError,
    RateLimitError,
    ValidationError
)


class TestJobAggregatorServiceTDD:
    """TDD Test cases defining expected behavior before implementation verification."""

    @pytest.fixture
    def service(self):
        """Create JobAggregatorService instance with test configuration."""
        config = {
            'api_sources': {
                'remoteok': {'enabled': True, 'api_key': 'test-key'},
                'greenhouse': {'enabled': True, 'companies': ['test-company']},
                'lever': {'enabled': True, 'companies': ['test-lever-company']}
            },
            'scraping_sources': {
                'indeed': {'enabled': True},
                'linkedin': {'enabled': True}
            },
            'deduplication': {
                'enabled': True,
                'similarity_threshold': 0.8
            }
        }
        return JobAggregatorService(config)

    @pytest.fixture
    def search_params(self):
        """Create sample search parameters."""
        return SearchParams(
            keywords="technical product manager",
            location="San Francisco",
            remote_only=False,
            job_type="full_time",
            max_age_days=7
        )

    @pytest.fixture
    def sample_aggregated_job(self):
        """Create sample aggregated job."""
        return AggregatedJob(
            id="test-job-1",
            source="remoteok",
            source_type=SourceType.API_AGGREGATOR,
            title="Senior Technical Product Manager",
            company="Test Company",
            location="San Francisco, CA",
            url="https://example.com/job/123",
            description="Great TPM role...",
            salary="$180k-220k",
            job_type="full_time",
            remote_friendly=True,
            tpm_keywords_found=5,
            date_posted=datetime.now(timezone.utc),
            aggregated_at=datetime.now(timezone.utc)
        )

    def test_service_initialization(self, service):
        """Test service initializes correctly with config."""
        assert service.config is not None
        assert hasattr(service, 'api_aggregators')
        assert hasattr(service, 'browser_scrapers')
        assert hasattr(service, 'dedupe_cache')

    def test_implements_service_contract(self, service):
        """Test service implements IJobAggregatorService protocol."""
        # Verify all required methods exist
        assert hasattr(service, 'aggregate_jobs')
        assert hasattr(service, 'get_source_statuses')
        assert hasattr(service, 'health_check')
        assert hasattr(service, 'get_enabled_sources')
        
        # Verify they are callable
        assert callable(service.aggregate_jobs)
        assert callable(service.get_source_statuses)
        assert callable(service.health_check)
        assert callable(service.get_enabled_sources)

    @pytest.mark.asyncio
    async def test_aggregate_jobs_success(self, service, search_params, sample_aggregated_job):
        """Test successful job aggregation from multiple sources."""
        # Mock the internal methods to return expected data
        with patch.object(service, '_collect_from_api_sources') as mock_api, \
             patch.object(service, '_collect_from_browser_scrapers') as mock_scrapers, \
             patch.object(service, '_deduplicate_jobs') as mock_dedupe, \
             patch.object(service, '_enrich_job_data') as mock_enrich:
            
            # Setup mocks to return sample data
            api_jobs = [sample_aggregated_job]
            scraper_jobs = []
            
            mock_api.return_value = api_jobs
            mock_scrapers.return_value = scraper_jobs
            mock_dedupe.return_value = api_jobs  # No duplicates
            mock_enrich.return_value = api_jobs  # Already enriched
            
            # Execute aggregation
            result = await service.aggregate_jobs(search_params, max_jobs_per_source=50)
            
            # Verify results
            assert isinstance(result, AggregationResult)
            assert len(result.jobs) == 1
            assert result.jobs[0].title == "Senior Technical Product Manager"
            assert result.total_collected >= 1
            assert result.total_deduplicated >= 0
            assert 'remoteok' in result.sources_used
            assert result.duration_seconds >= 0
            
            # Verify mocks were called
            mock_api.assert_called_once()
            mock_scrapers.assert_called_once()
            mock_dedupe.assert_called_once()
            mock_enrich.assert_called_once()

    @pytest.mark.asyncio
    async def test_aggregate_jobs_validation_error(self, service):
        """Test validation error for invalid search parameters."""
        # Test with completely empty search params
        invalid_params = SearchParams()  # No keywords, location, etc.
        
        with pytest.raises(ValidationError) as exc_info:
            await service.aggregate_jobs(invalid_params)
        
        assert "keywords" in str(exc_info.value).lower() or "search criteria" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_aggregate_jobs_with_source_failures(self, service, search_params):
        """Test graceful handling of individual source failures."""
        with patch.object(service, '_collect_from_api_sources') as mock_api, \
             patch.object(service, '_collect_from_browser_scrapers') as mock_scrapers:
            
            # Simulate one source failing, another succeeding
            mock_api.side_effect = SourceUnavailableError("API source failed")
            mock_scrapers.return_value = []  # Scrapers succeed but return no jobs
            
            # Should not raise exception but should handle gracefully
            result = await service.aggregate_jobs(search_params)
            
            # Should still return a result even with failures
            assert isinstance(result, AggregationResult)
            assert len(result.errors) > 0  # Should record the error
            assert "API source failed" in str(result.errors)

    @pytest.mark.asyncio
    async def test_deduplication_functionality(self, service):
        """Test cross-source job deduplication."""
        # Create duplicate jobs from different sources
        job1 = AggregatedJob(
            id="job-1",
            source="remoteok",
            source_type=SourceType.API_AGGREGATOR,
            title="Senior Product Manager",
            company="TestCorp",
            location="Remote"
        )
        
        job2 = AggregatedJob(
            id="job-2", 
            source="indeed",
            source_type=SourceType.BROWSER_SCRAPER,
            title="Senior Product Manager",  # Same title
            company="TestCorp",  # Same company
            location="Remote"  # Same location
        )
        
        job3 = AggregatedJob(
            id="job-3",
            source="linkedin",
            source_type=SourceType.BROWSER_SCRAPER,
            title="Junior Developer",  # Different role
            company="DifferentCorp",
            location="New York"
        )
        
        jobs_with_duplicates = [job1, job2, job3]
        
        # Test deduplication
        deduplicated = service._deduplicate_jobs(jobs_with_duplicates)
        
        # Should remove the duplicate (job1 and job2 are similar)
        assert len(deduplicated) == 2  # job1/job2 merged + job3
        
        # Should keep the unique jobs
        titles = [job.title for job in deduplicated]
        assert "Senior Product Manager" in titles
        assert "Junior Developer" in titles

    @pytest.mark.asyncio
    async def test_job_enrichment(self, service, sample_aggregated_job):
        """Test job data enrichment with metadata."""
        # Test with basic job data
        basic_job = AggregatedJob(
            id="basic-job",
            source="test",
            source_type=SourceType.API_AGGREGATOR,
            title="Product Manager at AI Startup",
            company="AI Corp",
            description="Looking for PM to work on ML products, remote work available"
        )
        
        jobs = [basic_job]
        enriched_jobs = service._enrich_job_data(jobs)
        
        assert len(enriched_jobs) == 1
        enriched_job = enriched_jobs[0]
        
        # Should add TPM keyword count
        assert enriched_job.tpm_keywords_found >= 0
        
        # Should detect remote work
        assert isinstance(enriched_job.remote_friendly, bool)
        
        # Should classify job type if not provided
        if enriched_job.job_type:
            assert enriched_job.job_type in ['entry', 'mid_level', 'senior', 'executive']

    @pytest.mark.asyncio
    async def test_get_source_statuses(self, service):
        """Test getting health status of all sources."""
        statuses = await service.get_source_statuses()
        
        assert isinstance(statuses, list)
        assert len(statuses) > 0
        
        for status in statuses:
            assert isinstance(status, SourceStatus)
            assert status.name
            assert isinstance(status.type, SourceType)
            assert isinstance(status.status, HealthStatus)
            assert isinstance(status.jobs_collected, int)

    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test service health monitoring."""
        health_status = await service.health_check()
        
        assert isinstance(health_status, dict)
        assert 'status' in health_status
        assert 'sources' in health_status
        assert 'total_sources' in health_status
        assert 'healthy_sources' in health_status
        assert 'timestamp' in health_status
        
        # Health status should be valid
        assert health_status['status'] in ['healthy', 'degraded', 'unhealthy']
        assert isinstance(health_status['total_sources'], int)
        assert isinstance(health_status['healthy_sources'], int)

    def test_get_enabled_sources(self, service):
        """Test getting enabled sources by type."""
        sources = service.get_enabled_sources()
        
        assert isinstance(sources, dict)
        assert 'api_sources' in sources
        assert 'scraping_sources' in sources
        
        # Should contain lists of source names
        assert isinstance(sources['api_sources'], list)
        assert isinstance(sources['scraping_sources'], list)
        
        # Should have some enabled sources based on config
        total_sources = len(sources['api_sources']) + len(sources['scraping_sources'])
        assert total_sources > 0

    @pytest.mark.asyncio
    async def test_rate_limit_handling(self, service, search_params):
        """Test proper handling of rate limit errors."""
        with patch.object(service, '_collect_from_api_sources') as mock_api:
            mock_api.side_effect = RateLimitError("Rate limit exceeded for RemoteOK")
            
            # Should handle rate limit gracefully
            result = await service.aggregate_jobs(search_params)
            
            # Should return result with error logged
            assert isinstance(result, AggregationResult)
            assert len(result.errors) > 0
            assert any("rate limit" in str(error).lower() for error in result.errors)

    def test_search_params_validation(self):
        """Test SearchParams data model validation."""
        # Valid search params
        valid_params = SearchParams(
            keywords="product manager",
            location="San Francisco",
            remote_only=True,
            job_type="senior",
            max_age_days=30
        )
        
        assert valid_params.keywords == "product manager"
        assert valid_params.remote_only is True
        assert valid_params.max_age_days == 30
        
        # Test to_dict conversion
        params_dict = valid_params.to_dict()
        assert isinstance(params_dict, dict)
        assert params_dict['keywords'] == "product manager"
        assert params_dict['remote_only'] is True

    def test_aggregated_job_model(self, sample_aggregated_job):
        """Test AggregatedJob data model."""
        job = sample_aggregated_job
        
        # Test required fields
        assert job.id
        assert job.source
        assert isinstance(job.source_type, SourceType)
        assert job.title
        assert job.company
        
        # Test to_dict conversion
        job_dict = job.to_dict()
        assert isinstance(job_dict, dict)
        assert job_dict['id'] == job.id
        assert job_dict['source_type'] == job.source_type.value
        assert job_dict['tpm_keywords_found'] == job.tpm_keywords_found

    def test_aggregation_result_model(self, sample_aggregated_job):
        """Test AggregationResult data model."""
        result = AggregationResult(
            jobs=[sample_aggregated_job],
            total_collected=1,
            total_deduplicated=0,
            sources_used=['remoteok'],
            duration_seconds=2.5,
            errors=[]
        )
        
        assert len(result.jobs) == 1
        assert result.total_collected == 1
        assert result.total_deduplicated == 0
        assert 'remoteok' in result.sources_used
        assert result.duration_seconds == 2.5
        
        # Test to_dict conversion
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert len(result_dict['jobs']) == 1
        assert result_dict['total_collected'] == 1

    @pytest.mark.asyncio
    async def test_concurrent_source_collection(self, service, search_params):
        """Test concurrent collection from multiple sources."""
        with patch.object(service, '_collect_from_single_api_source') as mock_single_api, \
             patch.object(service, '_collect_from_browser_scrapers') as mock_scrapers:
            
            # Mock multiple API sources returning different jobs
            mock_single_api.side_effect = [
                [AggregatedJob(id="1", source="remoteok", source_type=SourceType.API_AGGREGATOR, 
                              title="PM 1", company="Company1")],
                [AggregatedJob(id="2", source="greenhouse", source_type=SourceType.API_AGGREGATOR,
                              title="PM 2", company="Company2")]
            ]
            mock_scrapers.return_value = []
            
            result = await service.aggregate_jobs(search_params)
            
            # Should collect from multiple sources concurrently
            assert isinstance(result, AggregationResult)
            # The exact implementation may vary, but should handle multiple sources

    def test_tpm_keyword_detection(self, service):
        """Test TPM-specific keyword detection in job descriptions."""
        job_with_tpm_keywords = AggregatedJob(
            id="tpm-job",
            source="test",
            source_type=SourceType.API_AGGREGATOR,
            title="Technical Product Manager",
            company="Tech Corp",
            description="Looking for TPM with experience in product management, technical leadership, and cross-functional collaboration"
        )
        
        # Test keyword counting
        count = service._count_tpm_keywords(job_with_tpm_keywords)
        assert isinstance(count, int)
        assert count > 0  # Should find TPM-related keywords

    def test_remote_work_detection(self, service):
        """Test remote work opportunity detection."""
        remote_job = AggregatedJob(
            id="remote-job",
            source="test", 
            source_type=SourceType.API_AGGREGATOR,
            title="Product Manager - Remote",
            company="Remote Corp",
            description="Fully remote position with flexible working arrangements",
            location="Remote"
        )
        
        is_remote = service._detect_remote_work(remote_job)
        assert isinstance(is_remote, bool)
        assert is_remote is True  # Should detect remote work indicators
        
        office_job = AggregatedJob(
            id="office-job",
            source="test",
            source_type=SourceType.API_AGGREGATOR, 
            title="Product Manager",
            company="Office Corp",
            description="On-site position in our downtown office",
            location="New York, NY"
        )
        
        is_remote_office = service._detect_remote_work(office_job)
        assert is_remote_office is False  # Should not detect remote work