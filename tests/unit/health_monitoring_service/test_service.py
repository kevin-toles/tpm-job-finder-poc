"""
TDD Unit Tests for Health Monitoring Service

Following TDD methodology: RED → GREEN → REFACTOR
These tests define the requirements for the health monitoring microservice.
"""
import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, AsyncMock, patch
from dataclasses import dataclass

# Import types we'll need for the service contract
from tpm_job_finder_poc.shared.contracts.error_handler import HealthStatus, PerformanceMetrics, AlertStatus


class TestHealthMonitoringServiceInterface:
    """Test the health monitoring service interface contract."""
    
    def test_interface_exists(self):
        """Test that the health monitoring service interface exists."""
        # RED: This should fail initially
        from tpm_job_finder_poc.shared.contracts.health_monitoring_service import IHealthMonitoringService
        
        # Interface should exist
        assert IHealthMonitoringService is not None
        
        # Interface should have required methods
        assert hasattr(IHealthMonitoringService, 'check_system_health')
        assert hasattr(IHealthMonitoringService, 'check_service_health') 
        assert hasattr(IHealthMonitoringService, 'register_service')
        assert hasattr(IHealthMonitoringService, 'unregister_service')
        assert hasattr(IHealthMonitoringService, 'get_health_summary')
        assert hasattr(IHealthMonitoringService, 'get_service_metrics')
        assert hasattr(IHealthMonitoringService, 'set_alert_thresholds')
        assert hasattr(IHealthMonitoringService, 'get_alert_status')
    
    def test_interface_has_monitoring_methods(self):
        """Test that interface has comprehensive monitoring methods."""
        from tpm_job_finder_poc.shared.contracts.health_monitoring_service import IHealthMonitoringService
        
        # Service lifecycle methods
        assert hasattr(IHealthMonitoringService, 'start_monitoring')
        assert hasattr(IHealthMonitoringService, 'stop_monitoring')
        assert hasattr(IHealthMonitoringService, 'is_monitoring_active')
        
        # Metrics and reporting methods
        assert hasattr(IHealthMonitoringService, 'collect_metrics')
        assert hasattr(IHealthMonitoringService, 'get_historical_data')
        assert hasattr(IHealthMonitoringService, 'export_health_report')
        
        # Configuration methods
        assert hasattr(IHealthMonitoringService, 'update_configuration')
        assert hasattr(IHealthMonitoringService, 'get_configuration')


@pytest.mark.asyncio
class TestHealthMonitoringServiceImplementation:
    """Test the health monitoring service implementation."""
    
    @pytest.fixture
    def health_service_config(self):
        """Create test configuration for health monitoring service."""
        from tpm_job_finder_poc.health_monitoring_service.config import HealthMonitoringConfig
        
        return HealthMonitoringConfig(
            check_interval_seconds=30,
            alert_threshold_error_rate=0.05,
            alert_threshold_response_time_ms=5000,
            retention_days=7,
            enable_metrics_collection=True,
            enable_alerting=True,
            services_to_monitor=[
                "audit_service",
                "job_collection_service", 
                "storage_service",
                "llm_gateway_service"
            ]
        )
    
    @pytest.fixture
    def health_service(self, health_service_config):
        """Create health monitoring service instance for testing."""
        from tpm_job_finder_poc.health_monitoring_service.service import HealthMonitoringService
        
        service = HealthMonitoringService(health_service_config)
        return service
    
    async def test_service_initialization(self, health_service_config):
        """Test health monitoring service initialization."""
        from tpm_job_finder_poc.health_monitoring_service.service import HealthMonitoringService
        
        # Should initialize successfully
        service = HealthMonitoringService(health_service_config)
        assert service is not None
        assert service.config == health_service_config
        assert not service.is_monitoring_active()
    
    async def test_service_start_stop_monitoring(self, health_service):
        """Test starting and stopping monitoring."""
        # Initially not monitoring
        assert not health_service.is_monitoring_active()
        
        # Start monitoring
        await health_service.start_monitoring()
        assert health_service.is_monitoring_active()
        
        # Stop monitoring  
        await health_service.stop_monitoring()
        assert not health_service.is_monitoring_active()
    
    async def test_register_unregister_service(self, health_service):
        """Test registering and unregistering services for monitoring."""
        service_config = {
            "name": "test_service",
            "health_endpoint": "http://localhost:8080/health",
            "check_interval": 60,
            "timeout_ms": 5000
        }
        
        # Register service
        result = await health_service.register_service("test_service", service_config)
        assert result.success
        
        # Service should be registered
        services = await health_service.get_registered_services()
        assert "test_service" in services
        
        # Unregister service
        result = await health_service.unregister_service("test_service")
        assert result.success
        
        # Service should be removed
        services = await health_service.get_registered_services()
        assert "test_service" not in services
    
    async def test_check_system_health(self, health_service):
        """Test comprehensive system health check."""
        await health_service.start_monitoring()
        
        try:
            health_status = await health_service.check_system_health()
            
            # Should return comprehensive health status
            assert health_status is not None
            assert hasattr(health_status, 'overall_status')
            assert hasattr(health_status, 'services')
            assert hasattr(health_status, 'dependencies')
            assert hasattr(health_status, 'timestamp')
            
            # Overall status should be valid
            assert health_status.overall_status.value in ["healthy", "degraded", "unhealthy", "unknown"]
            
            # Should include service health details
            assert isinstance(health_status.services, dict)
            
            # Should include dependency health
            assert isinstance(health_status.dependencies, dict)
            
        finally:
            await health_service.stop_monitoring()
    
    async def test_check_individual_service_health(self, health_service):
        """Test checking individual service health."""
        # Register a service
        service_config = {
            "name": "test_service",
            "health_endpoint": "http://localhost:8080/health",
            "check_interval": 60,
            "timeout_ms": 5000
        }
        await health_service.register_service("test_service", service_config)
        
        # Mock HTTP response for health check
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            health_result = await health_service.check_service_health("test_service")
            
            assert health_result is not None
            assert hasattr(health_result, 'service_name')
            assert hasattr(health_result, 'status')
            assert hasattr(health_result, 'response_time_ms')
            assert hasattr(health_result, 'last_check')
            
            assert health_result.service_name == "test_service"
            assert health_result.status.value in ["healthy", "degraded", "unhealthy", "unknown"]
    
    async def test_get_health_summary(self, health_service):
        """Test getting overall health summary."""
        await health_service.start_monitoring()
        
        try:
            summary = await health_service.get_health_summary()
            
            # Should return comprehensive summary
            assert summary is not None
            assert "overall_status" in summary
            assert "total_services" in summary
            assert "healthy_services" in summary
            assert "unhealthy_services" in summary
            assert "degraded_services" in summary
            assert "unknown_services" in summary
            assert "system_metrics" in summary
            assert "last_updated" in summary
            
            # Counts should be consistent
            total = summary["total_services"]
            healthy = summary["healthy_services"]
            unhealthy = summary["unhealthy_services"]
            degraded = summary["degraded_services"]
            unknown = summary["unknown_services"]
            
            assert healthy + unhealthy + degraded + unknown == total
            
        finally:
            await health_service.stop_monitoring()
    
    async def test_collect_and_retrieve_metrics(self, health_service):
        """Test metrics collection and retrieval."""
        await health_service.start_monitoring()
        
        try:
            # Collect metrics
            await health_service.collect_metrics()
            
            # Get service metrics
            metrics = await health_service.get_service_metrics("system")
            
            assert metrics is not None
            assert "timestamp" in metrics
            assert "cpu_usage_percent" in metrics
            assert "memory_usage_mb" in metrics
            assert "disk_usage_percent" in metrics
            assert "network_connections" in metrics
            assert "uptime_seconds" in metrics
            
            # Values should be reasonable
            assert 0 <= metrics["cpu_usage_percent"] <= 100
            assert metrics["memory_usage_mb"] > 0
            assert 0 <= metrics["disk_usage_percent"] <= 100
            assert metrics["uptime_seconds"] >= 0
            
        finally:
            await health_service.stop_monitoring()
    
    async def test_alert_threshold_management(self, health_service):
        """Test setting and getting alert thresholds."""
        thresholds = {
            "error_rate": 0.05,
            "response_time_ms": 5000,
            "cpu_usage_percent": 80,
            "memory_usage_percent": 85,
            "disk_usage_percent": 90
        }
        
        # Set alert thresholds
        result = await health_service.set_alert_thresholds("test_service", thresholds)
        assert result.success
        
        # Get alert thresholds
        stored_thresholds = await health_service.get_alert_thresholds("test_service")
        assert stored_thresholds == thresholds
    
    async def test_alert_status_monitoring(self, health_service):
        """Test alert status monitoring and triggering."""
        # Set conservative thresholds
        thresholds = {
            "error_rate": 0.01,  # 1% error rate threshold
            "response_time_ms": 100  # 100ms response time threshold
        }
        await health_service.set_alert_thresholds("test_service", thresholds)
        
        # Simulate service with high error rate
        with patch.object(health_service, '_calculate_error_rate') as mock_error_rate:
            mock_error_rate.return_value = 0.05  # 5% error rate (above threshold)
            
            alert_status = await health_service.get_alert_status("test_service")
            
            assert alert_status is not None
            assert hasattr(alert_status, 'threshold_exceeded')
            assert hasattr(alert_status, 'alert_type')
            assert hasattr(alert_status, 'current_value')
            assert hasattr(alert_status, 'threshold_value')
            
            # Should detect threshold exceeded
            assert alert_status.threshold_exceeded
            assert alert_status.alert_type == "error_rate"
    
    async def test_historical_data_retention(self, health_service):
        """Test historical data collection and retention."""
        await health_service.start_monitoring()
        
        try:
            # Collect some historical data
            await health_service.collect_metrics()
            await asyncio.sleep(0.1)  # Small delay
            await health_service.collect_metrics()
            
            # Get historical data
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=1)
            
            historical_data = await health_service.get_historical_data(
                service_name="system",
                start_time=start_time,
                end_time=end_time
            )
            
            assert historical_data is not None
            assert isinstance(historical_data, list)
            assert len(historical_data) >= 1
            
            # Each entry should have timestamp and metrics
            for entry in historical_data:
                assert "timestamp" in entry
                assert "metrics" in entry
                
        finally:
            await health_service.stop_monitoring()
    
    async def test_health_report_export(self, health_service):
        """Test exporting comprehensive health reports."""
        await health_service.start_monitoring()
        
        try:
            # Generate health report
            report = await health_service.export_health_report(
                include_historical=True,
                format="json"
            )
            
            assert report is not None
            assert "report_metadata" in report
            assert "system_overview" in report
            assert "service_details" in report
            assert "metrics_summary" in report
            assert "alert_summary" in report
            
            # Report metadata should include generation info
            metadata = report["report_metadata"]
            assert "generated_at" in metadata
            assert "report_version" in metadata
            assert "services_monitored" in metadata
            
        finally:
            await health_service.stop_monitoring()
    
    async def test_configuration_management(self, health_service):
        """Test configuration updates and retrieval."""
        # Get current configuration
        current_config = await health_service.get_configuration()
        assert current_config is not None
        
        # Update configuration
        new_config = {
            "check_interval_seconds": 60,
            "alert_threshold_error_rate": 0.03,
            "enable_detailed_logging": True
        }
        
        result = await health_service.update_configuration(new_config)
        assert result.success
        
        # Verify configuration was updated
        updated_config = await health_service.get_configuration()
        assert updated_config["check_interval_seconds"] == 60
        assert updated_config["alert_threshold_error_rate"] == 0.03
        assert updated_config["enable_detailed_logging"] is True
    
    async def test_dependency_health_checks(self, health_service):
        """Test health checks for external dependencies."""
        dependencies = {
            "database": {
                "type": "database", 
                "connection_string": "postgresql://localhost:5432/test",
                "timeout_ms": 1000
            },
            "redis_cache": {
                "type": "redis",
                "connection_string": "redis://localhost:6379",
                "timeout_ms": 500
            },
            "file_system": {
                "type": "filesystem",
                "paths": ["/tmp", "/var/log"],
                "check_writable": True
            }
        }
        
        # Register dependencies
        for name, config in dependencies.items():
            result = await health_service.register_dependency(name, config)
            assert result.success
        
        # Check dependency health
        dependency_health = await health_service.check_dependency_health()
        
        assert dependency_health is not None
        assert isinstance(dependency_health, dict)
        
        for dep_name in dependencies.keys():
            assert dep_name in dependency_health
            dep_status = dependency_health[dep_name]
            assert hasattr(dep_status, 'status')
            assert hasattr(dep_status, 'response_time_ms')
            assert hasattr(dep_status, 'last_check')
            assert dep_status.status.value in ["healthy", "degraded", "unhealthy", "unknown"]
    
    async def test_concurrent_health_checks(self, health_service):
        """Test concurrent health checks for multiple services."""
        # Register multiple services
        services = {
            "service_1": {"health_endpoint": "http://localhost:8001/health"},
            "service_2": {"health_endpoint": "http://localhost:8002/health"},
            "service_3": {"health_endpoint": "http://localhost:8003/health"}
        }
        
        for name, config in services.items():
            await health_service.register_service(name, config)
        
        # Mock successful responses for all services
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Check all services concurrently
            start_time = datetime.now()
            health_results = await health_service.check_all_services_health()
            end_time = datetime.now()
            
            # Should complete quickly due to concurrency
            execution_time = (end_time - start_time).total_seconds()
            assert execution_time < 5.0  # Should be much faster than sequential
            
            # Should have results for all services
            assert len(health_results) == len(services)
            for service_name in services.keys():
                assert service_name in health_results
                assert health_results[service_name].status.value == "healthy"
    
    async def test_error_handling_and_resilience(self, health_service):
        """Test error handling and service resilience."""
        # Register service with invalid endpoint
        await health_service.register_service("invalid_service", {
            "health_endpoint": "http://invalid-host:9999/health",
            "timeout_ms": 1000
        })
        
        # Health check should handle errors gracefully
        health_result = await health_service.check_service_health("invalid_service")
        
        assert health_result is not None
        assert health_result.status.value == "unhealthy"
        assert health_result.error_message is not None
        assert "connection" in health_result.error_message.lower() or "timeout" in health_result.error_message.lower() or "connect" in health_result.error_message.lower()
    
    async def test_performance_metrics_calculation(self, health_service):
        """Test performance metrics calculation and aggregation."""
        await health_service.start_monitoring()
        
        try:
            # Simulate some metrics collection
            await health_service.collect_metrics()
            await asyncio.sleep(0.1)
            await health_service.collect_metrics()
            
            # Get performance metrics
            performance = await health_service.get_performance_metrics("system")
            
            assert performance is not None
            assert hasattr(performance, 'average_processing_time_ms')
            assert hasattr(performance, 'throughput_per_second')
            assert hasattr(performance, 'memory_usage_trend')
            assert hasattr(performance, 'cpu_usage_percent')
            
            # Values should be reasonable
            assert performance.average_processing_time_ms >= 0
            assert performance.throughput_per_second >= 0
            assert 0 <= performance.cpu_usage_percent <= 100
            
        finally:
            await health_service.stop_monitoring()


