"""
TDD Unit tests for API Gateway API endpoints.

Tests the FastAPI application layer including:
- Health check endpoints
- Metrics collection endpoints  
- Route management endpoints
- Gateway request processing endpoints
- Service discovery endpoints
- Admin configuration endpoints
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json
import uuid
import aiohttp
from aiohttp import ClientResponse
from io import BytesIO


class MockResponse:
    """Mock aiohttp response for testing."""
    def __init__(self, status=200, json_data=None, text_data=None, headers=None):
        self.status = status
        self._json_data = json_data or {}
        self._text_data = text_data or ""
        self.headers = headers or {}
        
    async def json(self):
        return self._json_data
        
    async def text(self):
        return self._text_data
        
    async def read(self):
        if self._text_data:
            return self._text_data.encode('utf-8')
        return json.dumps(self._json_data).encode('utf-8')
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

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
        loop.run_until_complete(service.start())
        yield
        # Cleanup
        loop.run_until_complete(service.stop())
    finally:
        loop.close()
        # Reset globals
        api_module.gateway_service = None
        api_module.config_manager = None

class TestAPIGatewayHealthAPI:
    """Test health check API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_health_check_endpoint(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_health_check_detailed(self, client):
        """Test detailed health check endpoint."""
        response = client.get("/health?detailed=true")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "details" in data
    
    def test_readiness_check(self, client):
        """Test readiness check endpoint."""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert "ready" in data


class TestAPIGatewayMetricsAPI:
    """Test metrics API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_metrics_endpoint(self, client):
        """Test metrics collection endpoint."""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "metrics" in data
    
    def test_prometheus_metrics(self, client):
        """Test Prometheus format metrics."""
        response = client.get("/metrics/prometheus")
        
        assert response.status_code == 200
        # Prometheus metrics should be plain text
        assert "text/plain" in response.headers.get("content-type", "")


class TestAPIGatewayRoutesAPI:
    """Test route management API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_list_routes(self, client):
        """Test listing routes."""
        response = client.get("/routes")
        
        assert response.status_code == 200
        data = response.json()
        assert "routes" in data
        assert isinstance(data["routes"], list)
    
    def test_register_route(self, client):
        """Test registering a new route."""
        route_data = {
            "route_id": "test-route",
            "path": "/api/v1/test",
            "target_service": "test-service",
            "target_path": "/",
            "target_port": 3000,
            "method": "GET",
            "enabled": True
        }
        
        response = client.post("/routes", json=route_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "route_id" in data
    
    def test_register_route_validation_error(self, client):
        """Test route registration with invalid data."""
        invalid_route_data = {
            "path": "",  # Invalid empty path
            "target_url": "invalid-url",  # Invalid URL
            "method": "INVALID"  # Invalid method
        }
        
        response = client.post("/routes", json=invalid_route_data)
        
        assert response.status_code == 422
    
    def test_get_route(self, client):
        """Test getting a specific route."""
        # First register a route
        route_data = {
            "route_id": "get-test-route",
            "path": "/api/v1/gettest",
            "target_service": "test-service",
            "target_path": "/", 
            "target_port": 3000,
            "method": "GET"
        }
        
        register_response = client.post("/routes", json=route_data)
        assert register_response.status_code == 201
        route_id = register_response.json()["route_id"]
        
        # Then get it
        response = client.get(f"/routes/{route_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["route"]["path"] == "/api/v1/gettest"
    
    def test_get_route_not_found(self, client):
        """Test getting non-existent route."""
        response = client.get("/routes/nonexistent")
        
        assert response.status_code == 404
    
    def test_update_route(self, client):
        """Test updating a route."""
        # First register a route
        route_data = {
            "route_id": "update-test-route",
            "path": "/api/v1/updatetest",
            "target_service": "test-service",
            "target_path": "/",
            "target_port": 3000,
            "method": "GET"
        }
        
        register_response = client.post("/routes", json=route_data)
        assert register_response.status_code == 201
        route_id = register_response.json()["route_id"]
        
        # Update it
        update_data = {
            "target_url": "http://localhost:4000",
            "enabled": False
        }
        
        response = client.put(f"/routes/{route_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_delete_route(self, client):
        """Test deleting a route."""
        # First register a route
        route_data = {
            "route_id": "delete-test-route",
            "path": "/api/v1/deletetest",
            "target_service": "test-service",
            "target_path": "/",
            "target_port": 3000,
            "method": "GET"
        }
        
        register_response = client.post("/routes", json=route_data)
        assert register_response.status_code == 201
        route_id = register_response.json()["route_id"]
        
        # Delete it
        response = client.delete(f"/routes/{route_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAPIGatewayRequestProcessingAPI:
    """Test API Gateway request processing endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    @pytest.fixture
    def mock_proxy_service(self):
        """Mock proxy service to avoid real HTTP calls."""
        with patch('tpm_job_finder_poc.api_gateway_service.service.ProxyService.proxy_request') as mock_proxy:
            # Create a mock ProxyResponse
            from tpm_job_finder_poc.shared.contracts.api_gateway_service import ProxyResponse
            
            mock_response = ProxyResponse(
                request_id="test-request-123",
                success=True,
                status_code=200,
                headers={"Content-Type": "application/json"},
                body=b'{"success": true, "service": "httpbin", "path": "/get"}',
                response_time_ms=150.0,
                error_message=None
            )
            
            mock_proxy.return_value = mock_response
            yield mock_proxy
    
    def test_process_gateway_request(self, client, mock_proxy_service):
        """Test processing a request through the gateway."""
        # First register a route for testing
        route_data = {
            "route_id": "process-test-route",
            "path": "/api/v1/processtest",
            "target_service": "httpbin",
            "target_path": "/get",
            "target_port": 80,
            "method": "GET",
            "requires_auth": False
        }
        
        register_response = client.post("/routes", json=route_data)
        assert register_response.status_code == 201
            
        # Make request through gateway
        response = client.get("/api/v1/processtest")
        
        assert response.status_code == 200
    
    def test_process_request_route_not_found(self, client):
        """Test processing request for non-existent route."""
        response = client.get("/api/v1/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "route not found" in data["detail"].lower()
    
    def test_process_request_method_not_allowed(self, client):
        """Test processing request with wrong HTTP method."""
        # Register GET route
        route_data = {
            "route_id": "method-test-route",
            "path": "/api/v1/getonly",
            "target_service": "test-service",
            "target_path": "/get",
            "target_port": 80,
            "method": "GET"
        }
        
        register_response = client.post("/routes", json=route_data)
        assert register_response.status_code == 201
        
        # Try POST on GET-only route
        response = client.post("/api/v1/getonly", json={"test": "data"})
        
        assert response.status_code == 405


class TestAPIGatewayRateLimitAPI:
    """Test rate limiting API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_create_rate_limit_rule(self, client):
        """Test creating a rate limit rule."""
        rule_data = {
            "rule_id": "test-rule",
            "scope": "IP_ADDRESS", 
            "scope_value": "192.168.1.100",
            "requests_per_window": 100,
            "window_seconds": 3600
        }
        
        response = client.post("/rate-limits", json=rule_data)
        
        # Debug output
        if response.status_code != 201:
            print(f"Error response: {response.status_code} - {response.text}")
            
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
    
    def test_list_rate_limit_rules(self, client):
        """Test listing rate limit rules."""
        response = client.get("/rate-limits")
        
        assert response.status_code == 200
        data = response.json()
        assert "rules" in data
        assert isinstance(data["rules"], list)
    
    def test_get_rate_limit_status(self, client):
        """Test getting rate limit status."""
        response = client.get("/rate-limits/status?scope=IP_ADDRESS&scope_value=192.168.1.1")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


class TestAPIGatewayServiceDiscoveryAPI:
    """Test service discovery API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_register_service(self, client):
        """Test registering a service."""
        service_data = {
            "service_name": "test-service",
            "host": "localhost",
            "port": 3000,
            "health_check_path": "/health"
        }
        
        response = client.post("/services", json=service_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
    
    def test_list_services(self, client):
        """Test listing registered services."""
        response = client.get("/services")
        
        assert response.status_code == 200
        data = response.json()
        assert "services" in data
        assert isinstance(data["services"], list)
    
    def test_service_health_check(self, client):
        """Test service health check."""
        response = client.get("/services/test-service/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "healthy" in data


class TestAPIGatewayAdminAPI:
    """Test admin configuration API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_reload_configuration(self, client):
        """Test reloading configuration."""
        response = client.post("/admin/reload-config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_get_configuration(self, client):
        """Test getting current configuration."""
        response = client.get("/admin/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "config" in data
    
    def test_update_configuration(self, client):
        """Test updating configuration."""
        config_updates = {
            "enable_rate_limiting": False,
            "default_rate_limit_requests": 2000
        }
        
        response = client.put("/admin/config", json=config_updates)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_reset_metrics(self, client):
        """Test resetting metrics."""
        response = client.post("/admin/reset-metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAPIGatewayMiddleware:
    """Test API Gateway middleware functionality."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_cors_middleware(self, client):
        """Test CORS middleware."""
        response = client.options("/health", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_request_id_middleware(self, client):
        """Test request ID middleware."""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "x-request-id" in response.headers
    
    def test_rate_limiting_middleware(self, client):
        """Test rate limiting middleware."""
        # Make multiple requests to test rate limiting
        responses = []
        for _ in range(5):
            response = client.get("/health")
            responses.append(response.status_code)
        
        # All should succeed (under normal rate limits)
        assert all(status == 200 for status in responses)
    
    def test_metrics_collection_middleware(self, client):
        """Test metrics collection middleware."""
        # Make a request
        client.get("/health")
        
        # Check metrics
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["metrics"]["total_requests"] > 0


class TestAPIGatewayErrorHandling:
    """Test API error handling."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from tpm_job_finder_poc.api_gateway_service.api import app
        return TestClient(app)
    
    def test_invalid_json_error(self, client):
        """Test handling of invalid JSON."""
        response = client.post("/routes", data="invalid json", headers={"Content-Type": "application/json"})
        
        assert response.status_code == 422
    
    def test_missing_fields_error(self, client):
        """Test handling of missing required fields."""
        response = client.post("/routes", json={})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @patch('tpm_job_finder_poc.api_gateway_service.api.gateway_service')
    def test_internal_server_error(self, mock_service, client):
        """Test handling of internal server errors."""
        mock_service.health_check.side_effect = Exception("Test error")
        
        response = client.get("/health?detailed=true")
        
        assert response.status_code == 500
        data = response.json()
        assert "internal server error" in data["detail"].lower()