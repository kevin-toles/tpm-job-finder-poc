"""
Storage Service Custom Exceptions
"""
from typing import Optional, Dict, Any, List
from .models import StorageErrorCode


class StorageServiceException(Exception):
    """Base exception for storage service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[StorageErrorCode] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class FileNotFoundException(StorageServiceException):
    """Exception raised when a file is not found."""
    
    def __init__(self, filename: str, details: Optional[Dict[str, Any]] = None):
        message = f"File not found: {filename}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.FILE_NOT_FOUND,
            details=details
        )
        self.filename = filename


class MetadataNotFoundException(StorageServiceException):
    """Exception raised when metadata is not found."""
    
    def __init__(self, filename: str, details: Optional[Dict[str, Any]] = None):
        message = f"Metadata not found for file: {filename}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.METADATA_NOT_FOUND,
            details=details
        )
        self.filename = filename


class InvalidPathException(StorageServiceException):
    """Exception raised for invalid file paths."""
    
    def __init__(self, path: str, details: Optional[Dict[str, Any]] = None):
        message = f"Invalid file path: {path}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.INVALID_PATH,
            details=details
        )
        self.path = path


class PermissionDeniedException(StorageServiceException):
    """Exception raised when access is denied."""
    
    def __init__(
        self,
        filename: str,
        user_id: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Permission denied for user {user_id} to {operation} file {filename}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.PERMISSION_DENIED,
            details=details
        )
        self.filename = filename
        self.user_id = user_id
        self.operation = operation


class StorageFullException(StorageServiceException):
    """Exception raised when storage is full."""
    
    def __init__(
        self,
        available_bytes: int = 0,
        required_bytes: int = 0,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Storage full. Available: {available_bytes} bytes, Required: {required_bytes} bytes"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.STORAGE_FULL,
            details=details
        )
        self.available_bytes = available_bytes
        self.required_bytes = required_bytes


class InvalidMetadataException(StorageServiceException):
    """Exception raised for invalid metadata."""
    
    def __init__(
        self,
        validation_errors: list,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Invalid metadata: {', '.join(validation_errors)}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.INVALID_METADATA,
            details=details
        )
        self.validation_errors = validation_errors


class EncryptionException(StorageServiceException):
    """Exception raised for encryption/decryption errors."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Encryption error during {operation}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.ENCRYPTION_ERROR,
            details=details
        )
        self.operation = operation


class AccessControlException(StorageServiceException):
    """Exception raised for access control errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code=StorageErrorCode.ACCESS_CONTROL_ERROR,
            details=details
        )


class CloudIntegrationException(StorageServiceException):
    """Exception raised for cloud integration errors."""
    
    def __init__(
        self,
        provider: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Cloud integration error with {provider} during {operation}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.CLOUD_INTEGRATION_ERROR,
            details=details
        )
        self.provider = provider
        self.operation = operation


class AuditLogException(StorageServiceException):
    """Exception raised for audit logging errors."""
    
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Audit log error during {operation}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.AUDIT_LOG_ERROR,
            details=details
        )
        self.operation = operation


class ServiceUnavailableException(StorageServiceException):
    """Exception raised when service is unavailable."""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        message = f"Storage service unavailable: {reason}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.SERVICE_UNAVAILABLE,
            details=details
        )
        self.reason = reason


class CircuitBreakerOpenException(StorageServiceException):
    """Exception raised when circuit breaker is open."""
    
    def __init__(self, service_name: str, details: Optional[Dict[str, Any]] = None):
        message = f"Circuit breaker open for {service_name}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.SERVICE_UNAVAILABLE,
            details=details
        )
        self.service_name = service_name


class ConfigurationException(StorageServiceException):
    """Exception raised for configuration errors."""
    
    def __init__(self, setting: str, details: Optional[Dict[str, Any]] = None):
        message = f"Configuration error for setting: {setting}"
        super().__init__(
            message=message,
            details=details
        )
        self.setting = setting


class ValidationException(StorageServiceException):
    """Exception raised for validation errors."""
    
    def __init__(
        self,
        field: str,
        value: Any,
        expected: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Validation error for field '{field}': got {value}, expected {expected}"
        super().__init__(
            message=message,
            details=details
        )
        self.field = field
        self.value = value
        self.expected = expected


class QuotaExceededException(StorageServiceException):
    """Exception raised when storage quota is exceeded."""
    
    def __init__(
        self,
        user_id: str,
        quota_type: str,
        current: int,
        limit: int,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Quota exceeded for user {user_id}: {quota_type} {current}/{limit}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.STORAGE_FULL,
            details=details
        )
        self.user_id = user_id


class ConcurrencyException(StorageServiceException):
    """Exception raised when concurrent access conflicts occur."""
    
    def __init__(
        self,
        resource: str,
        operation: Optional[str] = None,
        conflict_type: Optional[str] = None,
        details: Optional[str] = None
    ):
        if operation and conflict_type:
            message = f"Concurrency conflict on {resource} during {operation}: {conflict_type}"
        else:
            message = f"Concurrency conflict on resource: {resource}"
        
        super().__init__(message=message)
        self.resource = resource
        self.operation = operation
        self.conflict_type = conflict_type
        self.details = details


class HealthCheckException(StorageServiceException):
    """Exception raised when health checks fail."""
    
    def __init__(
        self,
        check_name: str,
        error_message: str,
        failed_checks: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Health check '{check_name}' failed: {error_message}"
        super().__init__(message=message, details=details)
        self.check_name = check_name
        self.error_message = error_message
        self.failed_checks = failed_checks
        self.details = details


class ConcurrencyException(StorageServiceException):
    """Exception raised for concurrency conflicts."""
    
    def __init__(
        self,
        filename: str,
        operation: str,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"Concurrency conflict for file {filename} during {operation}"
        super().__init__(
            message=message,
            details=details
        )
        self.filename = filename
        self.operation = operation