"""
Storage Service Custom Exceptions
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from .models import StorageErrorCode


class StorageServiceException(Exception):
    """Base exception for storage service errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[StorageErrorCode] = None,
        context: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context
        self.timestamp = timestamp or datetime.now()


class FileNotFoundException(StorageServiceException):
    """Exception raised when a file is not found."""
    
    def __init__(
        self,
        filename: str,
        path: str,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"File not found: {filename} at path {path}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.FILE_NOT_FOUND,
            context=context
        )
        self.filename = filename
        self.path = path


class MetadataNotFoundException(StorageServiceException):
    """Exception raised when metadata is not found."""
    
    def __init__(
        self,
        filename: str,
        metadata_key: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        if metadata_key:
            message = f"Metadata key '{metadata_key}' not found for file: {filename}"
        else:
            message = f"Metadata not found for file: {filename}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.METADATA_NOT_FOUND,
            context=context
        )
        self.filename = filename
        self.metadata_key = metadata_key


class InvalidPathException(StorageServiceException):
    """Exception raised for invalid file paths."""
    
    def __init__(
        self,
        path: str,
        reason: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        if reason:
            message = f"Invalid path '{path}': {reason}"
        else:
            message = f"Invalid path: {path}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.INVALID_PATH,
            context=context
        )
        self.path = path
        self.reason = reason


class PermissionDeniedException(StorageServiceException):
    """Exception raised when access is denied."""
    
    def __init__(
        self,
        resource: str,
        user_id: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = [f"Permission denied for resource: {resource}"]
        if user_id:
            parts.append(f"user: {user_id}")
        if operation:
            parts.append(f"operation: {operation}")
        message = ", ".join(parts)
        
        super().__init__(
            message=message,
            error_code=StorageErrorCode.PERMISSION_DENIED,
            context=context
        )
        self.resource = resource
        self.user_id = user_id
        self.operation = operation


class StorageFullException(StorageServiceException):
    """Exception raised when storage is full."""
    
    def __init__(
        self,
        current_size: Optional[int] = None,
        max_size: Optional[int] = None,
        required_size: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = ["Storage full"]
        if current_size is not None and max_size is not None:
            parts.append(f"current: {current_size}, max: {max_size}")
        if required_size is not None:
            parts.append(f"required: {required_size}")
        message = " - ".join(parts)
        
        super().__init__(
            message=message,
            error_code=StorageErrorCode.STORAGE_FULL,
            context=context
        )
        self.current_size = current_size
        self.max_size = max_size
        self.required_size = required_size


class InvalidMetadataException(StorageServiceException):
    """Exception raised for invalid metadata."""
    
    def __init__(
        self,
        metadata: Any,
        validation_errors: List[str],
        context: Optional[Dict[str, Any]] = None
    ):
        errors_str = ", ".join(validation_errors) if validation_errors else "Invalid metadata format"
        message = f"Invalid metadata: {errors_str}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.INVALID_METADATA,
            context=context
        )
        self.metadata = metadata
        self.validation_errors = validation_errors


class EncryptionException(StorageServiceException):
    """Exception raised for encryption/decryption errors."""
    
    def __init__(
        self,
        operation: str,
        algorithm: Optional[str] = None,
        details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = [f"Encryption error during {operation}"]
        if algorithm:
            parts.append(f"algorithm: {algorithm}")
        if details:
            parts.append(f"details: {details}")
        message = " - ".join(parts)
        
        super().__init__(
            message=message,
            error_code=StorageErrorCode.ENCRYPTION_ERROR,
            context=context
        )
        self.operation = operation
        self.algorithm = algorithm
        self.details = details


class AccessControlException(StorageServiceException):
    """Exception raised for access control errors."""
    
    def __init__(
        self,
        user_id: str,
        resource: str,
        required_permission: Optional[str] = None,
        current_permissions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = [f"Access control error for user {user_id} on resource {resource}"]
        if required_permission:
            parts.append(f"required: {required_permission}")
        if current_permissions:
            parts.append(f"current: {current_permissions}")
        message = " - ".join(parts)
        
        super().__init__(
            message=message,
            error_code=StorageErrorCode.ACCESS_CONTROL_ERROR,
            context=context
        )
        self.user_id = user_id
        self.resource = resource
        self.required_permission = required_permission
        self.current_permissions = current_permissions


class CloudIntegrationException(StorageServiceException):
    """Exception raised for cloud integration errors."""
    
    def __init__(
        self,
        provider: str,
        service: Optional[str] = None,
        operation: Optional[str] = None,
        error_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = [f"Cloud integration error with {provider}"]
        if service:
            parts.append(f"service: {service}")
        if operation:
            parts.append(f"operation: {operation}")
        if error_details:
            parts.append(f"details: {error_details}")
        message = " - ".join(parts)
        
        super().__init__(
            message=message,
            error_code=StorageErrorCode.CLOUD_INTEGRATION_ERROR,
            context=context
        )
        self.provider = provider
        self.service = service
        self.operation = operation
        self.error_details = error_details


class AuditLogException(StorageServiceException):
    """Exception raised for audit logging errors."""
    
    def __init__(
        self,
        operation: str,
        log_entry: Dict[str, Any],
        error_details: str,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"Audit log error during {operation}: {error_details}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.AUDIT_LOG_ERROR,
            context=context
        )
        self.operation = operation
        self.log_entry = log_entry
        self.error_details = error_details


class ServiceUnavailableException(StorageServiceException):
    """Exception raised when service is unavailable."""
    
    def __init__(
        self,
        service_name: str,
        reason: Optional[str] = None,
        retry_after_seconds: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = [f"Service unavailable: {service_name}"]
        if reason:
            parts.append(f"reason: {reason}")
        if retry_after_seconds:
            parts.append(f"retry after: {retry_after_seconds} seconds")
        message = " - ".join(parts)
        
        super().__init__(
            message=message,
            error_code=StorageErrorCode.SERVICE_UNAVAILABLE,
            context=context
        )
        self.service_name = service_name
        self.reason = reason
        self.retry_after_seconds = retry_after_seconds


class ConfigurationException(StorageServiceException):
    """Exception raised for configuration errors."""
    
    def __init__(
        self,
        config_key: str,
        config_value: Any,
        validation_error: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        parts = [f"Configuration error for key '{config_key}' with value {config_value}"]
        if validation_error:
            parts.append(f"error: {validation_error}")
        message = " - ".join(parts)
        
        super().__init__(message=message, context=context)
        self.config_key = config_key
        self.config_value = config_value
        self.validation_error = validation_error


class QuotaExceededException(StorageServiceException):
    """Exception raised when storage quota is exceeded."""
    
    def __init__(
        self,
        user_id: str,
        quota_type: str,
        current: int,
        limit: int,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"Quota exceeded for user {user_id}: {quota_type} {current}/{limit}"
        super().__init__(
            message=message,
            error_code=StorageErrorCode.STORAGE_FULL,
            context=context
        )
        self.user_id = user_id
        self.quota_type = quota_type
        self.current = current
        self.limit = limit


class ConcurrencyException(StorageServiceException):
    """Exception raised when concurrent access conflicts occur."""
    
    def __init__(
        self,
        resource: str,
        operation: Optional[str] = None,
        conflict_type: Optional[str] = None,
        details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        if operation and conflict_type:
            message = f"Concurrency conflict on {resource} during {operation}: {conflict_type}"
        else:
            message = f"Concurrency conflict on resource: {resource}"
        
        super().__init__(message=message, context=context)
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
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        message = f"Health check '{check_name}' failed: {error_message}"
        super().__init__(message=message, context=context)
        self.check_name = check_name
        self.error_message = error_message
        self.failed_checks = failed_checks
        self.details = details