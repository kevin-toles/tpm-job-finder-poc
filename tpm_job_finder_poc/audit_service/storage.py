"""
Audit Service Storage Abstraction

Provides storage interfaces and implementations for audit event persistence.
Supports multiple storage backends with async operations.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import asyncio
import json
import logging
from pathlib import Path
import os

from tpm_job_finder_poc.shared.contracts.audit_service import (
    AuditEvent,
    AuditQuery,
    AuditQueryResult,
    AuditStorageError
)


class IAuditStorage(ABC):
    """Abstract interface for audit event storage."""
    
    @abstractmethod
    async def store_event(self, event: AuditEvent) -> None:
        """Store a single audit event."""
        pass
    
    @abstractmethod
    async def store_events(self, events: List[AuditEvent]) -> None:
        """Store multiple audit events."""
        pass
    
    @abstractmethod
    async def query_events(self, query: AuditQuery) -> AuditQueryResult:
        """Query audit events with filtering."""
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get a specific audit event by ID."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Check storage health."""
        pass


class JsonFileAuditStorage(IAuditStorage):
    """
    File-based audit storage using JSON lines format.
    
    This implementation provides a simple, reliable audit storage
    suitable for development and small-scale deployments.
    """
    
    def __init__(self, 
                 file_path: Path, 
                 max_file_size_mb: int = 100,
                 backup_count: int = 5):
        """
        Initialize JSON file storage.
        
        Args:
            file_path: Path to the audit log file
            max_file_size_mb: Maximum file size before rotation
            backup_count: Number of backup files to keep
        """
        self.file_path = Path(file_path)
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.backup_count = backup_count
        self._lock = asyncio.Lock()
        self._logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def store_event(self, event: AuditEvent) -> None:
        """Store a single audit event."""
        await self.store_events([event])
    
    async def store_events(self, events: List[AuditEvent]) -> None:
        """Store multiple audit events."""
        if not events:
            return
        
        async with self._lock:
            try:
                # Check if file rotation is needed
                await self._rotate_if_needed()
                
                # Append events to file
                with open(self.file_path, 'a', encoding='utf-8') as f:
                    for event in events:
                        event_dict = self._event_to_dict(event)
                        json_line = json.dumps(event_dict, default=str, ensure_ascii=False)
                        f.write(json_line + '\n')
                
                self._logger.debug(f"Stored {len(events)} audit events")
                
            except Exception as e:
                self._logger.error(f"Failed to store audit events: {e}")
                raise AuditStorageError(f"Failed to store events: {e}") from e
    
    async def query_events(self, query: AuditQuery) -> AuditQueryResult:
        """Query audit events with filtering."""
        start_time = datetime.utcnow()
        
        try:
            matching_events = []
            total_count = 0
            
            # Read and filter events
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                event_dict = json.loads(line.strip())
                                event = self._dict_to_event(event_dict)
                                
                                if self._matches_query(event, query):
                                    total_count += 1
                                    if len(matching_events) < query.limit and total_count > query.offset:
                                        matching_events.append(event)
                                        
                            except (json.JSONDecodeError, ValueError) as e:
                                self._logger.warning(f"Failed to parse audit event: {e}")
                                continue
            
            # Sort events
            if query.order_by == "timestamp":
                matching_events.sort(
                    key=lambda e: e.timestamp,
                    reverse=query.order_desc
                )
            
            # Apply pagination
            start_idx = query.offset
            end_idx = start_idx + query.limit
            paginated_events = matching_events[start_idx:end_idx]
            
            query_duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return AuditQueryResult(
                events=paginated_events,
                total_count=total_count,
                has_more=total_count > query.offset + len(paginated_events),
                query_duration_ms=query_duration
            )
            
        except Exception as e:
            self._logger.error(f"Failed to query audit events: {e}")
            raise AuditStorageError(f"Failed to query events: {e}") from e
    
    async def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Get a specific audit event by ID."""
        try:
            if self.file_path.exists():
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                event_dict = json.loads(line.strip())
                                if event_dict.get('event_id') == event_id:
                                    return self._dict_to_event(event_dict)
                            except (json.JSONDecodeError, ValueError):
                                continue
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to get audit event {event_id}: {e}")
            raise AuditStorageError(f"Failed to get event: {e}") from e
    
    async def health_check(self) -> Dict[str, Any]:
        """Check storage health."""
        try:
            file_exists = self.file_path.exists()
            file_size = self.file_path.stat().st_size if file_exists else 0
            writable = self.file_path.parent.exists() and os.access(self.file_path.parent, os.W_OK)
            
            return {
                "status": "healthy" if writable else "unhealthy",
                "file_exists": file_exists,
                "file_size_bytes": file_size,
                "file_path": str(self.file_path),
                "writable": writable
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    def _event_to_dict(self, event: AuditEvent) -> Dict[str, Any]:
        """Convert audit event to dictionary."""
        return {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "level": event.level.value,
            "category": event.category.value,
            "action": event.action,
            "service_name": event.service_name,
            "user_id": event.user_id,
            "session_id": event.session_id,
            "request_id": event.request_id,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "message": event.message,
            "metadata": event.metadata,
            "error_code": event.error_code,
            "error_message": event.error_message,
            "stack_trace": event.stack_trace,
            "duration_ms": event.duration_ms
        }
    
    def _dict_to_event(self, event_dict: Dict[str, Any]) -> AuditEvent:
        """Convert dictionary to audit event."""
        from tpm_job_finder_poc.shared.contracts.audit_service import AuditLevel, AuditCategory
        
        return AuditEvent(
            event_id=event_dict["event_id"],
            timestamp=datetime.fromisoformat(event_dict["timestamp"]),
            level=AuditLevel(event_dict["level"]),
            category=AuditCategory(event_dict["category"]),
            action=event_dict["action"],
            service_name=event_dict["service_name"],
            user_id=event_dict.get("user_id"),
            session_id=event_dict.get("session_id"),
            request_id=event_dict.get("request_id"),
            resource_type=event_dict.get("resource_type"),
            resource_id=event_dict.get("resource_id"),
            message=event_dict.get("message", ""),
            metadata=event_dict.get("metadata", {}),
            error_code=event_dict.get("error_code"),
            error_message=event_dict.get("error_message"),
            stack_trace=event_dict.get("stack_trace"),
            duration_ms=event_dict.get("duration_ms")
        )
    
    def _matches_query(self, event: AuditEvent, query: AuditQuery) -> bool:
        """Check if event matches query filters."""
        # Time range
        if query.start_time and event.timestamp < query.start_time:
            return False
        if query.end_time and event.timestamp > query.end_time:
            return False
        
        # Filters
        if query.service_names and event.service_name not in query.service_names:
            return False
        if query.user_ids and event.user_id not in query.user_ids:
            return False
        if query.levels and event.level not in query.levels:
            return False
        if query.categories and event.category not in query.categories:
            return False
        if query.actions and event.action not in query.actions:
            return False
        if query.resource_types and event.resource_type not in query.resource_types:
            return False
        if query.resource_ids and event.resource_id not in query.resource_ids:
            return False
        
        # Search
        if query.message_contains and query.message_contains.lower() not in event.message.lower():
            return False
        
        return True
    
    async def _rotate_if_needed(self) -> None:
        """Rotate log file if it exceeds size limit."""
        if not self.file_path.exists():
            return
        
        file_size = self.file_path.stat().st_size
        if file_size < self.max_file_size_bytes:
            return
        
        # Rotate existing backups
        for i in range(self.backup_count - 1, 0, -1):
            old_backup = self.file_path.with_suffix(f'.{i}')
            new_backup = self.file_path.with_suffix(f'.{i + 1}')
            if old_backup.exists():
                old_backup.replace(new_backup)
        
        # Move current file to .1
        backup_file = self.file_path.with_suffix('.1')
        self.file_path.replace(backup_file)
        
        self._logger.info(f"Rotated audit log file: {self.file_path}")


def create_default_storage(base_path: Optional[Path] = None) -> IAuditStorage:
    """
    Create default audit storage for development/testing.
    
    Args:
        base_path: Base directory for audit files
        
    Returns:
        Configured audit storage instance
    """
    if base_path is None:
        base_path = Path("logs")
    
    audit_file = base_path / "audit.jsonl"
    return JsonFileAuditStorage(audit_file)