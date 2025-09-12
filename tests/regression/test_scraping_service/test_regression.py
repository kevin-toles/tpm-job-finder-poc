"""
Regression tests for tpm_job_finder_poc.scraping_service.

Tests to ensure that refactoring hasn't broken existing functionality:
- Service interfaces remain stable
- Performance hasn't degraded
- Error handling still works
- Configuration compatibility
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch

from tpm_job_finder_poc.scraping_service import (
    ServiceRegistry, 
    ScrapingOrchestrator,
    FetchParams,
    JobPosting,
    HealthStatus
)
from tpm_job_finder_poc.scraping_service.scrapers import IndeedScraper, LinkedInScraper


class TestServiceInterfaceRegression:
    """Test that service interfaces haven't changed."""
    
    def test_fetch_params_interface(self):
        """Test FetchParams interface stability."""
        # Original interface should still work
        params = FetchParams(
            keywords=["python"],
            location="Remote",
            limit=50
        )
        
        assert hasattr(params, 'keywords')
        assert hasattr(params, 'location')
        assert hasattr(params, 'limit')
        assert hasattr(params, 'extra_params')
        
        # Should support extra parameters
        params_with_extra = FetchParams(
            keywords=["java"],
            extra_params={'company': 'tech_startup'}
        )
        
        assert params_with_extra.extra_params['company'] == 'tech_startup'
        
    def test_job_posting_interface(self):
        """Test JobPosting interface stability."""
        from datetime import datetime, timezone
        
        # Original interface should still work
        job = JobPosting(
            id="test_123",
            source="test_source",
            company="Test Corp", 
            title="Developer",
            location="Remote",
            url="https://example.com/job",
            date_posted=datetime.now(timezone.utc)
        )
        
        # Required fields
        assert job.id == "test_123"
        assert job.source == "test_source"
        assert job.company == "Test Corp"
        assert job.title == "Developer"
        
        # Optional fields should work
        assert job.location == "Remote"
        assert job.url == "https://example.com/job"
        
    def test_health_status_enum(self):
        """Test HealthStatus enum values."""
        # Should have standard health states
        assert hasattr(HealthStatus, 'HEALTHY')
        assert hasattr(HealthStatus, 'DEGRADED') 
        assert hasattr(HealthStatus, 'UNHEALTHY')
        
        # Values should be strings for JSON serialization
        assert isinstance(HealthStatus.HEALTHY.value, str)
        
    def test_service_registry_methods(self):
        """Test ServiceRegistry method signatures."""
        registry = ServiceRegistry()
        
        # Core methods should exist with same signatures
        assert hasattr(registry, 'register_source')
        assert hasattr(registry, 'unregister_source')
        assert hasattr(registry, 'get_source')
        assert hasattr(registry, 'list_sources')
        
        # Async methods
        assert hasattr(registry, 'health_check_all')
        assert hasattr(registry, 'initialize_all_sources')
        assert hasattr(registry, 'cleanup_all_sources')


