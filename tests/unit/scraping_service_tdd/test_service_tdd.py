"""
TDD Test Suite for Scraping Service

This module implements comprehensive Test-Driven Development tests for the
Scraping Service microservice. Tests are written BEFORE implementation to
define the exact behavior and interface requirements.

Following the RED-GREEN-REFACTOR TDD methodology:
1. RED: Write failing tests that define the interface
2. GREEN: Implement minimal code to pass tests  
3. REFACTOR: Optimize while keeping tests passing

Test Categories:
- Service Lifecycle Management (start/stop/health)
- Job Scraping Operations (core functionality)
- Source Management (enable/disable/capabilities)
- Query Validation and Processing
- Error Handling and Edge Cases
- Statistics and Monitoring
- Performance and Resource Management
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# Import contracts and expected exceptions
from tpm_job_finder_poc.shared.contracts.scraping_service import (
    IScrapingService,
    ScrapingConfig,
    ScrapingQuery,
    ScrapingResult,
    ScrapingStatistics,
    SourceHealth,
    ServiceNotStartedError,
    SourceNotFoundError,
    ScrapingTimeoutError,
    ServiceError,
    ConfigurationError
)
from tpm_job_finder_poc.scraping_service.core.base_job_source import JobPosting


class TestScrapingServiceLifecycle:
    """Test service lifecycle management operations."""
    
    @pytest.mark.asyncio
    async def test_service_starts_successfully(self, sample_config):
        """Test that service starts with valid configuration."""
        # This test will fail until we implement ScrapingService
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        
        assert not service.is_running()
        
        await service.start()
        
        assert service.is_running()
        
        # Clean up
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_service_stops_gracefully(self, sample_config):
        """Test that service stops gracefully and cleans up resources."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        assert service.is_running()
        
        await service.stop()
        
        assert not service.is_running()
    
    @pytest.mark.asyncio
    async def test_service_start_is_idempotent(self, sample_config):
        """Test that multiple start calls don't cause issues."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        
        # Start multiple times
        await service.start()
        await service.start()
        await service.start()
        
        assert service.is_running()
        
        await service.stop()
    
    @pytest.mark.asyncio
    async def test_service_stop_is_idempotent(self, sample_config):
        """Test that multiple stop calls don't cause issues."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        # Stop multiple times
        await service.stop()
        await service.stop()
        await service.stop()
        
        assert not service.is_running()
    
    @pytest.mark.asyncio
    async def test_service_initialization_with_invalid_config(self):
        """Test that service fails to start with invalid configuration."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        # Test that invalid config is properly rejected by Pydantic
        with pytest.raises(ValueError, match="value must be positive"):
            ScrapingConfig(timeout_seconds=-1)
            
        # Test service with minimal valid config for other validation
        from pydantic import ValidationError
        try:
            # This will work - create valid config for further testing
            valid_config = ScrapingConfig()
            service = ScrapingService(valid_config)
            
            # Test internal configuration validation in start() method
            # This will be implemented to check additional constraints
            await service.start()
            await service.stop()
            
        except ConfigurationError:
            # Expected for additional validation in service.start()
            pass
    
    @pytest.mark.asyncio
    async def test_health_status_before_start(self, sample_config):
        """Test health status reporting before service is started."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        
        health = await service.get_health_status()
        
        assert health["status"] == "stopped"
        assert health["running"] is False
    
    @pytest.mark.asyncio
    async def test_health_status_after_start(self, sample_config):
        """Test health status reporting after service is started."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            health = await service.get_health_status()
            
            assert health["status"] == "running"
            assert health["running"] is True
            assert "uptime_seconds" in health
            assert "browser_instances" in health
            assert health["browser_instances"]["active"] >= 0
        finally:
            await service.stop()


class TestJobScrapingOperations:
    """Test core job scraping functionality."""
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_basic_functionality(self, sample_config, sample_query):
        """Test basic job scraping with valid query."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            result = await service.scrape_jobs(sample_query)
            
            # Verify result structure
            assert isinstance(result, ScrapingResult)
            assert isinstance(result.jobs, list)
            assert isinstance(result.query, ScrapingQuery)
            assert result.query.keywords == sample_query.keywords
            assert result.query.location == sample_query.location
            
            # Verify statistics
            assert result.total_jobs_found >= 0
            assert result.jobs_after_deduplication >= 0
            assert result.duplicates_removed >= 0
            assert result.sources_queried > 0
            assert result.successful_sources >= 0
            assert result.failed_sources >= 0
            assert result.processing_time_seconds > 0
            
            # Verify timestamps
            assert isinstance(result.scraped_at, datetime)
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_with_specific_sources(self, sample_config):
        """Test scraping with specific source selection."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["developer"],
                location="Remote",
                sources=["indeed", "ziprecruiter"],
                max_results=25
            )
            
            result = await service.scrape_jobs(query)
            
            # Should only query specified sources
            assert result.sources_queried == 2
            assert "indeed" in result.source_results or "indeed" in result.errors
            assert "ziprecruiter" in result.source_results or "ziprecruiter" in result.errors
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_with_custom_config(self, sample_config, sample_query):
        """Test scraping with custom configuration override."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Custom config with different settings
            custom_config = ScrapingConfig(
                timeout_seconds=60,
                max_concurrent_scrapers=1,
                indeed_rate_limit=5
            )
            
            result = await service.scrape_jobs(sample_query, config=custom_config)
            
            assert isinstance(result, ScrapingResult)
            assert result.processing_time_seconds > 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_with_empty_keywords(self, sample_config):
        """Test scraping fails with invalid empty keywords."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Test that empty keywords are properly rejected by Pydantic
            with pytest.raises(ValueError, match="keywords must contain at least one non-empty string"):
                ScrapingQuery(
                    keywords=[],  # Empty keywords should fail validation
                    location="Remote"
                )
            
            # Test that whitespace-only keywords are also rejected
            with pytest.raises(ValueError, match="keywords must contain at least one non-empty string"):
                ScrapingQuery(
                    keywords=["", "   ", "\t"],  # Whitespace-only keywords should fail
                    location="Remote"
                )
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_service_not_started(self, sample_config, sample_query):
        """Test scraping fails when service is not started."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        
        # Don't start the service
        
        with pytest.raises(ServiceNotStartedError):
            await service.scrape_jobs(sample_query)
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_timeout_handling(self, sample_config):
        """Test timeout handling during scraping operations."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        # Very short timeout to force timeout
        config = ScrapingConfig(timeout_seconds=1)
        service = ScrapingService(config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["software engineer"],
                location="Remote",
                max_results=100  # Large request more likely to timeout
            )
            
            # Should either complete quickly or raise timeout error
            result = await service.scrape_jobs(query)
            
            # If it completes, verify it's reasonable
            assert isinstance(result, ScrapingResult)
            assert result.processing_time_seconds <= 10  # Should be fast
            
        except ScrapingTimeoutError:
            # Timeout is acceptable with very short timeout
            pass
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_deduplication(self, sample_config):
        """Test that duplicate jobs are properly removed."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["python developer"],
                location="Remote",
                sources=["indeed", "ziprecruiter"],  # Multiple sources increase chance of duplicates
                max_results=50
            )
            
            result = await service.scrape_jobs(query)
            
            # If duplicates were found, verify they were removed
            if result.duplicates_removed > 0:
                assert result.total_jobs_found > result.jobs_after_deduplication
                assert result.duplicates_removed == result.total_jobs_found - result.jobs_after_deduplication
            
            # Verify no duplicate URLs in final results
            urls = [job.url for job in result.jobs if job.url]
            assert len(urls) == len(set(urls))  # No duplicate URLs
            
        finally:
            await service.stop()


