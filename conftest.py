# Global pytest configuration for performance optimization

import pytest
import os

def pytest_configure(config):
    """Configure pytest for optimal performance."""
    # Disable benchmark plugin warnings if xdist is active
    if hasattr(config.option, 'numprocesses') and config.option.numprocesses:
        config.addinivalue_line("filterwarnings", "ignore::UserWarning")

def pytest_collection_modifyitems(config, items):
    """Automatically mark slow tests based on patterns."""
    for item in items:
        # Mark large test files as potentially slow
        if 'test_complete_workflows.py' in item.nodeid or 'test_advanced_analytics' in item.nodeid:
            item.add_marker(pytest.mark.slow)

# Performance-focused fixtures
@pytest.fixture(scope="session")
def fast_mode():
    """Enable fast mode for tests - reduces delays and timeouts."""
    return os.getenv("PYTEST_FAST_MODE", "1") == "1"

@pytest.fixture
def minimal_delay(fast_mode):
    """Provide minimal delay for tests that need timing."""
    return 0.001 if fast_mode else 0.1
