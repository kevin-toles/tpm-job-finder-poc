"""
Health Monitoring Service Contract

Defines the interface for the health monitoring microservice following
the established patterns and engineering guidelines.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from tpm_job_finder_poc.shared.contracts.error_handler import (
    HealthStatus, 
    PerformanceMetrics, 
    AlertStatus
)


class ServiceHealthStatus(Enum):
    """Health status values for services."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"  
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealthResult:
    """Result of a service health check."""
    service_name: str
    status: ServiceHealthStatus
    response_time_ms: float
    last_check: datetime
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None


@dataclass
class SystemHealthStatus:
    """Overall system health status."""
    overall_status: ServiceHealthStatus
    services: Dict[str, ServiceHealthResult] 
    dependencies: Dict[str, ServiceHealthResult]
    timestamp: datetime
    total_services: int
    healthy_services: int
    unhealthy_services: int
    degraded_services: int
    unknown_services: int


@dataclass
class ServiceConfiguration:
    """Configuration for a monitored service."""
    name: str
    health_endpoint: str
    check_interval: int = 60  # seconds
    timeout_ms: int = 5000
    expected_status_codes: List[int] = None
    headers: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.expected_status_codes is None:
            self.expected_status_codes = [200]


@dataclass
class DependencyConfiguration:
    """Configuration for a monitored dependency."""
    name: str
    type: str  # database, redis, filesystem, etc.
    connection_string: Optional[str] = None
    timeout_ms: int = 1000
    check_interval: int = 300  # seconds
    custom_check: Optional[str] = None
    additional_config: Optional[Dict[str, Any]] = None


@dataclass
class MetricsData:
    """System and service metrics data."""
    timestamp: datetime
    cpu_usage_percent: float
    memory_usage_mb: float
    disk_usage_percent: float
    network_connections: int
    uptime_seconds: float
    custom_metrics: Optional[Dict[str, Any]] = None


@dataclass
class HealthReport:
    """Comprehensive health report."""
    report_metadata: Dict[str, Any]
    system_overview: SystemHealthStatus
    service_details: Dict[str, ServiceHealthResult]
    metrics_summary: Dict[str, Any]
    alert_summary: Dict[str, Any]
    historical_data: Optional[List[Dict[str, Any]]] = None


@dataclass
class OperationResult:
    """Result of a service operation."""
    success: bool
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class IHealthMonitoringService(ABC):
    """Interface for the Health Monitoring Service."""
    
    # Core health checking methods
    @abstractmethod
    async def check_system_health(self) -> SystemHealthStatus:
        """Check overall system health including all services and dependencies."""
        pass
    
    @abstractmethod
    async def check_service_health(self, service_name: str) -> ServiceHealthResult:
        """Check health of a specific registered service."""
        pass
    
    @abstractmethod
    async def check_all_services_health(self) -> Dict[str, ServiceHealthResult]:
        """Check health of all registered services concurrently."""
        pass
    
    @abstractmethod
    async def check_dependency_health(self) -> Dict[str, ServiceHealthResult]:
        """Check health of all registered dependencies."""
        pass
    
    # Service registration and management
    @abstractmethod
    async def register_service(self, service_name: str, config: Dict[str, Any]) -> OperationResult:
        """Register a service for health monitoring."""
        pass
    
    @abstractmethod
    async def unregister_service(self, service_name: str) -> OperationResult:
        """Unregister a service from health monitoring."""
        pass
    
    @abstractmethod
    async def get_registered_services(self) -> List[str]:
        """Get list of all registered services."""
        pass
    
    @abstractmethod
    async def register_dependency(self, dependency_name: str, config: Dict[str, Any]) -> OperationResult:
        """Register a dependency for health monitoring."""
        pass
    
    # Health monitoring lifecycle
    @abstractmethod
    async def start_monitoring(self) -> OperationResult:
        """Start the health monitoring background process."""
        pass
    
    @abstractmethod
    async def stop_monitoring(self) -> OperationResult:
        """Stop the health monitoring background process."""
        pass
    
    @abstractmethod
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active."""
        pass
    
    # Health summary and reporting
    @abstractmethod
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary with key metrics."""
        pass
    
    @abstractmethod
    async def export_health_report(self, 
                                   include_historical: bool = False, 
                                   format: str = "json") -> Dict[str, Any]:
        """Export comprehensive health report."""
        pass
    
    # Metrics collection and retrieval
    @abstractmethod
    async def collect_metrics(self) -> OperationResult:
        """Collect system and service metrics."""
        pass
    
    @abstractmethod
    async def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics for a specific service."""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self, service_name: str) -> PerformanceMetrics:
        """Get performance metrics for a service."""
        pass
    
    @abstractmethod
    async def get_historical_data(self, 
                                  service_name: str, 
                                  start_time: datetime, 
                                  end_time: datetime) -> List[Dict[str, Any]]:
        """Get historical metrics data for a service."""
        pass
    
    # Alert management
    @abstractmethod
    async def set_alert_thresholds(self, service_name: str, thresholds: Dict[str, Any]) -> OperationResult:
        """Set alert thresholds for a service."""
        pass
    
    @abstractmethod
    async def get_alert_thresholds(self, service_name: str) -> Dict[str, Any]:
        """Get alert thresholds for a service."""
        pass
    
    @abstractmethod
    async def get_alert_status(self, service_name: str) -> AlertStatus:
        """Get current alert status for a service."""
        pass
    
    @abstractmethod
    async def send_alert(self, alert_data: Dict[str, Any]) -> OperationResult:
        """Send an alert notification."""
        pass
    
    # Configuration management
    @abstractmethod
    async def update_configuration(self, config_updates: Dict[str, Any]) -> OperationResult:
        """Update service configuration."""
        pass
    
    @abstractmethod
    async def get_configuration(self) -> Dict[str, Any]:
        """Get current service configuration."""
        pass
    
    @abstractmethod
    async def reload_configuration(self) -> OperationResult:
        """Reload configuration from external source."""
        pass
    
    # Integration methods
    @abstractmethod
    async def log_health_event(self, 
                               event_type: str, 
                               service_name: str, 
                               details: Dict[str, Any]) -> OperationResult:
        """Log a health-related event to the audit system."""
        pass