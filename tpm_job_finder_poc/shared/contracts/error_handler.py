"""
Shared contracts and data models for Error Handler Service

This module defines the data models, interfaces, and contracts that the
ErrorHandlerServiceTDD must implement. These are derived from:
1. Current error_handler usage patterns in the codebase
2. TDD test requirements
3. Microservice architecture needs
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable
from enum import Enum
import uuid


class ErrorSeverity(Enum):
    """Error severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WARNING = "warning"
    INFO = "info"


class ErrorCategory(Enum):
    """Error categories for classification."""
    VALIDATION = "validation"
    SYSTEM = "system"
    NETWORK = "network"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    USER_ERROR = "user_error"


class ComponentCategory(Enum):
    """Component categories for error context."""
    FILE_PROCESSING = "file_processing"
    AI_SERVICE = "ai_service"
    DATA_COLLECTION = "data_collection"
    DATABASE = "database"
    CACHE = "cache"
    API = "api"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"


class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    SMS = "sms"
    SLACK = "slack"
    TEAMS = "teams"


class RecoveryStrategy(Enum):
    """Error recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    USE_DEFAULTS = "use_defaults"
    RESTART_SERVICE = "restart_service"
    IGNORE = "ignore"
    ESCALATE = "escalate"


@dataclass
class ErrorResult:
    """Result object returned by error handling operations."""
    # Core error information
    error_id: str
    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    component_category: ComponentCategory
    timestamp: datetime
    
    # Context information
    component: str
    method: Optional[str] = None
    file_path: Optional[str] = None
    original_context: Dict[str, Any] = field(default_factory=dict)
    enriched_context: Dict[str, Any] = field(default_factory=dict)
    
    # Error chain and stack trace
    error_chain: List[Dict[str, Any]] = field(default_factory=list)
    stack_trace: Optional[str] = None
    
    # Logging information
    logged_to_file: bool = False
    logged_to_database: bool = False
    log_file_path: Optional[str] = None
    structured_log_entry: Dict[str, Any] = field(default_factory=dict)
    
    # Notification information
    notification_sent: bool = False
    notification_channels: List[str] = field(default_factory=list)
    notification_status: Dict[str, str] = field(default_factory=dict)
    notification_processing_time_ms: float = 0.0
    webhook_payload: Optional[Dict[str, Any]] = None
    
    # Recovery information
    recovery_attempted: bool = False
    recovery_strategy: Optional[RecoveryStrategy] = None
    recovery_successful: bool = False
    
    # Processing metrics
    processing_time_ms: float = 0.0


@dataclass
class RetryResult:
    """Result of retry operations."""
    success: bool
    retry_count: int
    retry_delays: List[float] = field(default_factory=list)
    final_result: Any = None
    final_error: Optional[Exception] = None


@dataclass
class ErrorStatistics:
    """Error statistics and analytics."""
    total_errors: int
    error_by_type: Dict[str, int] = field(default_factory=dict)
    error_by_component: Dict[str, int] = field(default_factory=dict)
    error_by_severity: Dict[str, int] = field(default_factory=dict)
    error_by_category: Dict[str, int] = field(default_factory=dict)
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None


@dataclass
class ErrorTrends:
    """Error trend analysis."""
    total_errors: int
    errors_per_minute: float
    trend_direction: str  # "increasing", "stable", "decreasing"
    time_buckets: List[Dict[str, Any]] = field(default_factory=list)
    peak_error_time: Optional[datetime] = None
    lowest_error_time: Optional[datetime] = None


@dataclass
class ErrorPattern:
    """Detected error pattern."""
    pattern_id: str
    component: str
    error_type: str
    frequency: int
    common_keywords: List[str] = field(default_factory=list)
    first_occurrence: Optional[datetime] = None
    last_occurrence: Optional[datetime] = None
    severity_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class HealthStatus:
    """Service health status."""
    service_name: str
    status: str  # "healthy", "degraded", "unhealthy"
    uptime_seconds: float
    total_errors_handled: int
    memory_usage_mb: float
    errors_per_minute: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PerformanceMetrics:
    """Performance metrics for the service."""
    average_processing_time_ms: float
    errors_processed: int
    throughput_per_second: float
    memory_usage_trend: Dict[str, float] = field(default_factory=dict)
    peak_processing_time_ms: float = 0.0
    cpu_usage_percent: float = 0.0


@dataclass
class AlertStatus:
    """Alert threshold status."""
    threshold_exceeded: bool
    error_count: int
    threshold_limit: int
    alert_sent: bool
    time_window_minutes: int = 1


@dataclass
class ConfigurationResult:
    """Result of configuration operations."""
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ConfigurationValidation:
    """Configuration validation result."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class RateLimitStatus:
    """Rate limiting status."""
    current_rate: float
    limit: float
    time_window_seconds: int
    requests_remaining: int
    reset_time_seconds: float


@dataclass
class ErrorHandlerConfig:
    """Configuration for Error Handler Service."""
    service_name: str = "error_handler_tdd"
    log_level: str = "INFO"
    
    # Logging configuration
    enable_file_logging: bool = True
    enable_database_logging: bool = True
    log_file_path: Optional[str] = None
    log_retention_days: int = 30
    
    # Notification configuration
    enable_notifications: bool = True
    notification_channels: List[str] = field(default_factory=lambda: ["email"])
    webhook_url: Optional[str] = None
    admin_email: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    
    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    retry_strategy: str = "exponential_backoff"
    base_retry_delay: float = 0.1
    max_retry_delay: float = 60.0
    
    # Performance configuration
    max_errors_per_minute: int = 1000
    alert_threshold: int = 100
    enable_metrics: bool = True
    
    # Storage configuration
    error_retention_days: int = 30
    database_url: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "ErrorHandlerConfig":
        """Create configuration from environment variables."""
        import os
        
        config = cls()
        
        # String configurations
        if os.getenv("ERROR_HANDLER_SERVICE_NAME"):
            config.service_name = os.getenv("ERROR_HANDLER_SERVICE_NAME")
        if os.getenv("ERROR_HANDLER_LOG_LEVEL"):
            config.log_level = os.getenv("ERROR_HANDLER_LOG_LEVEL")
        if os.getenv("ERROR_HANDLER_WEBHOOK_URL"):
            config.webhook_url = os.getenv("ERROR_HANDLER_WEBHOOK_URL")
        if os.getenv("ERROR_HANDLER_ADMIN_EMAIL"):
            config.admin_email = os.getenv("ERROR_HANDLER_ADMIN_EMAIL")
        if os.getenv("ERROR_HANDLER_DATABASE_URL"):
            config.database_url = os.getenv("ERROR_HANDLER_DATABASE_URL")
        if os.getenv("ERROR_HANDLER_LOG_FILE_PATH"):
            config.log_file_path = os.getenv("ERROR_HANDLER_LOG_FILE_PATH")
        if os.getenv("ERROR_HANDLER_RETRY_STRATEGY"):
            config.retry_strategy = os.getenv("ERROR_HANDLER_RETRY_STRATEGY")
        
        # Boolean configurations
        if os.getenv("ERROR_HANDLER_ENABLE_FILE_LOGGING"):
            config.enable_file_logging = os.getenv("ERROR_HANDLER_ENABLE_FILE_LOGGING").lower() == "true"
        if os.getenv("ERROR_HANDLER_ENABLE_DATABASE_LOGGING"):
            config.enable_database_logging = os.getenv("ERROR_HANDLER_ENABLE_DATABASE_LOGGING").lower() == "true"
        if os.getenv("ERROR_HANDLER_ENABLE_NOTIFICATIONS"):
            config.enable_notifications = os.getenv("ERROR_HANDLER_ENABLE_NOTIFICATIONS").lower() == "true"
        if os.getenv("ERROR_HANDLER_ENABLE_METRICS"):
            config.enable_metrics = os.getenv("ERROR_HANDLER_ENABLE_METRICS").lower() == "true"
        
        # Integer configurations
        if os.getenv("ERROR_HANDLER_MAX_RETRIES"):
            config.max_retries = int(os.getenv("ERROR_HANDLER_MAX_RETRIES"))
        if os.getenv("ERROR_HANDLER_LOG_RETENTION_DAYS"):
            config.log_retention_days = int(os.getenv("ERROR_HANDLER_LOG_RETENTION_DAYS"))
        if os.getenv("ERROR_HANDLER_MAX_ERRORS_PER_MINUTE"):
            config.max_errors_per_minute = int(os.getenv("ERROR_HANDLER_MAX_ERRORS_PER_MINUTE"))
        if os.getenv("ERROR_HANDLER_ALERT_THRESHOLD"):
            config.alert_threshold = int(os.getenv("ERROR_HANDLER_ALERT_THRESHOLD"))
        if os.getenv("ERROR_HANDLER_ERROR_RETENTION_DAYS"):
            config.error_retention_days = int(os.getenv("ERROR_HANDLER_ERROR_RETENTION_DAYS"))
        
        # Float configurations
        if os.getenv("ERROR_HANDLER_RETRY_DELAY_SECONDS"):
            config.retry_delay_seconds = float(os.getenv("ERROR_HANDLER_RETRY_DELAY_SECONDS"))
        if os.getenv("ERROR_HANDLER_BASE_RETRY_DELAY"):
            config.base_retry_delay = float(os.getenv("ERROR_HANDLER_BASE_RETRY_DELAY"))
        if os.getenv("ERROR_HANDLER_MAX_RETRY_DELAY"):
            config.max_retry_delay = float(os.getenv("ERROR_HANDLER_MAX_RETRY_DELAY"))
        
        # List configurations
        if os.getenv("ERROR_HANDLER_NOTIFICATION_CHANNELS"):
            config.notification_channels = os.getenv("ERROR_HANDLER_NOTIFICATION_CHANNELS").split(",")
        
        return config


