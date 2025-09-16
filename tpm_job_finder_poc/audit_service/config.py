"""
Audit Service Configuration

Configuration management for audit service with environment variable support
and validation.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os


@dataclass
class StorageConfig:
    """Configuration for audit storage."""
    type: str = "file"  # file, database, etc.
    file_path: Optional[Path] = None
    max_file_size_mb: int = 100
    backup_count: int = 5
    
    # Database config (for future implementations)
    connection_string: Optional[str] = None
    table_name: str = "audit_events"
    
    @classmethod
    def from_env(cls) -> "StorageConfig":
        """Create storage config from environment variables."""
        return cls(
            type=os.getenv("AUDIT_STORAGE_TYPE", "file"),
            file_path=Path(os.getenv("AUDIT_FILE_PATH", "logs/audit.jsonl")),
            max_file_size_mb=int(os.getenv("AUDIT_MAX_FILE_SIZE_MB", "100")),
            backup_count=int(os.getenv("AUDIT_BACKUP_COUNT", "5")),
            connection_string=os.getenv("AUDIT_DB_CONNECTION_STRING"),
            table_name=os.getenv("AUDIT_DB_TABLE_NAME", "audit_events")
        )


@dataclass
class ServiceConfig:
    """Configuration for audit service behavior."""
    service_name: str = "audit_service"
    batch_size: int = 100
    flush_interval_seconds: float = 5.0
    
    @classmethod
    def from_env(cls) -> "ServiceConfig":
        """Create service config from environment variables."""
        return cls(
            service_name=os.getenv("AUDIT_SERVICE_NAME", "audit_service"),
            batch_size=int(os.getenv("AUDIT_BATCH_SIZE", "100")),
            flush_interval_seconds=float(os.getenv("AUDIT_FLUSH_INTERVAL", "5.0"))
        )


@dataclass
class APIConfig:
    """Configuration for audit service API."""
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    
    @classmethod
    def from_env(cls) -> "APIConfig":
        """Create API config from environment variables."""
        return cls(
            host=os.getenv("AUDIT_API_HOST", "0.0.0.0"),
            port=int(os.getenv("AUDIT_API_PORT", "8000")),
            log_level=os.getenv("AUDIT_API_LOG_LEVEL", "info")
        )


@dataclass
class AuditServiceConfig:
    """Complete audit service configuration."""
    storage: StorageConfig
    service: ServiceConfig
    api: APIConfig
    
    @classmethod
    def from_env(cls) -> "AuditServiceConfig":
        """Create complete config from environment variables."""
        return cls(
            storage=StorageConfig.from_env(),
            service=ServiceConfig.from_env(),
            api=APIConfig.from_env()
        )
    
    def validate(self) -> None:
        """Validate configuration."""
        # Validate storage config
        if self.storage.type == "file":
            if not self.storage.file_path:
                raise ValueError("File path required for file storage")
            
            # Ensure directory exists
            self.storage.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        elif self.storage.type == "database":
            if not self.storage.connection_string:
                raise ValueError("Connection string required for database storage")
        
        else:
            raise ValueError(f"Unsupported storage type: {self.storage.type}")
        
        # Validate service config
        if self.service.batch_size <= 0:
            raise ValueError("Batch size must be positive")
        
        if self.service.flush_interval_seconds <= 0:
            raise ValueError("Flush interval must be positive")
        
        # Validate API config
        if not (1 <= self.api.port <= 65535):
            raise ValueError("Port must be between 1 and 65535")


def load_config() -> AuditServiceConfig:
    """
    Load and validate audit service configuration.
    
    Returns:
        Validated configuration
    """
    config = AuditServiceConfig.from_env()
    config.validate()
    return config