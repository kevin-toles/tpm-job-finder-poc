"""
Tests for the Glassdoor scraper stub.
"""
import pytest
from datetime import datetime

from scraping_service.scrapers.glassdoor import GlassdoorScraper
# TODO: ScraperError not found, stub or update import as needed

@pytest.fixture
def scraper():
    """Create a Glassdoor scraper instance for testing."""
    config = {
        'use_proxy': False,
        'rate_limit': 60,
        'timeout': 30
    }
    return GlassdoorScraper(config)

def test_search_jobs_returns_empty_list(scraper):
    """Test that the stub search_jobs returns an empty list."""
    jobs = scraper.search_jobs("Technical Program Manager")
    assert isinstance(jobs, list)
    assert len(jobs) == 0

def test_get_job_details_raises_not_implemented(scraper):
    """Test that get_job_details raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        scraper.get_job_details("https://www.glassdoor.com/job-123")

def test_verify_access_returns_false(scraper):
    """Test that verify_access returns False for the stub."""
    assert scraper.verify_access() is False

def test_health_check_returns_not_implemented(scraper):
    """Test that health_check raises NotImplementedError for the stub."""
    with pytest.raises(NotImplementedError):
        status = scraper.health_check()
