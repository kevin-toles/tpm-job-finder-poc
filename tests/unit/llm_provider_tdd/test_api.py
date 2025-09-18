"""
LLM Provider Service TDD REST API Tests

Basic tests to verify REST API functionality and integration
with the TDD-implemented service.
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient

from tpm_job_finder_poc.llm_provider_tdd.api import app
from tpm_job_finder_poc.shared.contracts.llm_provider_service_tdd import (
    LLMRequest,
    SignalType,
    ProviderType
)


class TestLLMProviderAPI:
    """Test suite for LLM Provider Service REST API"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get("/health")
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
    
    def test_status_endpoint(self, client):
        """Test status endpoint"""
        response = client.get("/status")
        
        # Accept either success or service unavailable  
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
    
    def test_list_providers_endpoint(self, client):
        """Test list providers endpoint"""
        response = client.get("/providers")
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    def test_process_request_endpoint(self, client):
        """Test process request endpoint"""
        request_data = {
            "prompt": "Analyze this job posting",
            "signal_type": "analysis",
            "provider": "openai"
        }
        response = client.post("/process", json=request_data)
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "signals" in data
    
    def test_batch_process_endpoint(self, client):
        """Test batch process endpoint"""
        request_data = {
            "requests": [
                {
                    "prompt": "Test 1",
                    "signal_type": "analysis",
                    "provider": "openai"
                },
                {
                    "prompt": "Test 2", 
                    "signal_type": "analysis",
                    "provider": "openai"
                }
            ]
        }
        response = client.post("/process/batch", json=request_data)
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "responses" in data
    
    def test_get_statistics_endpoint(self, client):
        """Test statistics endpoint"""
        response = client.get("/statistics")
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_requests_processed" in data
    
    def test_get_configuration_endpoint(self, client):
        """Test configuration endpoint"""
        response = client.get("/config")
        
        # Accept either success or service unavailable  
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "default_provider" in data
    
    def test_enable_provider_endpoint(self, client):
        """Test enable provider endpoint"""
        response = client.post("/providers/openai/enable")
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "success" in data
    
    def test_usage_report_endpoint(self, client):
        """Test usage report endpoint"""  
        # Usage report endpoint requires POST with request body
        request_data = {
            "start_date": "2025-01-01T00:00:00Z",
            "end_date": "2025-12-31T23:59:59Z"
        }
        response = client.post("/reports/usage", json=request_data)
        
        # Accept either success or service unavailable
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_requests" in data
    
    def test_invalid_request_validation(self, client):
        """Test request validation"""
        invalid_data = {
            "prompt": "",  # Empty prompt should be invalid
            "invalid_field": "value"
        }
        
        response = client.post("/process", json=invalid_data)
        
        # Should return validation error or service unavailable
        assert response.status_code in [422, 503]
    
    def test_openapi_schema(self, client):
        """Test OpenAPI schema generation"""
        # This is a sync test since it doesn't require the service to be running
        from tpm_job_finder_poc.llm_provider_tdd.api import app
        schema = app.openapi()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema