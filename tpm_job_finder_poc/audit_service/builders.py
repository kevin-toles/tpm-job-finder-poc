"""
Audit Event Builder Implementation

Provides a fluent API for building audit events with proper validation
and context injection.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from tpm_job_finder_poc.shared.contracts.audit_service import (
    AuditEvent,
    AuditLevel,
    AuditCategory,
    IAuditEventBuilder,
    AuditEventValidationError
)


class AuditEventBuilder(IAuditEventBuilder):
    """
    Fluent builder for creating audit events.
    
    This builder provides a convenient way to construct audit events
    with proper validation and context injection.
    """
    
    def __init__(self, service_name: str):
        """Initialize builder with required service name."""
        self._service_name = service_name
        self._action: Optional[str] = None
        self._level: AuditLevel = AuditLevel.INFO
        self._category: AuditCategory = AuditCategory.SYSTEM_EVENT
        self._user_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._request_id: Optional[str] = None
        self._resource_type: Optional[str] = None
        self._resource_id: Optional[str] = None
        self._message: str = ""
        self._metadata: Dict[str, Any] = {}
        self._error_code: Optional[str] = None
        self._error_message: Optional[str] = None
        self._stack_trace: Optional[str] = None
        self._duration_ms: Optional[float] = None
    
    def action(self, action: str) -> 'AuditEventBuilder':
        """Set the action performed."""
        if not action or not action.strip():
            raise ValueError("action cannot be empty")
        self._action = action.strip()
        return self
    
    def level(self, level: AuditLevel) -> 'AuditEventBuilder':
        """Set the audit level."""
        if not isinstance(level, AuditLevel):
            raise ValueError(f"level must be an AuditLevel, got {type(level)}")
        self._level = level
        return self
    
    def category(self, category: AuditCategory) -> 'AuditEventBuilder':
        """Set the audit category."""
        if not isinstance(category, AuditCategory):
            raise ValueError(f"category must be an AuditCategory, got {type(category)}")
        self._category = category
        return self
    
    def user(self, user_id: str) -> 'AuditEventBuilder':
        """Set the user context."""
        if not user_id or not user_id.strip():
            raise ValueError("user_id cannot be empty")
        self._user_id = user_id.strip()
        return self
    
    def session(self, session_id: str) -> 'AuditEventBuilder':
        """Set the session context."""
        if not session_id or not session_id.strip():
            raise ValueError("session_id cannot be empty")
        self._session_id = session_id.strip()
        return self
    
    def request(self, request_id: str) -> 'AuditEventBuilder':
        """Set the request context."""
        if not request_id or not request_id.strip():
            raise ValueError("request_id cannot be empty")
        self._request_id = request_id.strip()
        return self
    
    def resource(self, resource_type: str, resource_id: str) -> 'AuditEventBuilder':
        """Set the resource context."""
        if not resource_type or not resource_type.strip():
            raise ValueError("resource_type cannot be empty")
        if not resource_id or not resource_id.strip():
            raise ValueError("resource_id cannot be empty")
        self._resource_type = resource_type.strip()
        self._resource_id = resource_id.strip()
        return self
    
    def message(self, message: str) -> 'AuditEventBuilder':
        """Set the event message."""
        self._message = message or ""
        return self
    
    def metadata(self, **kwargs: Any) -> 'AuditEventBuilder':
        """Add metadata to the event."""
        self._metadata.update(kwargs)
        return self
    
    def error(self, error_code: str, error_message: str, stack_trace: Optional[str] = None) -> 'AuditEventBuilder':
        """Set error information."""
        if not error_code or not error_code.strip():
            raise ValueError("error_code cannot be empty")
        if not error_message or not error_message.strip():
            raise ValueError("error_message cannot be empty")
        
        self._error_code = error_code.strip()
        self._error_message = error_message.strip()
        self._stack_trace = stack_trace
        self._level = AuditLevel.ERROR
        self._category = AuditCategory.ERROR_EVENT
        return self
    
    def duration(self, duration_ms: float) -> 'AuditEventBuilder':
        """Set performance duration."""
        if duration_ms < 0:
            raise ValueError("duration_ms cannot be negative")
        self._duration_ms = duration_ms
        return self
    
    def build(self) -> AuditEvent:
        """Build the final audit event."""
        if not self._action:
            raise ValueError("action is required - call action() before build()")
        
        return AuditEvent(
            action=self._action,
            level=self._level,
            category=self._category,
            service_name=self._service_name,
            user_id=self._user_id,
            session_id=self._session_id,
            request_id=self._request_id,
            resource_type=self._resource_type,
            resource_id=self._resource_id,
            message=self._message,
            metadata=self._metadata.copy(),
            error_code=self._error_code,
            error_message=self._error_message,
            stack_trace=self._stack_trace,
            duration_ms=self._duration_ms
        )


def create_audit_builder(service_name: str) -> AuditEventBuilder:
    """
    Create a new audit event builder for the given service.
    
    Args:
        service_name: Name of the service creating audit events
        
    Returns:
        New audit event builder instance
    """
    return AuditEventBuilder(service_name)