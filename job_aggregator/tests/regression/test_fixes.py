"""Regression tests for reported issues."""

import pytest
from ...aggregators import LinkedInScraper
from ..fixtures.response_mocks import SAMPLE_LINKEDIN_RESPONSE
from ..helpers.validation import validate_job_fields

@pytest.mark.regression
def test_empty_description_handling():
    """Regression test for issue #123: Empty job descriptions."""
    empty_description_response = {
        "jobs": [
            {
                "title": "Technical Program Manager",
                "company": "Example Corp",
                "location": "San Francisco, CA",
                "description": ""
            }
        ]
    }
    
    scraper = LinkedInScraper(search_terms=["TPM"])
    jobs = scraper._parse_response(empty_description_response)
    
    for job in jobs:
        errors = validate_job_fields(job)
        assert not errors, f"Job validation failed: {errors}"
        assert job["description"] == "Not specified"

@pytest.mark.regression
def test_malformed_url_handling():
    """Regression test for issue #145: Malformed application URLs."""
    response_with_bad_url = {
        "jobs": [
            {
                "title": "Technical Program Manager",
                "company": "Example Corp",
                "location": "San Francisco, CA",
                "description": "Sample description",
                "url": "http://example.com/jobs/<script>"
            }
        ]
    }
    
    scraper = LinkedInScraper(search_terms=["TPM"])
    jobs = scraper._parse_response(response_with_bad_url)
    
    for job in jobs:
        assert "<script>" not in job["url"], "URL contains unsafe characters"
