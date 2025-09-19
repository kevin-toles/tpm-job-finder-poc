"""
API Gateway Service Configuration Management.

This module handles configuration loading, validation, and management for the
API Gateway service including environment variables, configuration files,
and dynamic configuration updates.
"""

import os
import json
import yaml
import logging
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from tpm_job_finder_poc.shared.contracts.api_gateway_service import APIGatewayConfig

logger = logging.getLogger(__name__)


class ConfigurationLoader:
    """Loads configuration from various sources."""
    
    def load_from_environment(self) -> APIGatewayConfig:
        """Load configuration from environment variables."""
        config_dict = {}
        
        # Map environment variables to config fields
        env_mapping = {
            "GATEWAY_SERVICE_NAME": "service_name",
            "GATEWAY_HOST": "host", 
            "GATEWAY_PORT": "port",
            "GATEWAY_AUTH_SERVICE_URL": "auth_service_url",
            "GATEWAY_REQUIRE_AUTHENTICATION": "require_authentication",
            "GATEWAY_ENABLE_RATE_LIMITING": "enable_rate_limiting",
            "GATEWAY_DEFAULT_RATE_LIMIT_REQUESTS": "default_rate_limit_requests",
            "GATEWAY_DEFAULT_RATE_LIMIT_WINDOW_SECONDS": "default_rate_limit_window_seconds",
            "GATEWAY_MAX_CONCURRENT_REQUESTS": "max_concurrent_requests",
            "GATEWAY_REQUEST_TIMEOUT_SECONDS": "request_timeout_seconds",
            "GATEWAY_MAX_REQUEST_SIZE_BYTES": "max_request_size_bytes",
            "GATEWAY_ENABLE_CORS": "enable_cors",
            "GATEWAY_CORS_ORIGINS": "cors_origins",
            "GATEWAY_ENABLE_METRICS": "enable_metrics",
            "GATEWAY_LOG_LEVEL": "log_level"
        }
        
        for env_var, config_field in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert types
                if config_field in ["port", "default_rate_limit_requests", 
                                   "default_rate_limit_window_seconds", "max_concurrent_requests",
                                   "max_request_size_bytes"]:
                    config_dict[config_field] = int(value)
                elif config_field in ["request_timeout_seconds"]:
                    config_dict[config_field] = float(value)
                elif config_field in ["require_authentication", "enable_rate_limiting", 
                                     "enable_cors", "enable_metrics"]:
                    config_dict[config_field] = value.lower() in ("true", "1", "yes", "on")
                elif config_field == "cors_origins":
                    config_dict[config_field] = [origin.strip() for origin in value.split(",")]
                else:
                    config_dict[config_field] = value
        
        return APIGatewayConfig(**config_dict)
    
    def load_from_file(self, file_path: str) -> APIGatewayConfig:
        """Load configuration from a file (JSON or YAML)."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() in ['.yaml', '.yml']:
                    config_dict = yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    config_dict = json.load(f)
                else:
                    raise ValueError(f"Unsupported file format: {path.suffix}")
            
            # Flatten nested configuration if needed
            config_dict = self._flatten_config(config_dict)
            
            return APIGatewayConfig(**config_dict)
            
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid configuration file format: {e}")
    
    def merge_configurations(self, base_config: Dict[str, Any], 
                           override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two configuration dictionaries."""
        merged = base_config.copy()
        merged.update(override_config)
        return merged
    
    def _flatten_config(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested configuration structures."""
        flattened = {}
        
        for key, value in config_dict.items():
            if key == "rate_limiting" and isinstance(value, dict):
                # Handle nested rate limiting config
                if "enabled" in value:
                    flattened["enable_rate_limiting"] = value["enabled"]
                if "default_requests" in value:
                    flattened["default_rate_limit_requests"] = value["default_requests"]
                if "default_window_seconds" in value:
                    flattened["default_rate_limit_window_seconds"] = value["default_window_seconds"]
            elif key == "cors" and isinstance(value, dict):
                # Handle nested CORS config
                if "enabled" in value:
                    flattened["enable_cors"] = value["enabled"]
                if "origins" in value:
                    flattened["cors_origins"] = value["origins"]
            else:
                flattened[key] = value
        
        return flattened


class ConfigurationManager:
    """Manages configuration state and updates."""
    
    def __init__(self, initial_config: Optional[APIGatewayConfig] = None):
        self._current_config = initial_config or APIGatewayConfig()
        self._change_callbacks: List[Callable[[APIGatewayConfig, APIGatewayConfig], None]] = []
        self._loader = ConfigurationLoader()
    
    def get_current_configuration(self) -> APIGatewayConfig:
        """Get the current configuration."""
        return self._current_config
    
    def update_configuration(self, updates: Dict[str, Any]) -> bool:
        """Update the current configuration."""
        try:
            # Create new config with updates
            current_dict = self._config_to_dict(self._current_config)
            updated_dict = {**current_dict, **updates}
            
            # Validate new configuration
            new_config = APIGatewayConfig(**updated_dict)
            
            # Notify callbacks
            old_config = self._current_config
            self._current_config = new_config
            
            for callback in self._change_callbacks:
                try:
                    callback(old_config, new_config)
                except Exception as e:
                    logger.error(f"Configuration change callback failed: {e}")
            
            logger.info("Configuration updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration: {e}")
            raise ValueError(f"Invalid configuration update: {e}")
    
    def reload_configuration(self, file_path: str) -> bool:
        """Reload configuration from file."""
        try:
            new_config = self._loader.load_from_file(file_path)
            
            old_config = self._current_config
            self._current_config = new_config
            
            # Notify callbacks
            for callback in self._change_callbacks:
                try:
                    callback(old_config, new_config)
                except Exception as e:
                    logger.error(f"Configuration change callback failed: {e}")
            
            logger.info(f"Configuration reloaded from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def register_change_callback(self, callback: Callable[[APIGatewayConfig, APIGatewayConfig], None]) -> None:
        """Register a callback for configuration changes."""
        self._change_callbacks.append(callback)
    
    def _config_to_dict(self, config: APIGatewayConfig) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "service_name": config.service_name,
            "host": config.host,
            "port": config.port,
            "auth_service_url": config.auth_service_url,
            "require_authentication": config.require_authentication,
            "enable_rate_limiting": config.enable_rate_limiting,
            "default_rate_limit_requests": config.default_rate_limit_requests,
            "default_rate_limit_window_seconds": config.default_rate_limit_window_seconds,
            "max_concurrent_requests": config.max_concurrent_requests,
            "request_timeout_seconds": config.request_timeout_seconds,
            "max_request_size_bytes": config.max_request_size_bytes,
            "enable_cors": config.enable_cors,
            "cors_origins": config.cors_origins,
            "enable_metrics": config.enable_metrics,
            "log_level": config.log_level
        }


def validate_port(port: Any) -> bool:
    """Validate port number."""
    try:
        port_int = int(port)
        return 1 <= port_int <= 65535
    except (ValueError, TypeError):
        return False


def validate_url(url: Any) -> bool:
    """Validate URL format."""
    if not isinstance(url, str) or not url:
        return False
    
    try:
        parsed = urlparse(url)
        return parsed.scheme in ["http", "https"] and parsed.netloc
    except Exception:
        return False


def validate_cors_origins(origins: Any) -> bool:
    """Validate CORS origins configuration."""
    if not isinstance(origins, list) or not origins:
        return False
    
    for origin in origins:
        if not isinstance(origin, str):
            return False
        
        if origin == "*":
            continue
        
        # Validate origin URL format
        if not validate_url(origin):
            return False
    
    return True


def validate_rate_limit_config(requests: Any, window_seconds: Any) -> bool:
    """Validate rate limit configuration."""
    try:
        req_int = int(requests)
        window_int = int(window_seconds)
        return req_int > 0 and window_int > 0
    except (ValueError, TypeError):
        return False


def get_service_discovery_defaults() -> Dict[str, Any]:
    """Get default service discovery configuration."""
    return {
        "enabled": True,
        "discovery_interval_seconds": 30,
        "health_check_interval_seconds": 10,
        "unhealthy_threshold": 3,
        "healthy_threshold": 2
    }


def get_rate_limiting_defaults() -> Dict[str, Any]:
    """Get default rate limiting configuration."""
    return {
        "global_requests_per_window": 10000,
        "global_window_seconds": 3600,
        "user_requests_per_window": 1000, 
        "user_window_seconds": 3600,
        "ip_requests_per_window": 100,
        "ip_window_seconds": 300
    }


def get_security_defaults() -> Dict[str, Any]:
    """Get default security configuration."""
    return {
        "require_authentication": True,
        "enable_cors": True,
        "cors_origins": ["*"],
        "max_request_size_bytes": 10 * 1024 * 1024,  # 10MB
        "enable_request_logging": True
    }


class ConfigurationPersistence:
    """Handles configuration persistence and backups."""
    
    def save_configuration(self, config: APIGatewayConfig, file_path: str) -> bool:
        """Save configuration to file."""
        try:
            config_dict = {
                "service_name": config.service_name,
                "host": config.host,
                "port": config.port,
                "auth_service_url": config.auth_service_url,
                "require_authentication": config.require_authentication,
                "enable_rate_limiting": config.enable_rate_limiting,
                "default_rate_limit_requests": config.default_rate_limit_requests,
                "default_rate_limit_window_seconds": config.default_rate_limit_window_seconds,
                "max_concurrent_requests": config.max_concurrent_requests,
                "request_timeout_seconds": config.request_timeout_seconds,
                "max_request_size_bytes": config.max_request_size_bytes,
                "enable_cors": config.enable_cors,
                "cors_origins": config.cors_origins,
                "enable_metrics": config.enable_metrics,
                "log_level": config.log_level
            }
            
            with open(file_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def load_configuration(self, file_path: str) -> APIGatewayConfig:
        """Load configuration from file."""
        loader = ConfigurationLoader()
        return loader.load_from_file(file_path)
    
    def create_backup(self, config: APIGatewayConfig) -> str:
        """Create a backup of the current configuration."""
        import time
        timestamp = int(time.time())
        backup_path = f"gateway_config_backup_{timestamp}.json"
        
        self.save_configuration(config, backup_path)
        return backup_path
    
    def restore_from_backup(self, backup_path: str) -> APIGatewayConfig:
        """Restore configuration from backup."""
        return self.load_configuration(backup_path)