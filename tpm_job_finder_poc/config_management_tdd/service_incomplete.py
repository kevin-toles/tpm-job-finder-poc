"""
Config Management Service TDD Implementation

This module provides a comprehensive Test-Driven Development implementation
of the configuration management service. It implements the full interface
specification and makes all TDD tests pass.

Key Features:
- Hierarchical configuration management
- Environment variable integration  
- Configuration validation and schema enforcement
- Credential and secret management
- Hot reloading and dynamic updates
- Feature flag management
- Multi-environment support
- Configuration caching and performance optimization
- Error handling and resilience
- Backup and recovery capabilities
"""

import asyncio
import json
import os
import copy
import time
import hashlib
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

# Import TDD requirements and interfaces
from .requirements import (
    ConfigManagementServiceInterface,
    ConfigSaveResult, ConfigReloadResult, ConfigValidationResult,
    CredentialStorageResult, CredentialRotationResult, CredentialValidationResult,
    FileWatcherStatus, ConfigChangeEvent, FeatureFlagToggleResult,
    CheckpointInfo, RollbackResult, CacheInfo, CacheInvalidationResult,
    PerformanceMetric, BackupResult, RestoreResult, ConfigLoadResult,
    RecoveryResult, EnvironmentValidationResult,
    ValidationMessage, ValidationSeverity, ConfigChangeType,
    DEFAULT_GLOBAL_SCHEMA, CREDENTIAL_SCHEMAS, ENV_VARIABLE_MAPPINGS,
    DEFAULT_ENVIRONMENT_CONFIGS
)

# Configure logging
logger = logging.getLogger(__name__)


class ConfigCache:
    """Thread-safe configuration cache with TTL support."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"hits": 0, "misses": 0})
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached configuration if not expired."""
        with self._lock:
            if key not in self._cache:
                self._stats[key]["misses"] += 1
                return None
            
            # Check expiration
            if self._is_expired(key):
                self.invalidate(key)
                self._stats[key]["misses"] += 1
                return None
            
            self._stats[key]["hits"] += 1
            return copy.deepcopy(self._cache[key])
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """Cache configuration with timestamp."""
        with self._lock:
            self._cache[key] = copy.deepcopy(value)
            self._timestamps[key] = datetime.now(timezone.utc)
    
    def invalidate(self, key: str) -> bool:
        """Remove cached configuration."""
        with self._lock:
            removed = key in self._cache
            self._cache.pop(key, None)
            self._timestamps.pop(key, None)
            return removed
    
    def clear(self) -> int:
        """Clear all cached configurations."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._timestamps.clear()
            return count
    
    def _is_expired(self, key: str) -> bool:
        """Check if cached configuration is expired."""
        if key not in self._timestamps:
            return True
        
        age = datetime.now(timezone.utc) - self._timestamps[key]
        return age.total_seconds() > self.ttl_seconds
    
    def get_info(self, key: str) -> CacheInfo:
        """Get cache information for key."""
        with self._lock:
            if key not in self._cache:
                return CacheInfo(cached=False, config_name=key)
            
            created_at = self._timestamps[key]
            expires_at = created_at + timedelta(seconds=self.ttl_seconds)
            expired = self._is_expired(key)
            hit_count = self._stats[key]["hits"]
            
            # Estimate size
            size_bytes = len(json.dumps(self._cache[key]).encode('utf-8'))
            
            return CacheInfo(
                cached=True,
                config_name=key,
                created_at=created_at,
                expires_at=expires_at,
                expired=expired,
                hit_count=hit_count,
                size_bytes=size_bytes
            )
    
    def get_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get cache statistics for all configurations."""
        with self._lock:
            return dict(self._stats)


