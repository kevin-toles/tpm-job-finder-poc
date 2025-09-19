"""
Test fixtures for health monitoring service tests.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from tpm_job_finder_poc.health_monitoring_service.service import HealthMonitoringService
from tpm_job_finder_poc.health_monitoring_service.config import HealthMonitoringConfig


@pytest.fixture
async def health_service():
    """Create a health monitoring service instance for testing."""
    config = HealthMonitoringConfig(
        check_interval_seconds=10,  # Minimum allowed interval
        concurrent_checks=2,
        enable_metrics_collection=True,
        enable_alerting=True,
        max_historical_records=50,
        alert_threshold_error_rate=0.5,
        alert_threshold_response_time_ms=5000.0,
        services_to_monitor=["test_service"]
    )
    
    service = HealthMonitoringService(config)
    
    yield service
    
    # Cleanup
    if service.is_monitoring_active():
        await service.stop_monitoring()


@pytest.fixture
def mock_http_server():
    """Mock HTTP server for testing health endpoints."""
    return Mock()


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp session for testing HTTP requests."""
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = {"status": "healthy"}
    mock_session.get.return_value.__aenter__.return_value = mock_response
    return mock_session