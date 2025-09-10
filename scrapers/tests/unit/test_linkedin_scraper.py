"""Unit tests for LinkedIn scraper implementation."""

import pytest
from ...linkedin import LinkedInScraper
from ...config import ScraperConfig

@pytest.mark.asyncio
async def test_linkedin_search_params():
    """Test LinkedIn search parameter construction."""
    config = ScraperConfig()
    scraper = LinkedInScraper(config)
    
    params = scraper._build_search_params(
        search_terms=["Technical Program Manager"],
        location="San Francisco"
    )
    
    assert "keywords" in params
    assert "location" in params
    assert params["keywords"] == "Technical Program Manager"
    assert params["location"] == "San Francisco"

@pytest.mark.asyncio
async def test_linkedin_job_parsing():
    """Test LinkedIn job data parsing."""
    config = ScraperConfig()
    scraper = LinkedInScraper(config)
    
    sample_job = {
        "title": "Technical Program Manager",
        "company": "Example Corp",
        "location": "San Francisco, CA",
        "description": "Example job description"
    }
    
    parsed_job = scraper._parse_job(sample_job)
    
    assert parsed_job["title"] == sample_job["title"]
    assert parsed_job["company"] == sample_job["company"]
    assert parsed_job["location"] == sample_job["location"]
    assert parsed_job["description"] == sample_job["description"]
