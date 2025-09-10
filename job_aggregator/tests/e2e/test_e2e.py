"""End-to-end tests for job aggregator component."""

import pytest
import asyncio
import os
from datetime import datetime, timezone
from typing import List, Dict

from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.linkedin import LinkedInScraper
from job_aggregator.scrapers.indeed import IndeedScraper
from job_aggregator.scrapers.ziprecruiter import ZipRecruiterScraper
from job_aggregator.scrapers.config import JobScraperConfig

# Test configuration
TEST_SEARCH_TERMS = ["Technical Program Manager", "TPM"]
TEST_LOCATION = "United States"
TEST_CACHE_DIR = "/tmp/job_aggregator_e2e_cache"
TEST_CONFIG_FILE = "/tmp/job_aggregator_e2e_config.json"

@pytest.fixture(autouse=True)
def setup_e2e():
    """Setup for E2E tests."""
    # Create test directories
    os.makedirs(TEST_CACHE_DIR, exist_ok=True)
    
    # Create test config
    config = JobScraperConfig(TEST_CONFIG_FILE)
    for scraper in ['linkedin', 'indeed', 'ziprecruiter']:
        config.enable_scraper(scraper)
    config.save_config()
    
    yield
    
    # Cleanup
    import shutil
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)
    if os.path.exists(TEST_CONFIG_FILE):
        os.remove(TEST_CONFIG_FILE)
        
async def fetch_jobs_from_source(
    scraper_class,
    search_terms: List[str],
    location: str
) -> List[JobPosting]:
    """Fetch jobs from a specific source.
    
    Args:
        scraper_class: Scraper class to use
        search_terms: List of search terms
        location: Location to search in
        
    Returns:
        List of job postings
    """
    async with scraper_class(
        search_terms,
        location=location,
        config_file=TEST_CONFIG_FILE,
        cache_dir=TEST_CACHE_DIR
    ) as scraper:
        return await scraper.fetch_all_jobs()
        
async def fetch_all_jobs(
    search_terms: List[str],
    location: str
) -> Dict[str, List[JobPosting]]:
    """Fetch jobs from all sources in parallel.
    
    Args:
        search_terms: List of search terms
        location: Location to search in
        
    Returns:
        Dict of source name to list of jobs
    """
    scrapers = [
        LinkedInScraper,
        IndeedScraper,
        ZipRecruiterScraper
    ]
    
    # Create tasks for all scrapers
    tasks = [
        fetch_jobs_from_source(scraper, search_terms, location)
        for scraper in scrapers
    ]
    
    # Run all scrapers in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    jobs_by_source = {}
    for scraper, result in zip(scrapers, results):
        source = scraper.__name__.lower().replace('scraper', '')
        if isinstance(result, Exception):
            print(f"Error from {source}: {str(result)}")
            jobs_by_source[source] = []
        else:
            jobs_by_source[source] = result
            
    return jobs_by_source
    
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_job_search():
    """Test complete job search flow across all sources."""
    # Fetch jobs from all sources
    start_time = datetime.now(timezone.utc)
    jobs_by_source = await fetch_all_jobs(TEST_SEARCH_TERMS, TEST_LOCATION)
    duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Log timing information
    print(f"\nJob search completed in {duration:.2f} seconds")
    
    # Verify results from each source
    for source, jobs in jobs_by_source.items():
        print(f"\n{source.capitalize()} results: {len(jobs)} jobs")
        assert len(jobs) > 0, f"No jobs found from {source}"
        
        # Check for required fields
        for job in jobs:
            assert job.title, f"Missing title in {source} job"
            assert job.company, f"Missing company in {source} job"
            assert job.location, f"Missing location in {source} job"
            assert job.url, f"Missing URL in {source} job"
            assert job.date_posted, f"Missing date in {source} job"
            
        # Check for duplicates
        urls = set()
        for job in jobs:
            assert job.url not in urls, f"Duplicate job URL in {source}"
            urls.add(job.url)
            
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling across all sources."""
    # Disable one source
    config = JobScraperConfig(TEST_CONFIG_FILE)
    config.disable_scraper('linkedin')
    config.save_config()
    
    # Fetch jobs
    jobs_by_source = await fetch_all_jobs(TEST_SEARCH_TERMS, TEST_LOCATION)
    
    # Verify disabled source returns no results
    assert len(jobs_by_source['linkedin']) == 0
    
    # Verify other sources still work
    assert len(jobs_by_source['indeed']) > 0
    assert len(jobs_by_source['ziprecruiter']) > 0
    
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_cache_persistence():
    """Test cache persistence across runs."""
    # First run - should hit network
    start_time = datetime.now(timezone.utc)
    jobs1 = await fetch_all_jobs(TEST_SEARCH_TERMS, TEST_LOCATION)
    first_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Second run - should use cache
    start_time = datetime.now(timezone.utc)
    jobs2 = await fetch_all_jobs(TEST_SEARCH_TERMS, TEST_LOCATION)
    second_duration = (datetime.now(timezone.utc) - start_time).total_seconds()
    
    # Verify cache improved performance
    assert second_duration < first_duration / 2
    
    # Verify results are consistent
    for source in jobs1:
        assert len(jobs1[source]) == len(jobs2[source])
        
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_search_variations():
    """Test different search term variations."""
    variations = [
        ["Technical Program Manager"],
        ["TPM"],
        ["Technical Program Manager", "TPM"],
        ["Senior Technical Program Manager"]
    ]
    
    for terms in variations:
        jobs = await fetch_all_jobs(terms, TEST_LOCATION)
        
        # Verify each variation returns results
        for source, source_jobs in jobs.items():
            assert len(source_jobs) > 0, \
                f"No results for {terms} from {source}"
                
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_location_variations():
    """Test different location variations."""
    locations = [
        "United States",
        "Remote",
        "New York, NY",
        "San Francisco, CA"
    ]
    
    for location in locations:
        jobs = await fetch_all_jobs(TEST_SEARCH_TERMS, location)
        
        # Verify each location returns results
        for source, source_jobs in jobs.items():
            assert len(source_jobs) > 0, \
                f"No results for {location} from {source}"
                
            # Verify location handling
            for job in source_jobs:
                assert job.location, "Missing location"
                if location != "United States":
                    # Location should either match or be remote
                    assert (
                        location.lower() in job.location.lower() or
                        "remote" in job.location.lower()
                    )
