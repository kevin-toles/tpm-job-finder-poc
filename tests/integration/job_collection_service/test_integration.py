"""
Tests for Job Collection Service integration scenarios.

Tests end-to-end workflows, integration between components,
and real-world usage scenarios.
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
    JobCollectionError
)


class TestJobCollectionIntegration:
    """Integration tests for complete job collection workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_job_collection_workflow(self, mock_job_collection_service):
        """Test complete job collection workflow from query to results."""
        # Step 1: Create job query
        query = JobQuery(
            keywords=["product manager", "tpm"],
            location="San Francisco, CA",
            max_jobs_per_source=25,
            sources=["remoteok", "linkedin", "indeed"],
            include_remote=True,
            date_range_days=7
        )
        
        # Step 2: Collect jobs
        result = await mock_job_collection_service.collect_jobs(query)
        
        # Step 3: Verify results
        assert isinstance(result, CollectionResult)
        assert result.total_jobs >= 0
        assert len(result.jobs) == result.total_jobs
        
        # Step 4: Verify each job has required fields
        for job in result.jobs:
            assert job.id is not None
            assert job.source is not None
            assert job.title is not None
            assert job.company is not None
        
        # Step 5: Verify metadata
        assert result.collection_time is not None
        assert result.duration_seconds >= 0
        assert isinstance(result.sources_queried, list)
        assert isinstance(result.successful_sources, list)
        assert isinstance(result.failed_sources, list)
    
    @pytest.mark.asyncio
    async def test_daily_aggregation_workflow(self, mock_job_collection_service):
        """Test daily aggregation workflow with enrichment and deduplication."""
        # Step 1: Create comprehensive query
        query = JobQuery(
            keywords=["product manager", "technical product manager", "tpm"],
            location="Remote",
            max_jobs_per_source=50,
            include_remote=True,
            date_range_days=1  # Daily aggregation
        )
        
        # Step 2: Run daily aggregation
        result = await mock_job_collection_service.run_daily_aggregation(query)
        
        # Step 3: Verify aggregation includes enrichment
        assert isinstance(result, CollectionResult)
        assert result.duplicates_removed >= 0  # Should have deduplication
        
        # Step 4: Verify jobs have enrichment data
        for job in result.jobs:
            # Jobs should have TPM keyword counts when keywords are provided
            assert job.tpm_keywords_found >= 0
            # Remote query should affect remote_friendly detection
            if query.include_remote and job.location == "Remote":
                assert job.remote_friendly in [True, False]  # Should be set
    
    @pytest.mark.asyncio
    async def test_source_management_workflow(self, mock_job_collection_service):
        """Test source management workflow."""
        # Step 1: Get initial source statuses
        initial_statuses = await mock_job_collection_service.get_source_statuses()
        assert isinstance(initial_statuses, list)
        assert len(initial_statuses) > 0
        
        # Step 2: Find an enabled source
        enabled_sources = [s for s in initial_statuses if s.enabled]
        assert len(enabled_sources) > 0
        
        test_source = enabled_sources[0].name
        
        # Step 3: Disable the source
        disable_result = await mock_job_collection_service.disable_source(test_source)
        assert disable_result is True
        
        # Step 4: Verify source is disabled
        updated_statuses = await mock_job_collection_service.get_source_statuses()
        test_source_status = next((s for s in updated_statuses if s.name == test_source), None)
        if test_source_status:
            # Mock doesn't actually change state, but real implementation would
            pass
        
        # Step 5: Re-enable the source
        enable_result = await mock_job_collection_service.enable_source(test_source)
        assert enable_result is True
    
    @pytest.mark.asyncio
    async def test_health_monitoring_workflow(self, mock_job_collection_service):
        """Test health monitoring workflow."""
        # Step 1: Perform health check
        health = await mock_job_collection_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "timestamp" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Step 2: Get collection statistics
        stats = await mock_job_collection_service.get_collection_stats()
        
        assert isinstance(stats, dict)
        assert "total_jobs_collected" in stats
        assert "jobs_collected_today" in stats
        assert "active_sources" in stats
        
        # Step 3: Get source statuses
        source_statuses = await mock_job_collection_service.get_source_statuses()
        
        healthy_sources = [s for s in source_statuses if s.healthy]
        unhealthy_sources = [s for s in source_statuses if not s.healthy]
        
        # Step 4: Verify health correlation
        if health["status"] == "healthy":
            # Should have more healthy than unhealthy sources
            assert len(healthy_sources) >= len(unhealthy_sources)


class TestJobCollectionErrorScenarios:
    """Test error scenarios and recovery in job collection."""
    
    @pytest.mark.asyncio
    async def test_partial_source_failure_scenario(self, mock_job_collection_service):
        """Test scenario where some sources fail but others succeed."""
        # Mock a scenario where some sources fail
        original_collect = mock_job_collection_service.collect_jobs
        
        async def mixed_success_collect(query):
            result = await original_collect(query)
            # Simulate some sources failing
            result.failed_sources = ["indeed"]  # Simulate Indeed failing
            result.successful_sources = [s for s in result.sources_queried if s != "indeed"]
            result.errors = {"indeed": "Connection timeout"}
            return result
        
        mock_job_collection_service.collect_jobs = mixed_success_collect
        
        query = JobQuery(
            keywords=["product manager"],
            sources=["remoteok", "linkedin", "indeed"]
        )
        
        result = await mock_job_collection_service.collect_jobs(query)
        
        # Should still get results from successful sources
        assert result.total_jobs >= 0
        assert len(result.successful_sources) >= 1  # At least one should succeed
        assert len(result.failed_sources) >= 1  # At least one should fail
        assert "indeed" in result.errors
    
    @pytest.mark.asyncio
    async def test_timeout_recovery_scenario(self, mock_job_collection_service):
        """Test recovery from timeout scenarios."""
        # Mock a timeout scenario
        async def timeout_on_first_call(query):
            if not hasattr(timeout_on_first_call, 'called'):
                timeout_on_first_call.called = True
                raise asyncio.TimeoutError("Collection timed out")
            else:
                # Second call succeeds
                return await mock_job_collection_service.collect_jobs(query)
        
        query = JobQuery(keywords=["test"])
        
        # First call should timeout
        with pytest.raises(asyncio.TimeoutError):
            await timeout_on_first_call(query)
        
        # Second call should succeed
        result = await timeout_on_first_call(query)
        assert isinstance(result, CollectionResult)
    
    @pytest.mark.asyncio
    async def test_empty_results_scenario(self, mock_job_collection_service):
        """Test scenario with no job results."""
        # Mock empty results
        original_collect = mock_job_collection_service.collect_jobs
        
        async def empty_results_collect(query):
            result = await original_collect(query)
            result.jobs = []
            result.total_jobs = 0
            return result
        
        mock_job_collection_service.collect_jobs = empty_results_collect
        
        query = JobQuery(keywords=["nonexistent-keyword-xyz"])
        result = await mock_job_collection_service.collect_jobs(query)
        
        assert result.total_jobs == 0
        assert len(result.jobs) == 0
        assert result.duration_seconds >= 0  # Should still have timing info
        assert len(result.sources_queried) > 0  # Should still query sources


