"""
Unit Tests for Storage Service Models - RED Phase

Tests for data models, DTOs, and data structures used by the storage service.
"""

import pytest
from datetime import datetime, timedelta
from dataclasses import FrozenInstanceError

from tpm_job_finder_poc.storage_service.models import (
    StorageResult, StorageFileInfo, HealthStatus, HealthCheck,
    BulkOperationRequest, BulkOperationResult, AuditLogEntry,
    StorageMetrics, StorageConfiguration, FilterCriteria,
    StorageQuota, StorageOperationType, StorageErrorCode
)


class TestStorageResult:
    """Test StorageResult data model."""
    
    def test_storage_result_creation(self):
        """Test basic StorageResult creation."""
        result = StorageResult(
            success=True,
            message="Operation completed successfully"
        )
        
        assert result.success is True
        assert result.message == "Operation completed successfully"
        assert result.path is None
        assert result.metadata is None
        assert result.error_code is None
        assert result.operation_id is None
        assert isinstance(result.timestamp, datetime)
    
    def test_storage_result_with_all_fields(self):
        """Test StorageResult with all fields populated."""
        timestamp = datetime.now()
        metadata = {"test": "data"}
        
        result = StorageResult(
            success=False,
            message="Operation failed",
            path="/storage/test.txt",
            metadata=metadata,
            error_code=StorageErrorCode.FILE_NOT_FOUND,
            operation_id="op_123456",
            timestamp=timestamp
        )
        
        assert result.success is False
        assert result.message == "Operation failed"
        assert result.path == "/storage/test.txt"
        assert result.metadata == metadata
        assert result.error_code == StorageErrorCode.FILE_NOT_FOUND
        assert result.operation_id == "op_123456"
        assert result.timestamp == timestamp
    
    def test_storage_result_auto_timestamp(self):
        """Test automatic timestamp generation."""
        before = datetime.now()
        result = StorageResult(success=True, message="test")
        after = datetime.now()
        
        assert before <= result.timestamp <= after


class TestStorageFileInfo:
    """Test StorageFileInfo data model."""
    
    def test_storage_file_info_creation(self):
        """Test basic StorageFileInfo creation."""
        created_at = datetime.now() - timedelta(hours=1)
        modified_at = datetime.now()
        
        file_info = StorageFileInfo(
            filename="test.txt",
            path="/storage/files/test.txt",
            size=1024,
            created_at=created_at,
            modified_at=modified_at
        )
        
        assert file_info.filename == "test.txt"
        assert file_info.path == "/storage/files/test.txt"
        assert file_info.size == 1024
        assert file_info.created_at == created_at
        assert file_info.modified_at == modified_at
        assert file_info.metadata is None
        assert file_info.checksum is None
        assert file_info.mime_type is None
        assert file_info.access_count == 0
        assert file_info.last_accessed is None
    
    def test_storage_file_info_with_optional_fields(self):
        """Test StorageFileInfo with optional fields."""
        created_at = datetime.now() - timedelta(hours=1)
        modified_at = datetime.now()
        last_accessed = datetime.now() - timedelta(minutes=30)
        metadata = {"user_id": "user123", "type": "document"}
        
        file_info = StorageFileInfo(
            filename="document.pdf",
            path="/storage/files/document.pdf",
            size=2048,
            created_at=created_at,
            modified_at=modified_at,
            metadata=metadata,
            checksum="sha256:abc123",
            mime_type="application/pdf",
            access_count=5,
            last_accessed=last_accessed
        )
        
        assert file_info.metadata == metadata
        assert file_info.checksum == "sha256:abc123"
        assert file_info.mime_type == "application/pdf"
        assert file_info.access_count == 5
        assert file_info.last_accessed == last_accessed


class TestHealthStatus:
    """Test HealthStatus data model."""
    
    def test_health_status_creation(self):
        """Test basic HealthStatus creation."""
        checks = {"filesystem": True, "database": False}
        timestamp = datetime.now()
        
        health = HealthStatus(
            healthy=False,
            message="Database connection failed",
            checks=checks,
            timestamp=timestamp
        )
        
        assert health.healthy is False
        assert health.message == "Database connection failed"
        assert health.checks == checks
        assert health.timestamp == timestamp
        assert health.version is None
        assert health.uptime_seconds is None
    
    def test_health_status_with_optional_fields(self):
        """Test HealthStatus with optional fields."""
        checks = {"filesystem": True, "config": True}
        timestamp = datetime.now()
        
        health = HealthStatus(
            healthy=True,
            message="All systems operational",
            checks=checks,
            timestamp=timestamp,
            version="1.0.0",
            uptime_seconds=3600.5
        )
        
        assert health.healthy is True
        assert health.version == "1.0.0"
        assert health.uptime_seconds == 3600.5
    
    def test_health_status_auto_timestamp(self):
        """Test automatic timestamp generation."""
        before = datetime.now()
        health = HealthStatus(
            healthy=True,
            message="test",
            checks={},
            timestamp=None
        )
        after = datetime.now()
        
        assert before <= health.timestamp <= after