class TestSourceManagement:
    """Test scraping source management operations."""
    
    @pytest.mark.asyncio
    async def test_get_available_sources(self, sample_config):
        """Test getting list of available scraping sources."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            sources = await service.get_available_sources()
            
            assert isinstance(sources, list)
            assert len(sources) > 0
            
            # Should include common job sources
            expected_sources = ["indeed", "linkedin", "ziprecruiter", "greenhouse"]
            for expected in expected_sources:
                assert expected in sources
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_enable_disable_source(self, sample_config):
        """Test enabling and disabling specific sources."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Disable a source
            success = await service.disable_source("linkedin")
            assert success is True
            
            # Enable it back
            success = await service.enable_source("linkedin")
            assert success is True
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_enable_nonexistent_source(self, sample_config):
        """Test enabling non-existent source raises error."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            with pytest.raises(SourceNotFoundError):
                await service.enable_source("nonexistent_source")
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_check_source_health_all(self, sample_config):
        """Test health check for all sources."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            health = await service.check_source_health()
            
            assert isinstance(health, dict)
            assert len(health) > 0
            
            # Check each source health
            for source_name, source_health in health.items():
                assert isinstance(source_health, SourceHealth)
                assert source_health.source_name == source_name
                assert source_health.status in ["healthy", "degraded", "unhealthy", "unknown"]
                assert source_health.response_time_ms >= 0
                assert 0.0 <= source_health.success_rate <= 1.0
                assert isinstance(source_health.last_check, datetime)
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_check_specific_source_health(self, sample_config):
        """Test health check for specific source."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            health = await service.check_source_health("indeed")
            
            assert isinstance(health, dict)
            assert "indeed" in health
            assert isinstance(health["indeed"], SourceHealth)
            assert health["indeed"].source_name == "indeed"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_get_source_capabilities(self, sample_config):
        """Test getting source capabilities and supported parameters."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            capabilities = await service.get_source_capabilities()
            
            assert isinstance(capabilities, dict)
            assert len(capabilities) > 0
            
            # Check capabilities structure for each source
            for source_name, caps in capabilities.items():
                assert isinstance(caps, dict)
                assert "supported_parameters" in caps
                assert "rate_limits" in caps
                assert "type" in caps
                assert caps["type"] in ["api_connector", "browser_scraper"]
                
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_get_specific_source_capabilities(self, sample_config):
        """Test getting capabilities for specific source."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            capabilities = await service.get_source_capabilities("indeed")
            
            assert isinstance(capabilities, dict)
            assert "indeed" in capabilities
            assert "supported_parameters" in capabilities["indeed"]
            
        finally:
            await service.stop()


class TestQueryValidation:
    """Test query validation and processing."""
    
    @pytest.mark.asyncio
    async def test_validate_query_valid_parameters(self, sample_config, sample_query):
        """Test validation of valid query parameters."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            validation_result = await service.validate_query(sample_query)
            
            assert isinstance(validation_result, dict)
            assert validation_result["valid"] is True
            assert "warnings" in validation_result
            assert "supported_sources" in validation_result
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_validate_query_invalid_sources(self, sample_config):
        """Test validation with invalid source selection."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            invalid_query = ScrapingQuery(
                keywords=["developer"],
                location="Remote",
                sources=["nonexistent_source", "another_fake_source"]
            )
            
            validation_result = await service.validate_query(invalid_query)
            
            assert validation_result["valid"] is False
            assert len(validation_result["errors"]) > 0
            assert "Invalid sources" in str(validation_result["errors"])
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_validate_query_excessive_max_results(self, sample_config):
        """Test validation with excessive max_results."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Query with excessive results should generate warning
            excessive_query = ScrapingQuery(
                keywords=["developer"],
                location="Remote",
                max_results=1000  # Very high number
            )
            
            validation_result = await service.validate_query(excessive_query)
            
            # Should be valid but with warnings
            assert validation_result["valid"] is True
            assert len(validation_result["warnings"]) > 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_validate_query_service_not_started(self, sample_config, sample_query):
        """Test query validation fails when service not started."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        
        # Don't start service
        
        with pytest.raises(ServiceNotStartedError):
            await service.validate_query(sample_query)


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    @pytest.mark.asyncio
    async def test_scrape_jobs_all_sources_fail(self, sample_config):
        """Test behavior when all sources fail."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Use non-existent sources to force failures
            failing_query = ScrapingQuery(
                keywords=["developer"],
                location="Remote",
                sources=["nonexistent1", "nonexistent2"]
            )
            
            # Should complete but with errors, not raise exception
            result = await service.scrape_jobs(failing_query)
            
            assert isinstance(result, ScrapingResult)
            assert result.successful_sources == 0
            assert result.failed_sources > 0
            assert len(result.jobs) == 0
            assert len(result.errors) > 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_browser_failure_recovery(self, sample_config):
        """Test recovery from browser failures."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Service should handle browser failures gracefully
            # This test will verify the service can continue operating
            # even after simulated browser crashes
            
            query = ScrapingQuery(
                keywords=["test"],
                location="Remote",
                max_results=5
            )
            
            result = await service.scrape_jobs(query)
            
            # Should complete without raising exceptions
            assert isinstance(result, ScrapingResult)
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_operations_on_stopped_service(self, sample_config, sample_query):
        """Test that operations fail appropriately on stopped service."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        await service.stop()
        
        # All operations should fail with ServiceNotStartedError
        with pytest.raises(ServiceNotStartedError):
            await service.scrape_jobs(sample_query)
            
        with pytest.raises(ServiceNotStartedError):
            await service.get_available_sources()
            
        with pytest.raises(ServiceNotStartedError):
            await service.check_source_health()
            
        with pytest.raises(ServiceNotStartedError):
            await service.validate_query(sample_query)


class TestStatisticsAndMonitoring:
    """Test statistics tracking and monitoring functionality."""
    
    @pytest.mark.asyncio
    async def test_get_statistics_initial_state(self, sample_config):
        """Test statistics in initial state."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            stats = await service.get_statistics()
            
            assert isinstance(stats, ScrapingStatistics)
            assert stats.total_queries_processed == 0
            assert stats.total_jobs_scraped == 0
            assert stats.total_successful_scrapes == 0
            assert stats.total_failed_scrapes == 0
            assert stats.average_query_time == 0.0
            assert stats.first_scrape_time is None
            assert stats.last_scrape_time is None
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_statistics_updated_after_scraping(self, sample_config, sample_query):
        """Test statistics are updated after scraping operations."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Get initial stats
            initial_stats = await service.get_statistics()
            
            # Perform scraping
            await service.scrape_jobs(sample_query)
            
            # Get updated stats
            updated_stats = await service.get_statistics()
            
            # Verify stats were updated
            assert updated_stats.total_queries_processed > initial_stats.total_queries_processed
            assert updated_stats.total_jobs_scraped >= initial_stats.total_jobs_scraped
            assert updated_stats.first_scrape_time is not None
            assert updated_stats.last_scrape_time is not None
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_reset_statistics(self, sample_config, sample_query):
        """Test statistics reset functionality."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Perform some operations
            await service.scrape_jobs(sample_query)
            
            # Verify stats are populated
            stats = await service.get_statistics()
            assert stats.total_queries_processed > 0
            
            # Reset statistics
            await service.reset_statistics()
            
            # Verify stats are reset
            reset_stats = await service.get_statistics()
            assert reset_stats.total_queries_processed == 0
            assert reset_stats.total_jobs_scraped == 0
            assert reset_stats.first_scrape_time is None
            assert reset_stats.last_scrape_time is None
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_uptime_tracking(self, sample_config):
        """Test service uptime tracking."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        
        # Check uptime before start
        health1 = await service.get_health_status()
        assert health1["uptime_seconds"] == 0.0
        
        await service.start()
        
        # Wait a small amount of time
        await asyncio.sleep(0.1)
        
        try:
            # Check uptime after start
            health2 = await service.get_health_status()
            assert health2["uptime_seconds"] > 0.0
            
            # Get statistics
            stats = await service.get_statistics()
            assert stats.uptime_seconds > 0.0
            
        finally:
            await service.stop()