class TestHealthMonitoringServiceIntegration:
    """Test integration scenarios for health monitoring service."""
    
    @pytest.mark.asyncio
    async def test_integration_with_audit_service(self, health_service):
        """Test integration with audit service for logging health events."""
        # This would test integration with the audit service
        # For now, we'll test the interface exists
        assert hasattr(health_service, 'log_health_event')
        
        # Log a health event
        await health_service.log_health_event(
            event_type="service_unhealthy",
            service_name="test_service",
            details={"error": "Connection timeout"}
        )
    
    @pytest.mark.asyncio 
    async def test_integration_with_config_service(self, health_service):
        """Test integration with configuration service."""
        # Test that service can update configuration dynamically
        assert hasattr(health_service, 'reload_configuration')
        
        # Reload configuration
        result = await health_service.reload_configuration()
        assert result.success
    
    @pytest.mark.asyncio
    async def test_integration_with_notification_system(self, health_service):
        """Test integration with notification/alerting system."""
        # Test that service can send alerts
        assert hasattr(health_service, 'send_alert')
        
        # Send test alert
        alert_data = {
            "severity": "critical",
            "service": "test_service", 
            "message": "Service is down",
            "threshold_exceeded": "error_rate"
        }
        
        result = await health_service.send_alert(alert_data)
        assert result.success


