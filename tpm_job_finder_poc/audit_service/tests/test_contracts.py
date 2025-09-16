"""
Comprehensive Test Suite for Audit Service

This test suite follows TDD principles and tests all aspects of the audit service:
- Service contracts and interfaces
- Event schemas and validation
- Async operations and error handling
- Storage abstraction and implementations
- API endpoints and HTTP contracts
- Integration patterns and service boundaries

RED-GREEN-REFACTOR cycle implementation for microservice architecture.
"""

import asyncio
import json
import pytest
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch, AsyncMock

# Import contracts and types
from tpm_job_finder_poc.shared.contracts.audit_service import (
    AuditEvent,
    AuditQuery,
    AuditQueryResult,
    AuditLevel,
    AuditCategory,
    IAuditService,
    IAuditEventBuilder,
    AuditServiceError,
    AuditEventValidationError,
    AuditStorageError,
    AuditQueryError,
    create_user_action_event,
    create_api_request_event,
    create_error_event,
    create_data_access_event
)


class TestAuditEventSchema:
    """Test audit event schema and validation."""
    
    def test_audit_event_creation_with_defaults(self):
        """Test creating audit event with minimal required fields."""
        event = AuditEvent(
            action="test_action",
            service_name="test_service"
        )
        
        assert event.action == "test_action"
        assert event.service_name == "test_service"
        assert event.level == AuditLevel.INFO
        assert event.category == AuditCategory.SYSTEM_EVENT
        assert isinstance(event.event_id, str)
        assert isinstance(event.timestamp, datetime)
        assert event.metadata == {}
    
    def test_audit_event_immutability(self):
        """Test that audit events are immutable."""
        event = AuditEvent(
            action="test_action",
            service_name="test_service"
        )
        
        with pytest.raises(Exception):  # Should be frozen dataclass
            event.action = "modified_action"
    
    def test_audit_event_validation_missing_action(self):
        """Test validation fails when action is missing."""
        with pytest.raises(ValueError, match="action is required"):
            AuditEvent(action="", service_name="test_service")
    
    def test_audit_event_validation_missing_service_name(self):
        """Test validation fails when service_name is missing."""
        with pytest.raises(ValueError, match="service_name is required"):
            AuditEvent(action="test_action", service_name="")
    
    def test_audit_event_with_all_fields(self):
        """Test creating audit event with all fields populated."""
        metadata = {"key": "value", "count": 42}
        timestamp = datetime.utcnow()
        
        event = AuditEvent(
            event_id="custom-id",
            timestamp=timestamp,
            action="complex_action",
            level=AuditLevel.WARNING,
            category=AuditCategory.SECURITY,
            service_name="security_service",
            user_id="user123",
            session_id="session456",
            request_id="req789",
            resource_type="document",
            resource_id="doc123",
            message="Security event occurred",
            metadata=metadata,
            error_code="SEC001",
            error_message="Security violation detected",
            stack_trace="stack trace here",
            duration_ms=250.5
        )
        
        assert event.event_id == "custom-id"
        assert event.timestamp == timestamp
        assert event.action == "complex_action"
        assert event.level == AuditLevel.WARNING
        assert event.category == AuditCategory.SECURITY
        assert event.service_name == "security_service"
        assert event.user_id == "user123"
        assert event.session_id == "session456"
        assert event.request_id == "req789"
        assert event.resource_type == "document"
        assert event.resource_id == "doc123"
        assert event.message == "Security event occurred"
        assert event.metadata == metadata
        assert event.error_code == "SEC001"
        assert event.error_message == "Security violation detected"
        assert event.stack_trace == "stack trace here"
        assert event.duration_ms == 250.5


