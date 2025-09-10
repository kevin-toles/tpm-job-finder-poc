"""Integration tests for job aggregation system."""

import pytest
from ...aggregators import LinkedInScraper, IndeedScraper
from ..helpers.assertions import assert_valid_response_format

@pytest.mark.integration
@pytest.mark.asyncio
async def test_multiple_source_aggregation():
    """Test aggregating jobs from multiple sources."""
    scrapers = [
        LinkedInScraper(search_terms=["TPM"]),
        IndeedScraper(search_terms=["Technical Program Manager"])
    ]
    
    all_jobs = []
    for scraper in scrapers:
        async with scraper:
            jobs = await scraper.fetch_jobs(max_results=5)
            all_jobs.extend(jobs)
    
    assert len(all_jobs) > 0
    for job in all_jobs:
        assert_valid_job_data(job)
