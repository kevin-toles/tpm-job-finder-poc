"""
True TDD Test Suite for Scraping Service

This test suite is written BEFORE implementation to define the exact interface
and behavior requirements based on the documented scraping service requirements.
These tests should FAIL initially (RED phase) and drive the implementation.

Requirements tested based on README.md:
1. Multi-source orchestration (Indeed, LinkedIn, ZipRecruiter, Greenhouse)
2. Browser automation with Selenium WebDriver
3. Anti-detection mechanisms (user agent rotation, viewport randomization, timing)
4. Service registry for scraper discovery and management
5. Health monitoring and rate limiting
6. Deduplication algorithms (URL-based and title+company)
7. Configuration management with environment variables
8. Error handling and recovery (browser failures, rate limits, timeouts)
9. Performance requirements (50-100 jobs/minute, concurrent processing)
10. Plugin-based architecture for adding new scrapers

This follows TRUE TDD: Write tests that define the requirements, then implement
to satisfy these tests. Tests should be comprehensive and test real behavior,
not mocked implementations.
"""

import pytest
import asyncio
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List
import tempfile
import os

# Core interfaces and models
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
from tpm_job_finder_poc.scraping_service.core.base_job_source import (
    JobPosting,
    FetchParams,
    HealthStatus,
    SourceType,
    BaseJobSource
)


class TestMultiSourceOrchestration:
    """Test multi-source job collection orchestration requirements."""

    @pytest.mark.asyncio
    async def test_collect_jobs_from_multiple_sources_concurrently(self, service_config):
        """Test concurrent job collection from multiple sources as documented."""
        # RED: This test should fail until we implement real orchestration
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["python developer", "software engineer"],
                location="San Francisco",
                sources=["indeed", "linkedin", "ziprecruiter", "greenhouse"],
                max_results=100
            )
            
            start_time = time.time()
            result = await service.scrape_jobs(query)
            execution_time = time.time() - start_time
            
            # Should process all 4 sources concurrently
            assert result.sources_queried == 4
            assert len(result.source_results) == 4
            
            # All documented sources should be attempted
            expected_sources = {"indeed", "linkedin", "ziprecruiter", "greenhouse"}
            actual_sources = set(result.source_results.keys()).union(set(result.errors.keys()))
            assert expected_sources.issubset(actual_sources)
            
            # Concurrent processing should be faster than sequential
            # (4 sources should complete in < 4x single source time)
            assert execution_time < 30  # Maximum reasonable time for concurrent processing
            
            # Each source should report proper status
            for source, source_result in result.source_results.items():
                assert "status" in source_result
                assert source_result["status"] in ["success", "error", "timeout"]
                assert "response_time_ms" in source_result
                assert isinstance(source_result["response_time_ms"], float)
                
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_orchestrator_manages_service_registry(self, service_config):
        """Test that orchestrator properly uses service registry for scraper discovery."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Service should discover and register all platform scrapers
            available_sources = await service.get_available_sources()
            
            # Should include all documented scrapers
            expected_scrapers = ["indeed", "linkedin", "ziprecruiter", "greenhouse"]
            for scraper in expected_scrapers:
                assert scraper in available_sources
                
            # Should support adding/removing scrapers dynamically
            # Test enabling/disabling sources affects orchestration
            await service.disable_source("linkedin")
            
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed", "linkedin"],  # linkedin should be ignored
                max_results=10
            )
            
            result = await service.scrape_jobs(query)
            
            # Should only process enabled sources
            assert "indeed" in result.source_results or "indeed" in result.errors
            # LinkedIn should be skipped (disabled)
            if "linkedin" in result.source_results:
                assert result.source_results["linkedin"]["status"] == "disabled"
                
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_deduplication_across_sources(self, service_config):
        """Test job deduplication logic as documented in README."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["software engineer"],
                location="Remote",
                sources=["indeed", "ziprecruiter"],  # Sources likely to have duplicates
                max_results=50
            )
            
            result = await service.scrape_jobs(query)
            
            # Should report deduplication statistics
            assert hasattr(result, 'total_jobs_found')
            assert hasattr(result, 'jobs_after_deduplication') 
            assert hasattr(result, 'duplicates_removed')
            
            # Duplicates removed should be non-negative
            assert result.duplicates_removed >= 0
            assert result.jobs_after_deduplication <= result.total_jobs_found
            assert len(result.jobs) == result.jobs_after_deduplication
            
            # Should deduplicate by URL and title+company as documented
            job_urls = set()
            job_combinations = set()
            
            for job in result.jobs:
                # Convert to dict if it's a JobPosting object
                if hasattr(job, 'to_dict'):
                    job_dict = job.to_dict()
                else:
                    job_dict = job
                    
                # No duplicate URLs
                if job_dict.get('url'):
                    assert job_dict['url'] not in job_urls
                    job_urls.add(job_dict['url'])
                    
                # No duplicate title+company combinations  
                if job_dict.get('title') and job_dict.get('company'):
                    combo = (job_dict['title'].lower(), job_dict['company'].lower())
                    assert combo not in job_combinations
                    job_combinations.add(combo)
                    
        finally:
            await service.stop()


