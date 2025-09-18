"""
Unit Tests for Storage Service Exceptions - RED Phase

Tests for custom exception hierarchy and error handling mechanisms.
"""

import pytest
from datetime import datetime

from tpm_job_finder_poc.storage_service.exceptions import (
    StorageServiceException, FileNotFoundException, MetadataNotFoundException,
    InvalidPathException, PermissionDeniedException, StorageFullException,
    InvalidMetadataException, EncryptionException, AccessControlException,
    CloudIntegrationException, AuditLogException, ServiceUnavailableException,
    ConfigurationException, QuotaExceededException, ConcurrencyException,
    HealthCheckException
)
from tpm_job_finder_poc.storage_service.models import StorageErrorCode


class TestStorageServiceException:
    """Test base StorageServiceException class."""
    
    def test_base_exception_creation(self):
        """Test basic exception creation."""
        exc = StorageServiceException(
            message="Test error",
            error_code=StorageErrorCode.SERVICE_UNAVAILABLE
        )
        
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.error_code == StorageErrorCode.SERVICE_UNAVAILABLE
        assert exc.context is None
        assert isinstance(exc.timestamp, datetime)
    
    def test_base_exception_with_context(self):
        """Test exception with context."""
        context = {"user_id": "user123", "operation": "save_file"}
        timestamp = datetime.now()
        
        exc = StorageServiceException(
            message="Operation failed",
            error_code=StorageErrorCode.PERMISSION_DENIED,
            context=context,
            timestamp=timestamp
        )
        
        assert exc.context == context
        assert exc.timestamp == timestamp
    
    def test_base_exception_auto_timestamp(self):
        """Test automatic timestamp generation."""
        before = datetime.now()
        exc = StorageServiceException(
            message="test",
            error_code=StorageErrorCode.SERVICE_UNAVAILABLE
        )
        after = datetime.now()
        
        assert before <= exc.timestamp <= after
    
    def test_base_exception_inheritance(self):
        """Test that exception inherits from Exception."""
        exc = StorageServiceException(
            message="test",
            error_code=StorageErrorCode.SERVICE_UNAVAILABLE
        )
        
        assert isinstance(exc, Exception)
        assert isinstance(exc, StorageServiceException)


class TestFileNotFoundException:
    """Test FileNotFoundException class."""
    
    def test_file_not_found_creation(self):
        """Test FileNotFoundException creation."""
        exc = FileNotFoundException(
            filename="missing.txt",
            path="/storage/missing.txt"
        )
        
        assert "missing.txt" in str(exc)
        assert "/storage/missing.txt" in str(exc)
        assert exc.filename == "missing.txt"
        assert exc.path == "/storage/missing.txt"
        assert exc.error_code == StorageErrorCode.FILE_NOT_FOUND
        assert "not found" in str(exc).lower()
    
    def test_file_not_found_with_context(self):
        """Test FileNotFoundException with context."""
        context = {"user_id": "user123", "session_id": "session456"}
        
        exc = FileNotFoundException(
            filename="test.txt",
            path="/storage/test.txt",
            context=context
        )
        
        assert exc.context == context
        assert exc.filename == "test.txt"
        assert exc.path == "/storage/test.txt"
    
    def test_file_not_found_inheritance(self):
        """Test inheritance hierarchy."""
        exc = FileNotFoundException("test.txt", "/path/test.txt")
        
        assert isinstance(exc, StorageServiceException)
        assert isinstance(exc, FileNotFoundException)


class TestMetadataNotFoundException:
    """Test MetadataNotFoundException class."""
    
    def test_metadata_not_found_creation(self):
        """Test MetadataNotFoundException creation."""
        exc = MetadataNotFoundException(
            filename="test.txt",
            metadata_key="user_id"
        )
        
        assert "test.txt" in str(exc)
        assert "user_id" in str(exc)
        assert exc.filename == "test.txt"
        assert exc.metadata_key == "user_id"
        assert exc.error_code == StorageErrorCode.METADATA_NOT_FOUND
        assert "metadata" in str(exc).lower()
    
    def test_metadata_not_found_without_key(self):
        """Test MetadataNotFoundException without specific key."""
        exc = MetadataNotFoundException(
            filename="test.txt",
            metadata_key=None
        )
        
        assert exc.metadata_key is None
        assert "test.txt" in str(exc)
        assert "metadata not found" in str(exc).lower()


class TestInvalidPathException:
    """Test InvalidPathException class."""
    
    def test_invalid_path_creation(self):
        """Test InvalidPathException creation."""
        exc = InvalidPathException(
            path="../../../etc/passwd",
            reason="Path traversal not allowed"
        )
        
        assert "../../../etc/passwd" in str(exc)
        assert "Path traversal not allowed" in str(exc)
        assert exc.path == "../../../etc/passwd"
        assert exc.reason == "Path traversal not allowed"
        assert exc.error_code == StorageErrorCode.INVALID_PATH
    
    def test_invalid_path_without_reason(self):
        """Test InvalidPathException without specific reason."""
        exc = InvalidPathException(
            path="/invalid/path",
            reason=None
        )
        
        assert exc.reason is None
        assert "/invalid/path" in str(exc)
        assert "invalid path" in str(exc).lower()


class TestPermissionDeniedException:
    """Test PermissionDeniedException class."""
    
    def test_permission_denied_creation(self):
        """Test PermissionDeniedException creation."""
        exc = PermissionDeniedException(
            resource="confidential.txt",
            user_id="user123",
            operation="read"
        )
        
        assert "confidential.txt" in str(exc)
        assert "user123" in str(exc)
        assert "read" in str(exc)
        assert exc.resource == "confidential.txt"
        assert exc.user_id == "user123"
        assert exc.operation == "read"
        assert exc.error_code == StorageErrorCode.PERMISSION_DENIED
        assert "permission denied" in str(exc).lower()
    
    def test_permission_denied_optional_fields(self):
        """Test PermissionDeniedException with optional fields."""
        exc = PermissionDeniedException(
            resource="file.txt",
            user_id=None,
            operation=None
        )
        
        assert exc.user_id is None
        assert exc.operation is None
        assert "file.txt" in str(exc)


class TestStorageFullException:
    """Test StorageFullException class."""
    
    def test_storage_full_creation(self):
        """Test StorageFullException creation."""
        exc = StorageFullException(
            current_size=1000000000,  # 1GB
            max_size=1073741824,      # 1GB
            required_size=104857600   # 100MB
        )
        
        assert exc.current_size == 1000000000
        assert exc.max_size == 1073741824
        assert exc.required_size == 104857600
        assert exc.error_code == StorageErrorCode.STORAGE_FULL
        assert "storage full" in str(exc).lower()
        assert "1000000000" in str(exc)
    
    def test_storage_full_optional_fields(self):
        """Test StorageFullException with optional fields."""
        exc = StorageFullException(
            current_size=None,
            max_size=None,
            required_size=None
        )
        
        assert exc.current_size is None
        assert exc.max_size is None
        assert exc.required_size is None


class TestInvalidMetadataException:
    """Test InvalidMetadataException class."""
    
    def test_invalid_metadata_creation(self):
        """Test InvalidMetadataException creation."""
        exc = InvalidMetadataException(
            metadata={"invalid": True, "size": -1},
            validation_errors=["Size cannot be negative", "Invalid format"]
        )
        
        assert exc.metadata == {"invalid": True, "size": -1}
        assert exc.validation_errors == ["Size cannot be negative", "Invalid format"]
        assert exc.error_code == StorageErrorCode.INVALID_METADATA
        assert "invalid metadata" in str(exc).lower()
        assert "Size cannot be negative" in str(exc)
    
    def test_invalid_metadata_empty_errors(self):
        """Test InvalidMetadataException with empty validation errors."""
        exc = InvalidMetadataException(
            metadata={"test": "data"},
            validation_errors=[]
        )
        
        assert exc.validation_errors == []
        assert "invalid metadata" in str(exc).lower()


class TestEncryptionException:
    """Test EncryptionException class."""
    
    def test_encryption_exception_creation(self):
        """Test EncryptionException creation."""
        exc = EncryptionException(
            operation="encrypt",
            algorithm="AES-256",
            details="Key not found"
        )
        
        assert exc.operation == "encrypt"
        assert exc.algorithm == "AES-256"
        assert exc.details == "Key not found"
        assert exc.error_code == StorageErrorCode.ENCRYPTION_ERROR
        assert "encryption" in str(exc).lower()
        assert "encrypt" in str(exc)
        assert "AES-256" in str(exc)
    
    def test_encryption_exception_optional_fields(self):
        """Test EncryptionException with optional fields."""
        exc = EncryptionException(
            operation="decrypt",
            algorithm=None,
            details=None
        )
        
        assert exc.algorithm is None
        assert exc.details is None
        assert "decrypt" in str(exc)


class TestAccessControlException:
    """Test AccessControlException class."""
    
    def test_access_control_creation(self):
        """Test AccessControlException creation."""
        exc = AccessControlException(
            user_id="user123",
            resource="secure_file.txt",
            required_permission="admin",
            current_permissions=["read", "write"]
        )
        
        assert exc.user_id == "user123"
        assert exc.resource == "secure_file.txt"
        assert exc.required_permission == "admin"
        assert exc.current_permissions == ["read", "write"]
        assert exc.error_code == StorageErrorCode.ACCESS_CONTROL_ERROR
        assert "access control" in str(exc).lower()
        assert "user123" in str(exc)
        assert "admin" in str(exc)
    
    def test_access_control_optional_fields(self):
        """Test AccessControlException with optional fields."""
        exc = AccessControlException(
            user_id="user456",
            resource="file.txt",
            required_permission=None,
            current_permissions=None
        )
        
        assert exc.required_permission is None
        assert exc.current_permissions is None


class TestCloudIntegrationException:
    """Test CloudIntegrationException class."""
    
    def test_cloud_integration_creation(self):
        """Test CloudIntegrationException creation."""
        exc = CloudIntegrationException(
            provider="aws",
            service="s3",
            operation="upload",
            error_details="Connection timeout"
        )
        
        assert exc.provider == "aws"
        assert exc.service == "s3"
        assert exc.operation == "upload"
        assert exc.error_details == "Connection timeout"
        assert exc.error_code == StorageErrorCode.CLOUD_INTEGRATION_ERROR
        assert "cloud integration" in str(exc).lower()
        assert "aws" in str(exc)
        assert "s3" in str(exc)
    
    def test_cloud_integration_optional_fields(self):
        """Test CloudIntegrationException with optional fields."""
        exc = CloudIntegrationException(
            provider="gcp",
            service=None,
            operation=None,
            error_details=None
        )
        
        assert exc.service is None
        assert exc.operation is None
        assert exc.error_details is None


class TestAuditLogException:
    """Test AuditLogException class."""
    
    def test_audit_log_creation(self):
        """Test AuditLogException creation."""
        exc = AuditLogException(
            operation="log_access",
            log_entry={"user": "test", "action": "read"},
            error_details="Database connection failed"
        )
        
        assert exc.operation == "log_access"
        assert exc.log_entry == {"user": "test", "action": "read"}
        assert exc.error_details == "Database connection failed"
        assert exc.error_code == StorageErrorCode.AUDIT_LOG_ERROR
        assert "audit log" in str(exc).lower()
        assert "log_access" in str(exc)


class TestServiceUnavailableException:
    """Test ServiceUnavailableException class."""
    
    def test_service_unavailable_creation(self):
        """Test ServiceUnavailableException creation."""
        exc = ServiceUnavailableException(
            service_name="storage_service",
            reason="Maintenance mode",
            retry_after_seconds=300
        )
        
        assert exc.service_name == "storage_service"
        assert exc.reason == "Maintenance mode"
        assert exc.retry_after_seconds == 300
        assert exc.error_code == StorageErrorCode.SERVICE_UNAVAILABLE
        assert "service unavailable" in str(exc).lower()
        assert "storage_service" in str(exc)
        assert "300" in str(exc)
    
    def test_service_unavailable_optional_fields(self):
        """Test ServiceUnavailableException with optional fields."""
        exc = ServiceUnavailableException(
            service_name="test_service",
            reason=None,
            retry_after_seconds=None
        )
        
        assert exc.reason is None
        assert exc.retry_after_seconds is None


class TestConfigurationException:
    """Test ConfigurationException class."""
    
    def test_configuration_exception_creation(self):
        """Test ConfigurationException creation."""
        exc = ConfigurationException(
            config_key="storage.base_directory",
            config_value="/invalid/path",
            validation_error="Directory does not exist"
        )
        
        assert exc.config_key == "storage.base_directory"
        assert exc.config_value == "/invalid/path"
        assert exc.validation_error == "Directory does not exist"
        assert "configuration" in str(exc).lower()
        assert "storage.base_directory" in str(exc)
    
    def test_configuration_exception_optional_fields(self):
        """Test ConfigurationException with optional fields."""
        exc = ConfigurationException(
            config_key="test.key",
            config_value=None,
            validation_error=None
        )
        
        assert exc.config_value is None
        assert exc.validation_error is None


class TestQuotaExceededException:
    """Test QuotaExceededException class."""
    
    def test_quota_exceeded_creation(self):
        """Test QuotaExceededException creation."""
        exc = QuotaExceededException(
            user_id="user123",
            quota_type="file_count",
            current=1000,
            limit=1000
        )
        
        assert exc.user_id == "user123"
        assert "quota exceeded" in str(exc).lower()
        assert "user123" in str(exc)
        assert "file_count" in str(exc)
    
    def test_quota_exceeded_optional_fields(self):
        """Test QuotaExceededException with optional fields."""
        exc = QuotaExceededException(
            user_id="user456",
            quota_type="storage_size",
            current=100,
            limit=50
        )
        
        assert exc.user_id == "user456"


class TestConcurrencyException:
    """Test ConcurrencyException class."""
    
    def test_concurrency_exception_creation(self):
        """Test ConcurrencyException creation."""
        exc = ConcurrencyException(
            resource="file.txt",
            operation="write",
            conflict_type="lock_timeout",
            details="Resource locked by another process"
        )
        
        assert exc.resource == "file.txt"
        assert exc.operation == "write"
        assert exc.conflict_type == "lock_timeout"
        assert exc.details == "Resource locked by another process"
        assert "concurrency" in str(exc).lower()
        assert "file.txt" in str(exc)
        assert "write" in str(exc)
    
    def test_concurrency_exception_optional_fields(self):
        """Test ConcurrencyException with optional fields."""
        exc = ConcurrencyException(
            resource="test.txt",
            operation=None,
            conflict_type=None,
            details=None
        )
        
        assert exc.operation is None
        assert exc.conflict_type is None
        assert exc.details is None


class TestHealthCheckException:
    """Test HealthCheckException class."""
    
    def test_health_check_exception_creation(self):
        """Test HealthCheckException creation."""
        failed_checks = ["database", "filesystem"]
        
        exc = HealthCheckException(
            check_name="storage_health",
            error_message="Multiple subsystems failing",
            failed_checks=failed_checks,
            details={"database": "Connection refused", "filesystem": "Read-only"}
        )
        
        assert exc.check_name == "storage_health"
        assert exc.error_message == "Multiple subsystems failing"
        assert exc.failed_checks == failed_checks
        assert exc.details == {"database": "Connection refused", "filesystem": "Read-only"}
        assert "health check" in str(exc).lower()
        assert "storage_health" in str(exc)
    
    def test_health_check_exception_optional_fields(self):
        """Test HealthCheckException with optional fields."""
        exc = HealthCheckException(
            check_name="simple_check",
            error_message="Check failed",
            failed_checks=None,
            details=None
        )
        
        assert exc.failed_checks is None
        assert exc.details is None


class TestExceptionHierarchy:
    """Test exception inheritance and polymorphism."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from StorageServiceException."""
        exceptions = [
            FileNotFoundException("test.txt", "/path"),
            MetadataNotFoundException("test.txt", "key"),
            InvalidPathException("/invalid", "reason"),
            PermissionDeniedException("resource", "user", "op"),
            StorageFullException(100, 100, 50),
            InvalidMetadataException({}, []),
            EncryptionException("encrypt", "AES", "details"),
            AccessControlException("user", "resource", "perm", []),
            CloudIntegrationException("aws", "s3", "upload", "error"),
            AuditLogException("log", {}, "error"),
            ServiceUnavailableException("service", "reason", 300),
            ConfigurationException("key", "value", "error"),
            QuotaExceededException("user", "type", 1, 1),
            ConcurrencyException("resource", "op", "type", "details"),
            HealthCheckException("check", "error", [], {})
        ]
        
        for exc in exceptions:
            assert isinstance(exc, StorageServiceException)
            assert isinstance(exc, Exception)
            assert hasattr(exc, 'error_code')
            assert hasattr(exc, 'timestamp')
    
    def test_exception_polymorphism(self):
        """Test that exceptions can be caught polymorphically."""
        def raise_file_not_found():
            raise FileNotFoundException("test.txt", "/path")
        
        def raise_storage_full():
            raise StorageFullException(100, 100, 50)
        
        # Should be able to catch with base exception
        with pytest.raises(StorageServiceException):
            raise_file_not_found()
        
        with pytest.raises(StorageServiceException):
            raise_storage_full()
        
        # Should also be able to catch with specific exception
        with pytest.raises(FileNotFoundException):
            raise_file_not_found()
        
        with pytest.raises(StorageFullException):
            raise_storage_full()
    
    def test_exception_error_codes(self):
        """Test that exceptions have correct error codes."""
        exc_code_mapping = {
            FileNotFoundException("test.txt", "/path"): StorageErrorCode.FILE_NOT_FOUND,
            MetadataNotFoundException("test.txt", "key"): StorageErrorCode.METADATA_NOT_FOUND,
            InvalidPathException("/invalid", "reason"): StorageErrorCode.INVALID_PATH,
            PermissionDeniedException("resource", "user", "op"): StorageErrorCode.PERMISSION_DENIED,
            StorageFullException(100, 100, 50): StorageErrorCode.STORAGE_FULL,
            InvalidMetadataException({}, []): StorageErrorCode.INVALID_METADATA,
            EncryptionException("encrypt", "AES", "details"): StorageErrorCode.ENCRYPTION_ERROR,
            AccessControlException("user", "resource", "perm", []): StorageErrorCode.ACCESS_CONTROL_ERROR,
            CloudIntegrationException("aws", "s3", "upload", "error"): StorageErrorCode.CLOUD_INTEGRATION_ERROR,
            AuditLogException("log", {}, "error"): StorageErrorCode.AUDIT_LOG_ERROR,
            ServiceUnavailableException("service", "reason", 300): StorageErrorCode.SERVICE_UNAVAILABLE,
        }
        
        for exc, expected_code in exc_code_mapping.items():
            assert exc.error_code == expected_code
    
    def test_exception_string_representation(self):
        """Test string representation of exceptions."""
        exc = FileNotFoundException("missing.txt", "/storage/missing.txt")
        exc_str = str(exc)
        
        assert "missing.txt" in exc_str
        assert "/storage/missing.txt" in exc_str
        assert "not found" in exc_str.lower()
        
        # Test another exception
        exc2 = PermissionDeniedException("secret.txt", "user123", "read")
        exc2_str = str(exc2)
        
        assert "secret.txt" in exc2_str
        assert "user123" in exc2_str
        assert "read" in exc2_str
        assert "permission denied" in exc2_str.lower()


class TestExceptionUsage:
    """Test practical exception usage patterns."""
    
    def test_raising_and_catching_specific_exception(self):
        """Test raising and catching specific exceptions."""
        def storage_operation():
            raise FileNotFoundException("missing.txt", "/storage/missing.txt")
        
        with pytest.raises(FileNotFoundException) as exc_info:
            storage_operation()
        
        exc = exc_info.value
        assert exc.filename == "missing.txt"
        assert exc.path == "/storage/missing.txt"
        assert exc.error_code == StorageErrorCode.FILE_NOT_FOUND
    
    def test_exception_with_context(self):
        """Test exceptions with context information."""
        context = {
            "user_id": "user123",
            "session_id": "session456",
            "operation_id": "op789"
        }
        
        exc = PermissionDeniedException(
            resource="confidential.txt",
            user_id="user123",
            operation="read",
            context=context
        )
        
        assert exc.context == context
        assert exc.context["user_id"] == "user123"
        assert exc.context["session_id"] == "session456"
        assert exc.context["operation_id"] == "op789"
    
    def test_exception_chaining(self):
        """Test exception chaining patterns."""
        def inner_operation():
            raise ValueError("Inner error occurred")
        
        def outer_operation():
            try:
                inner_operation()
            except ValueError as e:
                raise StorageServiceException(
                    message="Storage operation failed",
                    error_code=StorageErrorCode.SERVICE_UNAVAILABLE
                ) from e
        
        with pytest.raises(StorageServiceException) as exc_info:
            outer_operation()
        
        exc = exc_info.value
        assert str(exc) == "Storage operation failed"
        assert exc.error_code == StorageErrorCode.SERVICE_UNAVAILABLE
        assert exc.__cause__ is not None
        assert isinstance(exc.__cause__, ValueError)
        assert str(exc.__cause__) == "Inner error occurred"