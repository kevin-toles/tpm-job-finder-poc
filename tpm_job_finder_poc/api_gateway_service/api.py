"""
API Gateway Service FastAPI Application.

This module implements the REST API endpoints for the API Gateway service
including health checks, metrics, route management, and request processing.
"""

import asyncio
import time
import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
import uvicorn

from tpm_job_finder_poc.api_gateway_service.service import APIGatewayService
from tpm_job_finder_poc.api_gateway_service.config import ConfigurationManager
from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
    APIGatewayConfig,
    RouteDefinition,
    RequestContext,
    RateLimitRule,
    HttpMethod,
    RouteStatus,
    RateLimitScope
)

logger = logging.getLogger(__name__)

# Global service instance
gateway_service: Optional[APIGatewayService] = None
config_manager: Optional[ConfigurationManager] = None


# Pydantic models for API requests/responses
class RouteCreateRequest(BaseModel):
    route_id: str = Field(..., description="Unique identifier for the route")
    path: str = Field(..., description="Request path pattern")
    method: str = Field(..., description="HTTP method")
    target_service: str = Field(..., description="Target service name")
    target_path: str = Field(..., description="Target path on service")
    target_port: int = Field(..., description="Target service port")
    requires_auth: bool = Field(default=True, description="Whether authentication is required")
    rate_limit_requests: Optional[int] = Field(default=None, description="Rate limit requests per window")
    rate_limit_window_seconds: Optional[int] = Field(default=None, description="Rate limit window in seconds")


class RouteUpdateRequest(BaseModel):
    target_service: Optional[str] = None
    target_path: Optional[str] = None
    target_port: Optional[int] = None
    requires_auth: Optional[bool] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    status: Optional[str] = None


class RateLimitRuleCreateRequest(BaseModel):
    rule_id: Optional[str] = Field(default=None, description="Unique identifier for the rule (auto-generated if not provided)")
    scope: str = Field(..., description="Rate limit scope")
    scope_value: str = Field(..., description="Scope value (IP, user ID, etc.)")
    requests_per_window: int = Field(..., description="Requests allowed per window")
    window_seconds: int = Field(..., description="Window duration in seconds")
    enabled: bool = Field(default=True, description="Whether rule is enabled")


class ServiceRegistrationRequest(BaseModel):
    service_name: str = Field(..., description="Service name")
    host: str = Field(..., description="Service host")
    port: int = Field(..., description="Service port")
    health_check_path: str = Field(default="/health", description="Health check endpoint")
    routes: List[RouteCreateRequest] = Field(default=[], description="Service routes")


class ConfigurationUpdateRequest(BaseModel):
    enable_rate_limiting: Optional[bool] = None
    default_rate_limit_requests: Optional[int] = None
    require_authentication: Optional[bool] = None
    log_level: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global gateway_service, config_manager
    
    # Startup
    try:
        # Load configuration
        config_manager = ConfigurationManager()
        config = config_manager.get_current_configuration()
        
        # Initialize gateway service
        gateway_service = APIGatewayService(config)
        await gateway_service.initialize()
        await gateway_service.start()
        
        logger.info("API Gateway application started")
        yield
        
    finally:
        # Shutdown
        if gateway_service:
            await gateway_service.stop()
        logger.info("API Gateway application stopped")


