"""Regression tests for reported issues."""

import pytest
import aiohttp
from src.core.base import BaseScraper
from src.core.config import ScraperConfig

@pytest.mark.regression
@pytest.mark.asyncio
async def test_rate_limit_regression():
    """Regression test for issue #156: Rate limiting not working correctly."""
    config = ScraperConfig(requests_per_minute=2)
    scraper = BaseScraper(config)
    
    start_time = time.time()
    async with scraper:
        # Should take at least 1 second due to rate limiting
        await scraper.make_request("https://example.com")
        await scraper.make_request("https://example.com")
        
    duration = time.time() - start_time
    assert duration >= 1.0, "Rate limiting not enforced correctly"

@pytest.mark.regression
@pytest.mark.asyncio
async def test_retry_regression():
    """Regression test for issue #178: Retry logic not respecting max retries."""
    config = ScraperConfig(max_retries=2)
    scraper = BaseScraper(config)
    
    with pytest.raises(aiohttp.ClientError):
        async with scraper:
            await scraper.make_request("https://non-existent-url.com")
    
    assert scraper.retry_count <= config.max_retries, \
        "Retry count exceeded configured maximum"

@pytest.mark.regression
def test_url_sanitization_regression():
    """Regression test for issue #189: URL sanitization bypass."""
    from src.core.linkedin import LinkedInScraper
    
    config = ScraperConfig()
    scraper = LinkedInScraper(config)
    
    malicious_data = {
        "url": "javascript:alert(1)",  # Should be sanitized
        "title": "Test Job",
        "company": "Test Co",
        "location": "Remote",
        "description": "Test Description"
    }
    
    job = scraper._parse_job(malicious_data)
    assert not job.url.startswith("javascript:"), \
        "URL sanitization failed to remove javascript protocol"

@pytest.mark.regression
@pytest.mark.asyncio
async def test_memory_leak_regression():
    """Regression test for issue #201: Memory leak in response caching."""
    from src.core.response_cache import ResponseCache
    import gc
    import psutil
    
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    cache = ResponseCache(max_age=60)
    
    # Simulate heavy usage
    for i in range(1000):
        cache.set(f"key{i}", f"value{i}" * 1000)
    
    # Force garbage collection
    gc.collect()
    
    current_memory = process.memory_info().rss
    memory_increase = current_memory - initial_memory
    
    # Should not increase memory by more than 10MB
    assert memory_increase < 10 * 1024 * 1024, \
        "Possible memory leak detected in response cache"