class TestHealthCheck:
    """Test HealthCheck data model."""
    
    def test_health_check_creation(self):
        """Test basic HealthCheck creation."""
        check = HealthCheck(
            name="filesystem",
            healthy=True,
            message="Filesystem accessible"
        )
        
        assert check.name == "filesystem"
        assert check.healthy is True
        assert check.message == "Filesystem accessible"
        assert check.duration_ms is None
        assert check.details is None
    
    def test_health_check_with_optional_fields(self):
        """Test HealthCheck with optional fields."""
        details = {"available_space": "10GB", "total_space": "100GB"}
        
        check = HealthCheck(
            name="storage",
            healthy=True,
            message="Storage healthy",
            duration_ms=15.5,
            details=details
        )
        
        assert check.duration_ms == 15.5
        assert check.details == details


class TestBulkOperationRequest:
    """Test BulkOperationRequest data model."""
    
    def test_bulk_operation_request_creation(self):
        """Test basic BulkOperationRequest creation."""
        operations = [
            {"action": "save", "file": "file1.txt"},
            {"action": "save", "file": "file2.txt"}
        ]
        
        request = BulkOperationRequest(operations=operations)
        
        assert request.operations == operations
        assert request.batch_id is None
        assert request.parallel_execution is False
        assert request.fail_fast is True
        assert request.metadata is None
    
    def test_bulk_operation_request_with_optional_fields(self):
        """Test BulkOperationRequest with optional fields."""
        operations = [{"action": "delete", "file": "old_file.txt"}]
        metadata = {"user_id": "user123", "reason": "cleanup"}
        
        request = BulkOperationRequest(
            operations=operations,
            batch_id="batch_001",
            parallel_execution=True,
            fail_fast=False,
            metadata=metadata
        )
        
        assert request.batch_id == "batch_001"
        assert request.parallel_execution is True
        assert request.fail_fast is False
        assert request.metadata == metadata


class TestBulkOperationResult:
    """Test BulkOperationResult data model."""
    
    def test_bulk_operation_result_creation(self):
        """Test basic BulkOperationResult creation."""
        start_time = datetime.now() - timedelta(seconds=10)
        end_time = datetime.now()
        results = [{"operation": 1, "success": True}, {"operation": 2, "success": False}]
        
        result = BulkOperationResult(
            batch_id="batch_001",
            total_operations=2,
            successful_operations=1,
            failed_operations=1,
            results=results,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=10.0
        )
        
        assert result.batch_id == "batch_001"
        assert result.total_operations == 2
        assert result.successful_operations == 1
        assert result.failed_operations == 1
        assert result.results == results
        assert result.start_time == start_time
        assert result.end_time == end_time
        assert result.duration_seconds == 10.0
    
    def test_bulk_operation_result_success_rate(self):
        """Test success rate calculation."""
        # 100% success rate
        result1 = BulkOperationResult(
            batch_id="batch_001",
            total_operations=5,
            successful_operations=5,
            failed_operations=0,
            results=[],
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=1.0
        )
        assert result1.success_rate == 100.0
        
        # 50% success rate
        result2 = BulkOperationResult(
            batch_id="batch_002",
            total_operations=4,
            successful_operations=2,
            failed_operations=2,
            results=[],
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=1.0
        )
        assert result2.success_rate == 50.0
        
        # 0 operations edge case
        result3 = BulkOperationResult(
            batch_id="batch_003",
            total_operations=0,
            successful_operations=0,
            failed_operations=0,
            results=[],
            start_time=datetime.now(),
            end_time=datetime.now(),
            duration_seconds=0.0
        )
        assert result3.success_rate == 100.0