class TestPerformanceRegression:
    """Test that performance hasn't regressed."""
    
    @pytest.fixture
    def registry_with_sources(self):
        """Create registry with mock sources for performance testing."""
        from tpm_job_finder_poc.scraping_service.core.base_job_source import BaseJobSource, SourceType, JobPosting, HealthStatus, HealthCheckResult
        from unittest.mock import AsyncMock, Mock
        from datetime import datetime, timezone
        
        # Create a test scraper class that properly inherits from BaseJobSource
        class TestJobSource(BaseJobSource):
            def __init__(self, name: str):
                super().__init__(name, SourceType.BROWSER_SCRAPER)
                self.job_index = int(name.split('_')[1]) if '_' in name else 0
                
            async def fetch_jobs(self, params):
                return [
                    JobPosting(
                        id=f"job_{self.job_index}_1",
                        source=self.name,
                        company=f"Test Company {self.job_index}",  # Make companies unique
                        title=f"Developer {self.job_index}",        # Make titles unique  
                        location="Remote",
                        url=f"https://example.com/job_{self.job_index}_1",
                        date_posted=datetime.now(timezone.utc)
                    )
                ]
                
            async def health_check(self):
                return HealthCheckResult(status=HealthStatus.HEALTHY, message="OK")
                
            async def initialize(self):
                return True
                
            async def cleanup(self):
                pass
                
            def get_rate_limits(self):
                from tpm_job_finder_poc.scraping_service.core.base_job_source import RateLimitConfig
                return RateLimitConfig(requests_per_minute=60)
                
            def get_supported_params(self):
                return {"keywords": "list", "location": "string", "limit": "int"}
        
        registry = ServiceRegistry()
        
        # Add multiple test sources
        for i in range(5):
            test_source = TestJobSource(f"source_{i}")
            registry.register_source(test_source)
            
        return registry
        
    @pytest.mark.asyncio
    async def test_concurrent_fetching_performance(self, registry_with_sources):
        """Test concurrent job fetching performance."""
        orchestrator = ScrapingOrchestrator(registry_with_sources, max_concurrent=3)
        
        params = FetchParams(keywords=["test"], location="Remote", limit=10)
        
        start_time = time.time()
        results = await orchestrator.fetch_all_sources(params)
        end_time = time.time()
        
        # Should complete quickly with concurrency
        assert (end_time - start_time) < 2.0  # Should be much faster
        assert results["metadata"]["total_jobs"] == 5  # One job per source
        
    @pytest.mark.asyncio
    async def test_health_check_performance(self, registry_with_sources):
        """Test health check performance across multiple sources."""
        orchestrator = ScrapingOrchestrator(registry_with_sources)
        
        start_time = time.time()
        health_results = await orchestrator.health_check_sources()
        end_time = time.time()
        
        # Should complete quickly
        assert (end_time - start_time) < 1.0
        assert len(health_results) == 5
        
    def test_registry_operations_performance(self, registry_with_sources):
        """Test registry operations performance."""
        # Operations should be fast
        start_time = time.time()
        
        # Multiple operations
        for _ in range(100):
            sources = registry_with_sources.list_sources()
            stats = registry_with_sources.get_registry_stats()
            source = registry_with_sources.get_source("source_1")
            
        end_time = time.time()
        
        # Should handle many operations quickly
        assert (end_time - start_time) < 0.5


class TestErrorHandlingRegression:
    """Test that error handling behavior is preserved."""
    
    @pytest.fixture
    def registry_with_failing_source(self):
        """Create registry with a source that fails."""
        from tpm_job_finder_poc.scraping_service.core.base_job_source import BaseJobSource, SourceType
        
        # Create a test scraper class that fails properly
        class FailingJobSource(BaseJobSource):
            def __init__(self):
                super().__init__("failing_source", SourceType.BROWSER_SCRAPER)
                
            async def fetch_jobs(self, params):
                raise Exception("Source failed")
                
            async def health_check(self):
                raise Exception("Health check failed")
                
            async def initialize(self):
                raise Exception("Init failed")
                
            async def cleanup(self):
                pass
                
            def get_rate_limits(self):
                from tpm_job_finder_poc.scraping_service.core.base_job_source import RateLimitConfig
                return RateLimitConfig(requests_per_minute=60)
                
            def get_supported_params(self):
                return {"keywords": "list", "location": "string"}
        
        registry = ServiceRegistry()
        failing_source = FailingJobSource()
        registry.register_source(failing_source)
        return registry
        
    @pytest.mark.asyncio
    async def test_graceful_error_handling(self, registry_with_failing_source):
        """Test that errors don't crash the system."""
        orchestrator = ScrapingOrchestrator(registry_with_failing_source)
        
        params = FetchParams(keywords=["test"], location="Remote")
        
        # Should not raise exception despite source failure
        results = await orchestrator.fetch_all_sources(params)
        
        assert results["metadata"]["total_jobs"] == 0
        assert results["metadata"]["failed_sources"] == 1
        assert "failing_source" in results["errors"]
        
    @pytest.mark.asyncio
    async def test_health_check_error_handling(self, registry_with_failing_source):
        """Test health check error handling."""
        orchestrator = ScrapingOrchestrator(registry_with_failing_source)
        
        # Should not crash on health check failures
        health_results = await orchestrator.health_check_sources()
        
        assert "failing_source" in health_results
        # Should report unhealthy status rather than crashing  
        assert health_results["failing_source"]["status"] == "unhealthy"
        
    @pytest.mark.asyncio
    async def test_initialization_error_handling(self, registry_with_failing_source):
        """Test initialization error handling."""
        # Should handle initialization failures gracefully
        results = await registry_with_failing_source.initialize_all_sources()
        
        assert "failing_source" in results
        assert results["failing_source"] is False  # Failed initialization


class TestConfigurationCompatibility:
    """Test backward compatibility of configuration."""
    
    def test_scraper_initialization_compatibility(self):
        """Test scraper initialization with minimal parameters."""
        # Should work with no parameters (backward compatibility)
        indeed = IndeedScraper()
        linkedin = LinkedInScraper()
        
        assert indeed.name == "indeed"
        assert linkedin.name == "linkedin"
        
        # Should work with credentials for LinkedIn
        linkedin_with_creds = LinkedInScraper(
            email="test@example.com", 
            password="password"
        )
        
        assert linkedin_with_creds.email == "test@example.com"
        
    def test_rate_limit_configuration(self):
        """Test rate limit configuration compatibility."""
        scrapers = [IndeedScraper(), LinkedInScraper()]
        
        for scraper in scrapers:
            rate_limits = scraper.get_rate_limits()
            
            # Should have standard rate limit structure
            assert hasattr(rate_limits, 'requests_per_minute')
            assert hasattr(rate_limits, 'requests_per_hour')
            
            # Should have reasonable defaults
            assert rate_limits.requests_per_minute > 0
            assert rate_limits.requests_per_hour > 0
            
    def test_selector_configuration(self):
        """Test CSS selector configuration compatibility."""
        scrapers = [IndeedScraper(), LinkedInScraper()]
        
        for scraper in scrapers:
            selectors = scraper.get_selectors()
            
            # Should be dictionary
            assert isinstance(selectors, dict)
            assert len(selectors) > 0
            
            # Should have core selectors
            assert any('job' in key for key in selectors.keys())


class TestDataFormatRegression:
    """Test that data formats haven't changed."""
    
    @pytest.mark.asyncio
    async def test_job_data_format(self):
        """Test that job posting data format is stable."""
        from datetime import datetime, timezone
        
        # Create job with all expected fields
        job = JobPosting(
            id="regression_test_job",
            source="test_source",
            company="Regression Test Co",
            title="Test Engineer", 
            location="Test City",
            url="https://test.example.com/job",
            date_posted=datetime.now(timezone.utc),
            salary="$100,000",
            description="Test job description",
            raw_data={"extra": "data"}
        )
        
        # Should have all expected attributes
        required_fields = [
            'id', 'source', 'company', 'title', 'location', 
            'url', 'date_posted', 'salary', 'description', 'raw_data'
        ]
        
        for field in required_fields:
            assert hasattr(job, field)
            
        # Should serialize to dict properly (for JSON/Excel export)
        if hasattr(job, 'to_dict'):
            job_dict = job.to_dict()
            assert isinstance(job_dict, dict)
            for field in ['id', 'source', 'company', 'title']:
                assert field in job_dict
                
    @pytest.mark.asyncio
    async def test_orchestrator_response_format(self):
        """Test orchestrator response format stability."""
        registry = ServiceRegistry()
        orchestrator = ScrapingOrchestrator(registry)
        
        params = FetchParams(keywords=["test"], location="Remote")
        
        results = await orchestrator.fetch_all_sources(params)
        
        # Should have expected response structure
        assert isinstance(results, dict)
        assert "jobs" in results
        assert "metadata" in results
        assert "errors" in results
        
        # Metadata should have expected fields
        metadata = results["metadata"]
        expected_metadata_fields = [
            "total_jobs", "raw_jobs", "duplicates_removed",
            "sources_queried", "successful_sources", "failed_sources",
            "fetch_start_time", "fetch_end_time", "fetch_duration_seconds"
        ]
        
        for field in expected_metadata_fields:
            assert field in metadata
            
    @pytest.mark.asyncio
    async def test_health_check_response_format(self):
        """Test health check response format."""
        from tpm_job_finder_poc.scraping_service.core.base_job_source import BaseJobSource, SourceType, HealthStatus, HealthCheckResult
        from datetime import datetime, timezone
        
        # Create a test source that returns proper health check
        class TestHealthSource(BaseJobSource):
            def __init__(self):
                super().__init__("test_source", SourceType.BROWSER_SCRAPER)
                
            async def fetch_jobs(self, params):
                return []
                
            async def health_check(self):
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="Test message",
                    timestamp=datetime.now(timezone.utc),
                    response_time_ms=100.0
                )
                
            async def initialize(self):
                return True
                
            async def cleanup(self):
                pass
                
            def get_rate_limits(self):
                from tpm_job_finder_poc.scraping_service.core.base_job_source import RateLimitConfig
                return RateLimitConfig(requests_per_minute=60)
                
            def get_supported_params(self):
                return {"keywords": "list", "location": "string"}
        
        registry = ServiceRegistry()
        test_source = TestHealthSource()
        registry.register_source(test_source)
        orchestrator = ScrapingOrchestrator(registry)
        
        health_results = await orchestrator.health_check_sources()
        
        # Should have expected format
        assert isinstance(health_results, dict)
        assert "test_source" in health_results
        
        source_health = health_results["test_source"]
        expected_health_fields = ["status", "message", "timestamp", "response_time_ms"]
        
        for field in expected_health_fields:
            assert field in source_health


class TestScrapingMethodRegression:
    """Test that scraping methods work as expected."""
    
    def test_scraper_method_signatures(self):
        """Test that scraper methods have correct signatures."""
        scrapers = [IndeedScraper(), LinkedInScraper()]
        
        for scraper in scrapers:
            # Core interface methods
            assert hasattr(scraper, 'get_search_url')
            assert hasattr(scraper, 'get_selectors')
            assert hasattr(scraper, 'parse_job_elements')
            assert hasattr(scraper, 'get_supported_params')
            
            # Base methods
            assert hasattr(scraper, 'fetch_jobs')
            assert hasattr(scraper, 'health_check')
            assert hasattr(scraper, 'initialize')
            assert hasattr(scraper, 'cleanup')
            
    def test_search_url_generation(self):
        """Test search URL generation hasn't broken."""
        indeed = IndeedScraper()
        linkedin = LinkedInScraper()
        
        # Should generate valid URLs
        indeed_url = indeed.get_search_url(q="python developer", l="San Francisco")
        assert "indeed.com" in indeed_url
        assert "python developer" in indeed_url or "python+developer" in indeed_url
        
        linkedin_url = linkedin.get_search_url(q="product manager", location="Remote")
        assert "linkedin.com" in linkedin_url
        assert "jobs/search" in linkedin_url
        
    def test_selector_retrieval(self):
        """Test CSS selector retrieval."""
        scrapers = [IndeedScraper(), LinkedInScraper()]
        
        for scraper in scrapers:
            selectors = scraper.get_selectors()
            
            # Should have job-related selectors
            assert isinstance(selectors, dict)
            
            # Should have some core job selectors
            job_selectors = [key for key in selectors.keys() if 'job' in key.lower()]
            assert len(job_selectors) > 0
            
    def test_supported_params_format(self):
        """Test supported parameters format."""
        scrapers = [IndeedScraper(), LinkedInScraper()]
        
        for scraper in scrapers:
            params = scraper.get_supported_params()
            
            assert isinstance(params, dict)
            
            # Should describe parameter structure
            for param_name, param_info in params.items():
                if isinstance(param_info, dict):
                    # Should have type information
                    assert "type" in param_info or "description" in param_info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
