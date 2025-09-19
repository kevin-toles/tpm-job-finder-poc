"""
API Gateway Service Package.

This package implements a unified API Gateway for the TPM Job Finder system,
providing routing, rate limiting, authentication, and request proxying capabilities.

Key Components:
- APIGatewayService: Main service implementation
- RoutingService: Route management and resolution
- RateLimitService: Rate limiting enforcement
- ProxyService: Request proxying to backend services
- AuthenticationIntegration: Auth service integration
- FastAPI application: REST API endpoints

Usage:
    from tpm_job_finder_poc.api_gateway_service import APIGatewayService
    from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
    
    config = APIGatewayConfig(
        service_name="my_gateway",
        port=8080,
        auth_service_url="http://auth:8001"
    )
    
    service = APIGatewayService(config)
    await service.initialize()
    await service.start()
"""

import logging
from typing import Optional

from .service import (
    APIGatewayService,
    RoutingService,
    RateLimitService,
    ProxyService,
    AuthenticationIntegration,
    MetricsCollector
)
from .config import (
    ConfigurationLoader,
    ConfigurationManager,
    ConfigurationPersistence
)

logger = logging.getLogger(__name__)

# Package version
__version__ = "1.0.0"

# Default configuration
DEFAULT_CONFIG = {
    "service_name": "api_gateway_service",
    "host": "0.0.0.0",
    "port": 8080,
    "auth_service_url": "http://localhost:8001",
    "require_authentication": True,
    "enable_rate_limiting": True,
    "default_rate_limit_requests": 1000,
    "default_rate_limit_window_seconds": 3600,
    "max_concurrent_requests": 1000,
    "request_timeout_seconds": 30.0,
    "max_request_size_bytes": 10 * 1024 * 1024,  # 10MB
    "enable_cors": True,
    "cors_origins": ["*"],
    "enable_metrics": True,
    "log_level": "INFO"
}


def create_gateway_service(config_dict: Optional[dict] = None) -> APIGatewayService:
    """
    Create a configured API Gateway service instance.
    
    Args:
        config_dict: Optional configuration dictionary. If not provided,
                    will use default configuration.
    
    Returns:
        Configured APIGatewayService instance
    
    Example:
        # Create with default config
        service = create_gateway_service()
        
        # Create with custom config
        custom_config = {"port": 9090, "enable_rate_limiting": False}
        service = create_gateway_service(custom_config)
    """
    from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig
    
    # Merge with defaults
    final_config = DEFAULT_CONFIG.copy()
    if config_dict:
        final_config.update(config_dict)
    
    config = APIGatewayConfig(**final_config)
    return APIGatewayService(config)


def load_gateway_service_from_env() -> APIGatewayService:
    """
    Create API Gateway service with configuration loaded from environment variables.
    
    Environment variables:
        GATEWAY_SERVICE_NAME: Service name
        GATEWAY_HOST: Host to bind to
        GATEWAY_PORT: Port to listen on
        GATEWAY_AUTH_SERVICE_URL: Authentication service URL
        GATEWAY_ENABLE_RATE_LIMITING: Enable rate limiting (true/false)
        GATEWAY_LOG_LEVEL: Logging level
        ... and more (see ConfigurationLoader for full list)
    
    Returns:
        Configured APIGatewayService instance
    
    Example:
        # Set environment variables
        os.environ["GATEWAY_PORT"] = "9090"
        os.environ["GATEWAY_ENABLE_RATE_LIMITING"] = "false"
        
        # Create service
        service = load_gateway_service_from_env()
    """
    loader = ConfigurationLoader()
    config = loader.load_from_environment()
    return APIGatewayService(config)


def load_gateway_service_from_file(config_file: str) -> APIGatewayService:
    """
    Create API Gateway service with configuration loaded from file.
    
    Args:
        config_file: Path to configuration file (JSON or YAML)
    
    Returns:
        Configured APIGatewayService instance
    
    Example:
        service = load_gateway_service_from_file("config/gateway.yaml")
    """
    loader = ConfigurationLoader()
    config = loader.load_from_file(config_file)
    return APIGatewayService(config)


# Convenience imports for common use cases
__all__ = [
    # Main service classes
    "APIGatewayService",
    "RoutingService", 
    "RateLimitService",
    "ProxyService",
    "AuthenticationIntegration",
    "MetricsCollector",
    
    # Configuration classes
    "ConfigurationLoader",
    "ConfigurationManager",
    "ConfigurationPersistence",
    
    # Factory functions
    "create_gateway_service",
    "load_gateway_service_from_env",
    "load_gateway_service_from_file",
    
    # Constants
    "DEFAULT_CONFIG",
    "__version__"
]