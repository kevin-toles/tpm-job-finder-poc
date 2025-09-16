"""
Tests for the Job Aggregator Service.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from tpm_job_finder_poc.job_aggregator.service import JobAggregatorService
from tpm_job_finder_poc.shared.contracts.job_aggregator_service import (
    SearchParams,
    AggregationResult,
    SourceStatus,
    SourceType,
    HealthStatus,
    ValidationError
)


class TestJobAggregatorService:
    """Test cases for JobAggregatorService."""

    @pytest.fixture
    def service(self):
        """Create a JobAggregatorService instance for testing."""
        config = {
            'greenhouse_companies': ['test-company'],
            'lever_companies': []
        }
        return JobAggregatorService(config)

    @pytest.fixture
    def search_params(self):
        """Create sample search parameters."""
        return SearchParams(
            keywords="python developer",
            location="San Francisco",
            remote_only=False,
            job_type="mid_level",
            max_age_days=7
        )

    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service.config is not None
        assert hasattr(service, 'api_aggregators')
        assert hasattr(service, 'browser_scrapers')

    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test health check returns expected format."""
        health = await service.health_check()
        
        assert "status" in health
        assert "timestamp" in health
        assert "version" in health
        assert health["status"] == "healthy"

    def test_get_enabled_sources(self, service):
        """Test getting enabled sources."""
        sources = service.get_enabled_sources()
        
        assert "api_aggregators" in sources
        assert "browser_scrapers" in sources
        assert isinstance(sources["api_aggregators"], list)
        assert isinstance(sources["browser_scrapers"], list)

    @pytest.mark.asyncio
    async def test_get_source_statuses(self, service):
        """Test getting source statuses."""
        statuses = await service.get_source_statuses()
        
        assert isinstance(statuses, list)
        for status in statuses:
            assert hasattr(status, 'name')
            assert hasattr(status, 'type')
            assert hasattr(status, 'status')

    @pytest.mark.asyncio
    async def test_aggregate_jobs_validation_error(self, service):
        """Test validation error when neither keywords nor location provided."""
        search_params = SearchParams()  # Empty params
        
        with pytest.raises(ValidationError):
            await service.aggregate_jobs(search_params)

    @pytest.mark.asyncio
    async def test_aggregate_jobs_success(self, service, search_params):
        """Test successful job aggregation."""
        # Mock the internal methods to avoid external dependencies
        with patch.object(service, '_collect_from_api_aggregators', return_value=[]):
            with patch.object(service, '_collect_from_browser_scrapers', return_value=[]):
                result = await service.aggregate_jobs(search_params)
                
                assert isinstance(result, AggregationResult)
                assert result.total_collected == 0
                assert result.total_deduplicated == 0
                assert isinstance(result.duration_seconds, float)

    def test_classify_job_type(self, service):
        """Test job type classification."""
        assert service._classify_job_type("Senior Python Developer") == "senior"
        assert service._classify_job_type("Junior Software Engineer") == "entry_level"
        assert service._classify_job_type("Engineering Manager") == "management"
        assert service._classify_job_type("Python Developer") == "mid_level"

    def test_detect_remote_work(self, service):
        """Test remote work detection."""
        assert service._detect_remote_work("Remote") == True
        assert service._detect_remote_work("Work from home") == True
        assert service._detect_remote_work("San Francisco, CA") == False
        assert service._detect_remote_work("") == False

    def test_count_tpm_keywords(self, service):
        """Test TPM keyword counting."""
        assert service._count_tpm_keywords("Technical Program Manager") == 1
        assert service._count_tpm_keywords("TPM - Infrastructure") == 1
        assert service._count_tpm_keywords("Software Engineer") == 0

    def test_deduplicate_jobs(self, service):
        """Test job deduplication."""
        jobs = [
            {"title": "Python Developer", "company": "Company A"},
            {"title": "Python Developer", "company": "Company A"},  # Duplicate
            {"title": "Python Developer", "company": "Company B"},  # Different company
        ]
        
        deduplicated = service._deduplicate_jobs(jobs)
        assert len(deduplicated) == 2  # One duplicate removed

    def test_enrich_job_data(self, service):
        """Test job data enrichment."""
        job = {
            "title": "Senior Technical Program Manager",
            "location": "Remote"
        }
        
        enrichment = service._enrich_job_data(job)
        
        assert enrichment["job_type"] == "senior"
        assert enrichment["remote_friendly"] == True
        assert enrichment["tpm_keywords_found"] == 1
        assert "aggregated_at" in enrichment


class TestSearchParams:
    """Test cases for SearchParams."""

    def test_search_params_creation(self):
        """Test SearchParams creation and to_dict method."""
        params = SearchParams(
            keywords="python",
            location="SF",
            remote_only=True
        )
        
        assert params.keywords == "python"
        assert params.location == "SF"
        assert params.remote_only == True
        
        dict_params = params.to_dict()
        assert dict_params["keywords"] == "python"
        assert dict_params["remote_only"] == True


class TestSourceStatus:
    """Test cases for SourceStatus."""

    def test_source_status_creation(self):
        """Test SourceStatus creation and to_dict method."""
        status = SourceStatus(
            name="test_source",
            type=SourceType.API_AGGREGATOR,
            status=HealthStatus.HEALTHY
        )
        
        assert status.name == "test_source"
        assert status.type == SourceType.API_AGGREGATOR
        assert status.status == HealthStatus.HEALTHY
        
        dict_status = status.to_dict()
        assert dict_status["name"] == "test_source"
        assert dict_status["type"] == "api_aggregator"
        assert dict_status["status"] == "healthy"


if __name__ == "__main__":
    pytest.main([__file__])