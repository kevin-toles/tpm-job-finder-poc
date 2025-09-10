"""Test utilities and fixtures for job aggregator tests."""

import json
import os
from typing import Dict, Any
import pytest
import aiohttp
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, MagicMock, patch
from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.base import BaseJobScraper

def load_test_html(filename: str) -> str:
    """Load test HTML file from fixtures directory.
    
    Args:
        filename: Name of the HTML file in tests/fixtures
        
    Returns:
        Contents of the HTML file
    """
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        filename
    )
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return f.read()
        
def load_test_json(filename: str) -> Dict[str, Any]:
    """Load test JSON file from fixtures directory.
    
    Args:
        filename: Name of the JSON file in tests/fixtures
        
    Returns:
        Parsed JSON data
    """
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        'fixtures',
        filename
    )
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)
        
class MockResponse:
    """Mock aiohttp response for testing."""
    
    def __init__(self, status: int, text: str):
        self.status = status
        self._text = text
        
    async def text(self) -> str:
        return self._text
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        pass
        
@pytest.fixture
def mock_session():
    """Fixture providing a mock aiohttp ClientSession."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    return session
    
@pytest.fixture
def mock_response():
    """Fixture for creating mock responses."""
    def _create_response(status: int = 200, text: str = ""):
        return MockResponse(status, text)
    return _create_response
    
@pytest.fixture
def mock_scraper():
    """Fixture providing a mock scraper instance."""
    scraper = AsyncMock(spec=BaseJobScraper)
    scraper.clean_text = BaseJobScraper._clean_text
    return scraper
    
@pytest.fixture
def sample_job_posting():
    """Fixture providing a sample JobPosting object."""
    return JobPosting(
        id="123",
        source="test",
        company="Test Company",
        title="Technical Program Manager",
        location="Remote",
        salary="$150,000 - $200,000",
        url="https://example.com/job/123",
        date_posted="2025-09-09T00:00:00Z",
        description="Test job description",
        raw={
            "title": "Technical Program Manager",
            "company": "Test Company",
            "location": "Remote",
            "salary": "$150,000 - $200,000",
            "url": "https://example.com/job/123",
            "posted_date": "2025-09-09T00:00:00Z",
            "description": "Test job description"
        }
    )
    
@pytest.fixture
def sample_search_html():
    """Fixture providing sample search results HTML."""
    return load_test_html('search_results.html')
    
@pytest.fixture
def sample_job_html():
    """Fixture providing sample job details HTML."""
    return load_test_html('job_details.html')
    
def assert_job_fields(job: JobPosting):
    """Helper to assert that a JobPosting has all required fields.
    
    Args:
        job: JobPosting object to validate
    """
    assert job.id is not None
    assert job.source is not None
    assert job.company is not None
    assert job.title is not None
    assert job.location is not None
    assert job.url is not None
    assert job.date_posted is not None
    assert job.description is not None
    assert isinstance(job.raw, dict)
    
def setup_mock_responses(mock_session, responses: Dict[str, tuple]):
    """Set up mock responses for URLs.
    
    Args:
        mock_session: Mock aiohttp.ClientSession
        responses: Dict of URL to (status, content) tuples
    """
    async def mock_get(url, **kwargs):
        if url in responses:
            status, content = responses[url]
            return MockResponse(status, content)
        return MockResponse(404, "Not Found")
        
    mock_session.get = AsyncMock(side_effect=mock_get)
    return mock_session