class TestAuditLogEntry:
    """Test AuditLogEntry data model."""
    
    def test_audit_log_entry_creation(self):
        """Test basic AuditLogEntry creation."""
        timestamp = datetime.now()
        
        entry = AuditLogEntry(
            timestamp=timestamp,
            operation=StorageOperationType.SAVE_FILE,
            filename="test.txt",
            user_id="user123",
            session_id="session456",
            ip_address="192.168.1.1",
            success=True,
            error_code=None,
            details=None,
            duration_ms=150.0
        )
        
        assert entry.timestamp == timestamp
        assert entry.operation == StorageOperationType.SAVE_FILE
        assert entry.filename == "test.txt"
        assert entry.user_id == "user123"
        assert entry.session_id == "session456"
        assert entry.ip_address == "192.168.1.1"
        assert entry.success is True
        assert entry.error_code is None
        assert entry.details is None
        assert entry.duration_ms == 150.0
    
    def test_audit_log_entry_with_error(self):
        """Test AuditLogEntry with error information."""
        details = {"attempted_path": "/invalid/path", "stack_trace": "..."}
        
        entry = AuditLogEntry(
            timestamp=None,  # Will be auto-generated
            operation=StorageOperationType.DELETE_FILE,
            filename="missing.txt",
            user_id="user456",
            session_id=None,
            ip_address=None,
            success=False,
            error_code=StorageErrorCode.FILE_NOT_FOUND,
            details=details,
            duration_ms=50.0
        )
        
        assert isinstance(entry.timestamp, datetime)
        assert entry.success is False
        assert entry.error_code == StorageErrorCode.FILE_NOT_FOUND
        assert entry.details == details
    
    def test_audit_log_entry_auto_timestamp(self):
        """Test automatic timestamp generation."""
        before = datetime.now()
        entry = AuditLogEntry(
            timestamp=None,
            operation=StorageOperationType.LIST_FILES,
            filename=None,
            user_id="user789",
            session_id=None,
            ip_address=None,
            success=True,
            error_code=None,
            details=None,
            duration_ms=None
        )
        after = datetime.now()
        
        assert before <= entry.timestamp <= after


class TestStorageMetrics:
    """Test StorageMetrics data model."""
    
    def test_storage_metrics_creation(self):
        """Test basic StorageMetrics creation."""
        timestamp = datetime.now()
        
        metrics = StorageMetrics(
            total_files=100,
            total_size_bytes=1024000,
            operations_per_minute=25.5,
            error_rate=2.1,
            average_response_time_ms=45.8,
            cache_hit_rate=85.5,
            disk_usage_percent=45.2,
            timestamp=timestamp
        )
        
        assert metrics.total_files == 100
        assert metrics.total_size_bytes == 1024000
        assert metrics.operations_per_minute == 25.5
        assert metrics.error_rate == 2.1
        assert metrics.average_response_time_ms == 45.8
        assert metrics.cache_hit_rate == 85.5
        assert metrics.disk_usage_percent == 45.2
        assert metrics.timestamp == timestamp
    
    def test_storage_metrics_auto_timestamp(self):
        """Test automatic timestamp generation."""
        before = datetime.now()
        metrics = StorageMetrics(
            total_files=0,
            total_size_bytes=0,
            operations_per_minute=0.0,
            error_rate=0.0,
            average_response_time_ms=0.0,
            cache_hit_rate=0.0,
            disk_usage_percent=0.0,
            timestamp=None
        )
        after = datetime.now()
        
        assert before <= metrics.timestamp <= after


class TestStorageConfiguration:
    """Test StorageConfiguration data model."""
    
    def test_storage_configuration_defaults(self):
        """Test StorageConfiguration with default values."""
        config = StorageConfiguration(base_directory="/storage")
        
        assert config.base_directory == "/storage"
        assert config.max_file_size_mb == 100
        assert config.max_total_size_gb == 10
        assert config.enable_encryption is False
        assert config.enable_access_control is False
        assert config.enable_cloud_integration is False
        assert config.cloud_provider is None
        assert config.audit_log_retention_days == 90
        assert config.metadata_cache_size == 1000
        assert config.enable_compression is False
        assert config.allowed_file_types == []
    
    def test_storage_configuration_custom_values(self):
        """Test StorageConfiguration with custom values."""
        allowed_types = ["pdf", "txt", "docx"]
        
        config = StorageConfiguration(
            base_directory="/custom/storage",
            max_file_size_mb=50,
            max_total_size_gb=5,
            enable_encryption=True,
            enable_access_control=True,
            enable_cloud_integration=True,
            cloud_provider="aws",
            audit_log_retention_days=365,
            metadata_cache_size=2000,
            enable_compression=True,
            allowed_file_types=allowed_types
        )
        
        assert config.base_directory == "/custom/storage"
        assert config.max_file_size_mb == 50
        assert config.max_total_size_gb == 5
        assert config.enable_encryption is True
        assert config.enable_access_control is True
        assert config.enable_cloud_integration is True
        assert config.cloud_provider == "aws"
        assert config.audit_log_retention_days == 365
        assert config.metadata_cache_size == 2000
        assert config.enable_compression is True
        assert config.allowed_file_types == allowed_types
    
    def test_storage_configuration_post_init(self):
        """Test post-initialization processing."""
        config = StorageConfiguration(
            base_directory="/test",
            allowed_file_types=None
        )
        
        # Should initialize empty list for allowed_file_types
        assert config.allowed_file_types == []