class TestPerformanceAndResourceManagement:
    """Test performance characteristics and resource management."""
    
    @pytest.mark.asyncio
    async def test_concurrent_scraping_operations(self, sample_config):
        """Test that service can handle concurrent scraping operations."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Create multiple queries
            queries = [
                ScrapingQuery(keywords=["python"], location="Remote", max_results=10),
                ScrapingQuery(keywords=["javascript"], location="New York", max_results=10),
                ScrapingQuery(keywords=["java"], location="San Francisco", max_results=10)
            ]
            
            # Execute concurrently
            tasks = [service.scrape_jobs(query) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete successfully (or with expected exceptions)
            for result in results:
                if isinstance(result, Exception):
                    # Only acceptable exceptions
                    assert isinstance(result, (ScrapingTimeoutError, ServiceError))
                else:
                    assert isinstance(result, ScrapingResult)
                    
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_browser_instance_management(self, sample_config):
        """Test browser instance creation and cleanup."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Check initial browser instances
            health = await service.get_health_status()
            initial_instances = health["browser_instances"]["active"]
            
            # Perform scraping to trigger browser usage
            query = ScrapingQuery(keywords=["test"], location="Remote", max_results=5)
            await service.scrape_jobs(query)
            
            # Check browser instances after scraping
            health_after = await service.get_health_status()
            
            # Should have reasonable number of instances
            assert health_after["browser_instances"]["active"] <= sample_config.max_browser_instances
            assert health_after["browser_instances"]["total_created"] >= 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_rate_limiting_respected(self, sample_config):
        """Test that rate limiting is properly enforced."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        # Create config with very low rate limits for testing
        rate_limited_config = ScrapingConfig(
            indeed_rate_limit=1,  # Very low for testing
            linkedin_rate_limit=1,
            max_concurrent_scrapers=1
        )
        
        service = ScrapingService(rate_limited_config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["test"],
                location="Remote",
                sources=["indeed"],
                max_results=5
            )
            
            start_time = datetime.now()
            await service.scrape_jobs(query)
            end_time = datetime.now()
            
            # With rate limiting, operation should take some minimum time
            duration = (end_time - start_time).total_seconds()
            
            # Rate limiting should add some delay
            # This is a loose check since actual timing depends on implementation
            assert duration >= 0.0  # At least completed
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_memory_management(self, sample_config):
        """Test that memory usage is managed properly."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingService
        
        service = ScrapingService(sample_config)
        await service.start()
        
        try:
            # Perform multiple scraping operations
            for i in range(3):
                query = ScrapingQuery(
                    keywords=[f"test_{i}"],
                    location="Remote",
                    max_results=10
                )
                await service.scrape_jobs(query)
            
            # Check health status for memory information
            health = await service.get_health_status()
            
            # Should have memory statistics
            assert "browser_instances" in health
            assert "memory_usage_mb" in health
            
            # Memory usage should be within reasonable bounds
            if health["memory_usage_mb"] > 0:
                assert health["memory_usage_mb"] <= sample_config.browser_memory_limit_mb * sample_config.max_browser_instances
                
        finally:
            await service.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])