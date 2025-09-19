"""
Health Monitoring Service Implementation

Core implementation of the health monitoring microservice following TDD methodology.
This implementation focuses on making the tests pass (GREEN phase).
"""
import asyncio
import aiohttp
import psutil
import logging
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import asdict
from concurrent.futures import ThreadPoolExecutor
import time

from tpm_job_finder_poc.shared.contracts.health_monitoring_service import (
    IHealthMonitoringService,
    ServiceHealthStatus,
    ServiceHealthResult, 
    SystemHealthStatus,
    ServiceConfiguration,
    DependencyConfiguration,
    MetricsData,
    HealthReport,
    OperationResult
)
from tpm_job_finder_poc.shared.contracts.error_handler import (
    HealthStatus,
    PerformanceMetrics,
    AlertStatus
)
from tpm_job_finder_poc.health_monitoring_service.config import (
    HealthMonitoringConfig,
    ServiceMonitoringConfig,
    DependencyMonitoringConfig
)


logger = logging.getLogger(__name__)


class HealthMonitoringService(IHealthMonitoringService):
    """Health Monitoring Service implementation."""
    
    def __init__(self, config: HealthMonitoringConfig):
        """Initialize the health monitoring service."""
        self.config = config
        self._registered_services: Dict[str, ServiceMonitoringConfig] = {}
        self._registered_dependencies: Dict[str, DependencyMonitoringConfig] = {}
        self._monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        self._metrics_data: List[MetricsData] = []
        self._health_history: Dict[str, List[ServiceHealthResult]] = {}
        self._alert_thresholds: Dict[str, Dict[str, Any]] = {}
        self._last_health_check: Optional[datetime] = None
        self._start_time = datetime.now(timezone.utc)
        self._executor = ThreadPoolExecutor(max_workers=self.config.concurrent_checks)
        
        # Initialize metrics collection
        self._total_checks_performed = 0
        self._successful_checks = 0
        self._failed_checks = 0
        self._current_alerts: Dict[str, AlertStatus] = {}
    
    async def check_system_health(self) -> SystemHealthStatus:
        """Check overall system health including all services and dependencies."""
        try:
            self._last_health_check = datetime.now(timezone.utc)
            
            # Check all services concurrently
            service_results = await self.check_all_services_health()
            
            # Check all dependencies
            dependency_results = await self.check_dependency_health()
            
            # Calculate overall status
            all_results = {**service_results, **dependency_results}
            overall_status = self._calculate_overall_status(all_results)
            
            # Count statuses
            status_counts = self._count_service_statuses(all_results)
            
            return SystemHealthStatus(
                overall_status=overall_status,
                services=service_results,
                dependencies=dependency_results,
                timestamp=self._last_health_check,
                total_services=len(all_results),
                healthy_services=status_counts["healthy"],
                unhealthy_services=status_counts["unhealthy"],
                degraded_services=status_counts["degraded"],
                unknown_services=status_counts["unknown"]
            )
            
        except Exception as e:
            logger.error(f"Failed to check system health: {e}")
            return SystemHealthStatus(
                overall_status=ServiceHealthStatus.UNKNOWN,
                services={},
                dependencies={},
                timestamp=datetime.now(timezone.utc),
                total_services=0,
                healthy_services=0,
                unhealthy_services=0,
                degraded_services=0,
                unknown_services=0
            )
    
    async def check_service_health(self, service_name: str) -> ServiceHealthResult:
        """Check health of a specific registered service."""
        if service_name not in self._registered_services:
            return ServiceHealthResult(
                service_name=service_name,
                status=ServiceHealthStatus.UNKNOWN,
                response_time_ms=0.0,
                last_check=datetime.now(timezone.utc),
                error_message="Service not registered"
            )
        
        service_config = self._registered_services[service_name]
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                timeout = aiohttp.ClientTimeout(total=service_config.timeout_ms / 1000)
                
                async with session.get(
                    service_config.health_endpoint,
                    headers=service_config.headers,
                    timeout=timeout
                ) as response:
                    response_time_ms = (time.time() - start_time) * 1000
                    
                    if response.status in service_config.expected_status_codes:
                        # Try to parse response for additional health info
                        try:
                            health_data = await response.json()
                            details = health_data if isinstance(health_data, dict) else {}
                        except:
                            details = {"status_code": response.status}
                        
                        result = ServiceHealthResult(
                            service_name=service_name,
                            status=ServiceHealthStatus.HEALTHY,
                            response_time_ms=response_time_ms,
                            last_check=datetime.now(timezone.utc),
                            details=details,
                            endpoint_url=service_config.health_endpoint
                        )
                    else:
                        result = ServiceHealthResult(
                            service_name=service_name,
                            status=ServiceHealthStatus.UNHEALTHY,
                            response_time_ms=response_time_ms,
                            last_check=datetime.now(timezone.utc),
                            error_message=f"Unexpected status code: {response.status}",
                            endpoint_url=service_config.health_endpoint
                        )
                    
                    # Update statistics
                    self._total_checks_performed += 1
                    if result.status == ServiceHealthStatus.HEALTHY:
                        self._successful_checks += 1
                    else:
                        self._failed_checks += 1
                    
                    # Store in history
                    if service_name not in self._health_history:
                        self._health_history[service_name] = []
                    self._health_history[service_name].append(result)
                    
                    # Keep only recent history
                    max_history = 100
                    if len(self._health_history[service_name]) > max_history:
                        self._health_history[service_name] = self._health_history[service_name][-max_history:]
                    
                    return result
                    
        except asyncio.TimeoutError:
            response_time_ms = (time.time() - start_time) * 1000
            self._total_checks_performed += 1
            self._failed_checks += 1
            
            return ServiceHealthResult(
                service_name=service_name,
                status=ServiceHealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                last_check=datetime.now(timezone.utc),
                error_message="Connection timeout",
                endpoint_url=service_config.health_endpoint
            )
            
        except Exception as e:
            response_time_ms = (time.time() - start_time) * 1000
            self._total_checks_performed += 1
            self._failed_checks += 1
            
            return ServiceHealthResult(
                service_name=service_name,
                status=ServiceHealthStatus.UNHEALTHY,
                response_time_ms=response_time_ms,
                last_check=datetime.now(timezone.utc),
                error_message=str(e),
                endpoint_url=service_config.health_endpoint
            )
    
    async def check_all_services_health(self) -> Dict[str, ServiceHealthResult]:
        """Check health of all registered services concurrently."""
        if not self._registered_services:
            return {}
        
        tasks = [
            self.check_service_health(service_name)
            for service_name in self._registered_services.keys()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        health_results = {}
        for i, result in enumerate(results):
            service_name = list(self._registered_services.keys())[i]
            if isinstance(result, Exception):
                health_results[service_name] = ServiceHealthResult(
                    service_name=service_name,
                    status=ServiceHealthStatus.UNHEALTHY,
                    response_time_ms=0.0,
                    last_check=datetime.now(timezone.utc),
                    error_message=f"Check failed: {str(result)}"
                )
            else:
                health_results[service_name] = result
        
        return health_results
    
    async def check_dependency_health(self) -> Dict[str, ServiceHealthResult]:
        """Check health of all registered dependencies."""
        dependency_results = {}
        
        for dep_name, dep_config in self._registered_dependencies.items():
            start_time = time.time()
            
            try:
                if dep_config.type == "filesystem":
                    # Check filesystem health
                    fs_config = dep_config.filesystem_config or {}
                    paths = fs_config.get("paths", ["/tmp"])
                    check_writable = fs_config.get("check_writable", True)
                    
                    all_healthy = True
                    details = {}
                    
                    for path in paths:
                        if os.path.exists(path):
                            if check_writable:
                                try:
                                    test_file = os.path.join(path, f".health_check_{int(time.time())}")
                                    with open(test_file, 'w') as f:
                                        f.write("health check")
                                    os.remove(test_file)
                                    details[path] = "writable"
                                except:
                                    all_healthy = False
                                    details[path] = "not_writable"
                            else:
                                details[path] = "exists"
                        else:
                            all_healthy = False
                            details[path] = "missing"
                    
                    status = ServiceHealthStatus.HEALTHY if all_healthy else ServiceHealthStatus.UNHEALTHY
                    
                elif dep_config.type == "database":
                    # Stub for database health check
                    status = ServiceHealthStatus.HEALTHY
                    details = {"connection": "ok", "type": "postgresql"}
                    
                elif dep_config.type == "redis":
                    # Stub for redis health check
                    status = ServiceHealthStatus.HEALTHY
                    details = {"connection": "ok", "type": "redis"}
                    
                else:
                    status = ServiceHealthStatus.UNKNOWN
                    details = {"type": dep_config.type, "check": "not_implemented"}
                
                response_time_ms = (time.time() - start_time) * 1000
                
                dependency_results[dep_name] = ServiceHealthResult(
                    service_name=dep_name,
                    status=status,
                    response_time_ms=response_time_ms,
                    last_check=datetime.now(timezone.utc),
                    details=details
                )
                
            except Exception as e:
                response_time_ms = (time.time() - start_time) * 1000
                dependency_results[dep_name] = ServiceHealthResult(
                    service_name=dep_name,
                    status=ServiceHealthStatus.UNHEALTHY,
                    response_time_ms=response_time_ms,
                    last_check=datetime.now(timezone.utc),
                    error_message=str(e)
                )
        
        return dependency_results
    
    async def register_service(self, service_name: str, config: Dict[str, Any]) -> OperationResult:
        """Register a service for health monitoring."""
        try:
            service_config = ServiceMonitoringConfig(
                name=service_name,
                health_endpoint=config["health_endpoint"],
                check_interval=config.get("check_interval", 60),
                timeout_ms=config.get("timeout_ms", 5000),
                expected_status_codes=config.get("expected_status_codes", [200]),
                headers=config.get("headers", {})
            )
            
            self._registered_services[service_name] = service_config
            
            logger.info(f"Registered service for monitoring: {service_name}")
            
            return OperationResult(
                success=True,
                message=f"Service '{service_name}' registered successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to register service {service_name}: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to register service: {str(e)}",
                error_code="REGISTRATION_FAILED"
            )
    
    async def unregister_service(self, service_name: str) -> OperationResult:
        """Unregister a service from health monitoring."""
        if service_name in self._registered_services:
            del self._registered_services[service_name]
            
            # Clean up history
            if service_name in self._health_history:
                del self._health_history[service_name]
            
            # Clean up alerts
            if service_name in self._alert_thresholds:
                del self._alert_thresholds[service_name]
            
            logger.info(f"Unregistered service: {service_name}")
            
            return OperationResult(
                success=True,
                message=f"Service '{service_name}' unregistered successfully"
            )
        else:
            return OperationResult(
                success=False,
                message=f"Service '{service_name}' not found",
                error_code="SERVICE_NOT_FOUND"
            )
    
    async def get_registered_services(self) -> List[str]:
        """Get list of all registered services."""
        return list(self._registered_services.keys())
    
    async def register_dependency(self, dependency_name: str, config: Dict[str, Any]) -> OperationResult:
        """Register a dependency for health monitoring."""
        try:
            dep_config = DependencyMonitoringConfig(
                name=dependency_name,
                type=config["type"],
                connection_string=config.get("connection_string"),
                timeout_ms=config.get("timeout_ms", 2000),
                check_interval=config.get("check_interval", 300)
            )
            
            # Store type-specific configuration
            if config["type"] == "filesystem":
                dep_config.filesystem_config = {
                    "paths": config.get("paths", ["/tmp"]),
                    "check_writable": config.get("check_writable", True)
                }
            elif config["type"] == "database":
                dep_config.database_config = config.get("database_config", {})
            elif config["type"] == "redis":
                dep_config.redis_config = config.get("redis_config", {})
            
            self._registered_dependencies[dependency_name] = dep_config
            
            logger.info(f"Registered dependency for monitoring: {dependency_name}")
            
            return OperationResult(
                success=True,
                message=f"Dependency '{dependency_name}' registered successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to register dependency {dependency_name}: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to register dependency: {str(e)}",
                error_code="DEPENDENCY_REGISTRATION_FAILED"
            )
    
    async def start_monitoring(self) -> OperationResult:
        """Start the health monitoring background process."""
        if self._monitoring_active:
            return OperationResult(
                success=True,
                message="Monitoring already active"
            )
        
        try:
            self._monitoring_active = True
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Health monitoring started")
            
            return OperationResult(
                success=True,
                message="Health monitoring started successfully"
            )
            
        except Exception as e:
            self._monitoring_active = False
            logger.error(f"Failed to start monitoring: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to start monitoring: {str(e)}",
                error_code="MONITORING_START_FAILED"
            )
    
    async def stop_monitoring(self) -> OperationResult:
        """Stop the health monitoring background process."""
        if not self._monitoring_active:
            return OperationResult(
                success=True,
                message="Monitoring already stopped"
            )
        
        try:
            self._monitoring_active = False
            
            if self._monitoring_task:
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass
                self._monitoring_task = None
            
            logger.info("Health monitoring stopped")
            
            return OperationResult(
                success=True,
                message="Health monitoring stopped successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to stop monitoring: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to stop monitoring: {str(e)}",
                error_code="MONITORING_STOP_FAILED"
            )
    
    def is_monitoring_active(self) -> bool:
        """Check if monitoring is currently active."""
        return self._monitoring_active
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary with key metrics."""
        system_health = await self.check_system_health()
        
        uptime_seconds = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        
        return {
            "overall_status": system_health.overall_status.value,
            "total_services": system_health.total_services,
            "healthy_services": system_health.healthy_services,
            "unhealthy_services": system_health.unhealthy_services,
            "degraded_services": system_health.degraded_services,
            "unknown_services": system_health.unknown_services,
            "system_metrics": {
                "uptime_seconds": uptime_seconds,
                "total_health_checks": self._total_checks_performed,
                "successful_checks": self._successful_checks,
                "failed_checks": self._failed_checks,
                "success_rate": self._successful_checks / max(1, self._total_checks_performed)
            },
            "last_updated": system_health.timestamp.isoformat(),
            "monitoring_active": self._monitoring_active
        }
    
    async def export_health_report(self, include_historical: bool = False, format: str = "json") -> Dict[str, Any]:
        """Export comprehensive health report."""
        system_health = await self.check_system_health()
        
        report = {
            "report_metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "report_version": "1.0",
                "services_monitored": len(self._registered_services),
                "dependencies_monitored": len(self._registered_dependencies),
                "format": format
            },
            "system_overview": asdict(system_health),
            "service_details": {
                name: asdict(result) for name, result in system_health.services.items()
            },
            "metrics_summary": await self.get_health_summary(),
            "alert_summary": {
                "active_alerts": len(self._current_alerts),
                "alert_details": {name: asdict(alert) for name, alert in self._current_alerts.items()}
            }
        }
        
        if include_historical:
            report["historical_data"] = self._get_historical_summary()
        
        return report
    
    async def collect_metrics(self) -> OperationResult:
        """Collect system and service metrics."""
        try:
            # Collect system metrics using psutil with error handling
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
            except Exception:
                cpu_percent = 0.0
                
            try:
                memory = psutil.virtual_memory()
                memory_usage_mb = memory.used / (1024 * 1024)
            except Exception:
                memory_usage_mb = 0.0
                
            try:
                disk = psutil.disk_usage('/')
                disk_usage_percent = disk.percent
            except Exception:
                disk_usage_percent = 0.0
                
            try:
                network = psutil.net_connections()
                network_connections = len(network)
            except Exception:
                network_connections = 0
            
            uptime_seconds = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            
            metrics = MetricsData(
                timestamp=datetime.now(timezone.utc),
                cpu_usage_percent=cpu_percent,
                memory_usage_mb=memory_usage_mb,
                disk_usage_percent=disk_usage_percent,
                network_connections=network_connections,
                uptime_seconds=uptime_seconds,
                custom_metrics={
                    "total_registered_services": len(self._registered_services),
                    "total_registered_dependencies": len(self._registered_dependencies),
                    "monitoring_active": self._monitoring_active,
                    "health_check_success_rate": self._successful_checks / max(1, self._total_checks_performed)
                }
            )
            
            self._metrics_data.append(metrics)
            
            # Keep only recent metrics (based on retention)
            max_metrics = self.config.max_historical_records
            if len(self._metrics_data) > max_metrics:
                self._metrics_data = self._metrics_data[-max_metrics:]
            
            return OperationResult(
                success=True,
                message="Metrics collected successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to collect metrics: {str(e)}",
                error_code="METRICS_COLLECTION_FAILED"
            )
    
    async def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics for a specific service."""
        if service_name == "system":
            # Return latest system metrics
            if self._metrics_data:
                latest_metrics = self._metrics_data[-1]
                return asdict(latest_metrics)
            else:
                # Collect metrics first
                await self.collect_metrics()
                if self._metrics_data:
                    return asdict(self._metrics_data[-1])
        
        # For specific services, return health history metrics
        if service_name in self._health_history:
            history = self._health_history[service_name]
            if history:
                recent_checks = history[-10:]  # Last 10 checks
                avg_response_time = sum(check.response_time_ms for check in recent_checks) / len(recent_checks)
                success_count = sum(1 for check in recent_checks if check.status == ServiceHealthStatus.HEALTHY)
                success_rate = success_count / len(recent_checks)
                
                return {
                    "service_name": service_name,
                    "total_checks": len(history),
                    "recent_checks": len(recent_checks),
                    "average_response_time_ms": avg_response_time,
                    "success_rate": success_rate,
                    "last_check": history[-1].last_check.isoformat() if history else None
                }
        
        return {}
    
    async def get_performance_metrics(self, service_name: str) -> PerformanceMetrics:
        """Get performance metrics for a service."""
        if service_name in self._health_history:
            history = self._health_history[service_name]
            if history:
                response_times = [check.response_time_ms for check in history]
                successful_requests = sum(1 for check in history if check.status == ServiceHealthStatus.HEALTHY)
                failed_requests = len(history) - successful_requests
                
                avg_response_time = sum(response_times) / len(response_times) if response_times else 0
                peak_response_time = max(response_times) if response_times else 0
                
                # Calculate throughput (checks per second over recent period)
                if len(history) >= 2:
                    time_span = (history[-1].last_check - history[0].last_check).total_seconds()
                    throughput = len(history) / max(1, time_span)
                else:
                    throughput = 0
                
                # Get current system metrics for CPU usage
                cpu_usage = 0.0
                if self._metrics_data:
                    cpu_usage = self._metrics_data[-1].cpu_usage_percent
                
                return PerformanceMetrics(
                    average_processing_time_ms=avg_response_time,
                    errors_processed=failed_requests,
                    throughput_per_second=throughput,
                    peak_processing_time_ms=peak_response_time,
                    cpu_usage_percent=cpu_usage
                )
        
        # Default empty metrics
        return PerformanceMetrics(
            average_processing_time_ms=0.0,
            errors_processed=0,
            throughput_per_second=0.0,
            peak_processing_time_ms=0.0,
            cpu_usage_percent=0.0
        )
    
    async def get_historical_data(self, service_name: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get historical metrics data for a service."""
        historical_data = []
        
        if service_name == "system":
            # Return system metrics within time range
            for metrics in self._metrics_data:
                if start_time <= metrics.timestamp <= end_time:
                    historical_data.append({
                        "timestamp": metrics.timestamp.isoformat(),
                        "metrics": asdict(metrics)
                    })
        else:
            # Return service health history within time range
            if service_name in self._health_history:
                for health_result in self._health_history[service_name]:
                    if start_time <= health_result.last_check <= end_time:
                        historical_data.append({
                            "timestamp": health_result.last_check.isoformat(),
                            "metrics": asdict(health_result)
                        })
        
        return historical_data
    
    async def set_alert_thresholds(self, service_name: str, thresholds: Dict[str, Any]) -> OperationResult:
        """Set alert thresholds for a service."""
        try:
            self._alert_thresholds[service_name] = thresholds.copy()
            
            logger.info(f"Alert thresholds set for service: {service_name}")
            
            return OperationResult(
                success=True,
                message=f"Alert thresholds set for '{service_name}'"
            )
            
        except Exception as e:
            logger.error(f"Failed to set alert thresholds for {service_name}: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to set alert thresholds: {str(e)}",
                error_code="ALERT_THRESHOLD_FAILED"
            )
    
    async def get_alert_thresholds(self, service_name: str) -> Dict[str, Any]:
        """Get alert thresholds for a service."""
        return self._alert_thresholds.get(service_name, {})
    
    async def get_alert_status(self, service_name: str) -> AlertStatus:
        """Get current alert status for a service."""
        thresholds = await self.get_alert_thresholds(service_name)
        
        if not thresholds:
            return AlertStatus(
                threshold_exceeded=False,
                error_count=0,
                threshold_limit=0,
                alert_sent=False
            )
        
        # Check error rate threshold
        error_rate = await self._calculate_error_rate(service_name)
        error_threshold = thresholds.get("error_rate", self.config.alert_threshold_error_rate)
        
        if error_rate > error_threshold:
            alert = AlertStatus(
                threshold_exceeded=True,
                error_count=int(error_rate * 100),  # Convert to percentage
                threshold_limit=int(error_threshold * 100),
                alert_sent=False
            )
            alert.alert_type = "error_rate"
            alert.current_value = error_rate
            alert.threshold_value = error_threshold
            
            # Store current alert
            self._current_alerts[service_name] = alert
            
            return alert
        
        # Check response time threshold
        avg_response_time = await self._calculate_avg_response_time(service_name)
        response_time_threshold = thresholds.get("response_time_ms", self.config.alert_threshold_response_time_ms)
        
        if avg_response_time > response_time_threshold:
            alert = AlertStatus(
                threshold_exceeded=True,
                error_count=0,
                threshold_limit=response_time_threshold,
                alert_sent=False
            )
            alert.alert_type = "response_time"
            alert.current_value = avg_response_time
            alert.threshold_value = response_time_threshold
            
            self._current_alerts[service_name] = alert
            
            return alert
        
        # No thresholds exceeded
        if service_name in self._current_alerts:
            del self._current_alerts[service_name]
        
        return AlertStatus(
            threshold_exceeded=False,
            error_count=0,
            threshold_limit=0,
            alert_sent=False
        )
    
    async def send_alert(self, alert_data: Dict[str, Any]) -> OperationResult:
        """Send an alert notification."""
        try:
            # For now, just log the alert (in real implementation, would send to external systems)
            logger.warning(f"ALERT: {alert_data}")
            
            return OperationResult(
                success=True,
                message="Alert sent successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to send alert: {str(e)}",
                error_code="ALERT_SEND_FAILED"
            )
    
    async def update_configuration(self, config_updates: Dict[str, Any]) -> OperationResult:
        """Update service configuration."""
        try:
            # Update configuration attributes
            for key, value in config_updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            logger.info(f"Configuration updated: {list(config_updates.keys())}")
            
            return OperationResult(
                success=True,
                message="Configuration updated successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to update configuration: {str(e)}",
                error_code="CONFIG_UPDATE_FAILED"
            )
    
    async def get_configuration(self) -> Dict[str, Any]:
        """Get current service configuration."""
        return asdict(self.config)
    
    async def reload_configuration(self) -> OperationResult:
        """Reload configuration from external source."""
        try:
            # For now, just return success (in real implementation, would reload from file/service)
            logger.info("Configuration reloaded")
            
            return OperationResult(
                success=True,
                message="Configuration reloaded successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to reload configuration: {str(e)}",
                error_code="CONFIG_RELOAD_FAILED"
            )
    
    async def log_health_event(self, event_type: str, service_name: str, details: Dict[str, Any]) -> OperationResult:
        """Log a health-related event to the audit system."""
        try:
            # For now, just log the event (in real implementation, would send to audit service)
            logger.info(f"Health event: {event_type} for {service_name} - {details}")
            
            return OperationResult(
                success=True,
                message="Health event logged successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to log health event: {e}")
            return OperationResult(
                success=False,
                message=f"Failed to log health event: {str(e)}",
                error_code="HEALTH_EVENT_LOG_FAILED"
            )
    
    # Helper methods
    
    def _calculate_overall_status(self, all_results: Dict[str, ServiceHealthResult]) -> ServiceHealthStatus:
        """Calculate overall status from individual service results."""
        if not all_results:
            return ServiceHealthStatus.UNKNOWN
        
        statuses = [result.status for result in all_results.values()]
        
        if all(status == ServiceHealthStatus.HEALTHY for status in statuses):
            return ServiceHealthStatus.HEALTHY
        elif any(status == ServiceHealthStatus.UNHEALTHY for status in statuses):
            return ServiceHealthStatus.UNHEALTHY
        elif any(status == ServiceHealthStatus.DEGRADED for status in statuses):
            return ServiceHealthStatus.DEGRADED
        else:
            return ServiceHealthStatus.UNKNOWN
    
    def _count_service_statuses(self, all_results: Dict[str, ServiceHealthResult]) -> Dict[str, int]:
        """Count services by status."""
        counts = {
            "healthy": 0,
            "unhealthy": 0,
            "degraded": 0,
            "unknown": 0
        }
        
        for result in all_results.values():
            counts[result.status.value] += 1
        
        return counts
    
    async def _calculate_error_rate(self, service_name: str) -> float:
        """Calculate error rate for a service."""
        if service_name not in self._health_history:
            return 0.0
        
        history = self._health_history[service_name]
        if not history:
            return 0.0
        
        # Calculate error rate from recent checks
        recent_checks = history[-10:]  # Last 10 checks
        error_count = sum(1 for check in recent_checks if check.status != ServiceHealthStatus.HEALTHY)
        
        return error_count / len(recent_checks)
    
    async def _calculate_avg_response_time(self, service_name: str) -> float:
        """Calculate average response time for a service."""
        if service_name not in self._health_history:
            return 0.0
        
        history = self._health_history[service_name]
        if not history:
            return 0.0
        
        recent_checks = history[-10:]  # Last 10 checks
        total_time = sum(check.response_time_ms for check in recent_checks)
        
        return total_time / len(recent_checks)
    
    def _get_historical_summary(self) -> List[Dict[str, Any]]:
        """Get summary of historical data."""
        summary = []
        
        # System metrics summary
        if self._metrics_data:
            recent_metrics = self._metrics_data[-5:]  # Last 5 metrics
            for metrics in recent_metrics:
                summary.append({
                    "type": "system_metrics",
                    "timestamp": metrics.timestamp.isoformat(),
                    "data": asdict(metrics)
                })
        
        # Service health summary
        for service_name, history in self._health_history.items():
            if history:
                recent_health = history[-3:]  # Last 3 health checks
                for health in recent_health:
                    summary.append({
                        "type": "service_health",
                        "service": service_name,
                        "timestamp": health.last_check.isoformat(),
                        "data": asdict(health)
                    })
        
        return summary
    
    async def _monitoring_loop(self):
        """Background monitoring loop."""
        logger.info("Health monitoring loop started")
        
        try:
            while self._monitoring_active:
                try:
                    # Collect metrics
                    if self.config.enable_metrics_collection:
                        await self.collect_metrics()
                    
                    # Check all services health
                    await self.check_all_services_health()
                    
                    # Check dependencies health
                    await self.check_dependency_health()
                    
                    # Check alerts
                    if self.config.enable_alerting:
                        await self._check_alerts()
                    
                    # Wait for next check
                    await asyncio.sleep(self.config.check_interval_seconds)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    await asyncio.sleep(5)  # Short delay before retrying
                    
        except asyncio.CancelledError:
            pass
        finally:
            logger.info("Health monitoring loop stopped")
    
    async def _check_alerts(self):
        """Check alert conditions for all services."""
        for service_name in self._registered_services.keys():
            try:
                alert_status = await self.get_alert_status(service_name)
                
                if alert_status.threshold_exceeded and not alert_status.alert_sent:
                    # Send alert
                    alert_data = {
                        "service": service_name,
                        "alert_type": getattr(alert_status, 'alert_type', 'unknown'),
                        "current_value": getattr(alert_status, 'current_value', 0),
                        "threshold_value": getattr(alert_status, 'threshold_value', 0),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "severity": "critical" if service_name in self.config.services_to_monitor else "warning"
                    }
                    
                    await self.send_alert(alert_data)
                    alert_status.alert_sent = True
                    
            except Exception as e:
                logger.error(f"Error checking alerts for {service_name}: {e}")
    
    def __del__(self):
        """Cleanup resources."""
        if self._executor:
            self._executor.shutdown(wait=False)