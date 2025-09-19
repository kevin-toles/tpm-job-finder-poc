"""
API Gateway Service Contracts

Interface definitions for API Gateway microservice including routing,
rate limiting, authentication integration, and unified entry point management.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union, Protocol
from enum import Enum
import uuid

# ================================================================================
# Core Data Models
# ================================================================================

class HttpMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class RouteStatus(str, Enum):
    """Route availability status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class RateLimitScope(str, Enum):
    """Rate limiting scope types."""
    GLOBAL = "global"
    USER = "user"
    IP_ADDRESS = "ip_address"
    API_KEY = "api_key"
    SERVICE = "service"

@dataclass
class RouteDefinition:
    """Definition of a routable endpoint."""
    route_id: str
    path: str
    method: HttpMethod
    target_service: str
    target_path: str
    target_port: int
    status: RouteStatus = RouteStatus.ACTIVE
    requires_auth: bool = True
    rate_limit_scope: Optional[RateLimitScope] = None
    rate_limit_requests: Optional[int] = None
    rate_limit_window_seconds: Optional[int] = None
    timeout_seconds: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RateLimitRule:
    """Rate limiting rule configuration."""
    rule_id: str
    scope: RateLimitScope
    scope_value: Optional[str]  # e.g., specific user_id, ip_address, etc.
    requests_per_window: int
    window_seconds: int
    burst_allowance: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RateLimitStatus:
    """Current rate limit status for a request."""
    scope: RateLimitScope
    scope_value: str
    current_count: int
    limit: int
    window_seconds: int
    reset_time: datetime
    blocked: bool = False
    remaining_requests: int = 0

@dataclass
class RequestContext:
    """Context information for an incoming request."""
    request_id: str
    method: HttpMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    client_ip: str
    user_agent: Optional[str] = None
    user_id: Optional[str] = None
    api_key: Optional[str] = None
    authenticated: bool = False
    auth_token: Optional[str] = None
    body: Optional[bytes] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class RoutingResult:
    """Result of route resolution."""
    success: bool
    route: Optional[RouteDefinition] = None
    target_url: str = ""
    error_message: str = ""
    status_code: int = 200
    should_proxy: bool = True

@dataclass
class ProxyRequest:
    """Request to be proxied to target service."""
    request_id: str
    target_url: str
    method: HttpMethod
    headers: Dict[str, str]
    body: Optional[bytes] = None
    timeout_seconds: float = 30.0

@dataclass
class ProxyResponse:
    """Response from proxied service."""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: bytes
    response_time_ms: float
    success: bool = True
    error_message: str = ""

@dataclass
class GatewayMetrics:
    """API Gateway operational metrics."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    authentication_failures: int = 0
    average_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    active_routes: int = 0
    active_connections: int = 0

@dataclass
class GatewayResponse:
    """Response from API Gateway processing."""
    success: bool
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b''
    error_message: Optional[str] = None
    response_time_ms: Optional[float] = None
    request_id: Optional[str] = None

@dataclass
class RouteResolutionResult:
    """Result of route resolution attempt."""
    success: bool
    route: Optional['RouteDefinition'] = None
    target_url: Optional[str] = None
    should_proxy: bool = False
    error_message: Optional[str] = None
    status_code: int = 200

# ================================================================================
# Service Interfaces
# ================================================================================

class IRoutingService(Protocol):
    """Interface for request routing management."""
    
    async def register_route(self, route: RouteDefinition) -> bool:
        """Register a new route definition."""
        ...
    
    async def unregister_route(self, route_id: str) -> bool:
        """Remove a route definition."""
        ...
    
    async def update_route(self, route_id: str, route: RouteDefinition) -> bool:
        """Update an existing route definition."""
        ...
    
    async def resolve_route(self, method: HttpMethod, path: str) -> RoutingResult:
        """Resolve a request to a target route."""
        ...
    
    async def list_routes(self, status: Optional[RouteStatus] = None) -> List[RouteDefinition]:
        """List all registered routes."""
        ...
    
    async def get_route(self, route_id: str) -> Optional[RouteDefinition]:
        """Get specific route by ID."""
        ...

class IRateLimitService(Protocol):
    """Interface for rate limiting management."""
    
    async def create_rule(self, rule: RateLimitRule) -> bool:
        """Create a new rate limit rule."""
        ...
    
    async def check_rate_limit(self, context: RequestContext) -> RateLimitStatus:
        """Check if request is within rate limits."""
        ...
    
    async def record_request(self, context: RequestContext) -> bool:
        """Record a request for rate limiting tracking."""
        ...
    
    async def get_rate_limit_status(self, scope: RateLimitScope, scope_value: str) -> Optional[RateLimitStatus]:
        """Get current rate limit status for scope."""
        ...
    
    async def reset_rate_limit(self, scope: RateLimitScope, scope_value: str) -> bool:
        """Reset rate limit counters for scope."""
        ...

class IProxyService(Protocol):
    """Interface for request proxying to backend services."""
    
    async def proxy_request(self, request: ProxyRequest) -> ProxyResponse:
        """Proxy request to target service."""
        ...
    
    async def health_check_service(self, service_name: str) -> bool:
        """Check if target service is healthy."""
        ...
    
    async def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get detailed status of target service."""
        ...

class IAPIGatewayService(Protocol):
    """Main API Gateway service interface."""
    
    async def initialize(self) -> None:
        """Initialize the API Gateway service."""
        ...
    
    async def start(self) -> None:
        """Start the API Gateway service."""
        ...
    
    async def stop(self) -> None:
        """Stop the API Gateway service."""
        ...
    
    async def process_request(self, context: RequestContext) -> ProxyResponse:
        """Process incoming request through gateway pipeline."""
        ...
    
    async def register_service_routes(self, service_name: str, routes: List[RouteDefinition]) -> bool:
        """Register routes for a backend service."""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Get gateway health status."""
        ...
    
    async def get_metrics(self) -> GatewayMetrics:
        """Get gateway operational metrics."""
        ...
    
    async def reload_configuration(self) -> bool:
        """Reload gateway configuration."""
        ...

# ================================================================================
# Configuration Models
# ================================================================================

@dataclass
class APIGatewayConfig:
    """Configuration for API Gateway service."""
    # Service Configuration
    service_name: str = "api_gateway_service"
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    log_level: str = "INFO"
    
    # Authentication Configuration
    auth_service_url: str = "http://localhost:8001"
    require_authentication: bool = True
    auth_timeout_seconds: float = 5.0
    
    # Rate Limiting Configuration
    enable_rate_limiting: bool = True
    default_rate_limit_requests: int = 1000
    default_rate_limit_window_seconds: int = 3600
    rate_limit_storage_url: str = "redis://localhost:6379/1"
    
    # Proxy Configuration
    default_proxy_timeout_seconds: float = 30.0
    request_timeout_seconds: float = 30.0
    max_concurrent_requests: int = 1000
    enable_request_logging: bool = True
    enable_response_caching: bool = False
    
    # Health Monitoring Configuration
    health_check_interval_seconds: int = 30
    health_check_timeout_seconds: float = 5.0
    unhealthy_threshold: int = 3
    
    # Metrics Configuration
    enable_metrics: bool = True
    metrics_retention_seconds: int = 3600
    
    # Security Configuration
    enable_cors: bool = True
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    max_request_size_bytes: int = 10 * 1024 * 1024  # 10MB
    
    # Service Discovery
    service_registry: Dict[str, Dict[str, Any]] = field(default_factory=dict)

# ================================================================================
# Exception Classes
# ================================================================================

class APIGatewayError(Exception):
    """Base exception for API Gateway errors."""
    pass

class RoutingError(APIGatewayError):
    """Raised when route resolution fails."""
    pass

class RateLimitExceededError(APIGatewayError):
    """Raised when rate limit is exceeded."""
    pass

class AuthenticationError(APIGatewayError):
    """Raised when authentication fails."""
    pass

class ProxyError(APIGatewayError):
    """Raised when request proxying fails."""
    pass

class ConfigurationError(APIGatewayError):
    """Raised when configuration is invalid."""
    pass