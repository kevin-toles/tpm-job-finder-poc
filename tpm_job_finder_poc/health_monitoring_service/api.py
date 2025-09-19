"""
Health Monitoring Service FastAPI Application

REST API endpoints for the health monitoring microservice.
"""
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import asyncio

from tpm_job_finder_poc.health_monitoring_service.service import HealthMonitoringService
from tpm_job_finder_poc.health_monitoring_service.config import HealthMonitoringConfig
from tpm_job_finder_poc.shared.contracts.health_monitoring_service import (
    ServiceHealthStatus,
    SystemHealthStatus,
    OperationResult
)


logger = logging.getLogger(__name__)


# Global service instance (will be initialized on startup)
health_service: Optional[HealthMonitoringService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifespan events."""
    global health_service
    
    # Startup
    try:
        # Create default configuration
        config = HealthMonitoringConfig()
        
        # Initialize the service
        health_service = HealthMonitoringService(config)
        
        # Start monitoring
        await health_service.start_monitoring()
        
        logger.info("Health monitoring service started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start health monitoring service: {e}")
        raise
    
    yield
    
    # Shutdown
    if health_service:
        try:
            await health_service.stop_monitoring()
            logger.info("Health monitoring service stopped")
        except Exception as e:
            logger.error(f"Error stopping health monitoring service: {e}")


# Request/Response Models
class ServiceRegistrationRequest(BaseModel):
    """Request model for service registration."""
    name: Optional[str] = Field(None, description="Service name (optional for specific endpoint)")
    health_endpoint: str = Field(..., description="Health check endpoint URL")
    check_interval: int = Field(default=60, description="Check interval in seconds")
    timeout_ms: int = Field(default=5000, description="Timeout in milliseconds")
    expected_status_codes: List[int] = Field(default=[200], description="Expected HTTP status codes")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers to include")


class DependencyRegistrationRequest(BaseModel):
    """Request model for dependency registration."""
    type: str = Field(..., description="Dependency type (database, redis, filesystem, etc.)")
    connection_string: Optional[str] = Field(None, description="Connection string if applicable")
    timeout_ms: int = Field(default=2000, description="Timeout in milliseconds")
    check_interval: int = Field(default=300, description="Check interval in seconds")
    paths: Optional[List[str]] = Field(None, description="File system paths (for filesystem type)")
    check_writable: bool = Field(default=True, description="Check if paths are writable")
    database_config: Optional[Dict[str, Any]] = Field(None, description="Database-specific configuration")
    redis_config: Optional[Dict[str, Any]] = Field(None, description="Redis-specific configuration")


class AlertThresholdRequest(BaseModel):
    """Request model for setting alert thresholds."""
    response_time_ms: Optional[float] = Field(None, description="Response time threshold in milliseconds")
    error_rate: Optional[float] = Field(None, description="Error rate threshold (0.0-1.0)")
    availability: Optional[float] = Field(None, description="Availability threshold (0.0-1.0)")


class HealthSummaryResponse(BaseModel):
    """Response model for health summary."""
    overall_status: str
    total_services: int
    healthy_services: int
    unhealthy_services: int
    degraded_services: int
    unknown_services: int
    system_metrics: Dict[str, Any]
    last_updated: str
    monitoring_active: bool


class ServiceHealthResponse(BaseModel):
    """Response model for individual service health."""
    service_name: str
    status: str
    response_time_ms: float
    last_check: str
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None


# FastAPI app instance with lifespan
app = FastAPI(
    title="Health Monitoring Service API",
    description="Microservice for monitoring system and service health",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


def get_health_service() -> HealthMonitoringService:
    """Dependency to get the health service instance."""
    if health_service is None:
        raise HTTPException(
            status_code=503,
            detail="Health monitoring service not initialized"
        )
    return health_service


# Health check endpoints
@app.get("/health", response_model=Dict[str, str])
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health/detailed", response_model=HealthSummaryResponse)
async def detailed_health_check(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Detailed health check with system status."""
    try:
        summary = await service.get_health_summary()
        
        return HealthSummaryResponse(
            overall_status=summary["overall_status"],
            total_services=summary["total_services"],
            healthy_services=summary["healthy_services"],
            unhealthy_services=summary["unhealthy_services"],
            degraded_services=summary["degraded_services"],
            unknown_services=summary["unknown_services"],
            system_metrics=summary["system_metrics"],
            last_updated=summary["last_updated"],
            monitoring_active=summary["monitoring_active"]
        )
        
    except Exception as e:
        logger.error(f"Error getting detailed health status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/status")
async def status_check(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get overall system status."""
    try:
        system_health = await service.check_system_health()
        summary = await service.get_health_summary()
        
        return {
            "status": system_health.overall_status.value,
            "services": {
                name: {
                    "status": result.status.value,
                    "response_time_ms": result.response_time_ms,
                    "last_check": result.last_check.isoformat(),
                    "error_message": result.error_message
                }
                for name, result in system_health.services.items()
            },
            "dependencies": {
                name: {
                    "status": result.status.value,
                    "response_time_ms": result.response_time_ms,
                    "last_check": result.last_check.isoformat(),
                    "error_message": result.error_message
                }
                for name, result in system_health.dependencies.items()
            },
            "timestamp": system_health.timestamp.isoformat(),
            "summary": {
                "total_services": system_health.total_services,
                "healthy_services": system_health.healthy_services,
                "unhealthy_services": system_health.unhealthy_services,
                "degraded_services": system_health.degraded_services,
                "unknown_services": system_health.unknown_services
            },
            "uptime_seconds": summary["system_metrics"]["uptime_seconds"],
            "monitoring_active": summary["monitoring_active"]
        }
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Service management endpoints
@app.get("/services", response_model=List[str])
async def get_services(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get list of registered services."""
    try:
        return await service.get_registered_services()
    except Exception as e:
        logger.error(f"Error getting registered services: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/services")
async def register_service_generic(
    request: ServiceRegistrationRequest,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Register a new service for health monitoring (generic endpoint)."""
    try:
        # Use the name from the request body
        service_name = getattr(request, 'name', 'unknown_service')
        
        config = {
            "health_endpoint": request.health_endpoint,
            "check_interval": request.check_interval,
            "timeout_ms": request.timeout_ms,
            "expected_status_codes": request.expected_status_codes,
            "headers": request.headers
        }
        
        result = await service.register_service(service_name, config)
        
        if result.success:
            return JSONResponse(
                status_code=201,
                content={"message": result.message, "service_name": service_name}
            )
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error registering service: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/services/{service_name}")
async def register_service(
    service_name: str,
    request: ServiceRegistrationRequest,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Register a new service for health monitoring."""
    try:
        config = {
            "health_endpoint": request.health_endpoint,
            "check_interval": request.check_interval,
            "timeout_ms": request.timeout_ms,
            "expected_status_codes": request.expected_status_codes,
            "headers": request.headers
        }
        
        result = await service.register_service(service_name, config)
        
        if result.success:
            return {"message": result.message, "service_name": service_name}
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error registering service {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/services/{service_name}")
async def unregister_service(
    service_name: str,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Unregister a service from health monitoring."""
    try:
        result = await service.unregister_service(service_name)
        
        if result.success:
            return JSONResponse(status_code=204, content=None)
        else:
            raise HTTPException(status_code=404, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error unregistering service {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/services/{service_name}")
async def get_service_info(
    service_name: str,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get information about a specific service."""
    try:
        # Check if service is registered
        registered_services = await service.get_registered_services()
        if service_name not in registered_services:
            raise HTTPException(status_code=404, detail=f"Service '{service_name}' not found")
        
        # Get health status
        health_result = await service.check_service_health(service_name)
        
        return {
            "service_name": service_name,
            "status": health_result.status.value,
            "response_time_ms": health_result.response_time_ms,
            "last_check": health_result.last_check.isoformat(),
            "error_message": health_result.error_message,
            "details": health_result.details,
            "endpoint_url": health_result.endpoint_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting service info for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/services/{service_name}/health", response_model=ServiceHealthResponse)
async def get_service_health(
    service_name: str,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get health status of a specific service."""
    try:
        result = await service.check_service_health(service_name)
        
        return ServiceHealthResponse(
            service_name=result.service_name,
            status=result.status.value,
            response_time_ms=result.response_time_ms,
            last_check=result.last_check.isoformat(),
            error_message=result.error_message,
            details=result.details,
            endpoint_url=result.endpoint_url
        )
        
    except Exception as e:
        logger.error(f"Error getting service health for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Dependency management endpoints
@app.post("/dependencies/{dependency_name}")
async def register_dependency(
    dependency_name: str,
    request: DependencyRegistrationRequest,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Register a new dependency for health monitoring."""
    try:
        config = {
            "type": request.type,
            "connection_string": request.connection_string,
            "timeout_ms": request.timeout_ms,
            "check_interval": request.check_interval
        }
        
        # Add type-specific configuration
        if request.type == "filesystem":
            config["paths"] = request.paths or ["/tmp"]
            config["check_writable"] = request.check_writable
        elif request.type == "database":
            config["database_config"] = request.database_config or {}
        elif request.type == "redis":
            config["redis_config"] = request.redis_config or {}
        
        result = await service.register_dependency(dependency_name, config)
        
        if result.success:
            return {"message": result.message, "dependency_name": dependency_name}
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error registering dependency {dependency_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Metrics endpoints
@app.get("/metrics")
async def get_metrics(
    service_name: Optional[str] = None,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get metrics for system or specific service."""
    try:
        if service_name:
            metrics = await service.get_service_metrics(service_name)
        else:
            # Get system metrics
            metrics = await service.get_service_metrics("system")
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/metrics/{service_name}/performance")
async def get_performance_metrics(
    service_name: str,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get performance metrics for a specific service."""
    try:
        metrics = await service.get_performance_metrics(service_name)
        
        return {
            "service_name": service_name,
            "average_processing_time_ms": metrics.average_processing_time_ms,
            "errors_processed": metrics.errors_processed,
            "throughput_per_second": metrics.throughput_per_second,
            "peak_processing_time_ms": metrics.peak_processing_time_ms,
            "cpu_usage_percent": metrics.cpu_usage_percent
        }
        
    except Exception as e:
        logger.error(f"Error getting performance metrics for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/metrics/{service_name}/historical")
async def get_historical_metrics(
    service_name: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get historical metrics for a service."""
    try:
        # Parse time parameters
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = datetime.now(timezone.utc) - timedelta(hours=1)
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = datetime.now(timezone.utc)
        
        historical_data = await service.get_historical_data(service_name, start_dt, end_dt)
        
        return {
            "service_name": service_name,
            "time_range": {
                "start": start_dt.isoformat(),
                "end": end_dt.isoformat()
            },
            "data_points": len(historical_data),
            "historical_data": historical_data
        }
        
    except Exception as e:
        logger.error(f"Error getting historical metrics for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Alert management endpoints
@app.post("/services/{service_name}/alerts/thresholds")
async def set_alert_thresholds(
    service_name: str,
    request: AlertThresholdRequest,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Set alert thresholds for a service."""
    try:
        thresholds = {}
        
        if request.response_time_ms is not None:
            thresholds["response_time_ms"] = request.response_time_ms
        if request.error_rate is not None:
            thresholds["error_rate"] = request.error_rate
        if request.availability is not None:
            thresholds["availability"] = request.availability
        
        result = await service.set_alert_thresholds(service_name, thresholds)
        
        if result.success:
            return {"message": result.message, "service_name": service_name, "thresholds": thresholds}
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error setting alert thresholds for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/services/{service_name}/alerts/status")
async def get_alert_status(
    service_name: str,
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get current alert status for a service."""
    try:
        alert_status = await service.get_alert_status(service_name)
        
        return {
            "service_name": service_name,
            "threshold_exceeded": alert_status.threshold_exceeded,
            "error_count": alert_status.error_count,
            "threshold_limit": alert_status.threshold_limit,
            "alert_sent": alert_status.alert_sent,
            "alert_type": getattr(alert_status, 'alert_type', None),
            "current_value": getattr(alert_status, 'current_value', None),
            "threshold_value": getattr(alert_status, 'threshold_value', None)
        }
        
    except Exception as e:
        logger.error(f"Error getting alert status for {service_name}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Configuration endpoints
@app.get("/config")
async def get_configuration(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get current service configuration."""
    try:
        config = await service.get_configuration()
        return config
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/config/reload")
async def reload_configuration(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Reload service configuration."""
    try:
        result = await service.reload_configuration()
        
        if result.success:
            return {"message": result.message}
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error reloading configuration: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Monitoring control endpoints
@app.post("/monitoring/start")
async def start_monitoring(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Start the health monitoring process."""
    try:
        result = await service.start_monitoring()
        
        if result.success:
            return {"message": result.message}
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/monitoring/stop")
async def stop_monitoring(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Stop the health monitoring process."""
    try:
        result = await service.stop_monitoring()
        
        if result.success:
            return {"message": result.message}
        else:
            raise HTTPException(status_code=400, detail=result.message)
            
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/monitoring/status")
async def get_monitoring_status(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get current monitoring status."""
    try:
        is_active = service.is_monitoring_active()
        return {"monitoring_active": is_active}
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Report generation endpoints
@app.get("/reports/health")
async def generate_health_report(
    include_historical: bool = False,
    format: str = "json",
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Generate comprehensive health report."""
    try:
        report = await service.export_health_report(
            include_historical=include_historical,
            format=format
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating health report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/report")
async def get_health_report(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get comprehensive health report (alias for /reports/health)."""
    try:
        report = await service.export_health_report(
            include_historical=False,
            format="json"
        )
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating health report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/alerts")
async def get_alerts(
    service: HealthMonitoringService = Depends(get_health_service)
):
    """Get current alerts and alert history."""
    try:
        # Get all registered services and check their alert status
        services = await service.get_registered_services()
        active_alerts = {}
        alert_history = []
        
        for service_name in services:
            alert_status = await service.get_alert_status(service_name)
            if alert_status.threshold_exceeded:
                active_alerts[service_name] = {
                    "alert_type": getattr(alert_status, 'alert_type', 'unknown'),
                    "current_value": getattr(alert_status, 'current_value', 0),
                    "threshold_value": getattr(alert_status, 'threshold_value', 0),
                    "alert_sent": alert_status.alert_sent
                }
        
        return {
            "active_alerts": active_alerts,
            "alert_history": alert_history,
            "total_active_alerts": len(active_alerts),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )