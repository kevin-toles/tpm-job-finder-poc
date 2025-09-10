"""
Tests for the Glassdoor scraper stub.
"""
import pytest
from datetime import datetime

from tpm_job_finder_poc.scraping_service.scrapers.glassdoor import GlassdoorScraper
from tpm_job_finder_poc.scraping_service.scrapers.base import ScraperError

@pytest.fixture
def scraper():
    """Create a Glassdoor scraper instance for testing."""
    config = {
        'use_proxy': False,
        'rate_limit': 60,
        'timeout': 30
    }
    return GlassdoorScraper(config)

@pytest.mark.asyncio
async def test_search_jobs_returns_empty_list(scraper):
    """Test that the stub search_jobs returns an empty list."""
    jobs = await scraper.search_jobs("Technical Program Manager")
    assert isinstance(jobs, list)
    assert len(jobs) == 0

@pytest.mark.asyncio
async def test_get_job_details_raises_not_implemented(scraper):
    """Test that get_job_details raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        await scraper.get_job_details("https://www.glassdoor.com/job-123")

@pytest.mark.asyncio
async def test_verify_access_returns_false(scraper):
    """Test that verify_access returns False."""
    assert await scraper.verify_access() is False

@pytest.mark.asyncio
async def test_health_check_returns_not_implemented(scraper):
    """Test that health_check returns not_implemented status."""
    status = await scraper.health_check()
    assert status['status'] == 'not_implemented'
    assert 'details' in status
    assert 'last_successful_scrape' in status