class TestFilterCriteria:
    """Test FilterCriteria data model."""
    
    def test_filter_criteria_defaults(self):
        """Test FilterCriteria with default values."""
        criteria = FilterCriteria()
        
        assert criteria.filename_pattern is None
        assert criteria.file_type is None
        assert criteria.size_min is None
        assert criteria.size_max is None
        assert criteria.created_after is None
        assert criteria.created_before is None
        assert criteria.modified_after is None
        assert criteria.modified_before is None
        assert criteria.metadata_filters == {}
        assert criteria.tags == []
    
    def test_filter_criteria_custom_values(self):
        """Test FilterCriteria with custom values."""
        created_after = datetime.now() - timedelta(days=30)
        created_before = datetime.now()
        modified_after = datetime.now() - timedelta(days=7)
        modified_before = datetime.now()
        metadata_filters = {"type": "document", "user_id": "user123"}
        tags = ["important", "work"]
        
        criteria = FilterCriteria(
            filename_pattern="*.pdf",
            file_type="application/pdf",
            size_min=1000,
            size_max=1000000,
            created_after=created_after,
            created_before=created_before,
            modified_after=modified_after,
            modified_before=modified_before,
            metadata_filters=metadata_filters,
            tags=tags
        )
        
        assert criteria.filename_pattern == "*.pdf"
        assert criteria.file_type == "application/pdf"
        assert criteria.size_min == 1000
        assert criteria.size_max == 1000000
        assert criteria.created_after == created_after
        assert criteria.created_before == created_before
        assert criteria.modified_after == modified_after
        assert criteria.modified_before == modified_before
        assert criteria.metadata_filters == metadata_filters
        assert criteria.tags == tags
    
    def test_filter_criteria_post_init(self):
        """Test post-initialization processing."""
        criteria = FilterCriteria(
            metadata_filters=None,
            tags=None
        )
        
        # Should initialize empty collections
        assert criteria.metadata_filters == {}
        assert criteria.tags == []


class TestStorageQuota:
    """Test StorageQuota data model."""
    
    def test_storage_quota_creation(self):
        """Test basic StorageQuota creation."""
        last_updated = datetime.now()
        
        quota = StorageQuota(
            user_id="user123",
            max_files=1000,
            max_size_bytes=1073741824,  # 1GB
            current_files=250,
            current_size_bytes=268435456,  # 256MB
            last_updated=last_updated
        )
        
        assert quota.user_id == "user123"
        assert quota.max_files == 1000
        assert quota.max_size_bytes == 1073741824
        assert quota.current_files == 250
        assert quota.current_size_bytes == 268435456
        assert quota.last_updated == last_updated
    
    def test_storage_quota_files_remaining(self):
        """Test files_remaining property calculation."""
        quota = StorageQuota(
            user_id="user123",
            max_files=100,
            max_size_bytes=1000000,
            current_files=30,
            current_size_bytes=300000,
            last_updated=datetime.now()
        )
        
        assert quota.files_remaining == 70
        
        # Test edge case - at limit
        quota.current_files = 100
        assert quota.files_remaining == 0
        
        # Test edge case - over limit
        quota.current_files = 110
        assert quota.files_remaining == 0
    
    def test_storage_quota_bytes_remaining(self):
        """Test bytes_remaining property calculation."""
        quota = StorageQuota(
            user_id="user123",
            max_files=100,
            max_size_bytes=1000000,
            current_files=30,
            current_size_bytes=300000,
            last_updated=datetime.now()
        )
        
        assert quota.bytes_remaining == 700000
        
        # Test edge case - at limit
        quota.current_size_bytes = 1000000
        assert quota.bytes_remaining == 0
        
        # Test edge case - over limit
        quota.current_size_bytes = 1100000
        assert quota.bytes_remaining == 0
    
    def test_storage_quota_usage_percent(self):
        """Test usage_percent property calculation."""
        quota = StorageQuota(
            user_id="user123",
            max_files=100,
            max_size_bytes=1000000,
            current_files=30,
            current_size_bytes=250000,  # 25% of max
            last_updated=datetime.now()
        )
        
        assert quota.usage_percent == 25.0
        
        # Test edge case - zero max size
        quota.max_size_bytes = 0
        assert quota.usage_percent == 0.0
        
        # Test edge case - 100% usage
        quota.max_size_bytes = 1000000
        quota.current_size_bytes = 1000000
        assert quota.usage_percent == 100.0


