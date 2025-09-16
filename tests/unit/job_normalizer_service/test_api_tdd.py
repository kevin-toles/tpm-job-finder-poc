"""TDD Test Suite for Job Normalizer Service API Endpoints

Tests for REST API endpoints, request/response validation, and HTTP behavior.
"""

import pytest
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import status

# API imports (will be implemented in GREEN phase)
from tpm_job_finder_poc.job_normalizer_service.api import app, get_service
from tpm_job_finder_poc.job_normalizer_service.service import JobNormalizerService
from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig

# Contract imports
from tpm_job_finder_poc.shared.contracts.job_normalizer_service import (
    NormalizationResult,
    NormalizationStatistics,
    JobNormalizationConfig
)


@pytest.fixture
def test_client():
    """Create test client for API testing."""
    # Clear any existing dependency overrides
    app.dependency_overrides = {}
    client = TestClient(app)
    yield client
    # Clean up after test
    app.dependency_overrides = {}


@pytest.fixture
def mock_service():
    """Create mock service for testing."""
    mock = AsyncMock(spec=JobNormalizerService)
    mock.is_running.return_value = True
    return mock


@pytest.fixture
def sample_raw_jobs():
    """Sample raw job data for testing."""
    return [
        {
            "id": "job1",
            "title": "Software Engineer",
            "company": "Tech Corp",
            "url": "https://example.com/job/1",
            "date_posted": datetime.now(timezone.utc).isoformat(),
            "location": "San Francisco, CA",
            "salary": "$100,000"
        },
        {
            "id": "job2",
            "title": "Product Manager",
            "company": "Product Corp",
            "url": "https://example.com/job/2",
            "date_posted": datetime.now(timezone.utc).isoformat(),
            "location": "New York, NY"
        }
    ]