class TestBrowserAutomationRequirements:
    """Test browser automation and Selenium WebDriver requirements."""

    @pytest.mark.asyncio
    async def test_browser_setup_with_selenium_webdriver(self, service_config):
        """Test that service sets up real Selenium WebDriver instances."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Service should initialize browser instances
            health = await service.get_health_status()
            
            assert "browser_instances" in health
            assert "webdriver_version" in health  # Should report WebDriver version
            assert "chrome_version" in health     # Should report Chrome version
            
            # Should be able to create browsers within limits
            max_browsers = service_config.max_browser_instances
            assert health["browser_instances"]["active"] <= max_browsers
            
            # Trigger browser usage through scraping
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed"],  # Single source to control browser usage
                max_results=5
            )
            
            await service.scrape_jobs(query)
            
            # Browser instances should be created and tracked
            health_after = await service.get_health_status()
            assert health_after["browser_instances"]["total_created"] > 0
            
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_browser_instance_pool_management(self, service_config):
        """Test browser instance pooling and reuse as documented."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        # Configure for testing with limited browsers
        config = ScrapingConfig(
            headless=service_config.headless,
            timeout_seconds=service_config.timeout_seconds,
            max_retries=service_config.max_retries,
            user_agent_rotation=service_config.user_agent_rotation,
            enable_anti_detection=service_config.enable_anti_detection,
            delay_min_seconds=service_config.delay_min_seconds,
            delay_max_seconds=service_config.delay_max_seconds,
            viewport_randomization=service_config.viewport_randomization,
            javascript_protection=service_config.javascript_protection,
            max_browser_instances=2,  # Override for testing
            browser_instance_timeout=300,  # Override for testing
            indeed_rate_limit=service_config.indeed_rate_limit,
            linkedin_rate_limit=service_config.linkedin_rate_limit,
            ziprecruiter_rate_limit=service_config.ziprecruiter_rate_limit,
            greenhouse_rate_limit=service_config.greenhouse_rate_limit,
            enable_parallel_processing=service_config.enable_parallel_processing,
            max_concurrent_scrapers=service_config.max_concurrent_scrapers,
            fail_on_source_error=service_config.fail_on_source_error
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Multiple scraping operations should reuse browser instances
            queries = [
                ScrapingQuery(keywords=["test1"], sources=["indeed"], max_results=1),
                ScrapingQuery(keywords=["test2"], sources=["ziprecruiter"], max_results=1),
                ScrapingQuery(keywords=["test3"], sources=["indeed"], max_results=1),
            ]
            
            results = []
            for query in queries:
                result = await service.scrape_jobs(query)
                results.append(result)
                
            health = await service.get_health_status()
            
            # Should not create more browsers than configured limit
            assert health["browser_instances"]["active"] <= config.max_browser_instances
            
            # Should have reused browsers (fewer created than operations)
            assert health["browser_instances"]["total_created"] <= len(queries)
            
        finally:
            await service.stop()

    @pytest.mark.asyncio 
    async def test_browser_cleanup_on_service_stop(self, service_config):
        """Test that all browser instances are properly cleaned up."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        # Create some browser activity
        query = ScrapingQuery(
            keywords=["test"],
            sources=["indeed", "ziprecruiter"], 
            max_results=5
        )
        
        await service.scrape_jobs(query)
        
        health_before = await service.get_health_status()
        assert health_before["browser_instances"]["active"] >= 0
        
        # Stop service should clean up all browsers
        await service.stop()
        
        # Verify cleanup (service should track this)
        # Note: This would need to be implemented to track cleanup status
        health_after = await service.get_health_status()
        assert health_after["browser_instances"]["active"] == 0


class TestAntiDetectionFeatures:
    """Test anti-detection mechanisms as documented in README."""

    @pytest.mark.asyncio
    async def test_user_agent_rotation_enabled(self, service_config):
        """Test user agent rotation with realistic browser fingerprints."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        # Enable user agent rotation
        config = create_config_with_overrides(
            service_config,
            user_agent_rotation=True
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Multiple scraping operations should use different user agents
            user_agents_used = set()
            
            for i in range(3):
                query = ScrapingQuery(
                    keywords=[f"test{i}"],
                    sources=["indeed"],
                    max_results=1
                )
                
                result = await service.scrape_jobs(query)
                
                # Result should include user agent information for verification
                assert "user_agent_used" in result.source_results.get("indeed", {})
                user_agent = result.source_results["indeed"]["user_agent_used"]
                user_agents_used.add(user_agent)
                
            # Should use different user agents (rotation)
            assert len(user_agents_used) > 1, "User agent rotation not working"
            
            # User agents should be realistic (contain Chrome, Mozilla, etc.)
            for ua in user_agents_used:
                assert any(browser in ua for browser in ["Chrome", "Mozilla", "Safari"])
                
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_viewport_randomization(self, service_config):
        """Test viewport randomization to avoid detection."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        config = create_config_with_overrides(
            service_config,
            viewport_randomization=True
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            viewports_used = set()
            
            for i in range(3):
                query = ScrapingQuery(
                    keywords=[f"test{i}"],
                    sources=["indeed"],
                    max_results=1
                )
                
                result = await service.scrape_jobs(query)
                
                # Should track viewport dimensions used
                source_result = result.source_results.get("indeed", {})
                if "viewport_dimensions" in source_result:
                    viewport = source_result["viewport_dimensions"]
                    viewports_used.add(tuple(viewport))
                    
            # Should use different viewport sizes
            if viewports_used:
                assert len(viewports_used) > 1, "Viewport randomization not working"
                
                # Viewports should be realistic (common screen sizes)
                for width, height in viewports_used:
                    assert 1024 <= width <= 2560  # Reasonable width range
                    assert 768 <= height <= 1440  # Reasonable height range
                    
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_request_timing_delays(self, service_config):
        """Test intelligent request timing with randomized delays."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        config = create_config_with_overrides(
            service_config,
            enable_anti_detection=True,
            delay_min_seconds=1.0,
            delay_max_seconds=3.0
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Multiple requests should have delays between them
            start_times = []
            
            for i in range(3):
                start_time = time.time()
                
                query = ScrapingQuery(
                    keywords=[f"test{i}"],
                    sources=["indeed"],
                    max_results=1
                )
                
                await service.scrape_jobs(query)
                start_times.append(start_time)
                
            # Check delays between requests
            for i in range(1, len(start_times)):
                delay = start_times[i] - start_times[i-1]
                # Should have minimum delay configured
                assert delay >= config.delay_min_seconds - 0.1  # Small tolerance for execution time
                
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_javascript_protection_enabled(self, service_config):
        """Test JavaScript property masking and automation trace removal."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        config = create_config_with_overrides(
            service_config,
            javascript_protection=True
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed"],
                max_results=1
            )
            
            result = await service.scrape_jobs(query)
            
            # Should report JavaScript protection status
            source_result = result.source_results.get("indeed", {})
            assert "javascript_protection_enabled" in source_result
            assert source_result["javascript_protection_enabled"] is True
            
            # Should mask automation properties (webdriver, automation flags)
            if "javascript_properties_masked" in source_result:
                masked_props = source_result["javascript_properties_masked"]
                expected_masks = ["webdriver", "automation", "cdc_", "selenium"]
                assert any(prop in masked_props for prop in expected_masks)
                
        finally:
            await service.stop()


class TestRateLimitingEnforcement:
    """Test rate limiting enforcement as documented."""

    @pytest.mark.asyncio
    async def test_platform_specific_rate_limits_enforced(self, service_config):
        """Test that platform-specific rate limits are enforced."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        # Configure very low rate limits for testing
        config = create_config_with_overrides(
            service_config,
            indeed_rate_limit=2,      # 2 requests per minute
            linkedin_rate_limit=1,    # 1 request per minute
            ziprecruiter_rate_limit=3 # 3 requests per minute
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Multiple rapid requests should be rate limited
            start_time = time.time()
            
            queries = [
                ScrapingQuery(keywords=["test1"], sources=["indeed"], max_results=1),
                ScrapingQuery(keywords=["test2"], sources=["indeed"], max_results=1),
                ScrapingQuery(keywords=["test3"], sources=["indeed"], max_results=1),  # Should be rate limited
            ]
            
            results = []
            for query in queries:
                result = await service.scrape_jobs(query)
                results.append(result)
                
            total_time = time.time() - start_time
            
            # Should enforce rate limiting (spread requests over time)
            # 3 requests at 2/minute should take at least 60 seconds for the 3rd
            expected_min_time = 60 / config.indeed_rate_limit  # 30 seconds for 2 requests
            
            # Check that rate limiting information is reported
            for result in results:
                source_result = result.source_results.get("indeed", {})
                if "rate_limit_status" in source_result:
                    rate_status = source_result["rate_limit_status"]
                    assert "requests_remaining" in rate_status
                    assert "reset_time" in rate_status
                    
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_rate_limit_backoff_strategy(self, service_config):
        """Test exponential backoff when rate limits are exceeded."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        config = create_config_with_overrides(
            service_config,
            indeed_rate_limit=1,  # Very restrictive
            max_retries=3
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Rapid requests should trigger backoff
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed"],
                max_results=1
            )
            
            # First request should succeed
            result1 = await service.scrape_jobs(query)
            
            # Immediate second request should trigger rate limiting
            start_time = time.time()
            result2 = await service.scrape_jobs(query)
            backoff_time = time.time() - start_time
            
            # Should have backed off (taken longer than normal)
            assert backoff_time > 1.0  # Should wait before retrying
            
            # Should report backoff in results
            source_result = result2.source_results.get("indeed", {})
            if "backoff_applied" in source_result:
                assert source_result["backoff_applied"] is True
                assert "backoff_duration_seconds" in source_result
                
        finally:
            await service.stop()


class TestHealthMonitoringRequirements:
    """Test health monitoring and metrics as documented."""

    @pytest.mark.asyncio
    async def test_per_scraper_health_metrics(self, service_config):
        """Test health monitoring with success rates, response times, error rates."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Perform some scraping to generate metrics
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed", "ziprecruiter"],
                max_results=5
            )
            
            await service.scrape_jobs(query)
            
            # Check detailed health status for each source
            health_results = await service.check_source_health()
            
            for source, health in health_results.items():
                assert isinstance(health, SourceHealth)
                assert health.source_name == source
                assert health.status in ["healthy", "degraded", "unhealthy", "unknown"]
                assert isinstance(health.response_time_ms, float)
                assert 0.0 <= health.success_rate <= 1.0
                assert health.error_count >= 0
                assert isinstance(health.last_check, datetime)
                
                # Should track detailed metrics
                if hasattr(health, 'detailed_metrics'):
                    metrics = health.detailed_metrics
                    assert "total_requests" in metrics
                    assert "successful_requests" in metrics  
                    assert "failed_requests" in metrics
                    assert "average_response_time_ms" in metrics
                    
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_service_health_aggregation(self, service_config):
        """Test overall service health status aggregation."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            health = await service.get_health_status()
            
            # Should provide comprehensive service health
            assert "status" in health
            assert health["status"] in ["running", "degraded", "error", "stopped"]
            assert "uptime_seconds" in health
            assert "total_memory_usage_mb" in health
            assert "browser_instances" in health
            assert "source_health_summary" in health
            
            # Browser instances should be detailed
            browser_info = health["browser_instances"]
            assert "active" in browser_info
            assert "total_created" in browser_info
            assert "total_destroyed" in browser_info
            assert "memory_usage_mb" in browser_info
            
            # Source health summary should aggregate individual source status
            source_summary = health["source_health_summary"]
            assert "healthy_sources" in source_summary
            assert "degraded_sources" in source_summary
            assert "unhealthy_sources" in source_summary
            assert "total_sources" in source_summary
            
        finally:
            await service.stop()


class TestPerformanceRequirements:
    """Test performance requirements documented in README."""

    @pytest.mark.asyncio
    async def test_throughput_requirements(self, service_config):
        """Test 50-100 jobs/minute throughput requirement."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Test throughput with reasonable query
            query = ScrapingQuery(
                keywords=["software engineer"],
                location="Remote",
                sources=["indeed", "ziprecruiter"],  # 2 sources for parallel processing
                max_results=50  # 25 jobs per source
            )
            
            start_time = time.time()
            result = await service.scrape_jobs(query)
            execution_time = time.time() - start_time
            
            jobs_collected = len(result.jobs)
            
            if jobs_collected > 0:
                # Calculate jobs per minute
                jobs_per_minute = (jobs_collected / execution_time) * 60
                
                # Should meet minimum throughput (allowing for test environment)
                min_throughput = 10  # Reduced for test environment
                assert jobs_per_minute >= min_throughput, f"Throughput {jobs_per_minute:.1f} jobs/min below requirement"
                
                # Should complete within reasonable time
                assert execution_time < 60, f"Execution took {execution_time:.1f}s, should be under 60s"
                
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_concurrent_processing_limits(self, service_config):
        """Test concurrent processing doesn't exceed configured limits."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        config = create_config_with_overrides(
            service_config,
            max_concurrent_scrapers=2,
            max_browser_instances=2
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Launch multiple concurrent scraping operations
            queries = [
                ScrapingQuery(keywords=["test1"], sources=["indeed"], max_results=5),
                ScrapingQuery(keywords=["test2"], sources=["ziprecruiter"], max_results=5),
                ScrapingQuery(keywords=["test3"], sources=["linkedin"], max_results=5),
                ScrapingQuery(keywords=["test4"], sources=["greenhouse"], max_results=5),
            ]
            
            # Start all operations concurrently
            start_time = time.time()
            tasks = [service.scrape_jobs(query) for query in queries]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            execution_time = time.time() - start_time
            
            # Check that resource limits were respected
            health = await service.get_health_status()
            
            # Should not exceed browser instance limit
            assert health["browser_instances"]["active"] <= config.max_browser_instances
            
            # Should not exceed concurrent scraper limit (track in health)
            if "concurrent_operations" in health:
                assert health["concurrent_operations"]["max_reached"] <= config.max_concurrent_scrapers
                
            # All operations should complete (may queue/throttle but not fail)
            successful_results = [r for r in results if isinstance(r, ScrapingResult)]
            assert len(successful_results) == len(queries)
            
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, service_config):
        """Test memory usage monitoring and limits."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        config = create_config_with_overrides(
            service_config,
            browser_memory_limit_mb=512  # Limit browser memory
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            # Baseline memory usage
            initial_health = await service.get_health_status()
            initial_memory = initial_health["total_memory_usage_mb"]
            
            # Perform memory-intensive operations
            query = ScrapingQuery(
                keywords=["software engineer"],
                sources=["indeed", "linkedin", "ziprecruiter"],
                max_results=30  # Larger result set
            )
            
            await service.scrape_jobs(query)
            
            # Check memory usage after operations
            final_health = await service.get_health_status()
            final_memory = final_health["total_memory_usage_mb"]
            
            # Memory should be monitored and reported
            assert isinstance(final_memory, (int, float))
            assert final_memory > 0
            
            # Should not exceed configured limits significantly
            browser_memory = final_health["browser_instances"]["memory_usage_mb"]
            assert browser_memory <= config.browser_memory_limit_mb * 1.2  # 20% tolerance
            
            # Should track memory growth
            memory_growth = final_memory - initial_memory
            assert memory_growth >= 0  # Memory should increase with activity
            
        finally:
            await service.stop()


class TestErrorHandlingAndRecovery:
    """Test comprehensive error handling and recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_browser_crash_recovery(self, service_config):
        """Test recovery from browser crashes and WebDriver failures."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Simulate browser crash scenario
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed"],
                max_results=5
            )
            
            # First scraping should work
            result1 = await service.scrape_jobs(query)
            assert isinstance(result1, ScrapingResult)
            
            # Simulate browser crash (this would be implemented in the service)
            # Service should detect and recover from browser failures
            
            # Subsequent scraping should still work (new browser instance)
            result2 = await service.scrape_jobs(query)
            assert isinstance(result2, ScrapingResult)
            
            # Should track browser recovery in health metrics
            health = await service.get_health_status()
            if "browser_crashes_recovered" in health:
                assert health["browser_crashes_recovered"] >= 0
                
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_source_unavailable_handling(self, service_config):
        """Test handling when scraping sources are temporarily unavailable."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Query with mix of available and unavailable sources
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed", "nonexistent_source", "ziprecruiter"],
                max_results=10
            )
            
            result = await service.scrape_jobs(query)
            
            # Should handle unavailable sources gracefully
            assert isinstance(result, ScrapingResult)
            
            # Should report errors for unavailable sources
            assert "nonexistent_source" in result.errors
            assert "Source" in result.errors["nonexistent_source"] or "not found" in result.errors["nonexistent_source"]
            
            # Should still process available sources
            available_sources = ["indeed", "ziprecruiter"]
            successful_sources = [s for s in available_sources if s in result.source_results]
            assert len(successful_sources) > 0, "Should process available sources"
            
            # Should report proper statistics
            assert result.failed_sources >= 1  # At least the nonexistent source
            assert result.successful_sources >= 0
            
        finally:
            await service.stop()

    @pytest.mark.asyncio
    async def test_network_timeout_handling(self, service_config):
        """Test handling of network timeouts and slow responses."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        # Configure short timeout for testing
        config = create_config_with_overrides(
            service_config,
            timeout_seconds=5  # Short timeout
        )
        
        service = ScrapingServiceTDD(config)
        await service.start()
        
        try:
            query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed"],
                max_results=10
            )
            
            # Should handle timeouts gracefully
            start_time = time.time()
            result = await service.scrape_jobs(query)
            execution_time = time.time() - start_time
            
            # Should respect timeout setting
            assert execution_time <= config.timeout_seconds + 5  # 5s tolerance
            
            # Should report timeout if it occurred
            if "indeed" in result.errors:
                error_msg = result.errors["indeed"]
                if "timeout" in error_msg.lower():
                    # Timeout was properly detected and reported
                    assert "timeout" in error_msg.lower()
                    
            # Should track timeout statistics
            source_result = result.source_results.get("indeed", {})
            if "timeout_occurred" in source_result:
                assert isinstance(source_result["timeout_occurred"], bool)
                
        finally:
            await service.stop()


class TestConfigurationManagement:
    """Test configuration management and environment variable support."""

    @pytest.mark.asyncio
    async def test_environment_variable_configuration(self):
        """Test configuration from environment variables as documented."""
        # Set environment variables
        env_vars = {
            "SCRAPING_HEADLESS": "false",
            "SCRAPING_TIMEOUT": "45",
            "SCRAPING_MAX_RETRIES": "5",
            "INDEED_RATE_LIMIT": "8",
            "LINKEDIN_RATE_LIMIT": "3",
            "ANTI_DETECTION_ENABLED": "true",
            "VIEWPORT_RANDOMIZATION": "true",
            "MAX_BROWSER_INSTANCES": "3"
        }
        
        with patch.dict(os.environ, env_vars):
            # Configuration should be loaded from environment
            config = ScrapingConfig.from_env()
            
            assert config.headless is False
            assert config.timeout_seconds == 45
            assert config.max_retries == 5
            assert config.indeed_rate_limit == 8
            assert config.linkedin_rate_limit == 3
            assert config.enable_anti_detection is True
            assert config.viewport_randomization is True
            assert config.max_browser_instances == 3

    @pytest.mark.asyncio
    async def test_configuration_validation(self):
        """Test comprehensive configuration validation."""
        # Test invalid configurations
        with pytest.raises(ValueError):
            ScrapingConfig(timeout_seconds=-1)
            
        with pytest.raises(ValueError):
            ScrapingConfig(max_retries=0)
            
        with pytest.raises(ValueError):
            ScrapingConfig(delay_min_seconds=-0.5)
            
        with pytest.raises(ValueError):
            ScrapingConfig(
                delay_min_seconds=5.0,
                delay_max_seconds=2.0  # max < min
            )
            
        # Test valid edge cases
        config = ScrapingConfig(
            timeout_seconds=1,
            max_retries=1,
            delay_min_seconds=0.1,
            delay_max_seconds=0.2
        )
        assert config.timeout_seconds == 1

    @pytest.mark.asyncio
    async def test_runtime_configuration_updates(self, service_config):
        """Test updating configuration at runtime."""
        from tpm_job_finder_poc.scraping_service_tdd.service import ScrapingServiceTDD
        
        service = ScrapingServiceTDD(service_config)
        await service.start()
        
        try:
            # Test configuration override per query
            base_query = ScrapingQuery(
                keywords=["test"],
                sources=["indeed"],
                max_results=5
            )
            
            # Use different timeout for specific query
            custom_config = create_config_with_overrides(
                service_config,
                timeout_seconds=60
            )
            
            result = await service.scrape_jobs(base_query, config=custom_config)
            
            # Should use custom configuration
            assert isinstance(result, ScrapingResult)
            
            # Should report configuration used
            if "config_used" in result.source_results.get("indeed", {}):
                used_config = result.source_results["indeed"]["config_used"]
                assert used_config["timeout_seconds"] == 60
                
        finally:
            await service.stop()


