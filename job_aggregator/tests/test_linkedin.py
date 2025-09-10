"""Unit tests for LinkedIn scraper."""

import pytest
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from unittest.mock import AsyncMock, patch

from job_aggregator.scrapers.linkedin import LinkedInScraper
from job_aggregator.tests.test_utils import (
    load_test_html,
    mock_session,
    mock_response,
    assert_job_fields,
    setup_mock_responses
)

@pytest.fixture
def scraper():
    """Fixture providing a LinkedIn scraper instance."""
    return LinkedInScraper(["Technical Program Manager"])
    
@pytest.mark.asyncio
async def test_search_success(scraper, mock_session):
    """Test successful job search."""
    # Load sample HTML
    html = load_test_html('linkedin_search.html')
    
    # Set up mock responses
    responses = {
        'https://www.linkedin.com/jobs/search?keywords=Technical+Program+Manager': (200, html)
    }
    mock_session = setup_mock_responses(mock_session, responses)
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            jobs = await scraper.search("Technical Program Manager")
            
    # Verify results
    assert len(jobs) > 0
    for job in jobs:
        assert_job_fields(job)
        assert job.source == "linkedin"
        
@pytest.mark.asyncio
async def test_search_no_results(scraper, mock_session, mock_response):
    """Test search with no results."""
    # Set up empty search results
    mock_session.get.return_value = mock_response(200, "<html><body></body></html>")
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            jobs = await scraper.search("NonexistentJobTitle")
            
    assert len(jobs) == 0
    
@pytest.mark.asyncio
async def test_search_network_error(scraper, mock_session):
    """Test handling of network errors."""
    # Simulate network error
    mock_session.get.side_effect = Exception("Network Error")
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            jobs = await scraper.search("Technical Program Manager")
            
    assert len(jobs) == 0
    
@pytest.mark.asyncio
async def test_get_job_details_success(scraper, mock_session):
    """Test successful job details retrieval."""
    # Load sample HTML
    html = load_test_html('linkedin_job.html')
    
    # Set up mock response
    job_url = "https://www.linkedin.com/jobs/view/123"
    responses = {job_url: (200, html)}
    mock_session = setup_mock_responses(mock_session, responses)
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            description = await scraper.get_job_details(job_url)
            
    assert description is not None
    assert len(description) > 0
    
@pytest.mark.asyncio
async def test_get_job_details_not_found(scraper, mock_session, mock_response):
    """Test job details not found."""
    # Set up 404 response
    mock_session.get.return_value = mock_response(404, "Not Found")
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            description = await scraper.get_job_details("https://www.linkedin.com/jobs/view/999")
            
    assert description is None
    
@pytest.mark.asyncio
async def test_date_parsing(scraper):
    """Test parsing of various date formats."""
    test_cases = [
        ("Just posted", datetime.now(timezone.utc)),
        ("1 hour ago", datetime.now(timezone.utc)),
        ("2 days ago", datetime.now(timezone.utc)),
        ("2023-09-09", datetime(2023, 9, 9, tzinfo=timezone.utc))
    ]
    
    for date_str, expected in test_cases:
        elem = BeautifulSoup(f'<time datetime="{date_str}"></time>', 'html.parser')
        result = scraper._parse_date(elem)
        
        # Allow small time differences for "ago" dates
        if "ago" in date_str or "Just posted" in date_str:
            diff = abs((result - expected).total_seconds())
            assert diff < 3600  # Within one hour
        else:
            assert result == expected
            
@pytest.mark.asyncio
async def test_selector_maintenance(scraper, mock_session):
    """Test selector maintenance and repair."""
    # Load sample HTML with modified selectors
    html = load_test_html('linkedin_search_modified.html')
    
    # Set up mock responses
    responses = {
        'https://www.linkedin.com/jobs/search?keywords=Technical+Program+Manager': (200, html)
    }
    mock_session = setup_mock_responses(mock_session, responses)
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            jobs = await scraper.search("Technical Program Manager")
            
    # Verify results even with modified selectors
    assert len(jobs) > 0
    for job in jobs:
        assert_job_fields(job)
        assert job.source == "linkedin"
        
@pytest.mark.asyncio
async def test_rate_limiting(scraper, mock_session, mock_response):
    """Test rate limiting functionality."""
    # Set up mock response
    mock_session.get.return_value = mock_response(200, "<html><body></body></html>")
    
    # Patch session creation and time
    with patch('aiohttp.ClientSession', return_value=mock_session), \
         patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        async with scraper:
            # Make multiple requests
            for _ in range(3):
                await scraper.search("Technical Program Manager")
                
    # Verify rate limiting was applied
    assert mock_sleep.called
    
@pytest.mark.asyncio
async def test_proxy_rotation(scraper, mock_session):
    """Test proxy rotation functionality."""
    # Configure scraper with proxies
    scraper.proxy_list = ["http://proxy1.com", "http://proxy2.com"]
    
    # Load sample HTML
    html = load_test_html('linkedin_search.html')
    
    # Set up mock response
    mock_session.get.return_value = mock_response(200, html)
    
    # Patch session creation
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with scraper:
            await scraper.search("Technical Program Manager")
            
    # Verify proxy was used
    call_kwargs = mock_session.get.call_args[1]
    assert 'proxy' in call_kwargs
    assert call_kwargs['proxy'] in scraper.proxy_list