class TestHealthEndpoint:
    """Test /health endpoint."""
    
    def test_health_check_success(self, test_client, mock_service):
        """Test health check returns 200 when service is healthy."""
        # Arrange
        mock_service.get_health_status.return_value = {
            "status": "healthy",
            "is_running": True,
            "uptime_seconds": 3600,
            "total_operations": 100,
            "error_rate": 0.01
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.get("/health")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert data["is_running"] is True
        assert "uptime_seconds" in data
    
    def test_health_check_service_not_running(self, test_client, mock_service):
        """Test health check returns 503 when service is not running."""
        # Arrange
        mock_service.is_running.return_value = False
        mock_service.get_health_status.return_value = {
            "status": "unhealthy",
            "is_running": False,
            "error": "Service stopped"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.get("/health")
        
        # Assert
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["is_running"] is False


class TestNormalizeJobsEndpoint:
    """Test /normalize-jobs endpoint."""
    
    def test_normalize_jobs_success(self, test_client, mock_service, sample_raw_jobs):
        """Test successful job normalization via API."""
        # Arrange
        expected_result = NormalizationResult(
            total_input_jobs=2,
            successful_normalizations=2,
            failed_normalizations=0,
            validation_errors=0,
            duplicates_removed=0,
            normalized_jobs=[],  # Simplified for test
            processing_time_seconds=1.5,
            jobs_per_second=1.33,
            validation_error_details=[],
            data_quality_score=0.95,
            completeness_score=0.90
        )
        mock_service.normalize_jobs.return_value = expected_result
        
        request_data = {
            "jobs": sample_raw_jobs,
            "source": "indeed",
            "config": {
                "enable_deduplication": True,
                "enable_field_normalization": True
            }
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/normalize-jobs", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_input_jobs"] == 2
        assert data["successful_normalizations"] == 2
        assert data["failed_normalizations"] == 0
        assert data["processing_time_seconds"] == 1.5
        
        # Verify service was called correctly
        mock_service.normalize_jobs.assert_called_once()
        call_args = mock_service.normalize_jobs.call_args
        assert call_args.kwargs["raw_jobs"] == sample_raw_jobs  # Keyword arg (jobs)
        assert call_args.kwargs["source"] == "indeed"  # Keyword arg (source)
        assert isinstance(call_args.kwargs["config"], JobNormalizationConfig)  # Keyword arg (config)
    
    def test_normalize_jobs_missing_required_fields(self, test_client, mock_service):
        """Test API validation for missing required fields."""
        # Arrange
        app.dependency_overrides[get_service] = lambda: mock_service
        
        invalid_request = {
            "jobs": []
            # Missing "source" field
        }
        
        # Act
        response = test_client.post("/normalize-jobs", json=invalid_request)
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert "detail" in data
        # Should contain validation error about missing "source" field
        assert any("source" in str(error) for error in data["detail"])
    
    def test_normalize_jobs_empty_jobs_list(self, test_client, mock_service):
        """Test API handles empty jobs list."""
        # Arrange
        expected_result = NormalizationResult(
            total_input_jobs=0,
            successful_normalizations=0,
            failed_normalizations=0,
            validation_errors=0,
            duplicates_removed=0,
            normalized_jobs=[],
            processing_time_seconds=0.1,
            jobs_per_second=0.0,
            validation_error_details=[],
            data_quality_score=1.0,
            completeness_score=1.0
        )
        mock_service.normalize_jobs.return_value = expected_result
        
        request_data = {
            "jobs": [],
            "source": "test"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/normalize-jobs", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_input_jobs"] == 0
    
    def test_normalize_jobs_service_not_started(self, test_client, mock_service):
        """Test API error when service is not started."""
        # Arrange
        from tpm_job_finder_poc.shared.contracts.job_normalizer_service import ServiceNotStartedError
        mock_service.normalize_jobs.side_effect = ServiceNotStartedError("Service not started")
        
        request_data = {
            "jobs": [{"id": "test", "title": "Test", "company": "Test", "url": "https://test.com", "date_posted": "2024-01-01T00:00:00Z"}],
            "source": "test"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/normalize-jobs", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert "Service not started" in data["detail"]
    
    def test_normalize_jobs_with_custom_config(self, test_client, mock_service):
        """Test API accepts custom normalization configuration."""
        # Arrange
        expected_result = NormalizationResult(
            total_input_jobs=1,
            successful_normalizations=1,
            failed_normalizations=0,
            validation_errors=0,
            duplicates_removed=0,
            normalized_jobs=[],
            processing_time_seconds=0.5,
            jobs_per_second=2.0,
            validation_error_details=[],
            data_quality_score=0.85,
            completeness_score=0.80
        )
        mock_service.normalize_jobs.return_value = expected_result
        
        request_data = {
            "jobs": [{
                "id": "test1",
                "title": "Engineer",
                "company": "Corp",
                "url": "https://example.com/1",
                "date_posted": datetime.now(timezone.utc).isoformat()
            }],
            "source": "custom",
            "config": {
                "enable_deduplication": False,
                "enable_field_normalization": True,
                "normalize_titles": False,
                "similarity_threshold": 0.95
            }
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/normalize-jobs", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        
        # Verify custom config was passed
        call_args = mock_service.normalize_jobs.call_args
        config = call_args.kwargs["config"]
        assert config.enable_deduplication is False
        assert config.normalize_titles is False
        assert config.similarity_threshold == 0.95


class TestValidateJobEndpoint:
    """Test /validate-job endpoint."""
    
    def test_validate_job_success(self, test_client, mock_service):
        """Test successful job validation via API."""
        # Arrange
        mock_service.validate_job.return_value = True
        
        request_data = {
            "job": {
                "id": "test123",
                "title": "Software Engineer",
                "company": "Tech Corp",
                "url": "https://example.com/job/123",
                "date_posted": datetime.now(timezone.utc).isoformat()
            },
            "source": "indeed"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/validate-job", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_valid"] is True
        assert "validation_errors" in data
    
    def test_validate_job_failure(self, test_client, mock_service):
        """Test job validation failure via API."""
        # Arrange
        mock_service.validate_job.return_value = False
        
        request_data = {
            "job": {
                "title": "Incomplete Job"
                # Missing required fields
            },
            "source": "test"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/validate-job", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_valid"] is False


class TestStatisticsEndpoint:
    """Test /statistics endpoint."""
    
    def test_get_statistics_success(self, test_client, mock_service):
        """Test successful statistics retrieval via API."""
        # Arrange
        expected_stats = NormalizationStatistics(
            total_jobs_processed=150,
            total_successful_normalizations=145,
            total_failed_normalizations=5,
            total_duplicates_removed=20,
            total_validation_errors=3,
            average_processing_time=1.2,
            average_throughput=83.33,
            peak_throughput=120.0,
            average_data_quality_score=0.92,
            average_completeness_score=0.88,
            jobs_by_source={"indeed": 100, "linkedin": 50},
            errors_by_source={"indeed": 2, "linkedin": 1},
            normalized_fields_count={"title": 145, "salary": 130},
            validation_errors_by_field={"salary": 2, "location": 1},
            first_processing_time=datetime.now(timezone.utc),
            last_processing_time=datetime.now(timezone.utc)
        )
        mock_service.get_statistics.return_value = expected_stats
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.get("/statistics")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_jobs_processed"] == 150
        assert data["total_successful_normalizations"] == 145
        assert data["jobs_by_source"]["indeed"] == 100
        assert data["average_processing_time"] == 1.2
    
    def test_reset_statistics_success(self, test_client, mock_service):
        """Test successful statistics reset via API."""
        # Arrange
        mock_service.reset_statistics.return_value = None
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/statistics/reset")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Statistics reset successfully"
        mock_service.reset_statistics.assert_called_once()


class TestServiceManagementEndpoints:
    """Test service lifecycle management endpoints."""
    
    def test_start_service_success(self, test_client, mock_service):
        """Test successful service start via API."""
        # Arrange
        mock_service.start.return_value = None
        mock_service.is_running.return_value = True
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/service/start")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Service started successfully"
        assert data["is_running"] is True
        mock_service.start.assert_called_once()
    
    def test_stop_service_success(self, test_client, mock_service):
        """Test successful service stop via API."""
        # Arrange
        mock_service.stop.return_value = None
        mock_service.is_running.return_value = False
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/service/stop")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Service stopped successfully"
        assert data["is_running"] is False
        mock_service.stop.assert_called_once()


class TestErrorHandling:
    """Test API error handling scenarios."""
    
    def test_internal_server_error_handling(self, test_client, mock_service):
        """Test API handles internal service errors."""
        # Arrange
        mock_service.normalize_jobs.side_effect = Exception("Internal service error")
        
        request_data = {
            "jobs": [{"id": "test", "title": "Test", "company": "Test", "url": "https://test.com", "date_posted": "2024-01-01T00:00:00Z"}],
            "source": "test"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/normalize-jobs", json=request_data)
        
        # Assert
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        data = response.json()
        assert "Internal service error" in data["detail"]
    
    def test_invalid_json_request(self, test_client):
        """Test API handles invalid JSON requests."""
        # Act
        response = test_client.post(
            "/normalize-jobs",
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Assert
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_large_payload_handling(self, test_client, mock_service):
        """Test API handles large payloads appropriately."""
        # Arrange - create large job list
        large_job_list = []
        for i in range(1500):  # Exceeds default max_batch_size of 1000
            large_job_list.append({
                "id": f"job{i}",
                "title": f"Engineer {i}",
                "company": f"Corp {i}",
                "url": f"https://example.com/job/{i}",
                "date_posted": datetime.now(timezone.utc).isoformat()
            })
        
        request_data = {
            "jobs": large_job_list,
            "source": "test"
        }
        
        app.dependency_overrides[get_service] = lambda: mock_service
        
        # Act
        response = test_client.post("/normalize-jobs", json=request_data)
        
        # Assert
        # Should either reject with 413 or accept and handle appropriately
        assert response.status_code in [status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, status.HTTP_200_OK]


class TestAPIDocumentation:
    """Test API documentation and schema generation."""
    
    def test_openapi_schema_generation(self, test_client):
        """Test that OpenAPI schema is generated correctly."""
        # Act
        response = test_client.get("/openapi.json")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
        
        # Verify key endpoints are documented
        paths = schema["paths"]
        assert "/health" in paths
        assert "/normalize-jobs" in paths
        assert "/validate-job" in paths
        assert "/statistics" in paths
    
    def test_docs_endpoint_accessible(self, test_client):
        """Test that API documentation endpoint is accessible."""
        # Act
        response = test_client.get("/docs")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]