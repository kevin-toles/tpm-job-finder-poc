"""Regression tests for job aggregator scrapers."""

import pytest
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any

from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.linkedin import LinkedInScraper
from job_aggregator.scrapers.indeed import IndeedScraper
from job_aggregator.scrapers.ziprecruiter import ZipRecruiterScraper

# Test configuration
SNAPSHOT_DIR = os.path.join(os.path.dirname(__file__), 'snapshots')
TEST_SEARCH_TERMS = ["Technical Program Manager"]
TEST_LOCATION = "United States"

def load_snapshot(filename: str) -> List[Dict[str, Any]]:
    """Load job data snapshot from file.
    
    Args:
        filename: Name of the snapshot file
        
    Returns:
        List of job posting data
    """
    path = os.path.join(SNAPSHOT_DIR, filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        return json.load(f)
        
def save_snapshot(filename: str, data: List[Dict[str, Any]]):
    """Save job data snapshot to file.
    
    Args:
        filename: Name of the snapshot file
        data: List of job posting data to save
    """
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    path = os.path.join(SNAPSHOT_DIR, filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
        
def compare_job_fields(current: Dict[str, Any], snapshot: Dict[str, Any]):
    """Compare job fields between current and snapshot data.
    
    Args:
        current: Current job posting data
        snapshot: Snapshot job posting data
    """
    # Compare field presence
    assert set(current.keys()) == set(snapshot.keys()), "Job field mismatch"
    
    # Compare field types
    for field in current:
        assert type(current[field]) == type(snapshot[field]), \
            f"Type mismatch for field {field}"
            
def serialize_job(job: JobPosting) -> Dict[str, Any]:
    """Serialize JobPosting for snapshot comparison.
    
    Args:
        job: JobPosting object to serialize
        
    Returns:
        Dict of serialized job data
    """
    return {
        "id": job.id,
        "source": job.source,
        "company": job.company,
        "title": job.title,
        "location": job.location,
        "salary": job.salary,
        "url": job.url,
        "date_posted": job.date_posted.isoformat() if job.date_posted else None,
        "description": job.description,
        "raw": job.raw
    }
    
@pytest.mark.regression
@pytest.mark.asyncio
async def test_linkedin_field_regression():
    """Test LinkedIn scraper for field regressions."""
    async with LinkedInScraper(TEST_SEARCH_TERMS, location=TEST_LOCATION) as scraper:
        jobs = await scraper.fetch_all_jobs()
        
    # Serialize current results
    current_data = [serialize_job(job) for job in jobs]
    
    # Load snapshot
    snapshot_data = load_snapshot('linkedin_jobs.json')
    
    if not snapshot_data:
        # Save initial snapshot
        save_snapshot('linkedin_jobs.json', current_data)
        pytest.skip("Initial snapshot created")
        
    # Compare results
    assert len(current_data) > 0, "No jobs found"
    for current_job in current_data:
        # Find matching job in snapshot
        matching_jobs = [j for j in snapshot_data if j['url'] == current_job['url']]
        if matching_jobs:
            compare_job_fields(current_job, matching_jobs[0])
            
@pytest.mark.regression
@pytest.mark.asyncio
async def test_indeed_field_regression():
    """Test Indeed scraper for field regressions."""
    async with IndeedScraper(TEST_SEARCH_TERMS, location=TEST_LOCATION) as scraper:
        jobs = await scraper.fetch_all_jobs()
        
    current_data = [serialize_job(job) for job in jobs]
    snapshot_data = load_snapshot('indeed_jobs.json')
    
    if not snapshot_data:
        save_snapshot('indeed_jobs.json', current_data)
        pytest.skip("Initial snapshot created")
        
    assert len(current_data) > 0, "No jobs found"
    for current_job in current_data:
        matching_jobs = [j for j in snapshot_data if j['url'] == current_job['url']]
        if matching_jobs:
            compare_job_fields(current_job, matching_jobs[0])
            
@pytest.mark.regression
@pytest.mark.asyncio
async def test_ziprecruiter_field_regression():
    """Test ZipRecruiter scraper for field regressions."""
    async with ZipRecruiterScraper(TEST_SEARCH_TERMS, location=TEST_LOCATION) as scraper:
        jobs = await scraper.fetch_all_jobs()
        
    current_data = [serialize_job(job) for job in jobs]
    snapshot_data = load_snapshot('ziprecruiter_jobs.json')
    
    if not snapshot_data:
        save_snapshot('ziprecruiter_jobs.json', current_data)
        pytest.skip("Initial snapshot created")
        
    assert len(current_data) > 0, "No jobs found"
    for current_job in current_data:
        matching_jobs = [j for j in snapshot_data if j['url'] == current_job['url']]
        if matching_jobs:
            compare_job_fields(current_job, matching_jobs[0])
            
@pytest.mark.regression
@pytest.mark.asyncio
async def test_selector_regression():
    """Test for selector regressions across all scrapers."""
    scrapers = [
        LinkedInScraper(TEST_SEARCH_TERMS),
        IndeedScraper(TEST_SEARCH_TERMS),
        ZipRecruiterScraper(TEST_SEARCH_TERMS)
    ]
    
    for scraper in scrapers:
        scraper_name = scraper.__class__.__name__.lower()
        async with scraper:
            # Get current selectors
            current_selectors = scraper.selector_maintainer._selectors
            
            # Load snapshot
            snapshot_data = load_snapshot(f'{scraper_name}_selectors.json')
            
            if not snapshot_data:
                save_snapshot(f'{scraper_name}_selectors.json', current_selectors)
                continue
                
            # Compare selectors
            for purpose, info in current_selectors.items():
                if purpose in snapshot_data:
                    assert info.selector == snapshot_data[purpose]['selector'], \
                        f"Selector changed for {purpose}"
                    assert info.required == snapshot_data[purpose]['required'], \
                        f"Required flag changed for {purpose}"
                        
@pytest.mark.regression
@pytest.mark.asyncio
async def test_performance_regression():
    """Test for performance regressions."""
    scrapers = [
        LinkedInScraper(TEST_SEARCH_TERMS),
        IndeedScraper(TEST_SEARCH_TERMS),
        ZipRecruiterScraper(TEST_SEARCH_TERMS)
    ]
    
    for scraper in scrapers:
        scraper_name = scraper.__class__.__name__.lower()
        async with scraper:
            start_time = datetime.now(timezone.utc)
            jobs = await scraper.fetch_all_jobs()
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Load performance snapshot
            snapshot_data = load_snapshot(f'{scraper_name}_performance.json')
            
            performance_data = {
                'duration': duration,
                'job_count': len(jobs),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            if not snapshot_data:
                save_snapshot(f'{scraper_name}_performance.json', performance_data)
                continue
                
            # Allow for some performance variance (50% slower)
            assert duration <= snapshot_data['duration'] * 1.5, \
                f"Performance regression in {scraper_name}"