# Service interface definitions
class IErrorClassifier(ABC):
    """Interface for error classification."""
    
    @abstractmethod
    async def classify_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify an error by type, severity, and category."""
        pass


class IErrorLogger(ABC):
    """Interface for error logging."""
    
    @abstractmethod
    async def log_error(self, error_result: ErrorResult) -> bool:
        """Log an error to the configured destinations."""
        pass


class INotificationService(ABC):
    """Interface for notification services."""
    
    @abstractmethod
    async def send_notification(self, error_result: ErrorResult, channels: List[NotificationChannel]) -> Dict[str, str]:
        """Send notifications through specified channels."""
        pass


class IRecoveryService(ABC):
    """Interface for error recovery services."""
    
    @abstractmethod
    async def attempt_recovery(self, error: Exception, context: Dict[str, Any], strategy: RecoveryStrategy) -> bool:
        """Attempt to recover from an error using specified strategy."""
        pass


class IRetryService(ABC):
    """Interface for retry services."""
    
    @abstractmethod
    async def retry_with_backoff(
        self, 
        func: Callable[[], Awaitable[Any]], 
        max_retries: int, 
        strategy: str
    ) -> RetryResult:
        """Retry a function with backoff strategy."""
        pass


class IErrorAnalytics(ABC):
    """Interface for error analytics."""
    
    @abstractmethod
    async def get_statistics(self, time_window_minutes: Optional[int] = None) -> ErrorStatistics:
        """Get error statistics for a time window."""
        pass
    
    @abstractmethod
    async def get_trends(self, time_window_minutes: int) -> ErrorTrends:
        """Get error trends analysis."""
        pass
    
    @abstractmethod
    async def detect_patterns(self) -> List[ErrorPattern]:
        """Detect error patterns and anomalies."""
        pass


class IErrorStorage(ABC):
    """Interface for error storage."""
    
    @abstractmethod
    async def store_error(self, error_result: ErrorResult) -> str:
        """Store an error and return its ID."""
        pass
    
    @abstractmethod
    async def get_error_by_id(self, error_id: str) -> Optional[ErrorResult]:
        """Retrieve an error by its ID."""
        pass
    
    @abstractmethod
    async def get_errors(self, filters: Dict[str, Any], limit: int = 100) -> List[ErrorResult]:
        """Get errors matching filters."""
        pass


# Exception classes
class ErrorHandlerServiceError(Exception):
    """Base exception for Error Handler Service."""
    pass


class ErrorClassificationError(ErrorHandlerServiceError):
    """Error in error classification."""
    pass


class ErrorLoggingError(ErrorHandlerServiceError):
    """Error in error logging."""
    pass


class NotificationError(ErrorHandlerServiceError):
    """Error in notification sending."""
    pass


class RecoveryError(ErrorHandlerServiceError):
    """Error in error recovery."""
    pass


class ConfigurationError(ErrorHandlerServiceError):
    """Error in configuration."""
    pass


class RateLimitExceededError(ErrorHandlerServiceError):
    """Rate limit exceeded."""
    pass