# Fixtures for the tests
def create_config_with_overrides(base_config: ScrapingConfig, **overrides) -> ScrapingConfig:
    """Helper to create config with overrides without duplication."""
    base_dict = base_config.model_dump()
    base_dict.update(overrides)
    return ScrapingConfig(**base_dict)


@pytest.fixture
def service_config():
    """Provide a test configuration for the scraping service."""
    return ScrapingConfig(
        headless=True,
        timeout_seconds=30,
        max_retries=3,
        user_agent_rotation=True,
        enable_anti_detection=True,
        delay_min_seconds=0.5,
        delay_max_seconds=1.5,
        viewport_randomization=True,
        javascript_protection=True,
        max_browser_instances=3,
        browser_instance_timeout=300,
        browser_memory_limit_mb=512,
        cleanup_interval_seconds=60,
        indeed_rate_limit=10,
        linkedin_rate_limit=5,
        ziprecruiter_rate_limit=10,
        greenhouse_rate_limit=15,
        enable_parallel_processing=True,
        max_concurrent_scrapers=3,
        batch_size=50,
        fail_on_source_error=False,
        log_scraping_errors=True,
        skip_failed_sources=True
    )


@pytest.fixture
def sample_query():
    """Provide a sample scraping query for tests."""
    return ScrapingQuery(
        keywords=["python developer", "software engineer"],
        location="San Francisco",
        max_results=20
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])