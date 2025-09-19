"""
TDD Unit tests initialization file for API Gateway Service tests.

This module sets up test configuration and shared fixtures for all
API Gateway service tests following TDD methodology.
"""

import pytest
import asyncio
import tempfile
import json
from unittest.mock import Mock, AsyncMock
from pathlib import Path


# Test configuration constants
TEST_SERVICE_NAME = "test_api_gateway_service"
TEST_PORT = 8888
TEST_AUTH_SERVICE_URL = "http://test-auth:8001"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_config():
    """Create test configuration for API Gateway."""
    from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
    
    return APIGatewayConfig(
        service_name=TEST_SERVICE_NAME,
        host="127.0.0.1",
        port=TEST_PORT,
        auth_service_url=TEST_AUTH_SERVICE_URL,
        enable_rate_limiting=True,
        default_rate_limit_requests=100,
        default_rate_limit_window_seconds=300,
        max_concurrent_requests=500,
        request_timeout_seconds=5.0,
        enable_cors=True,
        cors_origins=["http://localhost:3000"],
        enable_metrics=True,
        log_level="DEBUG"
    )


@pytest.fixture
def mock_auth_service():
    """Create mock authentication service."""
    mock_service = AsyncMock()
    mock_service.validate_token.return_value = {
        "valid": True,
        "user_id": "test_user",
        "permissions": ["read:jobs", "write:applications"]
    }
    return mock_service


@pytest.fixture
def mock_proxy_service():
    """Create mock proxy service."""
    mock_service = AsyncMock()
    mock_service.proxy_request.return_value = Mock(
        success=True,
        status_code=200,
        headers={"Content-Type": "application/json"},
        body=b'{"result": "success"}',
        response_time_ms=50.0
    )
    return mock_service


@pytest.fixture
def sample_routes():
    """Create sample routes for testing."""
    from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
        RouteDefinition, HttpMethod, RateLimitScope
    )
    
    return [
        RouteDefinition(
            route_id="auth-login",
            path="/api/v1/auth/login",
            method=HttpMethod.POST,
            target_service="auth_service",
            target_path="/auth/login",
            target_port=8001,
            requires_auth=False,
            rate_limit_scope=RateLimitScope.IP_ADDRESS,
            rate_limit_requests=10,
            rate_limit_window_seconds=300
        ),
        RouteDefinition(
            route_id="jobs-list",
            path="/api/v1/jobs",
            method=HttpMethod.GET,
            target_service="job_service",
            target_path="/jobs",
            target_port=8002,
            requires_auth=True,
            rate_limit_scope=RateLimitScope.USER,
            rate_limit_requests=100,
            rate_limit_window_seconds=3600
        ),
        RouteDefinition(
            route_id="notifications-send",
            path="/api/v1/notifications",
            method=HttpMethod.POST,
            target_service="notification_service",
            target_path="/notifications/send",
            target_port=8003,
            requires_auth=True,
            rate_limit_scope=RateLimitScope.USER,
            rate_limit_requests=50,
            rate_limit_window_seconds=3600
        )
    ]


@pytest.fixture
def sample_rate_limit_rules():
    """Create sample rate limit rules for testing."""
    from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
        RateLimitRule, RateLimitScope
    )
    
    return [
        RateLimitRule(
            rule_id="global-limit",
            scope=RateLimitScope.GLOBAL,
            scope_value="*",
            requests_per_window=10000,
            window_seconds=3600,
            enabled=True
        ),
        RateLimitRule(
            rule_id="user-limit",
            scope=RateLimitScope.USER,
            scope_value="test_user",
            requests_per_window=1000,
            window_seconds=3600,
            enabled=True
        ),
        RateLimitRule(
            rule_id="ip-limit",
            scope=RateLimitScope.IP_ADDRESS,
            scope_value="192.168.1.100",
            requests_per_window=100,
            window_seconds=300,
            enabled=True
        )
    ]


@pytest.fixture
def temp_config_file():
    """Create temporary configuration file for testing."""
    config_data = {
        "service_name": "temp_test_gateway",
        "port": 8999,
        "auth_service_url": "http://temp-auth:8001",
        "enable_rate_limiting": True,
        "default_rate_limit_requests": 500,
        "log_level": "DEBUG"
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config_data, f)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_metrics_collector():
    """Create mock metrics collector."""
    mock_collector = Mock()
    mock_collector.record_request.return_value = None
    mock_collector.record_response.return_value = None
    mock_collector.get_metrics.return_value = {
        "total_requests": 100,
        "successful_requests": 95,
        "failed_requests": 5,
        "rate_limited_requests": 2,
        "average_response_time_ms": 125.5,
        "active_routes": 10
    }
    return mock_collector


# Shared test utilities
class TestHelpers:
    """Shared test helper functions."""
    
    @staticmethod
    def create_request_context(path="/api/v1/test", method="GET", user_id=None, client_ip="192.168.1.100"):
        """Create a RequestContext for testing."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RequestContext, HttpMethod
        )
        import uuid
        
        return RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod(method),
            path=path,
            headers={"Authorization": f"Bearer token_{user_id}"} if user_id else {},
            query_params={},
            client_ip=client_ip,
            user_id=user_id,
            authenticated=user_id is not None
        )
    
    @staticmethod
    def create_proxy_request(target_url="http://test-service:8000/test", method="GET"):
        """Create a ProxyRequest for testing."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            ProxyRequest, HttpMethod
        )
        import uuid
        
        return ProxyRequest(
            request_id=str(uuid.uuid4()),
            target_url=target_url,
            method=HttpMethod(method),
            headers={},
            body=None,
            timeout_seconds=5.0
        )


# Export test helpers for easy import
__all__ = [
    "TEST_SERVICE_NAME",
    "TEST_PORT", 
    "TEST_AUTH_SERVICE_URL",
    "TestHelpers"
]