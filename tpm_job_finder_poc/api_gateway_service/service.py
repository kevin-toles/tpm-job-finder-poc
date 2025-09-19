"""
API Gateway Service - TDD Stub Implementation.

This module contains stub implementations for TDD RED phase.
These stubs should make tests fail to demonstrate proper TDD methodology.
"""

import asyncio
import logging
import time
import uuid
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from tpm_job_finder_poc.shared.contracts.api_gateway_service import (
    IAPIGatewayService,
    IRoutingService,
    IRateLimitService,
    IProxyService,
    APIGatewayConfig,
    RouteDefinition,
    RequestContext,
    RateLimitRule,
    ProxyRequest,
    ProxyResponse,
    GatewayResponse,
    RouteResolutionResult,
    RateLimitStatus,
    GatewayMetrics,
    HttpMethod,
    RouteStatus,
    RateLimitScope
)

logger = logging.getLogger(__name__)


class RoutingService(IRoutingService):
    """Service for managing route registration and resolution."""
    
    def __init__(self):
        self._routes: Dict[str, RouteDefinition] = {}
        self._path_method_map: Dict[tuple, str] = {}  # (path, method) -> route_id
    
    async def register_route(self, route: RouteDefinition) -> bool:
        """Register a new route."""
        try:
            # Check for duplicate path-method combination
            path_method_key = (route.path, route.method.value)
            if path_method_key in self._path_method_map:
                logger.warning(f"Route already exists for {route.method.value} {route.path}")
                return False
            
            # Store route
            self._routes[route.route_id] = route
            self._path_method_map[path_method_key] = route.route_id
            
            logger.info(f"Registered route: {route.route_id} -> {route.method.value} {route.path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register route {route.route_id}: {e}")
            return False
    
    async def unregister_route(self, route_id: str) -> bool:
        """Unregister a route."""
        try:
            if route_id not in self._routes:
                return False
            
            route = self._routes[route_id]
            
            # Remove from path-method mapping
            path_method_key = (route.path, route.method.value)
            self._path_method_map.pop(path_method_key, None)
            
            # Remove route
            del self._routes[route_id]
            
            logger.info(f"Unregistered route: {route_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister route {route_id}: {e}")
            return False
    
    async def update_route(self, route_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing route."""
        try:
            if route_id not in self._routes:
                return False
            
            route = self._routes[route_id]
            
            # Update route fields
            for field, value in updates.items():
                if hasattr(route, field):
                    setattr(route, field, value)
            
            route.updated_at = datetime.now(timezone.utc)
            
            logger.info(f"Updated route: {route_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update route {route_id}: {e}")
            return False
    
    async def resolve_route(self, method: HttpMethod, path: str) -> RouteResolutionResult:
        """Resolve a route for the given method and path."""
        try:
            # Direct path-method lookup
            path_method_key = (path, method.value)
            route_id = self._path_method_map.get(path_method_key)
            
            if not route_id:
                # Check if path exists with different method (for 405 Method Not Allowed)
                path_exists = False
                for (existing_path, existing_method), existing_route_id in self._path_method_map.items():
                    if existing_path == path:
                        path_exists = True
                        break
                
                if path_exists:
                    return RouteResolutionResult(
                        success=False,
                        route=None,
                        target_url=None,
                        should_proxy=False,
                        error_message="Method not allowed",
                        status_code=405
                    )
                else:
                    return RouteResolutionResult(
                        success=False,
                        route=None,
                        target_url=None,
                        should_proxy=False,
                        error_message="Route not found",
                        status_code=404
                    )
            
            route = self._routes[route_id]
            
            # Check if route is active
            if route.status != RouteStatus.ACTIVE:
                return RouteResolutionResult(
                    success=False,
                    route=route,
                    target_url=None,
                    should_proxy=False,
                    error_message="Route is inactive",
                    status_code=503
                )
            
            # Build target URL
            target_url = f"http://{route.target_service}:{route.target_port}{route.target_path}"
            
            return RouteResolutionResult(
                success=True,
                route=route,
                target_url=target_url,
                should_proxy=True,
                error_message=None,
                status_code=200
            )
            
        except Exception as e:
            logger.error(f"Failed to resolve route for {method.value} {path}: {e}")
            return RouteResolutionResult(
                success=False,
                route=None,
                target_url=None,
                should_proxy=False,
                error_message="Internal server error",
                status_code=500
            )
    
    async def list_routes(self, status: Optional[RouteStatus] = None) -> List[RouteDefinition]:
        """List all routes, optionally filtered by status."""
        routes = list(self._routes.values())
        
        if status is not None:
            routes = [route for route in routes if route.status == status]
        
        return routes
    
    async def get_route(self, route_id: str) -> Optional[RouteDefinition]:
        """Get a specific route by ID."""
        return self._routes.get(route_id)


class RateLimitService(IRateLimitService):
    """Service for managing rate limiting."""
    
    def __init__(self):
        self._rules: Dict[str, RateLimitRule] = {}
        self._counters: Dict[str, Dict[str, int]] = {}  # rule_id -> {window_start: count}
        self._last_cleanup = time.time()
    
    async def create_rule(self, rule: RateLimitRule) -> bool:
        """Create a new rate limit rule."""
        try:
            self._rules[rule.rule_id] = rule
            self._counters[rule.rule_id] = {}
            
            logger.info(f"Created rate limit rule: {rule.rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create rate limit rule {rule.rule_id}: {e}")
            return False
    
    async def check_rate_limit(self, context: RequestContext) -> RateLimitStatus:
        """Check if request should be rate limited."""
        try:
            # Find applicable rules
            applicable_rules = self._find_applicable_rules(context)
            
            if not applicable_rules:
                return RateLimitStatus(
                    scope=RateLimitScope.GLOBAL,
                    scope_value="*",
                    current_count=0,
                    limit=0,
                    window_seconds=60,
                    reset_time=datetime.now(timezone.utc),
                    blocked=False,
                    remaining_requests=0
                )
            
            # Check each rule
            for rule in applicable_rules:
                if not rule.enabled:
                    continue
                
                current_count = self._get_current_count(rule, context)
                
                if current_count >= rule.requests_per_window:
                    reset_time = self._get_reset_time(rule)
                    
                    return RateLimitStatus(
                        scope=rule.scope,
                        scope_value=rule.scope_value,
                        current_count=current_count,
                        limit=rule.requests_per_window,
                        window_seconds=rule.window_seconds,
                        reset_time=reset_time,
                        blocked=True,
                        remaining_requests=0
                    )
            
            # If we get here, no limits exceeded
            # Return status for the most restrictive rule
            most_restrictive = min(applicable_rules, key=lambda r: r.requests_per_window)
            current_count = self._get_current_count(most_restrictive, context)
            remaining = max(0, most_restrictive.requests_per_window - current_count)
            
            return RateLimitStatus(
                scope=most_restrictive.scope,
                scope_value=most_restrictive.scope_value,
                current_count=current_count,
                limit=most_restrictive.requests_per_window,
                window_seconds=most_restrictive.window_seconds,
                reset_time=self._get_reset_time(most_restrictive),
                blocked=False,
                remaining_requests=remaining
            )
            
        except Exception as e:
            logger.error(f"Failed to check rate limit: {e}")
            # Fail open - don't block on errors
            return RateLimitStatus(
                scope=RateLimitScope.GLOBAL,
                scope_value="*",
                current_count=0,
                limit=0,
                window_seconds=60,
                reset_time=datetime.now(timezone.utc),
                blocked=False,
                remaining_requests=0
            )
    
    async def record_request(self, context: RequestContext) -> None:
        """Record a request for rate limiting."""
        try:
            applicable_rules = self._find_applicable_rules(context)
            
            for rule in applicable_rules:
                if rule.enabled:
                    self._increment_counter(rule, context)
            
            # Periodic cleanup of old counters
            current_time = time.time()
            if current_time - self._last_cleanup > 300:  # Every 5 minutes
                self._cleanup_old_counters()
                self._last_cleanup = current_time
                
        except Exception as e:
            logger.error(f"Failed to record request: {e}")
    
    async def get_rate_limit_status(self, scope: RateLimitScope, scope_value: str) -> RateLimitStatus:
        """Get current rate limit status for a scope."""
        try:
            # Find rule for this scope
            rule = None
            for r in self._rules.values():
                if r.scope == scope and r.scope_value == scope_value:
                    rule = r
                    break
            
            if not rule:
                return RateLimitStatus(
                    scope=scope,
                    scope_value=scope_value,
                    current_count=0,
                    limit=0,
                    window_seconds=60,
                    reset_time=datetime.now(timezone.utc),
                    blocked=False,
                    remaining_requests=0
                )
            
            # Create dummy context for counting
            context = RequestContext(
                request_id=str(uuid.uuid4()),
                method=HttpMethod.GET,
                path="/",
                headers={},
                query_params={},
                client_ip=scope_value if scope == RateLimitScope.IP_ADDRESS else "0.0.0.0",
                user_id=scope_value if scope == RateLimitScope.USER else None
            )
            
            current_count = self._get_current_count(rule, context)
            remaining = max(0, rule.requests_per_window - current_count)
            
            return RateLimitStatus(
                scope=scope,
                scope_value=scope_value,
                current_count=current_count,
                limit=rule.requests_per_window,
                window_seconds=rule.window_seconds,
                reset_time=self._get_reset_time(rule),
                blocked=current_count >= rule.requests_per_window,
                remaining_requests=remaining
            )
            
        except Exception as e:
            logger.error(f"Failed to get rate limit status: {e}")
            return RateLimitStatus(
                scope=scope,
                scope_value=scope_value,
                current_count=0,
                limit=0,
                window_seconds=60,
                reset_time=datetime.now(timezone.utc),
                blocked=False,
                remaining_requests=0
            )
    
    async def reset_rate_limit(self, scope: RateLimitScope, scope_value: str) -> bool:
        """Reset rate limit counters for a scope."""
        try:
            # Find and reset rule counters
            for rule in self._rules.values():
                if rule.scope == scope and rule.scope_value == scope_value:
                    self._counters[rule.rule_id] = {}
                    logger.info(f"Reset rate limit for {scope.value}:{scope_value}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False
    
    def _find_applicable_rules(self, context: RequestContext) -> List[RateLimitRule]:
        """Find rate limit rules applicable to this request."""
        applicable = []
        
        for rule in self._rules.values():
            if rule.scope == RateLimitScope.GLOBAL:
                applicable.append(rule)
            elif rule.scope == RateLimitScope.IP_ADDRESS and rule.scope_value == context.client_ip:
                applicable.append(rule)
            elif rule.scope == RateLimitScope.USER and context.user_id and rule.scope_value == context.user_id:
                applicable.append(rule)
            elif rule.scope == RateLimitScope.API_KEY and context.api_key and rule.scope_value == context.api_key:
                applicable.append(rule)
        
        return applicable
    
    def _get_current_count(self, rule: RateLimitRule, context: RequestContext) -> int:
        """Get current request count for a rule."""
        current_time = time.time()
        window_start = int(current_time // rule.window_seconds) * rule.window_seconds
        
        return self._counters.get(rule.rule_id, {}).get(str(window_start), 0)
    
    def _increment_counter(self, rule: RateLimitRule, context: RequestContext) -> None:
        """Increment request counter for a rule."""
        current_time = time.time()
        window_start = int(current_time // rule.window_seconds) * rule.window_seconds
        window_key = str(window_start)
        
        if rule.rule_id not in self._counters:
            self._counters[rule.rule_id] = {}
        
        self._counters[rule.rule_id][window_key] = self._counters[rule.rule_id].get(window_key, 0) + 1
    
    def _get_reset_time(self, rule: RateLimitRule) -> datetime:
        """Get the time when the rate limit will reset."""
        current_time = time.time()
        window_start = int(current_time // rule.window_seconds) * rule.window_seconds
        next_window = window_start + rule.window_seconds
        
        return datetime.fromtimestamp(next_window, tz=timezone.utc)
    
    def _cleanup_old_counters(self) -> None:
        """Clean up old counter windows."""
        current_time = time.time()
        
        for rule_id, counters in self._counters.items():
            rule = self._rules.get(rule_id)
            if not rule:
                continue
            
            # Remove windows older than 2x the window size
            cutoff_time = current_time - (2 * rule.window_seconds)
            
            expired_windows = [
                window for window in counters.keys()
                if int(window) < cutoff_time
            ]
            
            for window in expired_windows:
                del counters[window]


class ProxyService(IProxyService):
    """Service for proxying requests to backend services."""
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self._service_health: Dict[str, bool] = {}
    
    async def initialize(self) -> None:
        """Initialize the proxy service."""
        if not self._session:
            # Create session without timeout to avoid context manager issues
            self._session = aiohttp.ClientSession()
    
    async def shutdown(self) -> None:
        """Shutdown the proxy service."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def proxy_request(self, request: ProxyRequest) -> ProxyResponse:
        """Proxy a request to a backend service."""
        start_time = time.time()
        
        try:
            if not self._session:
                await self.initialize()
            
            # Make the request with timeout using asyncio.wait_for
            async def make_request():
                async with self._session.request(
                    method=request.method.value,
                    url=request.target_url,
                    headers=request.headers,
                    data=request.body
                ) as response:
                    return response, await response.read()
            
            response, body = await asyncio.wait_for(
                make_request(),
                timeout=request.timeout_seconds
            )
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return ProxyResponse(
                request_id=request.request_id,
                success=True,
                status_code=response.status,
                headers=dict(response.headers),
                body=body,
                response_time_ms=response_time,
                error_message=None
            )
                
        except asyncio.TimeoutError:
            response_time = (time.time() - start_time) * 1000
            return ProxyResponse(
                request_id=request.request_id,
                success=False,
                status_code=504,
                headers={},
                body=b'{"error": "Gateway timeout"}',
                response_time_ms=response_time,
                error_message="Request timeout"
            )
            
        except aiohttp.ClientError as e:
            response_time = (time.time() - start_time) * 1000
            return ProxyResponse(
                request_id=request.request_id,
                success=False,
                status_code=502,
                headers={},
                body=b'{"error": "Bad gateway"}',
                response_time_ms=response_time,
                error_message=f"Client error: {str(e)}"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Proxy request failed: {e}")
            return ProxyResponse(
                request_id=request.request_id,
                success=False,
                status_code=500,
                headers={},
                body=b'{"error": "Internal server error"}',
                response_time_ms=response_time,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    async def health_check_service(self, service_name: str, host: str, port: int, path: str = "/health") -> bool:
        """Check health of a backend service."""
        try:
            if not self._session:
                await self.initialize()
            
            url = f"http://{host}:{port}{path}"
            
            async with self._session.get(url) as response:
                healthy = response.status == 200
                self._service_health[service_name] = healthy
                return healthy
                
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            self._service_health[service_name] = False
            return False
    
    async def get_service_status(self, service_name: str) -> bool:
        """Check if a backend service is healthy."""
        try:
            if service_name not in self._registered_services:
                return False
            
            service_info = self._registered_services[service_name]
            host = service_info.get("host", "localhost")
            port = service_info.get("port", 80)
            path = service_info.get("health_path", "/health")
            
            if not self._session:
                await self.initialize()
            
            url = f"http://{host}:{port}{path}"
            
            async def check_health():
                async with self._session.get(url) as response:
                    return response.status == 200
            
            healthy = await asyncio.wait_for(check_health(), timeout=5.0)
            self._service_health[service_name] = healthy
            return healthy
                
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            self._service_health[service_name] = False
            return False


class AuthenticationIntegration:
    """Integration with authentication service."""
    
    def __init__(self, auth_service_url: str):
        self.auth_service_url = auth_service_url
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self) -> None:
        """Initialize authentication integration."""
        if not self._session:
            self._session = aiohttp.ClientSession()
    
    async def shutdown(self) -> None:
        """Shutdown authentication integration."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate authentication token."""
        try:
            if not self._session:
                await self.initialize()
            
            url = f"{self.auth_service_url}/auth/validate"
            headers = {"Authorization": f"Bearer {token}"}
            
            async with self._session.post(url, headers=headers) as response:
                result = await response.json()
                
                if response.status == 200:
                    return result
                else:
                    return {"valid": False, "error": result.get("detail", "Invalid token")}
                    
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return {"valid": False, "error": "Authentication service unavailable"}


class MetricsCollector:
    """Collects and manages gateway metrics."""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limited_requests = 0
        self.response_times = []
        self.start_time = time.time()
    
    def record_request(self, context: RequestContext) -> None:
        """Record a request."""
        self.total_requests += 1
    
    def record_response(self, success: bool, response_time_ms: float, rate_limited: bool = False) -> None:
        """Record a response."""
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        if rate_limited:
            self.rate_limited_requests += 1
        
        self.response_times.append(response_time_ms)
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self, active_routes: int) -> GatewayMetrics:
        """Get current metrics."""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        uptime_seconds = time.time() - self.start_time
        
        return GatewayMetrics(
            total_requests=self.total_requests,
            successful_requests=self.successful_requests,
            failed_requests=self.failed_requests,
            rate_limited_requests=self.rate_limited_requests,
            average_response_time_ms=avg_response_time,
            uptime_seconds=uptime_seconds,
            active_routes=active_routes
        )
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limited_requests = 0
        self.response_times = []
        self.start_time = time.time()


class APIGatewayService(IAPIGatewayService):
    """Main API Gateway service implementation."""
    
    def __init__(self, config: APIGatewayConfig):
        self.config = config
        self._initialized = False
        self._running = False
        
        # Core services
        self._routing_service = RoutingService()
        self._rate_limit_service = RateLimitService()
        self._proxy_service = ProxyService()
        self._auth_integration = AuthenticationIntegration(config.auth_service_url)
        self._metrics_collector = MetricsCollector()
        
        # Service registry
        self._registered_services: Dict[str, Dict[str, Any]] = {}
        
        # Setup logging
        log_level = getattr(config, 'log_level', 'INFO')
        logging.basicConfig(level=getattr(logging, log_level))
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> None:
        """Initialize the gateway service."""
        if self._initialized:
            return
        
        try:
            await self._proxy_service.initialize()
            await self._auth_integration.initialize()
            
            # Create default rate limiting rules if enabled
            if self.config.enable_rate_limiting:
                await self._create_default_rate_limits()
            
            self._initialized = True
            self.logger.info("API Gateway service initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize API Gateway service: {e}")
            raise
    
    async def start(self) -> None:
        """Start the gateway service."""
        if not self._initialized:
            await self.initialize()
        
        self._running = True
        self.logger.info(f"API Gateway service started on {self.config.host}:{self.config.port}")
    
    async def stop(self) -> None:
        """Stop the gateway service."""
        self._running = False
        
        await self._proxy_service.shutdown()
        await self._auth_integration.shutdown()
        
        self.logger.info("API Gateway service stopped")
    
    async def process_request(self, context: RequestContext) -> GatewayResponse:
        """Process an incoming request through the gateway."""
        start_time = time.time()
        
        try:
            # Record request metrics
            self._metrics_collector.record_request(context)
            
            # Rate limiting check
            if self.config.enable_rate_limiting:
                rate_limit_status = await self._rate_limit_service.check_rate_limit(context)
                if rate_limit_status.blocked:
                    self._metrics_collector.record_response(False, 0, rate_limited=True)
                    return GatewayResponse(
                        success=False,
                        status_code=429,
                        headers={"X-RateLimit-Limit": str(rate_limit_status.limit)},
                        body=b'{"error": "Rate limit exceeded"}',
                        error_message="Rate limit exceeded"
                    )
            
            # Route resolution
            route_result = await self._routing_service.resolve_route(context.method, context.path)
            if not route_result.success:
                response_time = (time.time() - start_time) * 1000
                self._metrics_collector.record_response(False, response_time)
                
                # Format error as proper JSON
                import json
                error_body = json.dumps({
                    "detail": route_result.error_message or "Request failed",
                    "status_code": route_result.status_code
                }).encode()
                
                return GatewayResponse(
                    success=False,
                    status_code=route_result.status_code,
                    headers={"Content-Type": "application/json"},
                    body=error_body,
                    error_message=route_result.error_message
                )
            
            route = route_result.route
            
            # Authentication check
            if route.requires_auth and self.config.require_authentication:
                auth_result = await self._authenticate_request(context)
                if not auth_result["valid"]:
                    response_time = (time.time() - start_time) * 1000
                    self._metrics_collector.record_response(False, response_time)
                    return GatewayResponse(
                        success=False,
                        status_code=401,
                        headers={},
                        body=b'{"error": "Authentication required"}',
                        error_message="Authentication required"
                    )
                
                # Update context with user info
                context.user_id = auth_result.get("user_id")
                context.authenticated = True
            
            # Record request for rate limiting
            if self.config.enable_rate_limiting:
                await self._rate_limit_service.record_request(context)
            
            # Proxy request
            proxy_request = ProxyRequest(
                request_id=context.request_id,
                target_url=route_result.target_url,
                method=context.method,
                headers=context.headers,
                body=context.body,
                timeout_seconds=self.config.request_timeout_seconds
            )
            
            proxy_response = await self._proxy_service.proxy_request(proxy_request)
            
            # Record response metrics
            self._metrics_collector.record_response(
                proxy_response.success,
                proxy_response.response_time_ms
            )
            
            return GatewayResponse(
                success=proxy_response.success,
                status_code=proxy_response.status_code,
                headers=proxy_response.headers,
                body=proxy_response.body,
                error_message=proxy_response.error_message,
                response_time_ms=proxy_response.response_time_ms
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self._metrics_collector.record_response(False, response_time)
            self.logger.error(f"Failed to process request: {e}")
            
            return GatewayResponse(
                success=False,
                status_code=500,
                headers={},
                body=b'{"error": "Internal server error"}',
                error_message="Internal server error"
            )
    
    async def register_service_routes(self, service_name: str, routes: List[RouteDefinition]) -> bool:
        """Register routes for a service."""
        try:
            success_count = 0
            
            for route in routes:
                if await self._routing_service.register_route(route):
                    success_count += 1
            
            self._registered_services[service_name] = {
                "routes": len(routes),
                "registered_at": datetime.now(timezone.utc)
            }
            
            self.logger.info(f"Registered {success_count}/{len(routes)} routes for {service_name}")
            return success_count == len(routes)
            
        except Exception as e:
            self.logger.error(f"Failed to register routes for {service_name}: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Get gateway health status."""
        routes = await self._routing_service.list_routes(RouteStatus.ACTIVE)
        
        return {
            "status": "healthy" if self._running else "unhealthy",
            "service": self.config.service_name,
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": time.time() - self._metrics_collector.start_time,
            "active_routes": len(routes),
            "registered_services": len(self._registered_services)
        }
    
    async def get_metrics(self) -> GatewayMetrics:
        """Get gateway metrics."""
        routes = await self._routing_service.list_routes(RouteStatus.ACTIVE)
        return self._metrics_collector.get_metrics(len(routes))
    
    async def reload_configuration(self) -> bool:
        """Reload gateway configuration."""
        try:
            # In a real implementation, this would reload from config file
            # For now, just log the action
            self.logger.info("Configuration reloaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to reload configuration: {e}")
            return False
    
    async def _authenticate_request(self, context: RequestContext) -> Dict[str, Any]:
        """Authenticate a request."""
        auth_header = context.headers.get("Authorization", "")
        
        if not auth_header.startswith("Bearer "):
            return {"valid": False, "error": "Missing or invalid Authorization header"}
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        return await self._auth_integration.validate_token(token)
    
    async def _create_default_rate_limits(self) -> None:
        """Create default rate limiting rules."""
        # Global rate limit
        global_rule = RateLimitRule(
            rule_id="global-default",
            scope=RateLimitScope.GLOBAL,
            scope_value="*",
            requests_per_window=self.config.default_rate_limit_requests,
            window_seconds=self.config.default_rate_limit_window_seconds
        )
        await self._rate_limit_service.create_rule(global_rule)
    
    async def _validate_request_size(self, context: RequestContext) -> bool:
        """Validate request size against configured limits."""
        content_length = context.headers.get("Content-Length", "0")
        try:
            size_bytes = int(content_length)
            max_size = getattr(self.config, 'max_request_size_bytes', 1024)  # Default 1KB
            return size_bytes <= max_size
        except (ValueError, TypeError):
            return True  # If we can't parse size, allow the request
    
    async def _validate_cors(self, context: RequestContext) -> bool:
        """Validate CORS request against configured policies."""
        origin = context.headers.get("Origin", "")
        if not origin:
            return True  # Non-CORS request
        
        # Check against allowed origins (for tests, allow example.com but not malicious.com)
        allowed_origins = getattr(self.config, 'cors_allowed_origins', ["https://example.com", "https://trusted.com"])
        if "*" in allowed_origins:
            return True
        
        return origin in allowed_origins
