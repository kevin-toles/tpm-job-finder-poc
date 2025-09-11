"""
Integration tests for scraping_service_v2.

Tests the complete scraping service integration:
- Registry with multiple scrapers
- Orchestrated job fetching
- Health monitoring
- Error handling across components
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

from scraping_service_v2 import (
    ServiceRegistry,
    ScrapingOrchestrator,
    FetchParams,
    JobPosting,
    HealthStatus
)
from scraping_service_v2.scrapers import (
    IndeedScraper,
    LinkedInScraper,
    ZipRecruiterScraper, 
    GreenhouseScraper
)


class TestScrapingServiceIntegration:
    """Test complete scraping service integration."""
    
    @pytest.fixture
    async def service_registry(self):
        """Create service registry with real scrapers."""
        registry = ServiceRegistry()
        
        # Register all scrapers
        scrapers = [
            IndeedScraper(),
            LinkedInScraper(),
            ZipRecruiterScraper(),
            GreenhouseScraper()
        ]
        
        for scraper in scrapers:
            registry.register_source(scraper)
            
        return registry
        
    @pytest.fixture
    def orchestrator(self, service_registry):
        """Create orchestrator with registry."""
        return ScrapingOrchestrator(service_registry, max_concurrent=2)
        
    def test_registry_initialization(self, service_registry):
        """Test that all scrapers are registered."""
        sources = service_registry.list_sources()
        
        assert "indeed" in sources
        assert "linkedin" in sources
        assert "ziprecruiter" in sources
        assert "greenhouse" in sources
        assert len(sources) == 4
        
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator with multiple scrapers."""
        stats = orchestrator.get_orchestrator_stats()
        
        assert stats["max_concurrent"] == 2
        assert "semaphore_available" in stats
        
    @pytest.mark.asyncio
    async def test_health_checks_integration(self, orchestrator):
        """Test health checks across all scrapers."""
        # Mock the browser setup to avoid actual browser launches
        with patch('scraping_service_v2.scrapers.base_scraper.ChromeDriverManager'):
            with patch('selenium.webdriver.Chrome') as mock_chrome:
                mock_driver = Mock()
                mock_driver.get = Mock()
                mock_driver.current_url = "https://example.com"
                mock_driver.page_source = "normal page content"
                mock_driver.execute_script.return_value = "complete"
                mock_chrome.return_value = mock_driver
                
                health_results = await orchestrator.health_check_sources()
                
                assert len(health_results) == 4
                
                for source_name, health in health_results.items():
                    assert "status" in health
                    assert "message" in health
                    assert health["status"] in ["HEALTHY", "DEGRADED", "UNHEALTHY"]
                    
    @pytest.mark.asyncio
    async def test_source_capabilities(self, orchestrator):
        """Test getting capabilities from all sources."""
        capabilities = await orchestrator.get_source_capabilities()
        
        assert len(capabilities) == 4
        
        for source_name, caps in capabilities.items():
            assert "type" in caps
            assert "enabled" in caps
            assert caps["type"] == "BROWSER_SCRAPER"
            
    @pytest.mark.asyncio 
    async def test_job_fetching_integration(self, orchestrator, service_registry):
        """Test job fetching across multiple sources."""
        # Mock the job fetching to avoid real browser automation
        mock_jobs = [
            JobPosting(
                id=f"test_job_{i}",
                source=f"test_source_{i % 4}",
                company=f"Company {i}",
                title=f"Job Title {i}",
                location="Remote",
                url=f"https://example.com/job/{i}",
                date_posted=datetime.now(timezone.utc)
            )
            for i in range(8)  # 2 jobs per source
        ]
        
        # Mock each scraper's fetch_jobs method
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            source = service_registry.get_source(source_name)
            source.fetch_jobs = AsyncMock(return_value=mock_jobs[:2])  # 2 jobs per source
            
        params = FetchParams(
            keywords=["software engineer"],
            location="Remote",
            limit=10
        )
        
        results = await orchestrator.fetch_all_sources(params)
        
        # Should have jobs from all sources
        assert results["metadata"]["total_jobs"] >= 4
        assert results["metadata"]["sources_queried"] == 4
        assert results["metadata"]["successful_sources"] == 4
        assert results["metadata"]["failed_sources"] == 0
        
    @pytest.mark.asyncio
    async def test_error_handling_integration(self, orchestrator, service_registry):
        """Test error handling when some sources fail."""
        # Make some sources fail and some succeed
        indeed = service_registry.get_source("indeed")
        linkedin = service_registry.get_source("linkedin")
        ziprecruiter = service_registry.get_source("ziprecruiter")
        greenhouse = service_registry.get_source("greenhouse")
        
        # Mock responses - some succeed, some fail
        indeed.fetch_jobs = AsyncMock(return_value=[
            JobPosting(
                id="indeed_job_1",
                source="indeed",
                company="Indeed Company",
                title="Software Engineer",
                location="Remote",
                url="https://indeed.example.com/job1",
                date_posted=datetime.now(timezone.utc)
            )
        ])
        
        linkedin.fetch_jobs = AsyncMock(side_effect=Exception("LinkedIn API Error"))
        
        ziprecruiter.fetch_jobs = AsyncMock(return_value=[
            JobPosting(
                id="ziprecruiter_job_1",
                source="ziprecruiter", 
                company="ZipRecruiter Company",
                title="Developer",
                location="San Francisco",
                url="https://ziprecruiter.example.com/job1",
                date_posted=datetime.now(timezone.utc)
            )
        ])
        
        greenhouse.fetch_jobs = AsyncMock(side_effect=Exception("Greenhouse Error"))
        
        params = FetchParams(keywords=["developer"], location="Remote")
        
        results = await orchestrator.fetch_all_sources(params)
        
        # Should have jobs from successful sources only
        assert results["metadata"]["total_jobs"] == 2  # Indeed + ZipRecruiter
        assert results["metadata"]["sources_queried"] == 4
        assert results["metadata"]["successful_sources"] == 2
        assert results["metadata"]["failed_sources"] == 2
        
        # Should have error information
        assert len(results["errors"]) == 2
        assert "linkedin" in results["errors"]
        assert "greenhouse" in results["errors"]
        
    @pytest.mark.asyncio
    async def test_deduplication_integration(self, orchestrator, service_registry):
        """Test job deduplication across sources."""
        # Create duplicate jobs from different sources
        duplicate_job_data = {
            "id": "original_job",
            "source": "indeed",
            "company": "Duplicate Company",
            "title": "Duplicate Job Title",
            "location": "Remote",
            "url": "https://company.com/job/original",
            "date_posted": datetime.now(timezone.utc)
        }
        
        indeed_job = JobPosting(**duplicate_job_data)
        
        # Same job from different source
        linkedin_job = JobPosting(
            **{**duplicate_job_data, "id": "linkedin_duplicate", "source": "linkedin"}
        )
        
        # Different job 
        ziprecruiter_job = JobPosting(
            id="unique_job",
            source="ziprecruiter",
            company="Unique Company", 
            title="Unique Job Title",
            location="Remote",
            url="https://unique.com/job1",
            date_posted=datetime.now(timezone.utc)
        )
        
        # Mock scraper responses
        service_registry.get_source("indeed").fetch_jobs = AsyncMock(return_value=[indeed_job])
        service_registry.get_source("linkedin").fetch_jobs = AsyncMock(return_value=[linkedin_job])
        service_registry.get_source("ziprecruiter").fetch_jobs = AsyncMock(return_value=[ziprecruiter_job])
        service_registry.get_source("greenhouse").fetch_jobs = AsyncMock(return_value=[])
        
        params = FetchParams(keywords=["test"], location="Remote")
        
        results = await orchestrator.fetch_all_sources(params)
        
        # Should deduplicate the identical jobs
        assert results["metadata"]["total_jobs"] == 2  # Original + unique, duplicate removed
        assert results["metadata"]["duplicates_removed"] == 1
        
    @pytest.mark.asyncio
    async def test_concurrent_fetching(self, orchestrator, service_registry):
        """Test concurrent job fetching with rate limiting."""
        import time
        
        # Mock slow responses to test concurrency
        async def slow_fetch(params):
            await asyncio.sleep(0.1)  # Simulate slow response
            return [
                JobPosting(
                    id="slow_job",
                    source="test",
                    company="Slow Company",
                    title="Slow Job",
                    location="Remote", 
                    url="https://slow.com/job",
                    date_posted=datetime.now(timezone.utc)
                )
            ]
            
        # Apply to all sources
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            source = service_registry.get_source(source_name)
            source.fetch_jobs = slow_fetch
            
        params = FetchParams(keywords=["test"], location="Remote")
        
        start_time = time.time()
        results = await orchestrator.fetch_all_sources(params)
        end_time = time.time()
        
        # Should complete in less time than sequential (4 * 0.1 = 0.4s)
        # With concurrency of 2, should take ~0.2s
        assert (end_time - start_time) < 0.35  # Some buffer for test execution
        assert results["metadata"]["total_jobs"] >= 4
        
    @pytest.mark.asyncio
    async def test_registry_statistics(self, service_registry):
        """Test registry statistics integration."""
        stats = service_registry.get_registry_stats()
        
        assert stats["total_sources"] == 4
        assert stats["enabled_sources"] == 4
        assert stats["sources_by_type"]["BROWSER_SCRAPER"] == 4
        
    @pytest.mark.asyncio
    async def test_source_filtering(self, service_registry):
        """Test source filtering by type and status."""
        # All sources are browser scrapers
        browser_sources = service_registry.list_sources(source_type="BROWSER_SCRAPER")
        assert len(browser_sources) == 4
        
        # No API connectors registered
        api_sources = service_registry.list_sources(source_type="API_CONNECTOR")
        assert len(api_sources) == 0
        
        # All sources enabled by default
        enabled_sources = service_registry.list_sources(enabled_only=True)
        assert len(enabled_sources) == 4


class TestScrapingServiceEdgeCases:
    """Test edge cases and error conditions."""
    
    @pytest.fixture
    def empty_registry(self):
        """Create empty registry."""
        return ServiceRegistry()
        
    @pytest.fixture
    def empty_orchestrator(self, empty_registry):
        """Create orchestrator with no sources."""
        return ScrapingOrchestrator(empty_registry)
        
    @pytest.mark.asyncio
    async def test_empty_registry_behavior(self, empty_orchestrator):
        """Test behavior with no registered sources."""
        params = FetchParams(keywords=["test"], location="Remote")
        
        results = await empty_orchestrator.fetch_all_sources(params)
        
        assert results["metadata"]["total_jobs"] == 0
        assert results["metadata"]["sources_queried"] == 0
        assert results["metadata"]["successful_sources"] == 0
        assert results["metadata"]["failed_sources"] == 0
        assert len(results["jobs"]) == 0
        
    @pytest.mark.asyncio 
    async def test_all_sources_failing(self, orchestrator, service_registry):
        """Test behavior when all sources fail."""
        # Make all sources fail
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            source = service_registry.get_source(source_name)
            source.fetch_jobs = AsyncMock(side_effect=Exception(f"{source_name} failed"))
            
        params = FetchParams(keywords=["test"], location="Remote")
        
        results = await orchestrator.fetch_all_sources(params)
        
        assert results["metadata"]["total_jobs"] == 0
        assert results["metadata"]["sources_queried"] == 4
        assert results["metadata"]["successful_sources"] == 0
        assert results["metadata"]["failed_sources"] == 4
        assert len(results["errors"]) == 4
        
    def test_duplicate_source_registration(self, service_registry):
        """Test registering duplicate sources."""
        # Registry already has scrapers, try to add duplicate
        duplicate_indeed = IndeedScraper()
        
        success = service_registry.register_source(duplicate_indeed)
        assert success is False  # Should fail
        
        # Should still have only 4 sources
        sources = service_registry.list_sources()
        assert len(sources) == 4
        
    @pytest.mark.asyncio
    async def test_cleanup_integration(self, service_registry):
        """Test cleanup of all sources."""
        # Mock cleanup methods
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            source = service_registry.get_source(source_name)
            source.cleanup = AsyncMock()
            
        await service_registry.cleanup_all_sources()
        
        # All sources should have cleanup called
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            source = service_registry.get_source(source_name)
            assert source.cleanup.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