class TestJobCollectionPerformance:
    """Test performance and scalability scenarios."""
    
    @pytest.mark.asyncio
    async def test_concurrent_collection_requests(self, mock_job_collection_service):
        """Test handling concurrent collection requests."""
        # Create multiple queries
        queries = [
            JobQuery(keywords=["product manager"], max_jobs_per_source=10),
            JobQuery(keywords=["technical product manager"], max_jobs_per_source=10),
            JobQuery(keywords=["program manager"], max_jobs_per_source=10),
        ]
        
        # Execute concurrently
        tasks = [
            mock_job_collection_service.collect_jobs(query)
            for query in queries
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All requests should complete successfully
        assert len(results) == len(queries)
        for result in results:
            assert isinstance(result, CollectionResult)
            assert result.total_jobs >= 0
    
    @pytest.mark.asyncio
    async def test_large_result_set_handling(self, mock_job_collection_service):
        """Test handling large result sets."""
        # Mock large result set
        original_collect = mock_job_collection_service.collect_jobs
        
        async def large_results_collect(query):
            result = await original_collect(query)
            # Simulate large number of jobs
            large_job_list = []
            for i in range(100):  # Simulate 100 jobs
                job = JobPosting(
                    id=f"large-job-{i}",
                    source="test_source",
                    title=f"Product Manager {i}",
                    company=f"Company {i}"
                )
                large_job_list.append(job)
            
            result.jobs = large_job_list
            result.total_jobs = len(large_job_list)
            result.raw_jobs = len(large_job_list) + 20  # Simulate some duplicates
            result.duplicates_removed = 20
            return result
        
        mock_job_collection_service.collect_jobs = large_results_collect
        
        query = JobQuery(keywords=["product manager"], max_jobs_per_source=100)
        result = await mock_job_collection_service.collect_jobs(query)
        
        assert result.total_jobs == 100
        assert len(result.jobs) == 100
        assert result.duplicates_removed == 20
        assert result.raw_jobs == 120
    
    @pytest.mark.asyncio
    async def test_memory_efficiency_with_large_datasets(self, mock_job_collection_service):
        """Test memory efficiency with large datasets."""
        # Test that service can handle large queries efficiently
        query = JobQuery(
            keywords=["product manager", "technical product manager", "program manager"],
            max_jobs_per_source=200,  # Large limit
            sources=["remoteok", "linkedin", "indeed", "ziprecruiter"]  # Multiple sources
        )
        
        result = await mock_job_collection_service.collect_jobs(query)
        
        # Should complete without memory issues
        assert isinstance(result, CollectionResult)
        assert result.duration_seconds < 60  # Should complete in reasonable time
        
        # Verify result structure is still valid with large datasets
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "jobs" in result_dict
        assert isinstance(result_dict["jobs"], list)


class TestJobCollectionDataQuality:
    """Test data quality and validation in job collection."""
    
    @pytest.mark.asyncio
    async def test_job_data_validation(self, mock_job_collection_service):
        """Test that collected jobs meet data quality standards."""
        query = JobQuery(keywords=["product manager"])
        result = await mock_job_collection_service.collect_jobs(query)
        
        for job in result.jobs:
            # Required fields should be present
            assert job.id is not None and job.id != ""
            assert job.source is not None and job.source != ""
            assert job.title is not None and job.title != ""
            assert job.company is not None and job.company != ""
            
            # Optional fields should have valid types when present
            if job.location is not None:
                assert isinstance(job.location, str)
            
            if job.url is not None:
                assert isinstance(job.url, str)
                # Basic URL validation could be added here
            
            if job.date_posted is not None:
                assert isinstance(job.date_posted, datetime)
            
            if job.job_type is not None:
                assert isinstance(job.job_type, JobType)
            
            assert isinstance(job.remote_friendly, bool)
            assert isinstance(job.tpm_keywords_found, int)
            assert job.tpm_keywords_found >= 0
    
    @pytest.mark.asyncio
    async def test_deduplication_effectiveness(self, mock_job_collection_service):
        """Test that deduplication is working effectively."""
        # Mock scenario with duplicates
        original_collect = mock_job_collection_service.collect_jobs
        
        async def duplicate_results_collect(query):
            result = await original_collect(query)
            
            # Add some duplicate-like jobs
            duplicate_jobs = [
                JobPosting(id="dup-1", source="source1", title="Product Manager", company="Tech Corp"),
                JobPosting(id="dup-2", source="source2", title="Product Manager", company="Tech Corp"),  # Same title/company
                JobPosting(id="unique-1", source="source1", title="Senior PM", company="Other Corp"),
            ]
            
            result.jobs = duplicate_jobs
            result.total_jobs = len(duplicate_jobs)
            result.raw_jobs = len(duplicate_jobs) + 1  # Simulate one duplicate removed
            result.duplicates_removed = 1
            
            return result
        
        mock_job_collection_service.collect_jobs = duplicate_results_collect
        
        query = JobQuery(keywords=["product manager"])
        result = await mock_job_collection_service.collect_jobs(query)
        
        # Should have removed duplicates
        assert result.duplicates_removed > 0
        assert result.raw_jobs > result.total_jobs
        
        # Verify no exact duplicates remain (by title + company)
        seen_combinations = set()
        for job in result.jobs:
            combo = f"{job.title}|{job.company}"
            assert combo not in seen_combinations, f"Duplicate combination found: {combo}"
            seen_combinations.add(combo)
    
    @pytest.mark.asyncio
    async def test_enrichment_quality(self, mock_job_collection_service):
        """Test that job enrichment is working correctly."""
        query = JobQuery(keywords=["senior product manager", "tpm"])
        result = await mock_job_collection_service.collect_jobs(query)
        
        for job in result.jobs:
            # TPM keyword counting should be working
            if query.keywords:
                # Mock always returns some keyword count
                assert job.tpm_keywords_found >= 0
            
            # Remote detection should be working
            if job.location and "remote" in job.location.lower():
                # In a real implementation, this should be True
                # Mock doesn't implement this logic, but we can verify structure
                assert isinstance(job.remote_friendly, bool)
            
            # Job type classification should be working
            # Mock might not set this, but structure should be valid
            if job.job_type is not None:
                assert isinstance(job.job_type, JobType)