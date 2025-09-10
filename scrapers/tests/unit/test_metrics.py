"""Unit tests for scraper metrics collection."""

import pytest
from src.core.metrics import MetricsCollector

def test_record_request():
    """Test request recording."""
    MetricsCollector.record_request("linkedin", "success")
    # Verify counter increased
    assert MetricsCollector.SCRAPER_REQUESTS.labels(
        source="linkedin",
        status="success"
    )._value.get() > 0

def test_record_jobs_found():
    """Test jobs found recording."""
    initial = MetricsCollector.JOBS_FOUND.labels(source="linkedin")._value.get()
    MetricsCollector.record_jobs_found("linkedin", 5)
    after = MetricsCollector.JOBS_FOUND.labels(source="linkedin")._value.get()
    assert after - initial == 5

def test_record_cache_metrics():
    """Test cache metrics recording."""
    MetricsCollector.record_cache_hit("linkedin")
    assert MetricsCollector.CACHE_HITS.labels(source="linkedin")._value.get() > 0
    
    MetricsCollector.record_cache_miss("linkedin")
    assert MetricsCollector.CACHE_MISSES.labels(source="linkedin")._value.get() > 0

def test_record_error():
    """Test error recording."""
    MetricsCollector.record_error("linkedin", "ConnectionError")
    assert MetricsCollector.SCRAPER_ERRORS.labels(
        source="linkedin",
        error_type="ConnectionError"
    )._value.get() > 0

def test_update_health():
    """Test health status updates."""
    MetricsCollector.update_health("linkedin", True)
    assert MetricsCollector.SCRAPER_HEALTH.labels(source="linkedin")._value.get() == 1
    
    MetricsCollector.update_health("linkedin", False)
    assert MetricsCollector.SCRAPER_HEALTH.labels(source="linkedin")._value.get() == 0
