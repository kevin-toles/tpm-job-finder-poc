"""Test fixtures for job scraper tests."""

import pytest
from typing import Dict, Any
from src.core.config import Settings, ScraperConfig

# Mock job data
LINKEDIN_JOB_DATA = {
    "title": "Technical Program Manager",
    "company": "Example Corp",
    "location": "San Francisco, CA",
    "description": "Example job description",
    "url": "https://linkedin.com/jobs/123",
    "posted_date": "2025-09-08",
    "salary_range": "$150,000 - $200,000",
    "employment_type": "Full-time"
}

INDEED_JOB_DATA = {
    "jobtitle": "TPM",
    "company": "Tech Co",
    "formattedLocation": "Remote",
    "snippet": "Sample job description",
    "jobkey": "abc123",
    "formattedRelativeTime": "1 day ago",
    "formattedPayScale": "$140,000 - $180,000",
    "jobType": "Full-time"
}

ZIPRECRUITER_JOB_DATA = {
    "name": "Technical Program Manager",
    "hiring_company": {
        "name": "Startup Inc"
    },
    "location": "New York, NY",
    "snippet": "Exciting TPM role",
    "url": "https://ziprecruiter.com/jobs/456",
    "posted_time": "2025-09-08T12:00:00Z",
    "salary_interval": "$160,000 - $190,000",
    "employment_type": "Full-time"
}

# Mock API responses
MOCK_API_RESPONSES = {
    "linkedin": {
        "jobs": [LINKEDIN_JOB_DATA]
    },
    "indeed": {
        "results": [INDEED_JOB_DATA]
    },
    "ziprecruiter": {
        "jobs": [ZIPRECRUITER_JOB_DATA]
    }
}

@pytest.fixture
def test_settings():
    """Fixture for test settings."""
    return Settings(
        scrapers={
            "linkedin": ScraperConfig(
                enabled=True,
                requests_per_minute=2,
                cache_enabled=False
            ),
            "indeed": ScraperConfig(
                enabled=True,
                requests_per_minute=2,
                cache_enabled=False
            ),
            "ziprecruiter": ScraperConfig(
                enabled=True,
                requests_per_minute=2,
                cache_enabled=False
            )
        }
    )

@pytest.fixture
def mock_job_request():
    """Fixture for job request data."""
    return {
        "search_terms": ["Technical Program Manager"],
        "location": "San Francisco",
        "max_results": 5
    }

@pytest.fixture
def mock_responses():
    """Fixture for mock API responses."""
    return MOCK_API_RESPONSES
