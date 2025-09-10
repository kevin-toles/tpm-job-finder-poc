"""End-to-end tests for job aggregation system."""

import pytest
import asyncio
from ...aggregators import LinkedInScraper
from ..helpers.validation import validate_job_fields, validate_response_structure

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_job_search_workflow():
    """Test complete job search workflow."""
    # Initialize scraper
    search_terms = ["Technical Program Manager", "TPM"]
    async with LinkedInScraper(search_terms=search_terms) as scraper:
        # Fetch jobs
        jobs = await scraper.fetch_jobs(max_results=10)
        
        # Validate response
        response = {"jobs": jobs}
        structure_errors = validate_response_structure(response)
        assert not structure_errors, f"Response structure errors: {structure_errors}"
        
        # Validate each job
        for job in jobs:
            field_errors = validate_job_fields(job)
            assert not field_errors, f"Job field errors: {field_errors}"
            
        # Check job relevance
        for job in jobs:
            title = job["title"].lower()
            assert any(term.lower() in title for term in search_terms), \
                f"Job title '{job['title']}' not relevant to search terms"