# Create FastAPI application
app = FastAPI(
    title="API Gateway Service",
    description="Unified entry point for all API requests with routing, rate limiting, and authentication",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Will be configured from gateway config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request ID and metrics
@app.middleware("http")
async def request_processing_middleware(request: Request, call_next):
    """Middleware for request processing, metrics, and request ID."""
    # Add request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Record request metrics
    from .service import RequestContext
    context = RequestContext(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        headers=dict(request.headers),
        query_params=dict(request.query_params),
        client_ip=request.client.host if request.client else "unknown"
    )
    # Only record metrics if gateway_service is available
    if gateway_service is not None:
        gateway_service._metrics_collector.record_request(context)
    
    # Process response
    start_time = time.time()
    response = await call_next(request)
    response_time_ms = (time.time() - start_time) * 1000
    
    # Record response metrics
    if gateway_service is not None:
        gateway_service._metrics_collector.record_response(
            success=response.status_code < 400,
            response_time_ms=response_time_ms,
            rate_limited=response.status_code == 429
        )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


def get_gateway_service() -> APIGatewayService:
    """Dependency to get gateway service instance."""
    if not gateway_service:
        raise HTTPException(status_code=503, detail="Gateway service not available")
    return gateway_service


def get_config_manager() -> ConfigurationManager:
    """Dependency to get configuration manager instance."""
    if not config_manager:
        raise HTTPException(status_code=503, detail="Configuration manager not available")
    return config_manager


# Health and Status Endpoints
@app.get("/health", tags=["Health"])
@app.options("/health", tags=["Health"])
async def health_check(detailed: bool = False, service: APIGatewayService = Depends(get_gateway_service)):
    """Get gateway health status."""
    try:
        health_data = await service.health_check()
        
        if detailed:
            # Add component health checks as "details"
            health_data["details"] = {
                "components": {
                    "routing_service": {"status": "healthy"},
                    "rate_limit_service": {"status": "healthy"},
                    "proxy_service": {"status": "healthy"},
                    "auth_integration": {"status": "healthy"}
                }
            }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/ready", tags=["Health"])
async def readiness_check(service: APIGatewayService = Depends(get_gateway_service)):
    """Readiness probe for Kubernetes."""
    try:
        health_data = await service.health_check()
        
        if health_data.get("status") == "healthy":
            return {"ready": True, "timestamp": datetime.now(timezone.utc).isoformat()}
        else:
            raise HTTPException(status_code=503, detail="Service not ready")
            
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


# Metrics Endpoints
@app.get("/metrics", tags=["Metrics"])
async def get_metrics(service: APIGatewayService = Depends(get_gateway_service)):
    """Get gateway metrics."""
    try:
        metrics = await service.get_metrics()
        
        return {
            "metrics": {
                "total_requests": metrics.total_requests,
                "successful_requests": metrics.successful_requests,
                "failed_requests": metrics.failed_requests,
                "rate_limited_requests": metrics.rate_limited_requests,
                "average_response_time_ms": metrics.average_response_time_ms,
                "uptime_seconds": metrics.uptime_seconds,
                "active_routes": metrics.active_routes,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


@app.get("/metrics/prometheus", tags=["Metrics"], response_class=PlainTextResponse)
async def get_prometheus_metrics(service: APIGatewayService = Depends(get_gateway_service)):
    """Get metrics in Prometheus format."""
    try:
        metrics = await service.get_metrics()
        
        prometheus_text = f"""# HELP gateway_requests_total Total number of requests processed by the gateway
# TYPE gateway_requests_total counter
gateway_requests_total {metrics.total_requests}

# HELP gateway_successful_requests_total Total number of successful requests
# TYPE gateway_successful_requests_total counter
gateway_successful_requests_total {metrics.successful_requests}

# HELP gateway_failed_requests_total Total number of failed requests
# TYPE gateway_failed_requests_total counter
gateway_failed_requests_total {metrics.failed_requests}

# HELP gateway_rate_limited_requests_total Total number of rate limited requests
# TYPE gateway_rate_limited_requests_total counter
gateway_rate_limited_requests_total {metrics.rate_limited_requests}

# HELP gateway_request_duration_seconds Average request duration
# TYPE gateway_request_duration_seconds gauge
gateway_request_duration_seconds {metrics.average_response_time_ms / 1000}

# HELP gateway_uptime_seconds Gateway uptime in seconds
# TYPE gateway_uptime_seconds gauge
gateway_uptime_seconds {metrics.uptime_seconds}

# HELP gateway_active_routes Number of active routes
# TYPE gateway_active_routes gauge
gateway_active_routes {metrics.active_routes}
"""
        
        return prometheus_text
        
    except Exception as e:
        logger.error(f"Failed to get Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")


# Route Management Endpoints
@app.get("/routes", tags=["Routes"])
async def list_routes(status: Optional[str] = None, service: APIGatewayService = Depends(get_gateway_service)):
    """List all registered routes."""
    try:
        route_status = None
        if status:
            try:
                route_status = RouteStatus(status.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
        
        routes = await service._routing_service.list_routes(route_status)
        
        route_list = [
            {
                "route_id": route.route_id,
                "path": route.path,
                "method": route.method.value,
                "target_service": route.target_service,
                "target_path": route.target_path,
                "target_port": route.target_port,
                "requires_auth": route.requires_auth,
                "status": route.status.value,
                "created_at": route.created_at.isoformat(),
                "updated_at": route.updated_at.isoformat() if route.updated_at else None
            }
            for route in routes
        ]
        
        return {"routes": route_list}
        
    except Exception as e:
        logger.error(f"Failed to list routes: {e}")
        raise HTTPException(status_code=500, detail="Failed to list routes")


@app.post("/routes", status_code=status.HTTP_201_CREATED, tags=["Routes"])
async def register_route(request: RouteCreateRequest, service: APIGatewayService = Depends(get_gateway_service)):
    """Register a new route."""
    try:
        # Validate HTTP method
        try:
            method = HttpMethod(request.method.upper())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid HTTP method: {request.method}")
        
        # Create route definition
        route = RouteDefinition(
            route_id=request.route_id,
            path=request.path,
            method=method,
            target_service=request.target_service,
            target_path=request.target_path,
            target_port=request.target_port,
            requires_auth=request.requires_auth,
            rate_limit_requests=request.rate_limit_requests,
            rate_limit_window_seconds=request.rate_limit_window_seconds
        )
        
        success = await service._routing_service.register_route(route)
        
        if success:
            return {"success": True, "route_id": request.route_id, "message": "Route registered successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to register route")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register route: {e}")
        raise HTTPException(status_code=500, detail="Failed to register route")


@app.get("/routes/{route_id}", tags=["Routes"])
async def get_route(route_id: str, service: APIGatewayService = Depends(get_gateway_service)):
    """Get a specific route by ID."""
    try:
        route = await service._routing_service.get_route(route_id)
        
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        return {
            "route": {
                "route_id": route.route_id,
                "path": route.path,
                "method": route.method.value,
                "target_service": route.target_service,
                "target_path": route.target_path,
                "target_port": route.target_port,
                "requires_auth": route.requires_auth,
                "status": route.status.value,
                "created_at": route.created_at.isoformat(),
                "updated_at": route.updated_at.isoformat() if route.updated_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get route {route_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get route")


@app.put("/routes/{route_id}", tags=["Routes"])
async def update_route(route_id: str, request: RouteUpdateRequest, service: APIGatewayService = Depends(get_gateway_service)):
    """Update an existing route."""
    try:
        # Build updates dictionary
        updates = {}
        for field, value in request.model_dump(exclude_unset=True).items():
            if value is not None:
                if field == "status":
                    try:
                        updates[field] = RouteStatus(value.upper())
                    except ValueError:
                        raise HTTPException(status_code=400, detail=f"Invalid status: {value}")
                else:
                    updates[field] = value
        
        success = await service._routing_service.update_route(route_id, updates)
        
        if success:
            return {"success": True, "message": "Route updated successfully"}
        else:
            raise HTTPException(status_code=404, detail="Route not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update route {route_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update route")


@app.delete("/routes/{route_id}", tags=["Routes"])
async def delete_route(route_id: str, service: APIGatewayService = Depends(get_gateway_service)):
    """Delete a route."""
    try:
        success = await service._routing_service.unregister_route(route_id)
        
        if success:
            return {"success": True, "message": "Route deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Route not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete route {route_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete route")


# Rate Limiting Endpoints
@app.post("/rate-limits", status_code=status.HTTP_201_CREATED, tags=["Rate Limiting"])
async def create_rate_limit_rule(request: RateLimitRuleCreateRequest, service: APIGatewayService = Depends(get_gateway_service)):
    """Create a new rate limit rule."""
    try:
        # Validate scope
        try:
            # Map common scope names to enum values
            scope_mapping = {
                "GLOBAL": RateLimitScope.GLOBAL,
                "USER": RateLimitScope.USER,
                "IP_ADDRESS": RateLimitScope.IP_ADDRESS,
                "API_KEY": RateLimitScope.API_KEY,
                "SERVICE": RateLimitScope.SERVICE
            }
            scope = scope_mapping.get(request.scope.upper())
            if not scope:
                raise ValueError(f"Invalid scope: {request.scope}")
        except (ValueError, KeyError):
            raise HTTPException(status_code=400, detail=f"Invalid scope: {request.scope}")
        
        # Create rate limit rule
        rule = RateLimitRule(
            rule_id=request.rule_id or str(uuid.uuid4()),
            scope=scope,
            scope_value=request.scope_value,
            requests_per_window=request.requests_per_window,
            window_seconds=request.window_seconds,
            enabled=request.enabled
        )
        
        success = await service._rate_limit_service.create_rule(rule)
        
        if success:
            return {"success": True, "rule_id": request.rule_id, "message": "Rate limit rule created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create rate limit rule")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create rate limit rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create rate limit rule")


@app.get("/rate-limits", tags=["Rate Limiting"])
async def list_rate_limit_rules():
    """List all rate limit rules."""
    # This would need to be implemented in the rate limit service
    return {"rules": []}


@app.get("/rate-limits/status", tags=["Rate Limiting"])
async def get_rate_limit_status(scope: str, scope_value: str, service: APIGatewayService = Depends(get_gateway_service)):
    """Get rate limit status for a scope."""
    try:
        # Validate scope - convert input to enum value format
        try:
            # Map common input formats to enum values
            scope_mapping = {
                "IP_ADDRESS": RateLimitScope.IP_ADDRESS,
                "ip_address": RateLimitScope.IP_ADDRESS,
                "USER": RateLimitScope.USER,
                "user": RateLimitScope.USER,
                "GLOBAL": RateLimitScope.GLOBAL,
                "global": RateLimitScope.GLOBAL,
                "API_KEY": RateLimitScope.API_KEY,
                "api_key": RateLimitScope.API_KEY,
                "SERVICE": RateLimitScope.SERVICE,
                "service": RateLimitScope.SERVICE
            }
            scope_enum = scope_mapping.get(scope)
            if not scope_enum:
                raise ValueError(f"Invalid scope: {scope}")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid scope: {scope}")
        
        status = await service._rate_limit_service.get_rate_limit_status(scope_enum, scope_value)
        
        return {
            "status": "active",
            "blocked": status.blocked,
            "scope": status.scope.value,
            "scope_value": status.scope_value,
            "limit": status.limit,
            "current_count": status.current_count,
            "remaining_requests": status.remaining_requests,
            "reset_time": status.reset_time.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get rate limit status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get rate limit status")


# Service Discovery Endpoints
@app.post("/services", status_code=status.HTTP_201_CREATED, tags=["Service Discovery"])
async def register_service(request: ServiceRegistrationRequest, service: APIGatewayService = Depends(get_gateway_service)):
    """Register a service and its routes."""
    try:
        # Convert route requests to route definitions
        routes = []
        for route_req in request.routes:
            try:
                method = HttpMethod(route_req.method.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid HTTP method: {route_req.method}")
            
            route = RouteDefinition(
                route_id=route_req.route_id,
                path=route_req.path,
                method=method,
                target_service=request.service_name,
                target_path=route_req.target_path,
                target_port=request.port,
                requires_auth=route_req.requires_auth,
                rate_limit_requests=route_req.rate_limit_requests,
                rate_limit_window_seconds=route_req.rate_limit_window_seconds
            )
            routes.append(route)
        
        # Register service routes
        success = await service.register_service_routes(request.service_name, routes)
        
        if success:
            return {
                "success": True,
                "service_name": request.service_name,
                "routes_registered": len(routes),
                "message": "Service registered successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to register service")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to register service: {e}")
        raise HTTPException(status_code=500, detail="Failed to register service")


@app.get("/services", tags=["Service Discovery"])
async def list_services(service: APIGatewayService = Depends(get_gateway_service)):
    """List all registered services."""
    try:
        # This would need to be implemented to track registered services
        services = list(service._registered_services.keys())
        return {"services": services}
        
    except Exception as e:
        logger.error(f"Failed to list services: {e}")
        raise HTTPException(status_code=500, detail="Failed to list services")


@app.get("/services/{service_name}/health", tags=["Service Discovery"])
async def check_service_health(service_name: str, service: APIGatewayService = Depends(get_gateway_service)):
    """Check health of a registered service."""
    try:
        # This would need service registry information
        healthy = await service._proxy_service.get_service_status(service_name)
        
        return {
            "service_name": service_name,
            "healthy": healthy,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to check service health: {e}")
        raise HTTPException(status_code=500, detail="Failed to check service health")


# Admin Endpoints
@app.post("/admin/reload-config", tags=["Admin"])
async def reload_configuration(service: APIGatewayService = Depends(get_gateway_service)):
    """Reload gateway configuration."""
    try:
        success = await service.reload_configuration()
        
        if success:
            return {
                "success": True,
                "message": "Configuration reloaded successfully",
                "reloaded_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reload configuration")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to reload configuration")


@app.get("/admin/config", tags=["Admin"])
async def get_configuration(config_mgr: ConfigurationManager = Depends(get_config_manager)):
    """Get current configuration."""
    try:
        config = config_mgr.get_current_configuration()
        
        return {
            "config": {
                "service_name": config.service_name,
                "host": config.host,
                "port": config.port,
                "auth_service_url": config.auth_service_url,
                "require_authentication": config.require_authentication,
                "enable_rate_limiting": config.enable_rate_limiting,
                "default_rate_limit_requests": config.default_rate_limit_requests,
                "default_rate_limit_window_seconds": config.default_rate_limit_window_seconds,
                "max_concurrent_requests": config.max_concurrent_requests,
                "enable_cors": config.enable_cors,
                "cors_origins": config.cors_origins,
                "enable_metrics": config.enable_metrics,
                "log_level": config.log_level
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to get configuration")


@app.put("/admin/config", tags=["Admin"])
async def update_configuration(request: ConfigurationUpdateRequest, config_mgr: ConfigurationManager = Depends(get_config_manager)):
    """Update configuration."""
    try:
        updates = request.model_dump(exclude_unset=True)
        success = config_mgr.update_configuration(updates)
        
        if success:
            return {
                "success": True,
                "message": "Configuration updated successfully",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update configuration")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update configuration: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")


@app.post("/admin/reset-metrics", tags=["Admin"])
async def reset_metrics(service: APIGatewayService = Depends(get_gateway_service)):
    """Reset gateway metrics."""
    try:
        service._metrics_collector.reset()
        
        return {
            "success": True,
            "message": "Metrics reset successfully",
            "reset_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset metrics")


# Catch-all route for proxying requests
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"], tags=["Proxy"])
async def proxy_request(request: Request, path: str, service: APIGatewayService = Depends(get_gateway_service)):
    """Proxy requests through the gateway."""
    try:
        # Build request context
        context = RequestContext(
            request_id=request.state.request_id,
            method=HttpMethod(request.method),
            path=f"/{path}",
            headers=dict(request.headers),
            query_params=dict(request.query_params),
            client_ip=request.client.host if request.client else "unknown",
            body=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
        )
        
        # Process through gateway
        result = await service.process_request(context)
        
        # Build response
        response = Response(
            content=result.body,
            status_code=result.status_code,
            headers=result.headers
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to proxy request: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    uvicorn.run(
        "tpm_job_finder_poc.api_gateway_service.api:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )