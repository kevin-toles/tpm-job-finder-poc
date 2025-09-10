"""Integration tests for job aggregator scrapers."""

import pytest
import os
from typing import List
from datetime import datetime, timezone, timedelta

from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.linkedin import LinkedInScraper
from job_aggregator.scrapers.indeed import IndeedScraper
from job_aggregator.scrapers.ziprecruiter import ZipRecruiterScraper
from job_aggregator.scrapers.config import JobScraperConfig

# Test configuration
TEST_SEARCH_TERMS = ["Technical Program Manager", "TPM"]
TEST_LOCATION = "United States"
TEST_CACHE_DIR = "/tmp/job_aggregator_test_cache"

@pytest.fixture(autouse=True)
def setup_test_config():
    """Setup test configuration and cleanup."""
    # Create test cache directory
    os.makedirs(TEST_CACHE_DIR, exist_ok=True)
    
    # Create test config
    config = JobScraperConfig()
    for scraper in ['linkedin', 'indeed', 'ziprecruiter']:
        config.config[scraper].requests_per_minute = 2
        config.config[scraper].cache_enabled = True
        config.save_config()
        
    yield
    
    # Cleanup
    import shutil
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)
        
def validate_job_posting(job: JobPosting):
    """Validate job posting fields and data types."""
    assert isinstance(job.id, str)
    assert isinstance(job.source, str)
    assert isinstance(job.company, str)
    assert isinstance(job.title, str)
    assert isinstance(job.location, str)
    assert isinstance(job.url, str)
    assert isinstance(job.date_posted, datetime)
    assert isinstance(job.description, (str, type(None)))
    assert isinstance(job.raw, dict)
    
    # Validate required fields are not empty
    assert job.id
    assert job.source
    assert job.company
    assert job.title
    assert job.location
    assert job.url
    
    # Validate date is recent
    assert job.date_posted <= datetime.now(timezone.utc)
    assert job.date_posted >= datetime.now(timezone.utc) - timedelta(days=30)
    
    # Validate URL format
    assert job.url.startswith('http')
    
async def test_jobs_for_duplicates(jobs: List[JobPosting]):
    """Test that there are no duplicate jobs in results."""
    job_ids = set()
    job_urls = set()
    
    for job in jobs:
        assert job.id not in job_ids, f"Duplicate job ID: {job.id}"
        assert job.url not in job_urls, f"Duplicate job URL: {job.url}"
        job_ids.add(job.id)
        job_urls.add(job.url)
        
@pytest.mark.integration
@pytest.mark.asyncio
async def test_linkedin_integration():
    """Integration test for LinkedIn scraper."""
    async with LinkedInScraper(
        TEST_SEARCH_TERMS,
        location=TEST_LOCATION,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        jobs = await scraper.fetch_all_jobs()
        
    assert len(jobs) > 0
    for job in jobs:
        validate_job_posting(job)
        assert job.source == "linkedin"
    await test_jobs_for_duplicates(jobs)
    
@pytest.mark.integration
@pytest.mark.asyncio
async def test_indeed_integration():
    """Integration test for Indeed scraper."""
    async with IndeedScraper(
        TEST_SEARCH_TERMS,
        location=TEST_LOCATION,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        jobs = await scraper.fetch_all_jobs()
        
    assert len(jobs) > 0
    for job in jobs:
        validate_job_posting(job)
        assert job.source == "indeed"
    await test_jobs_for_duplicates(jobs)
    
@pytest.mark.integration
@pytest.mark.asyncio
async def test_ziprecruiter_integration():
    """Integration test for ZipRecruiter scraper."""
    async with ZipRecruiterScraper(
        TEST_SEARCH_TERMS,
        location=TEST_LOCATION,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        jobs = await scraper.fetch_all_jobs()
        
    assert len(jobs) > 0
    for job in jobs:
        validate_job_posting(job)
        assert job.source == "ziprecruiter"
    await test_jobs_for_duplicates(jobs)
    
@pytest.mark.integration
@pytest.mark.asyncio
async def test_rate_limiting_integration():
    """Test rate limiting across multiple requests."""
    async with LinkedInScraper(
        TEST_SEARCH_TERMS,
        location=TEST_LOCATION,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        start_time = datetime.now()
        
        # Make multiple requests
        for _ in range(3):
            jobs = await scraper.search(TEST_SEARCH_TERMS[0])
            assert len(jobs) > 0
            
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # With rate limit of 2 requests/minute, this should take at least 90 seconds
        assert duration >= 90
        
@pytest.mark.integration
@pytest.mark.asyncio
async def test_caching_integration():
    """Test response caching functionality."""
    async with LinkedInScraper(
        TEST_SEARCH_TERMS,
        location=TEST_LOCATION,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        # First request - should hit the network
        start_time = datetime.now()
        jobs1 = await scraper.search(TEST_SEARCH_TERMS[0])
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second request - should use cache
        start_time = datetime.now()
        jobs2 = await scraper.search(TEST_SEARCH_TERMS[0])
        second_duration = (datetime.now() - start_time).total_seconds()
        
        # Cached request should be significantly faster
        assert second_duration < first_duration / 2
        
        # Results should be the same
        assert len(jobs1) == len(jobs2)
        
@pytest.mark.integration
@pytest.mark.asyncio
async def test_selector_maintenance_integration():
    """Test selector maintenance across requests."""
    async with LinkedInScraper(
        TEST_SEARCH_TERMS,
        location=TEST_LOCATION,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        # Make initial request
        jobs1 = await scraper.search(TEST_SEARCH_TERMS[0])
        assert len(jobs1) > 0
        
        # Clear selector cache
        scraper.selector_maintainer._selectors = {}
        
        # Make another request - should still work with repaired selectors
        jobs2 = await scraper.search(TEST_SEARCH_TERMS[0])
        assert len(jobs2) > 0
