"""Unit tests for job scrapers."""

import pytest
from ...aggregators.linkedin_scraper import LinkedInScraper
from ..fixtures.response_mocks import SAMPLE_LINKEDIN_RESPONSE
from ..helpers.assertions import assert_valid_job_data

@pytest.mark.asyncio
async def test_linkedin_scraper_job_extraction():
    """Test that LinkedIn scraper correctly extracts job data."""
    scraper = LinkedInScraper(search_terms=["TPM"])
    jobs = scraper._parse_response(SAMPLE_LINKEDIN_RESPONSE)
    
    assert jobs
    for job in jobs:
        assert_valid_job_data(job)

@pytest.mark.asyncio
async def test_linkedin_scraper_rate_limiting():
    """Test that rate limiting works correctly."""
    scraper = LinkedInScraper(search_terms=["TPM"])
    await scraper.fetch_jobs(max_results=5)
    # Should not exceed rate limit
    assert scraper.request_count <= scraper.config.requests_per_minute