class TestEnums:
    """Test enum classes."""
    
    def test_storage_operation_type_enum(self):
        """Test StorageOperationType enum values."""
        assert StorageOperationType.SAVE_FILE.value == "save_file"
        assert StorageOperationType.RETRIEVE_FILE.value == "retrieve_file"
        assert StorageOperationType.DELETE_FILE.value == "delete_file"
        assert StorageOperationType.LIST_FILES.value == "list_files"
        assert StorageOperationType.SAVE_METADATA.value == "save_metadata"
        assert StorageOperationType.RETRIEVE_METADATA.value == "retrieve_metadata"
        assert StorageOperationType.DELETE_METADATA.value == "delete_metadata"
        assert StorageOperationType.UPDATE_METADATA.value == "update_metadata"
        assert StorageOperationType.BULK_OPERATION.value == "bulk_operation"
    
    def test_storage_error_code_enum(self):
        """Test StorageErrorCode enum values."""
        assert StorageErrorCode.FILE_NOT_FOUND.value == "FILE_NOT_FOUND"
        assert StorageErrorCode.METADATA_NOT_FOUND.value == "METADATA_NOT_FOUND"
        assert StorageErrorCode.INVALID_PATH.value == "INVALID_PATH"
        assert StorageErrorCode.PERMISSION_DENIED.value == "PERMISSION_DENIED"
        assert StorageErrorCode.STORAGE_FULL.value == "STORAGE_FULL"
        assert StorageErrorCode.INVALID_METADATA.value == "INVALID_METADATA"
        assert StorageErrorCode.ENCRYPTION_ERROR.value == "ENCRYPTION_ERROR"
        assert StorageErrorCode.ACCESS_CONTROL_ERROR.value == "ACCESS_CONTROL_ERROR"
        assert StorageErrorCode.CLOUD_INTEGRATION_ERROR.value == "CLOUD_INTEGRATION_ERROR"
        assert StorageErrorCode.AUDIT_LOG_ERROR.value == "AUDIT_LOG_ERROR"
        assert StorageErrorCode.SERVICE_UNAVAILABLE.value == "SERVICE_UNAVAILABLE"


class TestModelValidation:
    """Test model validation and edge cases."""
    
    def test_immutable_after_creation(self):
        """Test that dataclass instances behave as expected."""
        # Models should be mutable (standard dataclass behavior)
        result = StorageResult(success=True, message="test")
        result.message = "updated"
        assert result.message == "updated"
    
    def test_type_validation(self):
        """Test type validation for model fields."""
        # This would test type validation if we implement it
        # For now, just test that models accept expected types
        
        # Valid datetime
        timestamp = datetime.now()
        result = StorageResult(success=True, message="test", timestamp=timestamp)
        assert result.timestamp == timestamp
        
        # Valid list
        operations = [{"test": "data"}]
        request = BulkOperationRequest(operations=operations)
        assert request.operations == operations
    
    def test_model_representation(self):
        """Test string representation of models."""
        result = StorageResult(success=True, message="test")
        repr_str = repr(result)
        
        # Should contain class name and key fields
        assert "StorageResult" in repr_str
        assert "success=True" in repr_str
        assert "message='test'" in repr_str
    
    def test_model_equality(self):
        """Test model equality comparison."""
        timestamp = datetime.now()
        
        result1 = StorageResult(success=True, message="test", timestamp=timestamp)
        result2 = StorageResult(success=True, message="test", timestamp=timestamp)
        result3 = StorageResult(success=False, message="test", timestamp=timestamp)
        
        assert result1 == result2
        assert result1 != result3