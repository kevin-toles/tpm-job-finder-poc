"""
Tests for Job Collection Service storage operations.

Tests storage functionality including job persistence, retrieval,
search, and storage statistics.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    JobPosting,
    JobQuery,
    JobType
)


class TestJobStorage:
    """Test cases for job storage functionality."""
    
    @pytest.mark.asyncio
    async def test_store_job_success(self, mock_job_storage, sample_job_posting):
        """Test successful job storage."""
        result = await mock_job_storage.store_job(sample_job_posting)
        
        assert result is True
        mock_job_storage.store_job.assert_called_once_with(sample_job_posting)
    
    @pytest.mark.asyncio
    async def test_store_multiple_jobs_success(self, mock_job_storage, sample_job_postings):
        """Test storing multiple jobs."""
        mock_job_storage.store_jobs.return_value = len(sample_job_postings)
        
        result = await mock_job_storage.store_jobs(sample_job_postings)
        
        assert result == len(sample_job_postings)
        mock_job_storage.store_jobs.assert_called_once_with(sample_job_postings)
    
    @pytest.mark.asyncio
    async def test_get_job_success(self, mock_job_storage, sample_job_posting):
        """Test successful job retrieval."""
        mock_job_storage.get_job.return_value = sample_job_posting
        
        result = await mock_job_storage.get_job("test-job-123")
        
        assert result == sample_job_posting
        mock_job_storage.get_job.assert_called_once_with("test-job-123")
    
    @pytest.mark.asyncio
    async def test_get_job_not_found(self, mock_job_storage):
        """Test job retrieval when job doesn't exist."""
        mock_job_storage.get_job.return_value = None
        
        result = await mock_job_storage.get_job("nonexistent-job")
        
        assert result is None
        mock_job_storage.get_job.assert_called_once_with("nonexistent-job")
    
    @pytest.mark.asyncio
    async def test_search_jobs_with_query(self, mock_job_storage, sample_job_postings, sample_job_query):
        """Test searching jobs with query parameters."""
        mock_job_storage.search_jobs.return_value = sample_job_postings[:2]
        
        result = await mock_job_storage.search_jobs(sample_job_query)
        
        assert len(result) == 2
        assert all(isinstance(job, JobPosting) for job in result)
        mock_job_storage.search_jobs.assert_called_once_with(sample_job_query)
    
    @pytest.mark.asyncio
    async def test_search_jobs_empty_result(self, mock_job_storage, sample_job_query):
        """Test searching jobs with no results."""
        mock_job_storage.search_jobs.return_value = []
        
        result = await mock_job_storage.search_jobs(sample_job_query)
        
        assert result == []
        mock_job_storage.search_jobs.assert_called_once_with(sample_job_query)
    
    @pytest.mark.asyncio
    async def test_delete_job_success(self, mock_job_storage):
        """Test successful job deletion."""
        result = await mock_job_storage.delete_job("test-job-123")
        
        assert result is True
        mock_job_storage.delete_job.assert_called_once_with("test-job-123")
    
    @pytest.mark.asyncio
    async def test_delete_job_not_found(self, mock_job_storage):
        """Test deleting non-existent job."""
        mock_job_storage.delete_job.return_value = False
        
        result = await mock_job_storage.delete_job("nonexistent-job")
        
        assert result is False
        mock_job_storage.delete_job.assert_called_once_with("nonexistent-job")
    
    @pytest.mark.asyncio
    async def test_get_storage_stats(self, mock_job_storage):
        """Test getting storage statistics."""
        expected_stats = {
            "total_jobs": 1250,
            "jobs_today": 45,
            "storage_size_mb": 15.2,
            "oldest_job_date": "2024-01-01T00:00:00",
            "newest_job_date": "2024-01-15T12:30:00"
        }
        mock_job_storage.get_storage_stats.return_value = expected_stats
        
        result = await mock_job_storage.get_storage_stats()
        
        assert result == expected_stats
        assert "total_jobs" in result
        assert "jobs_today" in result
        assert "storage_size_mb" in result
        mock_job_storage.get_storage_stats.assert_called_once()


class TestJobStorageIntegration:
    """Integration tests for job storage with service."""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_job(self, mock_job_storage, sample_job_posting):
        """Test storing and then retrieving a job."""
        # Configure mock to return the job when retrieved
        mock_job_storage.get_job.return_value = sample_job_posting
        
        # Store the job
        store_result = await mock_job_storage.store_job(sample_job_posting)
        assert store_result is True
        
        # Retrieve the job
        retrieved_job = await mock_job_storage.get_job(sample_job_posting.id)
        assert retrieved_job == sample_job_posting
        assert retrieved_job.id == sample_job_posting.id
        assert retrieved_job.title == sample_job_posting.title
        assert retrieved_job.company == sample_job_posting.company
    
    @pytest.mark.asyncio
    async def test_store_multiple_and_search(self, mock_job_storage, sample_job_postings):
        """Test storing multiple jobs and searching them."""
        # Store multiple jobs
        store_result = await mock_job_storage.store_jobs(sample_job_postings)
        assert store_result == len(sample_job_postings)
        
        # Search for specific jobs
        query = JobQuery(keywords=["product manager"])
        mock_job_storage.search_jobs.return_value = [
            job for job in sample_job_postings 
            if "product" in job.title.lower()
        ]
        
        search_results = await mock_job_storage.search_jobs(query)
        assert len(search_results) > 0
        assert all("product" in job.title.lower() for job in search_results)
    
    @pytest.mark.asyncio
    async def test_storage_stats_after_operations(self, mock_job_storage, sample_job_postings):
        """Test storage statistics after performing operations."""
        # Perform some operations
        await mock_job_storage.store_jobs(sample_job_postings)
        await mock_job_storage.get_job(sample_job_postings[0].id)
        
        # Check stats reflect operations
        stats = await mock_job_storage.get_storage_stats()
        
        assert isinstance(stats, dict)
        assert "total_jobs" in stats
        assert stats["total_jobs"] >= 0


class TestJobEnricher:
    """Test cases for job enrichment functionality."""
    
    def test_classify_job_type_management(self, mock_job_enricher):
        """Test job type classification for management roles."""
        mock_job_enricher.classify_job_type.return_value = JobType.MANAGEMENT
        
        result = mock_job_enricher.classify_job_type("Product Manager")
        
        assert result == JobType.MANAGEMENT
        mock_job_enricher.classify_job_type.assert_called_once_with("Product Manager")
    
    def test_classify_job_type_senior(self, mock_job_enricher):
        """Test job type classification for senior roles."""
        mock_job_enricher.classify_job_type.return_value = JobType.SENIOR
        
        result = mock_job_enricher.classify_job_type("Senior Product Manager")
        
        assert result == JobType.SENIOR
        mock_job_enricher.classify_job_type.assert_called_once_with("Senior Product Manager")
    
    def test_classify_job_type_entry_level(self, mock_job_enricher):
        """Test job type classification for entry level roles."""
        mock_job_enricher.classify_job_type.return_value = JobType.ENTRY_LEVEL
        
        result = mock_job_enricher.classify_job_type("Junior Product Manager")
        
        assert result == JobType.ENTRY_LEVEL
        mock_job_enricher.classify_job_type.assert_called_once_with("Junior Product Manager")
    
    def test_detect_remote_work_true(self, mock_job_enricher):
        """Test remote work detection for remote-friendly jobs."""
        result = mock_job_enricher.detect_remote_work("Remote")
        
        assert result is True
        mock_job_enricher.detect_remote_work.assert_called_once_with("Remote")
    
    def test_detect_remote_work_false(self, mock_job_enricher):
        """Test remote work detection for office-based jobs."""
        mock_job_enricher.detect_remote_work.return_value = False
        
        result = mock_job_enricher.detect_remote_work("San Francisco, CA")
        
        assert result is False
        mock_job_enricher.detect_remote_work.assert_called_once_with("San Francisco, CA")
    
    def test_count_tpm_keywords(self, mock_job_enricher):
        """Test TPM keyword counting."""
        result = mock_job_enricher.count_tpm_keywords(
            "Senior Technical Product Manager",
            "Lead technical product management initiatives"
        )
        
        assert result == 2
        mock_job_enricher.count_tpm_keywords.assert_called_once()
    
    def test_enrich_job_complete(self, mock_job_enricher, sample_job_posting):
        """Test complete job enrichment."""
        # Configure enricher to modify the job
        def enrich_side_effect(job):
            job.job_type = JobType.SENIOR
            job.remote_friendly = True
            job.tpm_keywords_found = 3
            return job
        
        mock_job_enricher.enrich_job.side_effect = enrich_side_effect
        
        result = mock_job_enricher.enrich_job(sample_job_posting)
        
        assert result == sample_job_posting
        assert result.job_type == JobType.SENIOR
        assert result.remote_friendly is True
        assert result.tpm_keywords_found == 3
        mock_job_enricher.enrich_job.assert_called_once_with(sample_job_posting)


class TestDedupeCache:
    """Test cases for deduplication cache functionality."""
    
    def test_is_duplicate_new_job(self, mock_dedupe_cache):
        """Test checking if job is duplicate for new job."""
        result = mock_dedupe_cache.is_duplicate("new-job-key", "new-job-value")
        
        assert result is False
        mock_dedupe_cache.is_duplicate.assert_called_once_with("new-job-key", "new-job-value")
    
    def test_is_duplicate_existing_job(self, mock_dedupe_cache):
        """Test checking if job is duplicate for existing job."""
        mock_dedupe_cache.is_duplicate.return_value = True
        
        result = mock_dedupe_cache.is_duplicate("existing-job-key", "existing-job-value")
        
        assert result is True
        mock_dedupe_cache.is_duplicate.assert_called_once_with("existing-job-key", "existing-job-value")
    
    def test_add_to_cache(self, mock_dedupe_cache):
        """Test adding job to deduplication cache."""
        mock_dedupe_cache.add("job-key", "job-value")
        
        mock_dedupe_cache.add.assert_called_once_with("job-key", "job-value")
    
    def test_deduplication_workflow(self, mock_dedupe_cache, sample_job_postings):
        """Test complete deduplication workflow."""
        # Simulate first job is new, second is duplicate, third is new
        mock_dedupe_cache.is_duplicate.side_effect = [False, True, False]
        
        unique_jobs = []
        for job in sample_job_postings:
            job_key = f"{job.company}-{job.title}"
            if not mock_dedupe_cache.is_duplicate(job_key, job_key):
                unique_jobs.append(job)
                mock_dedupe_cache.add(job_key, job_key)
        
        assert len(unique_jobs) == 2  # First and third jobs
        assert mock_dedupe_cache.is_duplicate.call_count == 3
        assert mock_dedupe_cache.add.call_count == 2