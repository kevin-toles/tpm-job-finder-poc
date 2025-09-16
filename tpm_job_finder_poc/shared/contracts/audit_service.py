"""
Audit Service Contract - Defines the API interface for audit logging microservice.

This contract ensures type safety and clear boundaries between the audit service
and its consumers. All interactions with the audit service should go through
these interfaces.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import uuid


class AuditLevel(str, Enum):
    """Audit event severity levels."""
    DEBUG = "debug"
    INFO = "info" 
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Audit event categories for classification."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_EVENT = "system_event"
    USER_ACTION = "user_action"
    API_REQUEST = "api_request"
    ERROR_EVENT = "error_event"
    PERFORMANCE = "performance"
    SECURITY = "security"


@dataclass(frozen=True)
class AuditEvent:
    """
    Immutable audit event data structure.
    
    Represents a single auditable event in the system with all necessary
    context for compliance, debugging, and monitoring.
    """
    # Core event identification
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Event classification
    level: AuditLevel = AuditLevel.INFO
    category: AuditCategory = AuditCategory.SYSTEM_EVENT
    action: str = ""  # Action performed (e.g., "login", "job_scraped", "resume_uploaded")
    
    # Context information
    service_name: str = ""  # Which service generated this event
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    
    # Resource information
    resource_type: Optional[str] = None  # Type of resource affected
    resource_id: Optional[str] = None    # ID of specific resource
    
    # Event details
    message: str = ""  # Human-readable description
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional context
    
    # Error information (if applicable)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Performance metrics (if applicable)
    duration_ms: Optional[float] = None
    
    def __post_init__(self):
        """Validate audit event data."""
        if not self.action:
            raise ValueError("action is required for audit events")
        if not self.service_name:
            raise ValueError("service_name is required for audit events")


@dataclass
class AuditQuery:
    """Query parameters for retrieving audit events."""
    # Time range
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Filtering
    service_names: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    levels: Optional[List[AuditLevel]] = None
    categories: Optional[List[AuditCategory]] = None
    actions: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    resource_ids: Optional[List[str]] = None
    
    # Search
    message_contains: Optional[str] = None
    
    # Pagination
    limit: int = 100
    offset: int = 0
    
    # Ordering
    order_by: str = "timestamp"
    order_desc: bool = True


@dataclass
class AuditQueryResult:
    """Result of an audit query."""
    events: List[AuditEvent]
    total_count: int
    has_more: bool
    query_duration_ms: float


class AuditServiceError(Exception):
    """Base exception for audit service errors."""
    pass


class AuditEventValidationError(AuditServiceError):
    """Raised when audit event validation fails."""
    pass


class AuditStorageError(AuditServiceError):
    """Raised when audit storage operations fail."""
    pass


class AuditQueryError(AuditServiceError):
    """Raised when audit queries fail."""
    pass


class IAuditService(ABC):
    """
    Abstract interface for the audit service.
    
    This interface defines all operations that can be performed with
    the audit service. Implementations must provide async operations
    for scalability.
    """
    
    @abstractmethod
    async def log_event(self, event: AuditEvent) -> None:
        """
        Log a single audit event.
        
        Args:
            event: The audit event to log
            
        Raises:
            AuditEventValidationError: If event validation fails
            AuditStorageError: If storage operation fails
        """
        pass
    
    @abstractmethod
    async def log_events(self, events: List[AuditEvent]) -> None:
        """
        Log multiple audit events in batch.
        
        Args:
            events: List of audit events to log
            
        Raises:
            AuditEventValidationError: If any event validation fails
            AuditStorageError: If storage operation fails
        """
        pass
    
    @abstractmethod
    async def query_events(self, query: AuditQuery) -> AuditQueryResult:
        """
        Query audit events with filtering and pagination.
        
        Args:
            query: Query parameters and filters
            
        Returns:
            Query result with matching events and metadata
            
        Raises:
            AuditQueryError: If query execution fails
        """
        pass
    
    @abstractmethod
    async def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """
        Retrieve a specific audit event by ID.
        
        Args:
            event_id: Unique event identifier
            
        Returns:
            The audit event if found, None otherwise
            
        Raises:
            AuditStorageError: If storage operation fails
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check service health and return status information.
        
        Returns:
            Health status with service metadata
        """
        pass


class IAuditEventBuilder(ABC):
    """
    Builder interface for creating audit events with context.
    
    This interface provides a fluent API for building audit events
    with proper defaults and validation.
    """
    
    @abstractmethod
    def action(self, action: str) -> 'IAuditEventBuilder':
        """Set the action performed."""
        pass
    
    @abstractmethod
    def level(self, level: AuditLevel) -> 'IAuditEventBuilder':
        """Set the audit level."""
        pass
    
    @abstractmethod
    def category(self, category: AuditCategory) -> 'IAuditEventBuilder':
        """Set the audit category."""
        pass
    
    @abstractmethod
    def user(self, user_id: str) -> 'IAuditEventBuilder':
        """Set the user context."""
        pass
    
    @abstractmethod
    def session(self, session_id: str) -> 'IAuditEventBuilder':
        """Set the session context."""
        pass
    
    @abstractmethod
    def request(self, request_id: str) -> 'IAuditEventBuilder':
        """Set the request context."""
        pass
    
    @abstractmethod
    def resource(self, resource_type: str, resource_id: str) -> 'IAuditEventBuilder':
        """Set the resource context."""
        pass
    
    @abstractmethod
    def message(self, message: str) -> 'IAuditEventBuilder':
        """Set the event message."""
        pass
    
    @abstractmethod
    def metadata(self, **kwargs: Any) -> 'IAuditEventBuilder':
        """Add metadata to the event."""
        pass
    
    @abstractmethod
    def error(self, error_code: str, error_message: str, stack_trace: Optional[str] = None) -> 'IAuditEventBuilder':
        """Set error information."""
        pass
    
    @abstractmethod
    def duration(self, duration_ms: float) -> 'IAuditEventBuilder':
        """Set performance duration."""
        pass
    
    @abstractmethod
    def build(self) -> AuditEvent:
        """Build the final audit event."""
        pass


# Convenience functions for common audit events
def create_user_action_event(
    action: str,
    user_id: str,
    message: str,
    service_name: str,
    **metadata: Any
) -> AuditEvent:
    """Create a user action audit event."""
    return AuditEvent(
        action=action,
        category=AuditCategory.USER_ACTION,
        level=AuditLevel.INFO,
        user_id=user_id,
        message=message,
        service_name=service_name,
        metadata=metadata
    )


def create_api_request_event(
    action: str,
    request_id: str,
    duration_ms: float,
    service_name: str,
    user_id: Optional[str] = None,
    **metadata: Any
) -> AuditEvent:
    """Create an API request audit event."""
    return AuditEvent(
        action=action,
        category=AuditCategory.API_REQUEST,
        level=AuditLevel.INFO,
        user_id=user_id,
        request_id=request_id,
        duration_ms=duration_ms,
        service_name=service_name,
        message=f"API {action} completed in {duration_ms}ms",
        metadata=metadata
    )


def create_error_event(
    action: str,
    error_message: str,
    service_name: str,
    error_code: Optional[str] = None,
    stack_trace: Optional[str] = None,
    user_id: Optional[str] = None,
    **metadata: Any
) -> AuditEvent:
    """Create an error audit event."""
    return AuditEvent(
        action=action,
        category=AuditCategory.ERROR_EVENT,
        level=AuditLevel.ERROR,
        user_id=user_id,
        service_name=service_name,
        message=error_message,
        error_code=error_code,
        error_message=error_message,
        stack_trace=stack_trace,
        metadata=metadata
    )


def create_data_access_event(
    action: str,
    resource_type: str,
    resource_id: str,
    user_id: str,
    service_name: str,
    **metadata: Any
) -> AuditEvent:
    """Create a data access audit event."""
    return AuditEvent(
        action=action,
        category=AuditCategory.DATA_ACCESS,
        level=AuditLevel.INFO,
        user_id=user_id,
        resource_type=resource_type,
        resource_id=resource_id,
        service_name=service_name,
        message=f"User {user_id} performed {action} on {resource_type}:{resource_id}",
        metadata=metadata
    )