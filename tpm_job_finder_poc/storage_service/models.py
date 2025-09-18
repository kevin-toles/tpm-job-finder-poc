"""
Storage Models and Data Transfer Objects
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class StorageOperationType(Enum):
    """Types of storage operations for audit logging."""
    SAVE_FILE = "save_file"
    RETRIEVE_FILE = "retrieve_file"
    DELETE_FILE = "delete_file"
    LIST_FILES = "list_files"
    SAVE_METADATA = "save_metadata"
    RETRIEVE_METADATA = "retrieve_metadata"
    DELETE_METADATA = "delete_metadata"
    UPDATE_METADATA = "update_metadata"
    BULK_OPERATION = "bulk_operation"
    CUSTOM_EVENT = "custom_event"
    MAINTENANCE = "maintenance"
    
    def __str__(self):
        """Return the enum value for string representation."""
        return self.value


class StorageErrorCode(Enum):
    """Storage error codes for consistent error handling."""
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    METADATA_NOT_FOUND = "METADATA_NOT_FOUND"
    INVALID_PATH = "INVALID_PATH"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    STORAGE_FULL = "STORAGE_FULL"
    INVALID_METADATA = "INVALID_METADATA"
    ENCRYPTION_ERROR = "ENCRYPTION_ERROR"
    ACCESS_CONTROL_ERROR = "ACCESS_CONTROL_ERROR"
    CLOUD_INTEGRATION_ERROR = "CLOUD_INTEGRATION_ERROR"
    AUDIT_LOG_ERROR = "AUDIT_LOG_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


@dataclass
class StorageResult:
    """Result object for storage operations."""
    success: bool
    message: str
    path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_code: Optional[StorageErrorCode] = None
    operation_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class StorageFileInfo:
    """Information about a stored file."""
    filename: str
    path: str
    size: int
    created_at: datetime
    modified_at: datetime
    metadata: Optional[Dict[str, Any]] = None
    checksum: Optional[str] = None
    mime_type: Optional[str] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class HealthStatus:
    """Health status for the storage service."""
    healthy: bool
    message: str
    checks: Dict[str, bool]
    timestamp: datetime
    version: Optional[str] = None
    uptime_seconds: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class HealthCheck:
    """Individual health check result."""
    name: str
    healthy: bool
    message: str
    duration_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class BulkOperationRequest:
    """Request for bulk operations."""
    operations: list
    batch_id: Optional[str] = None
    parallel_execution: bool = False
    fail_fast: bool = True
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class BulkOperationResult:
    """Result of bulk operations."""
    batch_id: str
    total_operations: int
    successful_operations: int
    failed_operations: int
    results: list
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_operations == 0:
            return 100.0
        return (self.successful_operations / self.total_operations) * 100.0


@dataclass
class AuditLogEntry:
    """Audit log entry for storage operations."""
    timestamp: datetime
    operation: StorageOperationType
    filename: Optional[str]
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    success: bool
    error_code: Optional[StorageErrorCode]
    details: Optional[Dict[str, Any]]
    duration_ms: Optional[float]
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class StorageMetrics:
    """Storage service metrics."""
    total_files: int
    total_size_bytes: int
    operations_per_minute: float
    error_rate: float
    average_response_time_ms: float
    cache_hit_rate: float
    disk_usage_percent: float
    timestamp: datetime
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class StorageConfiguration:
    """Storage service configuration."""
    base_directory: str
    max_file_size_mb: int = 100
    max_total_size_gb: int = 10
    enable_encryption: bool = False
    enable_access_control: bool = False
    enable_cloud_integration: bool = False
    cloud_provider: Optional[str] = None
    audit_log_retention_days: int = 90
    metadata_cache_size: int = 1000
    enable_compression: bool = False
    allowed_file_types: Optional[list] = None
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = []


@dataclass
class FilterCriteria:
    """Criteria for filtering files and metadata."""
    filename_pattern: Optional[str] = None
    file_type: Optional[str] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    metadata_filters: Optional[Dict[str, Any]] = None
    tags: Optional[list] = None
    
    def __post_init__(self):
        if self.metadata_filters is None:
            self.metadata_filters = {}
        if self.tags is None:
            self.tags = []


@dataclass
class StorageQuota:
    """Storage quota information."""
    user_id: str
    max_files: int
    max_size_bytes: int
    current_files: int
    current_size_bytes: int
    last_updated: datetime
    
    @property
    def files_remaining(self) -> int:
        """Calculate remaining file capacity."""
        return max(0, self.max_files - self.current_files)
    
    @property
    def bytes_remaining(self) -> int:
        """Calculate remaining storage capacity."""
        return max(0, self.max_size_bytes - self.current_size_bytes)
    
    @property
    def usage_percent(self) -> float:
        """Calculate storage usage percentage."""
        if self.max_size_bytes == 0:
            return 0.0
        return (self.current_size_bytes / self.max_size_bytes) * 100.0


# Type aliases for convenience
StorageMetadata = Dict[str, Any]
StorageFilePath = str
StorageFileName = str
OperationId = str
UserId = str
SessionId = str