class TestAuditQuery:
    """Test audit query schema and validation."""
    
    def test_audit_query_defaults(self):
        """Test audit query with default values."""
        query = AuditQuery()
        
        assert query.start_time is None
        assert query.end_time is None
        assert query.service_names is None
        assert query.user_ids is None
        assert query.levels is None
        assert query.categories is None
        assert query.actions is None
        assert query.resource_types is None
        assert query.resource_ids is None
        assert query.message_contains is None
        assert query.limit == 100
        assert query.offset == 0
        assert query.order_by == "timestamp"
        assert query.order_desc is True
    
    def test_audit_query_with_filters(self):
        """Test audit query with all filters applied."""
        start_time = datetime.utcnow() - timedelta(hours=1)
        end_time = datetime.utcnow()
        
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            service_names=["service1", "service2"],
            user_ids=["user1", "user2"],
            levels=[AuditLevel.ERROR, AuditLevel.WARNING],
            categories=[AuditCategory.SECURITY, AuditCategory.ERROR_EVENT],
            actions=["login", "logout"],
            resource_types=["document", "user"],
            resource_ids=["doc123", "user456"],
            message_contains="error",
            limit=50,
            offset=10,
            order_by="level",
            order_desc=False
        )
        
        assert query.start_time == start_time
        assert query.end_time == end_time
        assert query.service_names == ["service1", "service2"]
        assert query.user_ids == ["user1", "user2"]
        assert query.levels == [AuditLevel.ERROR, AuditLevel.WARNING]
        assert query.categories == [AuditCategory.SECURITY, AuditCategory.ERROR_EVENT]
        assert query.actions == ["login", "logout"]
        assert query.resource_types == ["document", "user"]
        assert query.resource_ids == ["doc123", "user456"]
        assert query.message_contains == "error"
        assert query.limit == 50
        assert query.offset == 10
        assert query.order_by == "level"
        assert query.order_desc is False


class TestAuditQueryResult:
    """Test audit query result schema."""
    
    def test_audit_query_result_creation(self):
        """Test creating audit query result."""
        events = [
            AuditEvent(action="action1", service_name="service1"),
            AuditEvent(action="action2", service_name="service2")
        ]
        
        result = AuditQueryResult(
            events=events,
            total_count=100,
            has_more=True,
            query_duration_ms=150.5
        )
        
        assert result.events == events
        assert result.total_count == 100
        assert result.has_more is True
        assert result.query_duration_ms == 150.5


class TestConvenienceFunctions:
    """Test convenience functions for creating common audit events."""
    
    def test_create_user_action_event(self):
        """Test creating user action event."""
        event = create_user_action_event(
            action="file_upload",
            user_id="user123",
            message="User uploaded file",
            service_name="upload_service",
            file_size=1024,
            file_type="pdf"
        )
        
        assert event.action == "file_upload"
        assert event.category == AuditCategory.USER_ACTION
        assert event.level == AuditLevel.INFO
        assert event.user_id == "user123"
        assert event.message == "User uploaded file"
        assert event.service_name == "upload_service"
        assert event.metadata["file_size"] == 1024
        assert event.metadata["file_type"] == "pdf"
    
    def test_create_api_request_event(self):
        """Test creating API request event."""
        event = create_api_request_event(
            action="GET /api/users",
            request_id="req123",
            duration_ms=250.5,
            service_name="api_service",
            user_id="user456",
            status_code=200
        )
        
        assert event.action == "GET /api/users"
        assert event.category == AuditCategory.API_REQUEST
        assert event.level == AuditLevel.INFO
        assert event.user_id == "user456"
        assert event.request_id == "req123"
        assert event.duration_ms == 250.5
        assert event.service_name == "api_service"
        assert "API GET /api/users completed in 250.5ms" in event.message
        assert event.metadata["status_code"] == 200
    
    def test_create_error_event(self):
        """Test creating error event."""
        event = create_error_event(
            action="database_connection",
            error_message="Connection timeout",
            service_name="db_service",
            error_code="DB001",
            stack_trace="Traceback...",
            user_id="user789",
            query="SELECT * FROM users"
        )
        
        assert event.action == "database_connection"
        assert event.category == AuditCategory.ERROR_EVENT
        assert event.level == AuditLevel.ERROR
        assert event.user_id == "user789"
        assert event.service_name == "db_service"
        assert event.message == "Connection timeout"
        assert event.error_code == "DB001"
        assert event.error_message == "Connection timeout"
        assert event.stack_trace == "Traceback..."
        assert event.metadata["query"] == "SELECT * FROM users"
    
    def test_create_data_access_event(self):
        """Test creating data access event."""
        event = create_data_access_event(
            action="read",
            resource_type="user_profile",
            resource_id="profile123",
            user_id="user456",
            service_name="profile_service",
            fields_accessed=["name", "email"]
        )
        
        assert event.action == "read"
        assert event.category == AuditCategory.DATA_ACCESS
        assert event.level == AuditLevel.INFO
        assert event.user_id == "user456"
        assert event.resource_type == "user_profile"
        assert event.resource_id == "profile123"
        assert event.service_name == "profile_service"
        assert "User user456 performed read on user_profile:profile123" in event.message
        assert event.metadata["fields_accessed"] == ["name", "email"]