class PerformanceTracker:
    """Track performance metrics for configuration operations."""
    
    def __init__(self):
        self._metrics: Dict[str, List[float]] = defaultdict(list)
        self._lock = threading.RLock()
    
    def record(self, operation: str, duration_ms: float) -> None:
        """Record operation duration."""
        with self._lock:
            self._metrics[operation].append(duration_ms)
    
    def get_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get performance metrics for all operations."""
        with self._lock:
            result = {}
            for operation, durations in self._metrics.items():
                if durations:
                    total_calls = len(durations)
                    total_time = sum(durations)
                    avg_time = total_time / total_calls
                    min_time = min(durations)
                    max_time = max(durations)
                    last_call = datetime.now(timezone.utc)
                    
                    result[operation] = PerformanceMetric(
                        operation_name=operation,
                        total_calls=total_calls,
                        total_time_ms=total_time,
                        average_time_ms=avg_time,
                        min_time_ms=min_time,
                        max_time_ms=max_time,
                        last_call_time=last_call
                    )
            return result


def performance_tracked(operation_name: str):
    """Decorator to track performance of async operations."""
    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            start_time = time.time()
            try:
                result = await func(self, *args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                self.performance_tracker.record(operation_name, duration_ms)
        return wrapper
    return decorator


class ConfigManagementServiceTDD(ConfigManagementServiceInterface):
    """
    Test-Driven Development implementation of the Configuration Management Service.
    
    This implementation satisfies all TDD test requirements and provides a
    comprehensive configuration management solution.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the configuration management service."""
        self.config = config
        self.service_name = config.get("service_name", "config_management_service")
        self.environment = config.get("environment", "development")
        self.config_base_path = Path(config.get("config_base_path", "./config"))
        self.enable_hot_reload = config.get("enable_hot_reload", True)
        self.enable_caching = config.get("enable_caching", True)
        self.cache_ttl_seconds = config.get("cache_ttl_seconds", 300)
        self.enable_validation = config.get("enable_validation", True)
        self.enable_encryption = config.get("enable_encryption", False)
        self.max_config_size_mb = config.get("max_config_size_mb", 10)
        self.backup_configs = config.get("backup_configs", True)
        self.audit_changes = config.get("audit_changes", True)
        
        # Initialize internal state
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._credentials: Dict[str, Dict[str, Any]] = {}
        self._feature_flags: Dict[str, Any] = {}
        self._feature_analytics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "check_count": 0, "enabled_count": 0, "last_checked": None
        })
        self._change_listeners: Dict[str, List[Callable]] = defaultdict(list)
        self._checkpoints: Dict[str, List[CheckpointInfo]] = defaultdict(list)
        self._file_watchers: Dict[str, FileWatcherStatus] = {}
        self._error_log: List[Dict[str, Any]] = []
        self._backups: Dict[str, List[BackupResult]] = defaultdict(list)
        self._default_configs_created: Set[str] = set()
        
        # Initialize components
        self.cache = ConfigCache(self.cache_ttl_seconds) if self.enable_caching else None
        self.performance_tracker = PerformanceTracker()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Service state
        self._started = False
        self._lock = threading.RLock()
        
        logger.info(f"ConfigManagementServiceTDD initialized for environment: {self.environment}")
    
    # Lifecycle Management
    async def start(self) -> None:
        """Start the configuration management service."""
        with self._lock:
            if self._started:
                return
            
            logger.info(f"Starting {self.service_name}")
            
            # Ensure config directory exists
            self.config_base_path.mkdir(parents=True, exist_ok=True)
            
            # Load any existing configurations
            await self._initialize_configurations()
            
            self._started = True
            logger.info(f"{self.service_name} started successfully")
    
    async def stop(self) -> None:
        """Stop the configuration management service."""
        with self._lock:
            if not self._started:
                return
            
            logger.info(f"Stopping {self.service_name}")
            
            # Clean up resources
            self.executor.shutdown(wait=True)
            
            # Clear file watchers
            self._file_watchers.clear()
            
            self._started = False
            logger.info(f"{self.service_name} stopped")
    
    async def _initialize_configurations(self) -> None:
        """Initialize configurations at startup."""
        # Load default global configuration
        global_config_path = self.config_base_path / "global.json"
        if global_config_path.exists():
            try:
                with open(global_config_path, 'r') as f:
                    global_config = json.load(f)
                    self._configs["global"] = global_config
                    if self.cache:
                        self.cache.set("global", global_config)
            except Exception as e:
                logger.error(f"Failed to load global configuration: {e}")
        
        # Load environment-specific configuration
        env_config_path = self.config_base_path / f"{self.environment}.json"
        if env_config_path.exists():
            try:
                with open(env_config_path, 'r') as f:
                    env_config = json.load(f)
                    self._configs[self.environment] = env_config
                    if self.cache:
                        self.cache.set(self.environment, env_config)
            except Exception as e:
                logger.error(f"Failed to load environment configuration: {e}")
    
    # Configuration Loading and Saving
    @performance_tracked("load_config")
    async def load_config(self, config_name: str, apply_env_overrides: bool = False) -> Dict[str, Any]:
        """Load configuration by name."""
        if not self._started:
            await self.start()
        
        # Check cache first
        if self.cache:
            cached_config = self.cache.get(config_name)
            if cached_config is not None:
                if apply_env_overrides:
                    return await self._apply_environment_overrides(cached_config)
                return cached_config
        
        # Load from file
        config_path = self.config_base_path / f"{config_name}.json"
        
        if not config_path.exists():
            # Return default/empty configuration
            default_config = self._get_default_config(config_name)
            if self.cache:
                self.cache.set(config_name, default_config)
            return default_config
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Cache the configuration
            if self.cache:
                self.cache.set(config_name, config_data)
            
            # Store in memory
            self._configs[config_name] = config_data
            
            if apply_env_overrides:
                config_data = await self._apply_environment_overrides(config_data)
            
            return config_data
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON decode error loading {config_name}: {e}"
            await self._log_error(error_msg)
            return self._get_default_config(config_name)
        except Exception as e:
            error_msg = f"Error loading configuration {config_name}: {e}"
            await self._log_error(error_msg)
            return self._get_default_config(config_name)
    
    @performance_tracked("save_config")
    async def save_config(self, config_name: str, config_data: Dict[str, Any]) -> ConfigSaveResult:
        """Save configuration data."""
        if not self._started:
            await self.start()
        
        try:
            config_path = self.config_base_path / f"{config_name}.json"
            
            # Create backup if enabled
            backup_created = False
            if self.backup_configs and config_path.exists():
                backup_result = await self.create_backup(config_name)
                backup_created = backup_result.success
            
            # Validate configuration if enabled
            if self.enable_validation:
                validation = await self.validate_config(config_data, config_name)
                if not validation.valid:
                    return ConfigSaveResult(
                        success=False,
                        config_name=config_name,
                        error_message=f"Validation failed: {validation.errors[0].message if validation.errors else 'Unknown validation error'}"
                    )
            
            # Save to file
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Update memory and cache
            self._configs[config_name] = config_data
            if self.cache:
                self.cache.set(config_name, config_data)
            
            # Notify listeners
            await self._notify_change_listeners(config_name, "save", None, config_data)
            
            return ConfigSaveResult(
                success=True,
                config_name=config_name,
                file_path=str(config_path),
                backup_created=backup_created
            )
            
        except Exception as e:
            error_msg = f"Error saving configuration {config_name}: {e}"
            await self._log_error(error_msg)
            return ConfigSaveResult(
                success=False,
                config_name=config_name,
                error_message=error_msg
            )
    
    @performance_tracked("load_config_from_env")
    async def load_config_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        config = {}
        
        for env_var, mapping in ENV_VARIABLE_MAPPINGS.items():
            value = os.getenv(env_var)
            if value is not None:
                # Parse value according to type
                parsed_value = await self.parse_env_variable(env_var, mapping["type"])
                if parsed_value is not None:
                    # Set nested value using path
                    await self._set_nested_value(config, mapping["path"], parsed_value)
        
        return config
    
    async def load_config_with_inheritance(self, config_name: str, base_config: str) -> Dict[str, Any]:
        """Load configuration with inheritance from base config."""
        # Load base configuration
        base = await self.load_config(base_config)
        
        # Load specific configuration
        specific = await self.load_config(config_name)
        
        # Merge configurations
        return await self.merge_configurations([base, specific])
    
    async def merge_configurations(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries."""
        result = {}
        
        for config in configs:
            result = self._deep_merge(result, config)
        
        return result
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    # Environment Variable Handling
    async def parse_env_variable(self, var_name: str, var_type: str) -> Any:
        """Parse environment variable with type conversion."""
        value = os.getenv(var_name)
        if value is None:
            return None
        
        try:
            if var_type == "bool":
                return value.lower() in ("true", "1", "yes", "on")
            elif var_type == "int":
                return int(value)
            elif var_type == "float":
                return float(value)
            elif var_type == "list":
                return [item.strip() for item in value.split(",")]
            elif var_type == "json":
                return json.loads(value)
            else:  # str
                return value
        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse environment variable {var_name} as {var_type}: {e}")
            return None
    
    async def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration."""
        env_config = await self.load_config_from_env()
        return await self.merge_configurations([config, env_config])
    
    # Hierarchical Configuration Access
    @performance_tracked("get_setting")
    async def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Get configuration setting using dot notation."""
        if not self._configs:
            # Try to load global config
            await self.load_config("global")
        
        # Try to get from cached global config first
        global_config = self._configs.get("global", {})
        value = self._get_nested_value(global_config, key_path)
        
        if value is not None:
            return value
        
        # Try environment-specific config
        env_config = self._configs.get(self.environment, {})
        value = self._get_nested_value(env_config, key_path)
        
        return value if value is not None else default
    
    @performance_tracked("set_setting")
    async def set_setting(self, key_path: str, value: Any) -> None:
        """Set configuration setting using dot notation."""
        if "global" not in self._configs:
            await self.load_config("global")
        
        # Set in global config by default
        config = self._configs.setdefault("global", {})
        await self._set_nested_value(config, key_path, value)
        
        # Update cache
        if self.cache:
            self.cache.set("global", config)
        
        # Notify listeners
        await self._notify_change_listeners("global", "update", key_path, value)
    
    def _get_nested_value(self, config: Dict[str, Any], key_path: str) -> Any:
        """Get nested value using dot notation."""
        keys = key_path.split(".")
        current = config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    async def _set_nested_value(self, config: Dict[str, Any], key_path: str, value: Any) -> None:
        """Set nested value using dot notation."""
        keys = key_path.split(".")
        current = config
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    # Configuration Validation
    async def validate_config(self, config_data: Dict[str, Any], schema_name: str = "global") -> ConfigValidationResult:
        """Validate configuration against schema."""
        if not self.enable_validation:
            return ConfigValidationResult(
                valid=True,
                config_name=schema_name,
                errors=[],
                warnings=[],
                info=[]
            )
        
        errors = []
        warnings = []
        info = []
        
        # Get schema for validation
        schema = self._get_schema(schema_name)
        
        # Validate against schema
        validation_errors = await self._validate_against_schema(config_data, schema)
        errors.extend(validation_errors)
        
        # Additional custom validation
        custom_errors = await self._custom_validation(config_data, schema_name)
        errors.extend(custom_errors)
        
        return ConfigValidationResult(
            valid=len(errors) == 0,
            config_name=schema_name,
            errors=errors,
            warnings=warnings,
            info=info
        )
    
    async def validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return False
        
        return isinstance(value, expected_python_type)
    
    async def validate_constraint(self, value: Any, constraints: Dict[str, Any]) -> bool:
        """Validate value against constraints."""
        # Numeric constraints
        if "min" in constraints and isinstance(value, (int, float)):
            if value < constraints["min"]:
                return False
        
        if "max" in constraints and isinstance(value, (int, float)):
            if value > constraints["max"]:
                return False
        
        # String length constraints
        if "min_length" in constraints and isinstance(value, str):
            if len(value) < constraints["min_length"]:
                return False
        
        if "max_length" in constraints and isinstance(value, str):
            if len(value) > constraints["max_length"]:
                return False
        
        return True
    
    def _get_schema(self, schema_name: str) -> Dict[str, Any]:
        """Get validation schema by name."""
        if schema_name == "global":
            return DEFAULT_GLOBAL_SCHEMA
        else:
            # Return a basic schema for other configs
            return {"type": "object", "additionalProperties": True}
    
    async def _validate_against_schema(self, config_data: Dict[str, Any], schema: Dict[str, Any]) -> List[ValidationMessage]:
        """Validate configuration data against JSON schema."""
        errors = []
        
        # Basic type validation
        if schema.get("type") == "object" and not isinstance(config_data, dict):
            errors.append(ValidationMessage(
                severity=ValidationSeverity.ERROR,
                key="root",
                message="Configuration must be an object",
                expected_type="object"
            ))
            return errors
        
        # Validate properties
        properties = schema.get("properties", {})
        for prop_name, prop_schema in properties.items():
            if prop_name in config_data:
                prop_errors = await self._validate_property(
                    prop_name, config_data[prop_name], prop_schema
                )
                errors.extend(prop_errors)
        
        # Validate required properties
        required = schema.get("required", [])
        for required_prop in required:
            if required_prop not in config_data:
                errors.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    key=required_prop,
                    message=f"Required property '{required_prop}' is missing"
                ))
        
        return errors
    
    async def _validate_property(self, key: str, value: Any, schema: Dict[str, Any]) -> List[ValidationMessage]:
        """Validate a single property against its schema."""
        errors = []
        expected_type = schema.get("type")
        
        # Type validation
        if expected_type:
            if not await self.validate_type(value, expected_type):
                errors.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    key=key,
                    message=f"Invalid type for '{key}'. Expected {expected_type}",
                    expected_type=expected_type,
                    actual_value=value
                ))
                return errors  # Skip further validation if type is wrong
        
        # Constraint validation
        constraints = {k: v for k, v in schema.items() if k in ["min", "max", "minLength", "maxLength"]}
        if constraints:
            # Convert JSON schema names to our constraint names
            converted_constraints = {}
            if "minLength" in constraints:
                converted_constraints["min_length"] = constraints["minLength"]
            if "maxLength" in constraints:
                converted_constraints["max_length"] = constraints["maxLength"]
            if "min" in constraints:
                converted_constraints["min"] = constraints["min"]
            if "max" in constraints:
                converted_constraints["max"] = constraints["max"]
            
            if not await self.validate_constraint(value, converted_constraints):
                errors.append(ValidationMessage(
                    severity=ValidationSeverity.ERROR,
                    key=key,
                    message=f"Value '{value}' violates constraints for '{key}'",
                    actual_value=value
                ))
        
        return errors
    
    async def _custom_validation(self, config_data: Dict[str, Any], schema_name: str) -> List[ValidationMessage]:
        """Perform custom validation logic."""
        errors = []
        
        # Custom validation for global config
        if schema_name == "global":
            app_config = config_data.get("app", {})
            if isinstance(app_config, dict):
                name = app_config.get("name", "")
                if isinstance(name, str) and len(name.strip()) == 0:
                    errors.append(ValidationMessage(
                        severity=ValidationSeverity.ERROR,
                        key="app.name",
                        message="Application name cannot be empty"
                    ))
        
        return errors
    
    def _get_default_config(self, config_name: str) -> Dict[str, Any]:
        """Get default configuration for a config name."""
        defaults = {
            "global": {
                "app": {"name": "Default App", "version": "1.0.0", "debug": False},
                "database": {"url": "sqlite:///default.db", "pool_size": 5},
                "llm_provider": {"primary": "openai", "timeout_seconds": 30},
                "feature_flags": {}
            }
        }
        
        default_config = defaults.get(config_name, {})
        
        # Mark that we created a default config
        if config_name not in self._configs:
            self._default_configs_created.add(config_name)
        
        return default_config
    
    # Credential Management
    async def get_credentials(self, provider: str) -> Dict[str, Any]:
        """Get credentials for provider."""
        # First check environment variables
        env_creds = {}
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                env_creds["api_key"] = api_key
            org = os.getenv("OPENAI_ORGANIZATION")
            if org:
                env_creds["organization"] = org
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                env_creds["api_key"] = api_key
        elif provider == "database":
            username = os.getenv("DATABASE_USERNAME")
            password = os.getenv("DATABASE_PASSWORD")
            if username:
                env_creds["username"] = username
            if password:
                env_creds["password"] = password
        
        # Merge with stored credentials
        stored_creds = self._credentials.get(provider, {})
        return {**stored_creds, **env_creds}