class TestHealthMonitoringServiceAPI:
    """Test HTTP API endpoints for health monitoring service."""
    
    @pytest.fixture
    def api_client(self):
        """Create FastAPI test client for health monitoring service."""
        from tpm_job_finder_poc.health_monitoring_service.api import app
        from tpm_job_finder_poc.health_monitoring_service.service import HealthMonitoringService
        from tpm_job_finder_poc.health_monitoring_service.config import HealthMonitoringConfig
        from fastapi.testclient import TestClient
        
        # Initialize service for testing
        config = HealthMonitoringConfig(check_interval_seconds=10, concurrent_checks=2)
        service = HealthMonitoringService(config)
        
        # Override the global health_service in the API module
        import tpm_job_finder_poc.health_monitoring_service.api as api_module
        api_module.health_service = service
        
        return TestClient(app)
    
    def test_health_endpoint(self, api_client):
        """Test /health endpoint."""
        response = api_client.get("/health/detailed")
        assert response.status_code == 200
        
        data = response.json()
        assert "overall_status" in data
        assert "total_services" in data
        assert "healthy_services" in data
        assert "last_updated" in data
    
    def test_status_endpoint(self, api_client):
        """Test /status endpoint."""
        response = api_client.get("/status")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "uptime_seconds" in data
        assert "monitoring_active" in data
    
    def test_services_endpoint(self, api_client):
        """Test /services endpoint for service management."""
        # List services
        response = api_client.get("/services")
        assert response.status_code == 200
        
        # Register new service
        service_data = {
            "name": "test_service",
            "health_endpoint": "http://localhost:8080/health",
            "check_interval": 60
        }
        response = api_client.post("/services", json=service_data)
        assert response.status_code == 201
        
        # Get specific service
        response = api_client.get("/services/test_service")
        assert response.status_code == 200
        
        # Delete service
        response = api_client.delete("/services/test_service")
        assert response.status_code == 204
    
    def test_metrics_endpoint(self, api_client):
        """Test /metrics endpoint."""
        response = api_client.get("/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "timestamp" in data
        assert "cpu_usage_percent" in data
        assert "uptime_seconds" in data
    
    def test_alerts_endpoint(self, api_client):
        """Test /alerts endpoint."""
        response = api_client.get("/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "active_alerts" in data
        assert "alert_history" in data
    
    def test_report_endpoint(self, api_client):
        """Test /report endpoint."""
        response = api_client.get("/report")
        assert response.status_code == 200
        
        data = response.json()
        assert "report_metadata" in data
        assert "system_overview" in data
        assert "service_details" in data