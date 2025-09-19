"""
Comprehensive TDD unit tests for API Gateway Service.

This test suite follows TDD methodology (RED → GREEN → REFACTOR) and defines
all requirements for the API Gateway service including:
- Unified entry point for all API requests
- Dynamic route registration and management
- Rate limiting with multiple scopes (global, user, IP, API key)
- Authentication integration with auth service
- Request proxying to backend services
- Health monitoring and metrics collection
- Service discovery and load balancing
- CORS and security policy enforcement

Test Structure:
1. Interface and Contract Tests (Service contracts)
2. Routing Service Tests (Route management and resolution)
3. Rate Limiting Tests (Multiple scopes and enforcement)
4. Authentication Integration Tests (Auth service integration)
5. Proxy Service Tests (Request forwarding and response handling)
6. Gateway Service Tests (End-to-end request processing)
7. Configuration Tests (Service configuration management)
8. API Tests (FastAPI REST endpoints)
9. Health and Metrics Tests (Monitoring and observability)
10. Security Tests (CORS, input validation, security policies)
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import json
import uuid
import aiohttp
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Import API Gateway contracts
from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
    HttpMethod, RouteDefinition, RequestContext, RateLimitScope, 
    RateLimitStatus, ProxyResponse
)

# Test Configuration
pytest_plugins = ['pytest_asyncio']

@pytest.fixture(scope="session", autouse=True)
def setup_gateway_service():
    """Setup gateway service for API tests."""
    from tpm_job_finder_poc.api_gateway_service.config import ConfigurationManager
    from tpm_job_finder_poc.api_gateway_service.service import APIGatewayService
    import tpm_job_finder_poc.api_gateway_service.api as api_module
    
    # Initialize configuration and service
    config_manager = ConfigurationManager()
    config = config_manager.get_current_configuration()
    service = APIGatewayService(config)
    
    # Set global variables that the API depends on
    api_module.gateway_service = service
    api_module.config_manager = config_manager
    
    # Initialize the service synchronously for testing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(service.initialize())
    finally:
        # Clean up but don't close the loop yet as tests need it
        pass
    
    yield service
    
    # Cleanup after all tests
    if service._running:
        loop.run_until_complete(service.stop())
    loop.close()

class TestAPIGatewayServiceInterface:
    """Test API Gateway service interface and contracts (TDD RED Phase)."""
    
    def test_api_gateway_service_interface_exists(self):
        """Test that APIGatewayService interface exists with required methods."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import IAPIGatewayService
        
        # Check interface exists with required methods
        required_methods = [
            'initialize', 'start', 'stop', 'process_request',
            'register_service_routes', 'health_check', 'get_metrics',
            'reload_configuration'
        ]
        
        for method in required_methods:
            assert hasattr(IAPIGatewayService, method), f"Missing method: {method}"
    
    def test_routing_service_interface_exists(self):
        """Test that RoutingService interface exists with required methods."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import IRoutingService
        
        required_methods = [
            'register_route', 'unregister_route', 'update_route',
            'resolve_route', 'list_routes', 'get_route'
        ]
        
        for method in required_methods:
            assert hasattr(IRoutingService, method), f"Missing method: {method}"
    
    def test_rate_limit_service_interface_exists(self):
        """Test that RateLimitService interface exists with required methods."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import IRateLimitService
        
        required_methods = [
            'create_rule', 'check_rate_limit', 'record_request',
            'get_rate_limit_status', 'reset_rate_limit'
        ]
        
        for method in required_methods:
            assert hasattr(IRateLimitService, method), f"Missing method: {method}"
    
    def test_proxy_service_interface_exists(self):
        """Test that ProxyService interface exists with required methods."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import IProxyService
        
        required_methods = [
            'proxy_request', 'health_check_service', 'get_service_status'
        ]
        
        for method in required_methods:
            assert hasattr(IProxyService, method), f"Missing method: {method}"

class TestAPIGatewayDataModels:
    """Test API Gateway data models and validation."""
    
    def test_route_definition_model(self):
        """Test RouteDefinition model creation and validation."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RouteDefinition, HttpMethod, RouteStatus, RateLimitScope
        )
        
        route = RouteDefinition(
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
        )
        
        assert route.route_id == "auth-login"
        assert route.method == HttpMethod.POST
        assert route.target_service == "auth_service"
        assert route.requires_auth is False
        assert route.rate_limit_scope == RateLimitScope.IP_ADDRESS
        assert isinstance(route.created_at, datetime)
    
    def test_request_context_model(self):
        """Test RequestContext model creation and validation."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RequestContext, HttpMethod
        )
        
        context = RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod.GET,
            path="/api/v1/jobs",
            headers={"Authorization": "Bearer token123"},
            query_params={"limit": "10"},
            client_ip="192.168.1.100",
            user_id="user123",
            authenticated=True
        )
        
        assert context.method == HttpMethod.GET
        assert context.path == "/api/v1/jobs"
        assert context.authenticated is True
        assert context.user_id == "user123"
        assert isinstance(context.timestamp, datetime)
    
    def test_rate_limit_rule_model(self):
        """Test RateLimitRule model creation and validation."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RateLimitRule, RateLimitScope
        )
        
        rule = RateLimitRule(
            rule_id="user-limit",
            scope=RateLimitScope.USER,
            scope_value="user123",
            requests_per_window=1000,
            window_seconds=3600,
            burst_allowance=50
        )
        
        assert rule.scope == RateLimitScope.USER
        assert rule.requests_per_window == 1000
        assert rule.window_seconds == 3600
        assert rule.enabled is True

class TestRoutingService:
    """Test routing service functionality."""
    
    @pytest.fixture
    def routing_service(self):
        """Create routing service for testing."""
        from tpm_job_finder_poc.api_gateway_service.service import RoutingService
        return RoutingService()
    
    @pytest.mark.asyncio
    async def test_register_route(self, routing_service):
        """Test route registration."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RouteDefinition, HttpMethod
        )
        
        route = RouteDefinition(
            route_id="test-route",
            path="/api/v1/test",
            method=HttpMethod.GET,
            target_service="test_service",
            target_path="/test",
            target_port=8000
        )
        
        result = await routing_service.register_route(route)
        assert result is True
        
        # Verify route was registered
        retrieved_route = await routing_service.get_route("test-route")
        assert retrieved_route is not None
        assert retrieved_route.path == "/api/v1/test"
        assert retrieved_route.target_service == "test_service"
    
    @pytest.mark.asyncio
    async def test_resolve_route_success(self, routing_service):
        """Test successful route resolution."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RouteDefinition, HttpMethod
        )
        
        # Register a route
        route = RouteDefinition(
            route_id="jobs-list",
            path="/api/v1/jobs",
            method=HttpMethod.GET,
            target_service="job_service",
            target_path="/jobs",
            target_port=8002
        )
        await routing_service.register_route(route)
        
        # Resolve the route
        result = await routing_service.resolve_route(HttpMethod.GET, "/api/v1/jobs")
        
        assert result.success is True
        assert result.route is not None
        assert result.route.target_service == "job_service"
        assert result.target_url == "http://job_service:8002/jobs"
        assert result.should_proxy is True
    
    @pytest.mark.asyncio
    async def test_resolve_route_not_found(self, routing_service):
        """Test route resolution for non-existent route."""
        result = await routing_service.resolve_route(HttpMethod.GET, "/api/v1/nonexistent")
        
        assert result.success is False
        assert result.route is None
        assert result.error_message == "Route not found"
        assert result.status_code == 404
        assert result.should_proxy is False
    
    @pytest.mark.asyncio
    async def test_list_routes(self, routing_service):
        """Test listing registered routes."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RouteDefinition, HttpMethod, RouteStatus
        )
        
        # Register multiple routes
        routes = [
            RouteDefinition("route1", "/api/v1/auth", HttpMethod.POST, "auth_service", "/auth", 8001),
            RouteDefinition("route2", "/api/v1/jobs", HttpMethod.GET, "job_service", "/jobs", 8002),
            RouteDefinition("route3", "/api/v1/notifications", HttpMethod.POST, "notification_service", "/notifications", 8003, status=RouteStatus.INACTIVE)
        ]
        
        for route in routes:
            await routing_service.register_route(route)
        
        # List all routes
        all_routes = await routing_service.list_routes()
        assert len(all_routes) == 3
        
        # List only active routes
        active_routes = await routing_service.list_routes(RouteStatus.ACTIVE)
        assert len(active_routes) == 2

class TestRateLimitService:
    """Test rate limiting service functionality."""
    
    @pytest.fixture
    def rate_limit_service(self):
        """Create rate limit service for testing."""
        from tpm_job_finder_poc.api_gateway_service.service import RateLimitService
        return RateLimitService()
    
    @pytest.mark.asyncio
    async def test_create_rate_limit_rule(self, rate_limit_service):
        """Test creating rate limit rules."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RateLimitRule, RateLimitScope
        )
        
        rule = RateLimitRule(
            rule_id="user-limit",
            scope=RateLimitScope.USER,
            scope_value="user123",
            requests_per_window=100,
            window_seconds=3600
        )
        
        result = await rate_limit_service.create_rule(rule)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_rate_limit_within_limits(self, rate_limit_service):
        """Test rate limit check when within limits."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RequestContext, HttpMethod, RateLimitRule, RateLimitScope
        )
        
        # Create rate limit rule
        rule = RateLimitRule(
            rule_id="ip-limit",
            scope=RateLimitScope.IP_ADDRESS,
            scope_value="192.168.1.100",
            requests_per_window=10,
            window_seconds=300
        )
        await rate_limit_service.create_rule(rule)
        
        # Create request context
        context = RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod.GET,
            path="/api/v1/test",
            headers={},
            query_params={},
            client_ip="192.168.1.100"
        )
        
        # Check rate limit (first request)
        status = await rate_limit_service.check_rate_limit(context)
        
        assert status.blocked is False
        assert status.current_count <= status.limit
        assert status.remaining_requests > 0
        assert status.scope == RateLimitScope.IP_ADDRESS
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self, rate_limit_service):
        """Test rate limit check when limit is exceeded."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RequestContext, HttpMethod, RateLimitRule, RateLimitScope
        )
        
        # Create strict rate limit rule
        rule = RateLimitRule(
            rule_id="strict-limit",
            scope=RateLimitScope.IP_ADDRESS,
            scope_value="192.168.1.200",
            requests_per_window=1,
            window_seconds=300
        )
        await rate_limit_service.create_rule(rule)
        
        context = RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod.GET,
            path="/api/v1/test",
            headers={},
            query_params={},
            client_ip="192.168.1.200"
        )
        
        # First request should pass
        await rate_limit_service.record_request(context)
        
        # Second request should be blocked
        status = await rate_limit_service.check_rate_limit(context)
        assert status.blocked is True
        assert status.remaining_requests == 0

class TestAuthenticationIntegration:
    """Test authentication integration functionality."""
    
    @pytest.fixture
    def auth_integration(self):
        """Create authentication integration for testing."""
        from tpm_job_finder_poc.api_gateway_service.service import AuthenticationIntegration
        return AuthenticationIntegration(auth_service_url="http://localhost:8001")
    
    @pytest.mark.asyncio
    async def test_validate_token_success(self, auth_integration):
        """Test successful token validation."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock successful auth response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json.return_value = asyncio.Future()
            mock_response.json.return_value.set_result({
                "valid": True,
                "user_id": "user123",
                "permissions": ["read:jobs", "write:applications"]
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await auth_integration.validate_token("valid_token")
            
            assert result["valid"] is True
            assert result["user_id"] == "user123"
            assert "read:jobs" in result["permissions"]
    
    @pytest.mark.asyncio
    async def test_validate_token_invalid(self, auth_integration):
        """Test invalid token validation."""
        with patch('aiohttp.ClientSession.post') as mock_post:
            # Mock invalid auth response
            mock_response = Mock()
            mock_response.status = 401
            mock_response.json.return_value = asyncio.Future()
            mock_response.json.return_value.set_result({
                "valid": False,
                "error": "Invalid token"
            })
            mock_post.return_value.__aenter__.return_value = mock_response
            
            result = await auth_integration.validate_token("invalid_token")
            
            assert result["valid"] is False
            assert "error" in result

class TestProxyService:
    """Test proxy service functionality."""
    
    @pytest.fixture
    def proxy_service(self):
        """Create proxy service for testing."""
        from tpm_job_finder_poc.api_gateway_service.service import ProxyService
        return ProxyService()
    
    @pytest.mark.asyncio
    async def test_proxy_request_success(self, proxy_service):
        """Test successful request proxying."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            ProxyRequest, HttpMethod
        )
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Mock successful proxy response
            mock_response = Mock()
            mock_response.status = 200
            mock_response.headers = {"Content-Type": "application/json"}
            mock_response.read.return_value = asyncio.Future()
            mock_response.read.return_value.set_result(b'{"success": true}')
            mock_request.return_value.__aenter__.return_value = mock_response
            
            proxy_request = ProxyRequest(
                request_id=str(uuid.uuid4()),
                target_url="http://test-service:8000/api/test",
                method=HttpMethod.GET,
                headers={"Authorization": "Bearer token"}
            )
            
            response = await proxy_service.proxy_request(proxy_request)
            
            assert response.success is True
            assert response.status_code == 200
            assert response.body == b'{"success": true}'
            assert "Content-Type" in response.headers
    
    @pytest.mark.asyncio
    async def test_proxy_request_timeout(self, proxy_service):
        """Test request proxying with timeout."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            ProxyRequest, HttpMethod
        )
        
        with patch('aiohttp.ClientSession.request') as mock_request:
            # Mock timeout
            mock_request.side_effect = asyncio.TimeoutError()
            
            proxy_request = ProxyRequest(
                request_id=str(uuid.uuid4()),
                target_url="http://slow-service:8000/api/test",
                method=HttpMethod.GET,
                headers={},
                timeout_seconds=1.0
            )
            
            response = await proxy_service.proxy_request(proxy_request)
            
            assert response.success is False
            assert "timeout" in response.error_message.lower()
            assert response.status_code == 504

class TestAPIGatewayService:
    """Test main API Gateway service functionality."""
    
    @pytest.fixture
    def gateway_config(self):
        """Create gateway configuration for testing."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
        
        return APIGatewayConfig(
            service_name="test_api_gateway",
            host="0.0.0.0",
            port=8080,
            auth_service_url="http://localhost:8001",
            enable_rate_limiting=True,
            default_rate_limit_requests=1000,
            default_rate_limit_window_seconds=3600
        )
    
    @pytest.fixture
    def gateway_service(self, gateway_config):
        """Create API Gateway service for testing."""
        from tpm_job_finder_poc.api_gateway_service.service import APIGatewayService
        return APIGatewayService(gateway_config)
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, gateway_service):
        """Test service initialization."""
        await gateway_service.initialize()
        
        # Service should be initialized but not started
        assert gateway_service._initialized is True
        assert gateway_service._running is False
    
    @pytest.mark.asyncio
    async def test_service_lifecycle(self, gateway_service):
        """Test service start/stop lifecycle."""
        await gateway_service.initialize()
        await gateway_service.start()
        
        assert gateway_service._running is True
        
        await gateway_service.stop()
        assert gateway_service._running is False
    
    @pytest.mark.asyncio
    async def test_process_request_authenticated(self, gateway_service):
        """Test processing authenticated request."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RequestContext, HttpMethod, RouteDefinition
        )
        
        await gateway_service.initialize()
        
        # Register a test route
        route = RouteDefinition(
            route_id="test-route",
            path="/api/v1/test",
            method=HttpMethod.GET,
            target_service="test_service",
            target_path="/test",
            target_port=8000,
            requires_auth=True
        )
        await gateway_service._routing_service.register_route(route)
        
        # Mock authentication and proxy
        with patch.object(gateway_service._auth_integration, 'validate_token') as mock_auth, \
             patch.object(gateway_service._proxy_service, 'proxy_request') as mock_proxy:
            
            mock_auth.return_value = {"valid": True, "user_id": "user123"}
            mock_proxy.return_value = Mock(
                success=True,
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=b'{"result": "success"}',
                response_time_ms=50.0
            )
            
            context = RequestContext(
                request_id=str(uuid.uuid4()),
                method=HttpMethod.GET,
                path="/api/v1/test",
                headers={"Authorization": "Bearer valid_token"},
                query_params={},
                client_ip="192.168.1.100"
            )
            
            response = await gateway_service.process_request(context)
            
            assert response.success is True
            assert response.status_code == 200
            mock_auth.assert_called_once()
            mock_proxy.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_request_unauthenticated(self, gateway_service):
        """Test processing request without authentication."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RequestContext, HttpMethod, RouteDefinition
        )
        
        await gateway_service.initialize()
        
        # Register a route that requires auth
        route = RouteDefinition(
            route_id="protected-route",
            path="/api/v1/protected",
            method=HttpMethod.GET,
            target_service="test_service",
            target_path="/protected",
            target_port=8000,
            requires_auth=True
        )
        await gateway_service._routing_service.register_route(route)
        
        context = RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod.GET,
            path="/api/v1/protected",
            headers={},  # No Authorization header
            query_params={},
            client_ip="192.168.1.100"
        )
        
        response = await gateway_service.process_request(context)
        
        assert response.success is False
        assert response.status_code == 401
        assert "authentication" in response.error_message.lower()
    
    @pytest.mark.asyncio
    async def test_register_service_routes(self, gateway_service):
        """Test registering routes for a service."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
            RouteDefinition, HttpMethod
        )
        
        await gateway_service.initialize()
        
        routes = [
            RouteDefinition(
                route_id="job-list",
                path="/api/v1/jobs",
                method=HttpMethod.GET,
                target_service="job_service",
                target_path="/jobs",
                target_port=8002
            ),
            RouteDefinition(
                route_id="job-create",
                path="/api/v1/jobs",
                method=HttpMethod.POST,
                target_service="job_service",
                target_path="/jobs",
                target_port=8002
            )
        ]
        
        result = await gateway_service.register_service_routes("job_service", routes)
        assert result is True
        
        # Verify routes were registered
        all_routes = await gateway_service._routing_service.list_routes()
        assert len(all_routes) == 2

class TestAPIGatewayConfiguration:
    """Test API Gateway configuration management."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
        
        config = APIGatewayConfig()
        
        assert config.service_name == "api_gateway_service"
        assert config.port == 8080
        assert config.require_authentication is True
        assert config.enable_rate_limiting is True
        assert config.default_rate_limit_requests == 1000
        assert config.max_concurrent_requests == 1000
    
    def test_custom_configuration(self):
        """Test custom configuration values."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
        
        config = APIGatewayConfig(
            service_name="custom_gateway",
            port=9090,
            auth_service_url="http://auth:8001",
            enable_rate_limiting=False,
            max_concurrent_requests=500
        )
        
        assert config.service_name == "custom_gateway"
        assert config.port == 9090
        assert config.auth_service_url == "http://auth:8001"
        assert config.enable_rate_limiting is False
        assert config.max_concurrent_requests == 500

class TestAPIGatewayHealthAndMetrics:
    """Test health monitoring and metrics collection."""
    
    @pytest.fixture
    def gateway_service(self):
        """Create gateway service for health testing."""
        from tpm_job_finder_poc.api_gateway_service.service import APIGatewayService
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
        
        config = APIGatewayConfig()
        return APIGatewayService(config)
    
    @pytest.mark.asyncio
    async def test_health_check(self, gateway_service):
        """Test gateway health check."""
        await gateway_service.initialize()
        
        health = await gateway_service.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "service" in health
        assert "uptime_seconds" in health
        assert "version" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
    
    @pytest.mark.asyncio
    async def test_get_metrics(self, gateway_service):
        """Test metrics collection."""
        await gateway_service.initialize()
        
        metrics = await gateway_service.get_metrics()
        
        assert hasattr(metrics, 'total_requests')
        assert hasattr(metrics, 'successful_requests')
        assert hasattr(metrics, 'failed_requests')
        assert hasattr(metrics, 'rate_limited_requests')
        assert hasattr(metrics, 'average_response_time_ms')
        assert hasattr(metrics, 'active_routes')
        assert isinstance(metrics.total_requests, int)
        assert isinstance(metrics.average_response_time_ms, float)

class TestAPIGatewayAPI:
    """Test API Gateway REST API endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create FastAPI test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_health_endpoint(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
    
    def test_metrics_endpoint(self, api_client):
        """Test metrics endpoint."""
        response = api_client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
        metrics = data["metrics"]
        assert "total_requests" in metrics
        assert "successful_requests" in metrics
        assert "failed_requests" in metrics
    
    def test_routes_list_endpoint(self, api_client):
        """Test routes listing endpoint."""
        response = api_client.get("/routes")
        
        assert response.status_code == 200
        data = response.json()
        assert "routes" in data
        routes = data["routes"]
        assert isinstance(routes, list)
    
    def test_route_registration_endpoint(self, api_client):
        """Test route registration endpoint."""
        route_data = {
            "route_id": "test-route",
            "path": "/api/v1/test",
            "method": "GET",
            "target_service": "test_service",
            "target_path": "/test",
            "target_port": 8000
        }
        
        response = api_client.post("/routes", json=route_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

class TestAPIGatewaySecurity:
    """Test API Gateway security features."""
    
    @pytest.fixture
    def gateway_service(self):
        """Create gateway service for security testing."""
        from tpm_job_finder_poc.api_gateway_service.service import APIGatewayService
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
        
        config = APIGatewayConfig(
            enable_cors=True,
            cors_origins=["https://example.com"],
            max_request_size_bytes=1024
        )
        return APIGatewayService(config)
    
    @pytest.mark.asyncio
    async def test_cors_validation(self, gateway_service):
        """Test CORS policy enforcement."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import RequestContext, HttpMethod
        
        await gateway_service.initialize()
        
        # Valid origin
        context = RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod.OPTIONS,
            path="/api/v1/test",
            headers={"Origin": "https://example.com"},
            query_params={},
            client_ip="192.168.1.100"
        )
        
        result = await gateway_service._validate_cors(context)
        assert result is True
        
        # Invalid origin
        context.headers["Origin"] = "https://malicious.com"
        result = await gateway_service._validate_cors(context)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_request_size_validation(self, gateway_service):
        """Test request size limits."""
        from tpm_job_finder_poc.shared.contracts.api_gateway_service import RequestContext, HttpMethod
        
        await gateway_service.initialize()
        
        # Small request
        context = RequestContext(
            request_id=str(uuid.uuid4()),
            method=HttpMethod.POST,
            path="/api/v1/test",
            headers={"Content-Length": "500"},
            query_params={},
            client_ip="192.168.1.100"
        )
        
        result = await gateway_service._validate_request_size(context)
        assert result is True
        
        # Large request
        context.headers["Content-Length"] = "2048"
        result = await gateway_service._validate_request_size(context)
        assert result is False