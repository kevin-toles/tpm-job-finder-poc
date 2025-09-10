"""Test configuration and fixtures."""

import pytest
import asyncio
import os
from pathlib import Path

# Test configuration
TEST_CONFIG = {
    "linkedin": {
        "enabled": True,
        "requests_per_minute": 2,  # Lower rate for testing
        "cache_enabled": True,
        "cache_max_age": 60,  # Short cache for testing
        "proxy_enabled": False,
        "browser_simulation_enabled": False,
        "captcha_service_enabled": False
    }
}

# Test search parameters
TEST_SEARCH_TERMS = ["Technical Program Manager", "TPM"]
TEST_LOCATIONS = ["San Francisco, CA", "Remote"]

@pytest.fixture
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG

@pytest.fixture
def search_params():
    """Provide test search parameters."""
    return {
        "terms": TEST_SEARCH_TERMS,
        "locations": TEST_LOCATIONS
    }

@pytest.fixture
async def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
