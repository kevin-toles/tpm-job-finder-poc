"""Test configuration and shared fixtures."""

import pytest
import asyncio
from src.core.config import Settings, ScraperConfig
from src.core.metrics import MetricsCollector
from src.api.main import app
from httpx import AsyncClient

# Reset metrics between tests
@pytest.fixture(autouse=True)
def reset_metrics():
    """Reset all metrics before each test."""
    # Clear all metric values
    for metric in [
        MetricsCollector.SCRAPER_REQUESTS,
        MetricsCollector.JOBS_FOUND,
        MetricsCollector.CACHE_HITS,
        MetricsCollector.CACHE_MISSES,
        MetricsCollector.SCRAPER_ERRORS
    ]:
        metric.clear()
    yield

# Test settings
@pytest.fixture
def test_settings():
    """Provide test settings."""
    return Settings(
        scrapers={
            source: ScraperConfig(
                enabled=True,
                requests_per_minute=10,
                cache_enabled=False,
                max_retries=1
            )
            for source in ["linkedin", "indeed", "ziprecruiter"]
        }
    )

# Async client
@pytest.fixture
async def client():
    """Provide async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

# Event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Mark tests by type
def pytest_collection_modifyitems(items):
    """Add markers based on test location."""
    for item in items:
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "regression" in str(item.fspath):
            item.add_marker(pytest.mark.regression)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
