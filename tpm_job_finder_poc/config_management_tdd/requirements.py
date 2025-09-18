"""
Config Management Service TDD - Requirements and Interface Specification

This module defines the exact interface, data structures, and requirements
that the ConfigManagementServiceTDD must implement to pass all TDD tests.

This serves as the contract between the test suite and the implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union, Callable, AsyncGenerator
from pathlib import Path


class ConfigChangeType(Enum):
    """Types of configuration changes."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RELOAD = "reload"


class ValidationSeverity(Enum):
    """Validation message severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ConfigSaveResult:
    """Result of configuration save operation."""
    success: bool
    config_name: str
    file_path: Optional[str] = None
    backup_created: bool = False
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ConfigReloadResult:
    """Result of configuration reload operation."""
    success: bool
    config_name: str
    changes_detected: bool = False
    changed_keys: List[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.changed_keys is None:
            self.changed_keys = []
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ValidationMessage:
    """Configuration validation message."""
    severity: ValidationSeverity
    key: str
    message: str
    expected_type: Optional[str] = None
    actual_value: Any = None


@dataclass
class ConfigValidationResult:
    """Result of configuration validation."""
    valid: bool
    config_name: str
    errors: List[ValidationMessage]
    warnings: List[ValidationMessage]
    info: List[ValidationMessage]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.info is None:
            self.info = []


@dataclass
class CredentialStorageResult:
    """Result of credential storage operation."""
    success: bool
    provider: str
    encrypted: bool = False
    backup_created: bool = False
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class CredentialRotationResult:
    """Result of credential rotation operation."""
    success: bool
    provider: str
    old_credentials_backed_up: bool = False
    new_credentials_active: bool = False
    rotation_id: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class CredentialValidationResult:
    """Result of credential validation."""
    valid: bool
    provider: str
    errors: List[str]
    required_fields: List[str]
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.required_fields is None:
            self.required_fields = []


@dataclass
class FileWatcherStatus:
    """Status of file watcher for configuration."""
    active: bool
    config_name: str
    file_path: Optional[str] = None
    last_modified: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class ConfigChangeEvent:
    """Configuration change event."""
    config_name: str
    key: str
    old_value: Any
    new_value: Any
    change_type: ConfigChangeType
    timestamp: datetime
    source: str = "manual"  # manual, file_watcher, api, etc.


@dataclass
class FeatureFlagToggleResult:
    """Result of feature flag toggle operation."""
    success: bool
    flag_name: str
    previous_value: bool
    new_value: bool
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class CheckpointInfo:
    """Information about a configuration checkpoint."""
    checkpoint_id: str
    config_name: str
    created_at: datetime
    description: Optional[str] = None
    config_snapshot: Dict[str, Any] = None


@dataclass
class RollbackResult:
    """Result of configuration rollback operation."""
    success: bool
    checkpoint_id: str
    config_name: str
    restored_keys: List[str]
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.restored_keys is None:
            self.restored_keys = []
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class CacheInfo:
    """Information about configuration cache."""
    cached: bool
    config_name: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    expired: bool = False
    hit_count: int = 0
    size_bytes: int = 0


@dataclass
class CacheInvalidationResult:
    """Result of cache invalidation operation."""
    success: bool
    config_name: str
    entries_cleared: int = 0
    error_message: Optional[str] = None


@dataclass
class PerformanceMetric:
    """Performance metric for an operation."""
    operation_name: str
    total_calls: int
    total_time_ms: float
    average_time_ms: float
    min_time_ms: float
    max_time_ms: float
    last_call_time: datetime


@dataclass
class BackupResult:
    """Result of configuration backup operation."""
    success: bool
    config_name: str
    backup_id: str
    backup_path: str
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RestoreResult:
    """Result of configuration restore operation."""
    success: bool
    config_name: str
    backup_id: str
    restored_keys: List[str]
    error_message: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.restored_keys is None:
            self.restored_keys = []
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class ConfigLoadResult:
    """Result of configuration load operation with validation."""
    success: bool
    config_name: str
    config_data: Optional[Dict[str, Any]] = None
    validation_failed: bool = False
    validation_errors: List[ValidationMessage] = None
    recovery_options: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


@dataclass
class RecoveryResult:
    """Result of automatic configuration recovery."""
    success: bool
    config_name: str
    errors_corrected: int = 0
    warnings_remaining: int = 0
    recovery_actions: List[str] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.recovery_actions is None:
            self.recovery_actions = []


@dataclass
class EnvironmentValidationResult:
    """Result of environment configuration validation."""
    valid: bool
    environment: str
    required_settings: List[str]
    missing_settings: List[str]
    invalid_settings: List[str]
    errors: List[str]
    
    def __post_init__(self):
        if self.required_settings is None:
            self.required_settings = []
        if self.missing_settings is None:
            self.missing_settings = []
        if self.invalid_settings is None:
            self.invalid_settings = []
        if self.errors is None:
            self.errors = []


class ConfigManagementServiceInterface(ABC):
    """
    Abstract interface that ConfigManagementServiceTDD must implement.
    
    This interface defines all the methods that the TDD tests expect.
    The actual implementation should inherit from this interface.
    """
    
    # Lifecycle Management
    @abstractmethod
    async def start(self) -> None:
        """Start the configuration management service."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the configuration management service."""
        pass
    
    # Configuration Loading and Saving
    @abstractmethod
    async def load_config(self, config_name: str, apply_env_overrides: bool = False) -> Dict[str, Any]:
        """Load configuration by name."""
        pass
    
    @abstractmethod
    async def save_config(self, config_name: str, config_data: Dict[str, Any]) -> ConfigSaveResult:
        """Save configuration data."""
        pass
    
    @abstractmethod
    async def load_config_from_env(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        pass
    
    @abstractmethod
    async def load_config_with_inheritance(self, config_name: str, base_config: str) -> Dict[str, Any]:
        """Load configuration with inheritance from base config."""
        pass
    
    @abstractmethod
    async def merge_configurations(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries."""
        pass
    
    # Environment Variable Handling
    @abstractmethod
    async def parse_env_variable(self, var_name: str, var_type: str) -> Any:
        """Parse environment variable with type conversion."""
        pass
    
    # Hierarchical Configuration Access
    @abstractmethod
    async def get_setting(self, key_path: str, default: Any = None) -> Any:
        """Get configuration setting using dot notation."""
        pass
    
    @abstractmethod
    async def set_setting(self, key_path: str, value: Any) -> None:
        """Set configuration setting using dot notation."""
        pass
    
    # Configuration Validation
    @abstractmethod
    async def validate_config(self, config_data: Dict[str, Any], schema_name: str = "global") -> ConfigValidationResult:
        """Validate configuration against schema."""
        pass
    
    @abstractmethod
    async def validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type."""
        pass
    
    @abstractmethod
    async def validate_constraint(self, value: Any, constraints: Dict[str, Any]) -> bool:
        """Validate value against constraints."""
        pass
    
    # Credential Management
    @abstractmethod
    async def get_credentials(self, provider: str) -> Dict[str, Any]:
        """Get credentials for provider."""
        pass
    
    @abstractmethod
    async def store_credentials(self, provider: str, credentials: Dict[str, Any]) -> CredentialStorageResult:
        """Store credentials securely."""
        pass
    
    @abstractmethod
    async def rotate_credentials(self, provider: str, new_credentials: Dict[str, Any]) -> CredentialRotationResult:
        """Rotate credentials for provider."""
        pass
    
    @abstractmethod
    async def validate_credentials(self, provider: str, credentials: Dict[str, Any]) -> CredentialValidationResult:
        """Validate credentials for provider."""
        pass
    
    # Hot Reloading
    @abstractmethod
    async def reload_config(self, config_name: str) -> ConfigReloadResult:
        """Reload configuration from file."""
        pass
    
    @abstractmethod
    async def enable_file_watching(self, config_name: str) -> None:
        """Enable file watching for configuration."""
        pass
    
    @abstractmethod
    async def get_file_watcher_status(self, config_name: str) -> FileWatcherStatus:
        """Get file watcher status."""
        pass
    
    @abstractmethod
    async def handle_file_change_event(self, change_event: Dict[str, Any]) -> bool:
        """Handle file change event."""
        pass
    
    # Change Notifications
    @abstractmethod
    async def register_change_listener(self, config_name: str, listener: Callable[[ConfigChangeEvent], None]) -> None:
        """Register configuration change listener."""
        pass
    
    # Checkpoints and Rollback
    @abstractmethod
    async def create_checkpoint(self, config_name: str) -> str:
        """Create configuration checkpoint."""
        pass
    
    @abstractmethod
    async def rollback_to_checkpoint(self, config_name: str, checkpoint_id: str) -> RollbackResult:
        """Rollback to configuration checkpoint."""
        pass
    
    # Feature Flags
    @abstractmethod
    async def is_feature_enabled(self, flag_name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if feature flag is enabled."""
        pass
    
    @abstractmethod
    async def toggle_feature_flag(self, flag_name: str) -> FeatureFlagToggleResult:
        """Toggle feature flag."""
        pass
    
    @abstractmethod
    async def load_feature_flags(self, feature_config: Dict[str, Any]) -> None:
        """Load feature flag configuration."""
        pass
    
    @abstractmethod
    async def get_feature_flag_analytics(self) -> Dict[str, Dict[str, Any]]:
        """Get feature flag usage analytics."""
        pass
    
    # Environment Support
    @abstractmethod
    async def load_environment_config(self, environment: str) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        pass
    
    @abstractmethod
    async def detect_environment(self) -> str:
        """Detect current environment."""
        pass
    
    @abstractmethod
    async def get_effective_config(self) -> Dict[str, Any]:
        """Get effective configuration with all overrides applied."""
        pass
    
    @abstractmethod
    async def validate_environment_config(self, environment: str) -> EnvironmentValidationResult:
        """Validate environment configuration."""
        pass
    
    # Caching and Performance
    @abstractmethod
    async def get_cache_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get cache statistics."""
        pass
    
    @abstractmethod
    async def get_cache_info(self, config_name: str) -> CacheInfo:
        """Get cache information for configuration."""
        pass
    
    @abstractmethod
    async def invalidate_cache(self, config_name: str) -> CacheInvalidationResult:
        """Invalidate configuration cache."""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, PerformanceMetric]:
        """Get performance metrics."""
        pass
    
    # Error Handling and Recovery
    @abstractmethod
    async def get_error_log(self) -> List[Dict[str, Any]]:
        """Get error log entries."""
        pass
    
    @abstractmethod
    async def was_default_config_created(self, config_name: str) -> bool:
        """Check if default configuration was created."""
        pass
    
    @abstractmethod
    async def force_load_config(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Force load configuration data (for testing)."""
        pass
    
    @abstractmethod
    async def get_current_config(self, config_name: str) -> Dict[str, Any]:
        """Get current configuration state."""
        pass
    
    @abstractmethod
    async def create_backup(self, config_name: str) -> BackupResult:
        """Create configuration backup."""
        pass
    
    @abstractmethod
    async def restore_from_backup(self, config_name: str, backup_id: str) -> RestoreResult:
        """Restore configuration from backup."""
        pass
    
    @abstractmethod
    async def load_config_with_validation(self, config_name: str, config_data: Dict[str, Any]) -> ConfigLoadResult:
        """Load configuration with validation."""
        pass
    
    @abstractmethod
    async def apply_automatic_recovery(self, config_name: str, recovery_options: Dict[str, Any]) -> RecoveryResult:
        """Apply automatic configuration recovery."""
        pass


# Configuration Schemas for Validation
DEFAULT_GLOBAL_SCHEMA = {
    "type": "object",
    "required": ["app"],
    "properties": {
        "app": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "version": {"type": "string"},
                "debug": {"type": "boolean"}
            }
        },
        "database": {
            "type": "object",
            "properties": {
                "url": {"type": "string"},
                "pool_size": {"type": "integer", "min": 1}
            }
        },
        "llm_provider": {
            "type": "object",
            "properties": {
                "primary": {"type": "string"},
                "timeout_seconds": {"type": "integer", "min": 1},
                "max_retries": {"type": "integer", "min": 0}
            }
        },
        "job_sources": {
            "type": "object",
            "properties": {
                "enabled": {"type": "array"},
                "max_jobs_per_source": {"type": "integer", "min": 1}
            }
        },
        "feature_flags": {
            "type": "object",
            "additionalProperties": {"type": "boolean"}
        }
    },
    "additionalProperties": True
}

# Credential validation schemas
CREDENTIAL_SCHEMAS = {
    "openai": {
        "required": ["api_key"],
        "properties": {
            "api_key": {"type": "string", "pattern": r"^sk-[a-zA-Z0-9\-_]{10,}$"},
            "organization": {"type": "string"}
        }
    },
    "anthropic": {
        "required": ["api_key"],
        "properties": {
            "api_key": {"type": "string", "pattern": r"^sk-[a-zA-Z0-9\-_]{10,}$"},
            "version": {"type": "string"}
        }
    },
    "database": {
        "required": ["username", "password"],
        "properties": {
            "username": {"type": "string"},
            "password": {"type": "string", "minLength": 8},
            "host": {"type": "string"},
            "port": {"type": "integer", "min": 1, "max": 65535}
        }
    },
    "test_provider": {
        "required": ["api_key"],
        "properties": {
            "api_key": {"type": "string"},
            "secret": {"type": "string"}
        }
    }
}

# Environment variable mapping
ENV_VARIABLE_MAPPINGS = {
    "DEBUG": {"path": "app.debug", "type": "bool"},
    "APP_DEBUG": {"path": "app.debug", "type": "bool"},
    "DATABASE_URL": {"path": "database.url", "type": "str"},
    "DB_URL": {"path": "database.url", "type": "str"},
    "LLM_TIMEOUT": {"path": "llm_provider.timeout_seconds", "type": "int"},
    "LLM_TIMEOUT_SECONDS": {"path": "llm_provider.timeout_seconds", "type": "int"},
    "OPENAI_API_KEY": {"path": "credentials.openai.api_key", "type": "str"},
    "FEATURE_MULTI_RESUME": {"path": "feature_flags.enable_multi_resume", "type": "bool"},
    "FEATURE_ENABLE_AUTO_APPLY": {"path": "feature_flags.enable_auto_apply", "type": "bool"},
    "MAX_RETRIES": {"path": "llm_provider.max_retries", "type": "int"}
}

# Default configurations by environment
DEFAULT_ENVIRONMENT_CONFIGS = {
    "development": {
        "app": {"debug": True},
        "database": {"url": "sqlite:///dev.db"},
        "llm_provider": {"timeout_seconds": 60},
        "feature_flags": {"enable_debug_mode": True}
    },
    "staging": {
        "app": {"debug": False},
        "database": {"url": "postgresql://staging-db:5432/jobs"},
        "llm_provider": {"timeout_seconds": 45},
        "feature_flags": {"enable_debug_mode": False}
    },
    "production": {
        "app": {"debug": False},
        "database": {"url": "postgresql://prod-db:5432/jobs"},
        "llm_provider": {"timeout_seconds": 30},
        "feature_flags": {"enable_debug_mode": False}
    }
}