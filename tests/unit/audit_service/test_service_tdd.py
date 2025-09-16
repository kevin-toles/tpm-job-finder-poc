"""
TDD Tests for Audit Service - RED# Implementation imports - what we're testing
from tpm_job_finder_poc.audit_service.service import AuditService
from tpm_job_finder_poc.audit_service.storage import JsonFileAuditStorage, IAuditStorage
from tpm_job_finder_poc.audit_service.config import AuditServiceConfig
from tpm_job_finder_poc.audit_service.builders import AuditEventBuildere
Following proper TDD: Write failing tests first to define expected behavior

Based on documentation analysis and shared contracts, the Audit Service should:
1. Implement IAuditService protocol  
2. Provide async event logging (single and batch)
3. Support event querying with filtering
4. Offer event builders for fluent API construction
5. Handle storage abstraction with multiple backends
6. Implement health monitoring and service lifecycle
7. Provide comprehensive error handling with specific exceptions
8. Support high-performance async operations with buffering
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

# Test imports - these define the expected interface
from tpm_job_finder_poc.shared.contracts.audit_service import (
    IAuditService,
    IAuditEventBuilder,
    AuditEvent,
    AuditQuery,
    AuditQueryResult,
    AuditLevel,
    AuditCategory,
    AuditServiceError,
    AuditEventValidationError,
    AuditStorageError
)

# Implementation imports - what we're testing
from tpm_job_finder_poc.audit_service.service import AuditService
from tpm_job_finder_poc.audit_service.storage import JsonFileAuditStorage, IAuditStorage
from tpm_job_finder_poc.audit_service.config import AuditServiceConfig
from tpm_job_finder_poc.audit_service.builders import AuditEventBuilder


class TestAuditServiceTDD:
    """TDD tests for audit service implementation."""
    
    @pytest.fixture
    def temp_storage_path(self):
        """Create temporary storage path for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def mock_storage(self):
        """Mock storage for isolation testing."""
        storage = Mock(spec=IAuditStorage)
        storage.store_event = AsyncMock()
        storage.store_events = AsyncMock()
        storage.query_events = AsyncMock()
        storage.get_event = AsyncMock()
        storage.health_check = AsyncMock(return_value={'status': 'healthy'})
        storage.start = AsyncMock()
        storage.stop = AsyncMock()
        return storage
    
    @pytest.fixture
    def service_config(self):
        """Default service configuration."""
        from tpm_job_finder_poc.audit_service.config import StorageConfig, ServiceConfig, APIConfig
        return AuditServiceConfig(
            storage=StorageConfig(type="file", file_path=Path("test_audit.jsonl")),
            service=ServiceConfig(service_name="test_audit_service", batch_size=10),
            api=APIConfig(host="127.0.0.1", port=8001)
        )
    
    @pytest.fixture 
    async def service(self, temp_storage_path, service_config):
        """Create audit service with file storage."""
        storage = JsonFileAuditStorage(
            file_path=temp_storage_path / "audit.jsonl",
            max_file_size_mb=1,
            backup_count=2
        )
        service = AuditService(
            storage=storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        await service.start()
        yield service
        await service.stop()
    
    @pytest.fixture
    def sample_audit_event(self):
        """Sample audit event for testing."""
        return AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION, 
            action="user_login",
            service_name="auth_service",
            user_id="user123",
            session_id="session456",
            message="User logged in successfully",
            metadata={"ip_address": "192.168.1.100", "user_agent": "Chrome/96.0"},
            timestamp=datetime.now(timezone.utc)
        )
    
    def test_service_initialization(self, mock_storage, service_config):
        """Test that service initializes correctly with required dependencies."""
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        
        # Service should implement the contract
        assert isinstance(service, IAuditService)
        assert service.storage == mock_storage
        assert not service._is_running
        assert service._event_buffer == []
        
    def test_implements_service_contract(self, mock_storage, service_config):
        """Test that service correctly implements IAuditService protocol."""
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        
        # Should have all required methods
        assert hasattr(service, 'log_event')
        assert hasattr(service, 'log_events')
        assert hasattr(service, 'query_events') 
        assert hasattr(service, 'get_event')
        assert hasattr(service, 'health_check')
        assert hasattr(service, 'start')
        assert hasattr(service, 'stop')
        assert hasattr(service, 'flush')
        assert hasattr(service, 'create_event_builder')
        
        # Methods should be callable
        assert callable(service.log_event)
        assert callable(service.log_events)
        assert callable(service.query_events)
        assert callable(service.get_event)
        assert callable(service.health_check)
        assert callable(service.start)
        assert callable(service.stop)
        assert callable(service.flush)
        assert callable(service.create_event_builder)

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, mock_storage, service_config):
        """Test service start/stop lifecycle management."""
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        
        # Should start correctly
        await service.start()
        assert service._is_running
        mock_storage.start.assert_called_once()
        
        # Should stop correctly
        await service.stop()
        assert not service._is_running
        mock_storage.stop.assert_called_once()
        
        # Should handle double start/stop gracefully
        await service.start()
        await service.start()  # Should not error
        await service.stop()
        await service.stop()   # Should not error

    @pytest.mark.asyncio
    async def test_log_single_event(self, service, sample_audit_event):
        """Test logging a single audit event."""
        await service.log_event(sample_audit_event)
        
        # Event should be processed
        assert len(service._event_buffer) == 1 or len(service._event_buffer) == 0  # May be flushed already
        
        # Should be able to query the event
        query = AuditQuery(
            service_names=["auth_service"],
            levels=[AuditLevel.INFO],
            limit=10
        )
        result = await service.query_events(query)
        assert isinstance(result, AuditQueryResult)
        assert len(result.events) == 1
        assert result.events[0].action == "user_login"

    @pytest.mark.asyncio 
    async def test_log_multiple_events_batch(self, service):
        """Test batch logging of multiple events."""
        events = []
        for i in range(5):
            event = AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.DATA_ACCESS,
                action="job_search",
                service_name="job_service", 
                user_id=f"user{i}",
                message=f"User searched for jobs: query {i}",
                metadata={"query": f"Python Developer {i}", "results": 10 + i}
            )
            events.append(event)
        
        await service.log_events(events)
        
        # All events should be processed
        query = AuditQuery(service_names=["job_service"], limit=20)
        result = await service.query_events(query)
        assert len(result.events) == 5
        
        # Events should be in correct order
        for i, event in enumerate(result.events):
            assert event.user_id == f"user{i}"
            assert f"query {i}" in event.message

    @pytest.mark.asyncio
    async def test_event_querying_with_filters(self, service):
        """Test event querying with various filters."""
        # Create diverse events
        events = [
            AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.USER_ACTION,
                action="login",
                service_name="auth_service",
                user_id="user1"
            ),
            AuditEvent(
                level=AuditLevel.ERROR,
                category=AuditCategory.SYSTEM_EVENT,
                action="database_error",
                service_name="data_service",
                user_id="system"
            ),
            AuditEvent(
                level=AuditLevel.WARNING,
                category=AuditCategory.SECURITY,
                action="failed_auth",
                service_name="auth_service",
                user_id="user2"
            )
        ]
        
        await service.log_events(events)
        
        # Test level filtering
        info_query = AuditQuery(levels=[AuditLevel.INFO])
        info_result = await service.query_events(info_query)
        assert len(info_result.events) == 1
        assert info_result.events[0].level == AuditLevel.INFO
        
        # Test service filtering
        auth_query = AuditQuery(service_names=["auth_service"])
        auth_result = await service.query_events(auth_query)
        assert len(auth_result.events) == 2
        
        # Test category filtering
        security_query = AuditQuery(categories=[AuditCategory.SECURITY])
        security_result = await service.query_events(security_query)
        assert len(security_result.events) == 1
        assert security_result.events[0].category == AuditCategory.SECURITY
        
        # Test user filtering
        user1_query = AuditQuery(user_ids=["user1"])
        user1_result = await service.query_events(user1_query)
        assert len(user1_result.events) == 1
        assert user1_result.events[0].user_id == "user1"
        
        # Test limit
        limited_query = AuditQuery(limit=2)
        limited_result = await service.query_events(limited_query)
        assert len(limited_result.events) <= 2

    @pytest.mark.asyncio
    async def test_get_specific_event(self, service, sample_audit_event):
        """Test retrieving a specific event by ID."""
        await service.log_event(sample_audit_event)
        
        # Should be able to retrieve by event ID
        retrieved_event = await service.get_event(sample_audit_event.event_id)
        assert retrieved_event is not None
        assert retrieved_event.event_id == sample_audit_event.event_id
        assert retrieved_event.action == sample_audit_event.action
        
        # Non-existent event should return None
        non_existent = await service.get_event("non-existent-id")
        assert non_existent is None

    @pytest.mark.asyncio
    async def test_event_builder_integration(self, service):
        """Test event builder integration with service."""
        builder = service.create_event_builder()
        assert isinstance(builder, IAuditEventBuilder)
        
        # Builder should create valid events
        event = (builder
                .level(AuditLevel.WARNING)
                .category(AuditCategory.PERFORMANCE) 
                .action("slow_query")
                .service_name("database_service")  # Override service name
                .message("Query took 5.2 seconds")
                .metadata(query="SELECT * FROM jobs", duration=5.2)
                .build())
        
        assert isinstance(event, AuditEvent)
        assert event.level == AuditLevel.WARNING
        assert event.category == AuditCategory.PERFORMANCE
        assert event.action == "slow_query"
        assert event.service_name == "database_service"  # Should be overridden
        assert event.metadata["duration"] == 5.2
        
        # Event should be loggable
        await service.log_event(event)
        retrieved = await service.get_event(event.event_id)
        assert retrieved.action == "slow_query"

    @pytest.mark.asyncio
    async def test_buffering_and_flushing(self, mock_storage, service_config):
        """Test event buffering and manual flushing."""
        service_config.service.batch_size = 5  # Set small batch size
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        await service.start()
        
        # Add events to buffer
        events = []
        for i in range(3):
            event = AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.USER_ACTION,
                action=f"action_{i}",
                service_name="test_service"
            )
            events.append(event)
            await service.log_event(event)
        
        # Events should be buffered (not flushed yet)
        assert len(service._event_buffer) == 3
        mock_storage.store_events.assert_not_called()
        
        # Manual flush should store events
        await service.flush()
        assert len(service._event_buffer) == 0
        mock_storage.store_events.assert_called_once()
        
        await service.stop()

    @pytest.mark.asyncio
    async def test_automatic_batch_flushing(self, mock_storage, service_config):
        """Test automatic flushing when batch size is reached."""
        service_config.service.batch_size = 3  # Small batch size
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        await service.start()
        
        # Add events up to batch size
        for i in range(3):
            event = AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.USER_ACTION,
                action=f"action_{i}",
                service_name="test_service"
            )
            await service.log_event(event)
        
        # Should auto-flush when batch size reached
        await asyncio.sleep(0.1)  # Allow for async processing
        mock_storage.store_events.assert_called()
        
        await service.stop()

    @pytest.mark.asyncio
    async def test_periodic_flushing(self, mock_storage, service_config):
        """Test periodic flushing based on flush interval."""
        service_config.service.flush_interval_seconds = 0.1  # Very short interval for testing
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        await service.start()
        
        # Add one event (below batch threshold)
        event = AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION,
            action="test_action",
            service_name="test_service"
        )
        await service.log_event(event)
        
        # Wait for flush interval
        await asyncio.sleep(0.2)
        
        # Should have flushed due to timer
        mock_storage.store_events.assert_called()
        
        await service.stop()

    @pytest.mark.asyncio
    async def test_error_handling_validation(self, service):
        """Test validation error handling."""
        # Test service-level validation (message length)
        with pytest.raises(AuditEventValidationError):
            long_message_event = AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.USER_ACTION,
                action="test_action",
                service_name="test_service",
                message="x" * 10001  # Exceeds 10000 character limit
            )
            await service.log_event(long_message_event)

    @pytest.mark.asyncio
    async def test_error_handling_storage_failures(self, service_config):
        """Test handling of storage failures."""
        # Mock storage that fails
        failing_storage = Mock(spec=IAuditStorage)
        failing_storage.start = AsyncMock()
        failing_storage.stop = AsyncMock()
        failing_storage.store_event = AsyncMock(side_effect=AuditStorageError("Storage failed"))
        failing_storage.store_events = AsyncMock(side_effect=AuditStorageError("Storage failed"))
        
        service = AuditService(
            storage=failing_storage, 
            service_name=service_config.service.service_name,
            batch_size=1,  # Force immediate flush
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        await service.start()
        
        # Storage errors should be propagated
        event = AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION,
            action="test_action",
            service_name="test_service"
        )
        
        with pytest.raises(AuditStorageError):
            await service.log_event(event)
        
        await service.stop()

    @pytest.mark.asyncio
    async def test_health_check(self, service):
        """Test service health check functionality."""
        health = await service.health_check()
        
        assert isinstance(health, dict)
        assert 'status' in health
        assert 'service' in health 
        assert 'storage' in health
        assert 'timestamp' in health
        
        # Service should be healthy
        assert health['status'] in ['healthy', 'degraded', 'unhealthy']
        assert isinstance(health['service'], dict)
        assert isinstance(health['storage'], dict)
        
        # Should include metrics
        assert 'events_processed' in health['service']
        assert 'buffer_size' in health['service']
        assert 'started' in health['service']

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, service):
        """Test concurrent event logging and querying."""
        # Create multiple tasks for concurrent logging
        log_tasks = []
        for i in range(10):
            event = AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.API_REQUEST,
                action=f"api_call_{i}",
                service_name="api_service",
                user_id=f"user{i}",
                message=f"API call {i}"
            )
            task = asyncio.create_task(service.log_event(event))
            log_tasks.append(task)
        
        # Execute all logging tasks concurrently
        await asyncio.gather(*log_tasks)
        
        # Concurrent querying
        query_tasks = []
        for _ in range(5):
            query = AuditQuery(service_names=["api_service"], limit=20)
            task = asyncio.create_task(service.query_events(query))
            query_tasks.append(task)
        
        results = await asyncio.gather(*query_tasks)
        
        # All queries should succeed
        for result in results:
            assert isinstance(result, AuditQueryResult)
            assert len(result.events) == 10

    @pytest.mark.asyncio
    async def test_query_pagination(self, service):
        """Test query result pagination."""
        # Create many events
        events = []
        for i in range(25):
            event = AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.DATA_ACCESS,
                action="data_read",
                service_name="data_service",
                message=f"Read operation {i}"
            )
            events.append(event)
        
        await service.log_events(events)
        
        # Test pagination with limit and offset
        page1_query = AuditQuery(
            service_names=["data_service"],
            limit=10,
            offset=0
        )
        page1_result = await service.query_events(page1_query)
        assert len(page1_result.events) == 10
        assert page1_result.total_count == 25
        assert page1_result.has_more is True
        
        page2_query = AuditQuery(
            service_names=["data_service"],
            limit=10,
            offset=10
        )
        page2_result = await service.query_events(page2_query)
        assert len(page2_result.events) == 10
        assert page2_result.has_more is True
        
        # Events should be different between pages
        page1_ids = {event.event_id for event in page1_result.events}
        page2_ids = {event.event_id for event in page2_result.events}
        assert len(page1_ids.intersection(page2_ids)) == 0

    @pytest.mark.asyncio
    async def test_time_range_filtering(self, service):
        """Test querying events within specific time ranges."""
        base_time = datetime.now(timezone.utc)
        
        # Create events at different times
        past_event = AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION,
            action="past_action",
            service_name="test_service",
            timestamp=base_time.replace(hour=base_time.hour-1)  # 1 hour ago
        )
        
        current_event = AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION,
            action="current_action",
            service_name="test_service",
            timestamp=base_time
        )
        
        await service.log_events([past_event, current_event])
        
        # Query with time range
        recent_query = AuditQuery(
            service_names=["test_service"],
            start_time=base_time - timedelta(minutes=30),  # 30 minutes ago
            end_time=base_time + timedelta(minutes=30)     # 30 minutes future
        )
        
        recent_result = await service.query_events(recent_query)
        
        # Should only get the current event
        assert len(recent_result.events) == 1
        assert recent_result.events[0].action == "current_action"

    def test_audit_event_model_validation(self):
        """Test audit event data model validation."""
        # Valid event should create successfully
        valid_event = AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION,
            action="test_action",
            service_name="test_service"
        )
        
        assert valid_event.level == AuditLevel.INFO
        assert valid_event.category == AuditCategory.USER_ACTION
        assert valid_event.action == "test_action"
        assert valid_event.service_name == "test_service"
        assert isinstance(valid_event.event_id, str)
        assert isinstance(valid_event.timestamp, datetime)
        
    def test_audit_query_model_validation(self):
        """Test audit query data model validation."""
        # Valid query should create successfully
        query = AuditQuery(
            service_names=["service1", "service2"],
            levels=[AuditLevel.INFO, AuditLevel.ERROR],
            categories=[AuditCategory.USER_ACTION],
            user_ids=["user1"],
            limit=50,
            offset=10
        )
        
        assert query.service_names == ["service1", "service2"]
        assert query.levels == [AuditLevel.INFO, AuditLevel.ERROR]
        assert query.categories == [AuditCategory.USER_ACTION]
        assert query.user_ids == ["user1"]
        assert query.limit == 50
        assert query.offset == 10

    def test_audit_query_result_model(self):
        """Test audit query result data model."""
        events = [
            AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.USER_ACTION,
                action="action1",
                service_name="service1"
            ),
            AuditEvent(
                level=AuditLevel.INFO,
                category=AuditCategory.USER_ACTION,
                action="action2", 
                service_name="service1"
            )
        ]
        
        result = AuditQueryResult(
            events=events,
            total_count=10,
            has_more=True,
            query_duration_ms=25.5
        )
        
        assert len(result.events) == 2
        assert result.total_count == 10
        assert result.has_more is True
        assert result.query_duration_ms == 25.5

    @pytest.mark.asyncio
    async def test_service_shutdown_cleanup(self, mock_storage, service_config):
        """Test that service properly cleans up on shutdown."""
        service = AuditService(
            storage=mock_storage, 
            service_name=service_config.service.service_name,
            batch_size=service_config.service.batch_size,
            flush_interval_seconds=service_config.service.flush_interval_seconds
        )
        await service.start()
        
        # Add some events to buffer
        event = AuditEvent(
            level=AuditLevel.INFO,
            category=AuditCategory.USER_ACTION,
            action="test_action",
            service_name="test_service"
        )
        await service.log_event(event)
        
        # Shutdown should flush remaining events
        await service.stop()
        
        # Buffer should be empty and storage should have been called
        assert len(service._event_buffer) == 0
        mock_storage.store_events.assert_called()
        mock_storage.stop.assert_called_once()