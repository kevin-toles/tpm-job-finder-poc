"""Unit tests for base scraper functionality."""

import pytest
import aiohttp
from ...base import BaseScraper
from ...config import ScraperConfig

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test that rate limiting works correctly."""
    config = ScraperConfig(requests_per_minute=2)
    scraper = BaseScraper(config)
    
    async with scraper:
        # Should not exceed rate limit
        for _ in range(3):
            await scraper.make_request("https://example.com")
            
    assert scraper.request_count <= config.requests_per_minute

@pytest.mark.asyncio
async def test_browser_simulation():
    """Test browser simulation headers."""
    config = ScraperConfig(browser_simulation_enabled=True)
    scraper = BaseScraper(config)
    
    headers = scraper._get_headers()
    assert "User-Agent" in headers
    assert "Accept" in headers
    assert "Accept-Language" in headers

@pytest.mark.asyncio
async def test_retry_logic():
    """Test retry logic with failed requests."""
    config = ScraperConfig(max_retries=3)
    scraper = BaseScraper(config)
    
    with pytest.raises(aiohttp.ClientError):
        async with scraper:
            await scraper.make_request("https://non-existent-url.com")
    
    assert scraper.retry_count == config.max_retries