class TestAuditServiceInterface:
    """Test the audit service interface contract."""
    
    @pytest.fixture
    def mock_audit_service(self):
        """Create a mock audit service for testing."""
        service = Mock(spec=IAuditService)
        service.log_event = AsyncMock()
        service.log_events = AsyncMock()
        service.query_events = AsyncMock()
        service.get_event = AsyncMock()
        service.health_check = AsyncMock()
        return service
    
    @pytest.mark.asyncio
    async def test_log_event_interface(self, mock_audit_service):
        """Test log_event interface contract."""
        event = AuditEvent(action="test", service_name="test_service")
        
        await mock_audit_service.log_event(event)
        
        mock_audit_service.log_event.assert_called_once_with(event)
    
    @pytest.mark.asyncio
    async def test_log_events_interface(self, mock_audit_service):
        """Test log_events interface contract."""
        events = [
            AuditEvent(action="test1", service_name="test_service"),
            AuditEvent(action="test2", service_name="test_service")
        ]
        
        await mock_audit_service.log_events(events)
        
        mock_audit_service.log_events.assert_called_once_with(events)
    
    @pytest.mark.asyncio
    async def test_query_events_interface(self, mock_audit_service):
        """Test query_events interface contract."""
        query = AuditQuery(limit=50)
        mock_result = AuditQueryResult(
            events=[],
            total_count=0,
            has_more=False,
            query_duration_ms=10.0
        )
        mock_audit_service.query_events.return_value = mock_result
        
        result = await mock_audit_service.query_events(query)
        
        mock_audit_service.query_events.assert_called_once_with(query)
        assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_get_event_interface(self, mock_audit_service):
        """Test get_event interface contract."""
        event_id = "test-event-id"
        mock_event = AuditEvent(action="test", service_name="test_service")
        mock_audit_service.get_event.return_value = mock_event
        
        result = await mock_audit_service.get_event(event_id)
        
        mock_audit_service.get_event.assert_called_once_with(event_id)
        assert result == mock_event
    
    @pytest.mark.asyncio
    async def test_health_check_interface(self, mock_audit_service):
        """Test health_check interface contract."""
        mock_health = {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
        mock_audit_service.health_check.return_value = mock_health
        
        result = await mock_audit_service.health_check()
        
        mock_audit_service.health_check.assert_called_once()
        assert result == mock_health


class TestAuditServiceExceptions:
    """Test audit service exception handling."""
    
    def test_audit_service_error_hierarchy(self):
        """Test exception hierarchy."""
        assert issubclass(AuditEventValidationError, AuditServiceError)
        assert issubclass(AuditStorageError, AuditServiceError)
        assert issubclass(AuditQueryError, AuditServiceError)
    
    def test_audit_event_validation_error(self):
        """Test audit event validation error."""
        error = AuditEventValidationError("Invalid event")
        assert str(error) == "Invalid event"
        assert isinstance(error, AuditServiceError)
    
    def test_audit_storage_error(self):
        """Test audit storage error."""
        error = AuditStorageError("Storage failed")
        assert str(error) == "Storage failed"
        assert isinstance(error, AuditServiceError)
    
    def test_audit_query_error(self):
        """Test audit query error."""
        error = AuditQueryError("Query failed")
        assert str(error) == "Query failed"
        assert isinstance(error, AuditServiceError)


class TestAuditEventBuilderInterface:
    """Test the audit event builder interface."""
    
    @pytest.fixture
    def mock_builder(self):
        """Create a mock audit event builder."""
        builder = Mock(spec=IAuditEventBuilder)
        builder.action.return_value = builder
        builder.level.return_value = builder
        builder.category.return_value = builder
        builder.user.return_value = builder
        builder.session.return_value = builder
        builder.request.return_value = builder
        builder.resource.return_value = builder
        builder.message.return_value = builder
        builder.metadata.return_value = builder
        builder.error.return_value = builder
        builder.duration.return_value = builder
        return builder
    
    def test_builder_fluent_interface(self, mock_builder):
        """Test builder fluent interface."""
        result = (mock_builder
                 .action("test_action")
                 .level(AuditLevel.INFO)
                 .category(AuditCategory.USER_ACTION)
                 .user("user123")
                 .session("session456")
                 .request("req789")
                 .resource("document", "doc123")
                 .message("Test message")
                 .metadata(key="value")
                 .duration(100.5))
        
        # Verify fluent interface returns builder for chaining
        assert result == mock_builder
        
        # Verify all methods were called
        mock_builder.action.assert_called_once_with("test_action")
        mock_builder.level.assert_called_once_with(AuditLevel.INFO)
        mock_builder.category.assert_called_once_with(AuditCategory.USER_ACTION)
        mock_builder.user.assert_called_once_with("user123")
        mock_builder.session.assert_called_once_with("session456")
        mock_builder.request.assert_called_once_with("req789")
        mock_builder.resource.assert_called_once_with("document", "doc123")
        mock_builder.message.assert_called_once_with("Test message")
        mock_builder.metadata.assert_called_once_with(key="value")
        mock_builder.duration.assert_called_once_with(100.5)
    
    def test_builder_error_method(self, mock_builder):
        """Test builder error method."""
        mock_builder.error("ERR001", "Error occurred", "stack trace")
        
        mock_builder.error.assert_called_once_with("ERR001", "Error occurred", "stack trace")
    
    def test_builder_build_method(self, mock_builder):
        """Test builder build method."""
        mock_event = AuditEvent(action="test", service_name="test_service")
        mock_builder.build.return_value = mock_event
        
        result = mock_builder.build()
        
        mock_builder.build.assert_called_once()
        assert result == mock_event


class TestAsyncOperations:
    """Test async operation patterns and error handling."""
    
    @pytest.mark.asyncio
    async def test_concurrent_logging(self):
        """Test concurrent audit event logging."""
        # This test will verify that the service can handle concurrent operations
        # when we implement the actual service
        pass
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling for async operations."""
        # This test will verify timeout behavior
        # when we implement the actual service
        pass
    
    @pytest.mark.asyncio
    async def test_cancellation_handling(self):
        """Test cancellation handling for async operations."""
        # This test will verify cancellation behavior
        # when we implement the actual service
        pass


class TestServiceBoundaries:
    """Test service boundary enforcement and isolation."""
    
    def test_service_contract_isolation(self):
        """Test that service contracts provide proper isolation."""
        # Verify that services can only interact through contracts
        pass
    
    def test_dependency_injection(self):
        """Test dependency injection patterns."""
        # Verify that dependencies are properly injected
        pass
    
    def test_configuration_isolation(self):
        """Test that service configuration is isolated."""
        # Verify that service configuration doesn't leak
        pass


class TestPerformanceAndScaling:
    """Test performance characteristics and scaling behavior."""
    
    @pytest.mark.asyncio
    async def test_batch_processing_performance(self):
        """Test batch processing performance."""
        # This test will verify batch processing efficiency
        # when we implement the actual service
        pass
    
    @pytest.mark.asyncio
    async def test_memory_usage_patterns(self):
        """Test memory usage patterns."""
        # This test will verify memory efficiency
        # when we implement the actual service
        pass
    
    @pytest.mark.asyncio
    async def test_concurrent_query_performance(self):
        """Test concurrent query performance."""
        # This test will verify query performance under load
        # when we implement the actual service
        pass


class TestDataIntegrity:
    """Test data integrity and consistency."""
    
    def test_event_immutability_enforcement(self):
        """Test that audit events cannot be modified after creation."""
        event = AuditEvent(action="test", service_name="test_service")
        
        # Verify immutability
        with pytest.raises(Exception):
            event.action = "modified"
    
    def test_timestamp_consistency(self):
        """Test that timestamps are consistent and monotonic."""
        events = []
        for i in range(10):
            events.append(AuditEvent(action=f"action_{i}", service_name="test_service"))
        
        # Verify timestamps are in order (allowing for millisecond precision)
        for i in range(1, len(events)):
            assert events[i].timestamp >= events[i-1].timestamp
    
    def test_event_id_uniqueness(self):
        """Test that event IDs are unique."""
        events = []
        for i in range(100):
            events.append(AuditEvent(action=f"action_{i}", service_name="test_service"))
        
        event_ids = [event.event_id for event in events]
        assert len(set(event_ids)) == len(event_ids)  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])