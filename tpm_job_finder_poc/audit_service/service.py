"""
Audit Service Implementation

Core service for audit event management with async operations,
event validation, and comprehensive logging capabilities.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import asyncio
import logging
import uuid

from tpm_job_finder_poc.shared.contracts.audit_service import (
    AuditEvent,
    AuditQuery,
    AuditQueryResult,
    IAuditService,
    IAuditEventBuilder,
    AuditServiceError,
    AuditEventValidationError,
    AuditStorageError
)
from .storage import IAuditStorage
from .builders import AuditEventBuilder


class AuditService(IAuditService):
    """
    Production audit service implementation.
    
    Provides comprehensive audit event management with:
    - Asynchronous event processing
    - Validation and error handling
    - Storage abstraction
    - Performance monitoring
    """
    
    def __init__(self, 
                 storage: IAuditStorage,
                 service_name: str = "audit_service",
                 batch_size: int = 100,
                 flush_interval_seconds: float = 5.0):
        """
        Initialize audit service.
        
        Args:
            storage: Storage backend for audit events
            service_name: Name of this service instance
            batch_size: Maximum events to batch before flushing
            flush_interval_seconds: Maximum time between flushes
        """
        self.storage = storage
        self.service_name = service_name
        self.batch_size = batch_size
        self.flush_interval_seconds = flush_interval_seconds
        
        self._logger = logging.getLogger(__name__)
        self._event_buffer: List[AuditEvent] = []
        self._buffer_lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Performance counters
        self._events_processed = 0
        self._events_failed = 0
        self._last_flush_time = datetime.now(timezone.utc)
    
    async def start(self) -> None:
        """Start the audit service."""
        if self._is_running:
            return
        
        # Start storage layer first
        await self.storage.start()
        
        self._is_running = True
        self._flush_task = asyncio.create_task(self._periodic_flush())
        self._logger.info(f"Audit service started: {self.service_name}")
    
    async def stop(self) -> None:
        """Stop the audit service and flush remaining events."""
        if not self._is_running:
            return
        
        self._is_running = False
        
        # Cancel periodic flush
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining events
        try:
            await self._flush_buffer()
        except (AuditStorageError, Exception) as e:
            self._logger.error(f"Failed to flush remaining events during shutdown: {e}")
            # Don't re-raise during shutdown to avoid blocking stop
        
        # Stop storage layer
        await self.storage.stop()
        
        self._logger.info(f"Audit service stopped: {self.service_name}")
    
    async def log_event(self, event: AuditEvent) -> None:
        """Log a single audit event."""
        try:
            # Validate event
            self._validate_event(event)
            
            # Add to buffer
            async with self._buffer_lock:
                self._event_buffer.append(event)
                
                # Flush if buffer is full
                if len(self._event_buffer) >= self.batch_size:
                    await self._flush_buffer_unlocked()
            
            self._events_processed += 1
            
        except ValueError as e:
            # Convert dataclass validation errors to service validation errors
            self._events_failed += 1
            raise AuditEventValidationError(str(e))
        except (AuditServiceError, AuditEventValidationError, AuditStorageError):
            # Re-raise audit-specific errors
            self._events_failed += 1
            raise
        except Exception as e:
            self._events_failed += 1
            self._logger.error(f"Failed to log audit event: {e}")
            raise AuditServiceError(f"Failed to log event: {e}") from e
    
    async def log_events(self, events: List[AuditEvent]) -> None:
        """Log multiple audit events."""
        if not events:
            return
        
        try:
            # Validate all events
            for event in events:
                self._validate_event(event)
            
            # Add to buffer
            async with self._buffer_lock:
                self._event_buffer.extend(events)
                
                # Flush if buffer is full
                if len(self._event_buffer) >= self.batch_size:
                    await self._flush_buffer_unlocked()
            
            self._events_processed += len(events)
            
        except Exception as e:
            self._events_failed += len(events)
            self._logger.error(f"Failed to log {len(events)} audit events: {e}")
            raise AuditServiceError(f"Failed to log events: {e}") from e
    
    async def query_events(self, query: AuditQuery) -> AuditQueryResult:
        """Query audit events."""
        try:
            # Flush buffer to ensure latest events are included
            await self._flush_buffer()
            
            # Execute query
            result = await self.storage.query_events(query)
            
            self._logger.debug(
                f"Query returned {len(result.events)} events "
                f"(total: {result.total_count}, duration: {result.query_duration_ms}ms)"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to query audit events: {e}")
            raise AuditServiceError(f"Failed to query events: {e}") from e
    
    async def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get a specific audit event by ID."""
        try:
            # Check buffer first
            async with self._buffer_lock:
                for event in self._event_buffer:
                    if event.event_id == event_id:
                        return event
            
            # Check storage
            return await self.storage.get_event(event_id)
            
        except Exception as e:
            self._logger.error(f"Failed to get audit event {event_id}: {e}")
            raise AuditServiceError(f"Failed to get event: {e}") from e
    
    def create_event_builder(self) -> IAuditEventBuilder:
        """Create a new audit event builder."""
        return AuditEventBuilder(self.service_name)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check service health."""
        try:
            # Check storage health
            storage_health = await self.storage.health_check()
            
            # Calculate uptime and performance metrics
            now = datetime.now(timezone.utc)
            buffer_size = len(self._event_buffer)
            time_since_flush = (now - self._last_flush_time).total_seconds()
            
            health_status = {
                "service": {
                    "name": self.service_name,
                    "status": "healthy" if self._is_running else "stopped",
                    "running": self._is_running,
                    "started": self._is_running,
                    "buffer_size": buffer_size,
                    "time_since_last_flush_seconds": time_since_flush,
                    "events_processed": self._events_processed,
                    "events_failed": self._events_failed,
                    "success_rate": (
                        self._events_processed / (self._events_processed + self._events_failed)
                        if self._events_processed + self._events_failed > 0 else 1.0
                    )
                },
                "storage": storage_health
            }
            
            # Overall health
            overall_healthy = (
                self._is_running and 
                storage_health.get("status") == "healthy" and
                buffer_size < self.batch_size * 2  # Not severely backed up
            )
            
            health_status["status"] = "healthy" if overall_healthy else "unhealthy"
            health_status["timestamp"] = now.isoformat()
            
            return health_status
            
        except Exception as e:
            self._logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "service": {
                    "name": self.service_name,
                    "error": str(e)
                }
            }
    
    async def flush(self) -> None:
        """Manually flush buffered events."""
        await self._flush_buffer()
    
    def _validate_event(self, event: AuditEvent) -> None:
        """Validate audit event."""
        if not event.event_id:
            raise AuditEventValidationError("Event ID is required")
        
        if not event.action:
            raise AuditEventValidationError("Action is required")
        
        if not event.service_name:
            raise AuditEventValidationError("Service name is required")
        
        if len(event.message) > 10000:  # Reasonable message length limit
            raise AuditEventValidationError("Message too long (max 10000 characters)")
        
        # Validate metadata size
        if event.metadata and len(str(event.metadata)) > 50000:
            raise AuditEventValidationError("Metadata too large (max 50KB)")
    
    async def _flush_buffer(self) -> None:
        """Flush the event buffer to storage."""
        async with self._buffer_lock:
            await self._flush_buffer_unlocked()
    
    async def _flush_buffer_unlocked(self) -> None:
        """Flush buffer without acquiring lock (must be called with lock held)."""
        if not self._event_buffer:
            return
        
        try:
            events_to_flush = self._event_buffer.copy()
            self._event_buffer.clear()
            
            # Store events
            await self.storage.store_events(events_to_flush)
            
            self._last_flush_time = datetime.now(timezone.utc)
            self._logger.debug(f"Flushed {len(events_to_flush)} audit events")
            
        except Exception as e:
            # Re-add events to buffer on failure
            self._event_buffer.extend(events_to_flush)
            self._logger.error(f"Failed to flush events: {e}")
            raise
    
    async def _periodic_flush(self) -> None:
        """Periodically flush the event buffer."""
        while self._is_running:
            try:
                await asyncio.sleep(self.flush_interval_seconds)
                
                if self._is_running:  # Check again after sleep
                    await self._flush_buffer()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Error in periodic flush: {e}")
                # Continue running despite errors


def create_audit_service(storage: IAuditStorage, 
                        service_name: str = "audit_service") -> IAuditService:
    """
    Create a configured audit service instance.
    
    Args:
        storage: Storage backend
        service_name: Name for this service instance
        
    Returns:
        Configured audit service
    """
    return AuditService(storage, service_name)