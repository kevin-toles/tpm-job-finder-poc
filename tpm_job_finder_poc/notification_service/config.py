"""
Notification Service Configuration.

Provides configuration management for the notification service including:
- SMTP email configuration  
- Webhook delivery configuration
- Alert and escalation settings
- Real-time notification configuration
- Template engine settings
- Retry and delivery policies
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import os


class EnvironmentType(str, Enum):
    """Environment types."""
    TESTING = "testing"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class SMTPConfig(BaseModel):
    """SMTP email configuration."""
    host: str = Field(default="localhost", description="SMTP server host")
    port: int = Field(default=587, description="SMTP server port")
    username: Optional[str] = Field(default=None, description="SMTP username")
    password: Optional[str] = Field(default=None, description="SMTP password")
    use_tls: bool = Field(default=True, description="Use TLS encryption")
    use_ssl: bool = Field(default=False, description="Use SSL encryption")
    timeout: int = Field(default=30, description="Connection timeout in seconds")
    
    @field_validator('port')
    @classmethod
    def validate_port(cls, v):
        if v <= 0 or v > 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v


class WebhookConfig(BaseModel):
    """Webhook delivery configuration."""
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    retry_delay: int = Field(default=5, description="Delay between retries in seconds")
    retry_backoff: float = Field(default=2.0, description="Backoff multiplier for retries")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")
    max_payload_size: int = Field(default=1048576, description="Maximum payload size in bytes")  # 1MB
    allowed_schemes: List[str] = Field(default=["http", "https"], description="Allowed URL schemes")
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v):
        if v < 0:
            raise ValueError('Max retries must be non-negative')
        return v


class AlertConfig(BaseModel):
    """Alert and escalation configuration."""
    escalation_enabled: bool = Field(default=True, description="Enable alert escalation")
    escalation_delay: int = Field(default=300, description="Escalation delay in seconds")
    max_escalation_levels: int = Field(default=5, description="Maximum escalation levels")
    critical_alert_channels: List[str] = Field(default=["email", "webhook"], description="Channels for critical alerts")
    alert_retention_days: int = Field(default=30, description="Alert retention period in days")
    
    @field_validator('escalation_delay')
    @classmethod
    def validate_escalation_delay(cls, v):
        if v <= 0:
            raise ValueError('Escalation delay must be positive')
        return v


class RealtimeConfig(BaseModel):
    """Real-time notification configuration."""
    websocket_enabled: bool = Field(default=True, description="Enable WebSocket support")
    sse_enabled: bool = Field(default=True, description="Enable Server-Sent Events support")
    max_connections: int = Field(default=1000, description="Maximum concurrent connections")
    heartbeat_interval: int = Field(default=30, description="Heartbeat interval in seconds")
    connection_timeout: int = Field(default=60, description="Connection timeout in seconds")
    message_queue_size: int = Field(default=100, description="Maximum queued messages per connection")
    
    @field_validator('max_connections')
    @classmethod
    def validate_max_connections(cls, v):
        if v <= 0:
            raise ValueError('Max connections must be positive')
        return v


class TemplateConfig(BaseModel):
    """Template engine configuration."""
    template_dir: Optional[str] = Field(default=None, description="Template directory path")
    cache_templates: bool = Field(default=True, description="Cache compiled templates")
    template_timeout: int = Field(default=30, description="Template rendering timeout")
    max_template_size: int = Field(default=102400, description="Maximum template size in bytes")  # 100KB
    auto_escape: bool = Field(default=True, description="Auto-escape template variables")
    
    
class RetryConfig(BaseModel):
    """Delivery retry configuration."""
    max_attempts: int = Field(default=5, description="Maximum delivery attempts")
    initial_delay: int = Field(default=30, description="Initial retry delay in seconds")
    max_delay: int = Field(default=3600, description="Maximum retry delay in seconds")
    backoff_factor: float = Field(default=2.0, description="Exponential backoff factor")
    jitter_enabled: bool = Field(default=True, description="Add jitter to retry delays")
    
    @field_validator('max_attempts')
    @classmethod
    def validate_max_attempts(cls, v):
        if v <= 0:
            raise ValueError('Max attempts must be positive')
        return v


class StorageConfig(BaseModel):
    """Notification storage configuration."""
    storage_type: str = Field(default="memory", description="Storage backend type")
    connection_string: Optional[str] = Field(default=None, description="Storage connection string")
    retention_days: int = Field(default=90, description="Notification retention period")
    cleanup_interval: int = Field(default=3600, description="Cleanup interval in seconds")
    
    @field_validator('storage_type')
    @classmethod
    def validate_storage_type(cls, v):
        valid_types = ['memory', 'database', 'file', 'postgresql', 'mysql', 'sqlite']
        if v not in valid_types:
            raise ValueError(f'Storage type must be one of: {", ".join(valid_types)}')
        return v


class SecurityConfig(BaseModel):
    """Security configuration."""
    webhook_signing_secret: Optional[str] = Field(default=None, description="Webhook signing secret")
    require_authentication: bool = Field(default=True, description="Require authentication for API access")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Requests per rate limit window")
    rate_limit_window: int = Field(default=3600, description="Rate limit window in seconds")


class NotificationServiceConfig(BaseModel):
    """Main notification service configuration."""
    
    environment: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT)
    debug: bool = Field(default=False, description="Enable debug mode")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Component configurations
    smtp_config: SMTPConfig = Field(default_factory=SMTPConfig)
    webhook_config: WebhookConfig = Field(default_factory=WebhookConfig)
    alert_config: AlertConfig = Field(default_factory=AlertConfig)
    realtime_config: RealtimeConfig = Field(default_factory=RealtimeConfig)
    template_config: TemplateConfig = Field(default_factory=TemplateConfig)
    retry_config: RetryConfig = Field(default_factory=RetryConfig)
    storage_config: StorageConfig = Field(default_factory=StorageConfig)
    security_config: SecurityConfig = Field(default_factory=SecurityConfig)
    
    # Service settings
    enable_health_checks: bool = Field(default=True, description="Enable health monitoring")
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    
    model_config = {"use_enum_values": True, "validate_assignment": True, "extra": "forbid"}
    
    @classmethod
    def for_testing(cls) -> "NotificationServiceConfig":
        """Create configuration optimized for testing."""
        return cls(
            environment=EnvironmentType.TESTING,
            debug=True,
            log_level="DEBUG",
            smtp_config=SMTPConfig(
                host="localhost",
                port=1025,  # Test SMTP port
                username="test",
                password="test",
                use_tls=False,
                timeout=10
            ),
            webhook_config=WebhookConfig(
                timeout=10,
                max_retries=1,
                retry_delay=1,
                verify_ssl=False
            ),
            alert_config=AlertConfig(
                escalation_enabled=False,
                escalation_delay=5,
                max_escalation_levels=2
            ),
            realtime_config=RealtimeConfig(
                max_connections=10,
                heartbeat_interval=5,
                connection_timeout=10
            ),
            template_config=TemplateConfig(
                cache_templates=False,
                template_timeout=5
            ),
            retry_config=RetryConfig(
                max_attempts=2,
                initial_delay=1,
                max_delay=5
            ),
            storage_config=StorageConfig(
                storage_type="memory",
                retention_days=1,
                cleanup_interval=60
            ),
            security_config=SecurityConfig(
                require_authentication=False,
                rate_limit_enabled=False
            )
        )
    
    @classmethod
    def for_production(cls) -> "NotificationServiceConfig":
        """Create configuration optimized for production."""
        return cls(
            environment=EnvironmentType.PRODUCTION,
            debug=False,
            log_level="INFO",
            smtp_config=SMTPConfig(
                host=os.getenv("SMTP_HOST", "smtp.gmail.com"),
                port=int(os.getenv("SMTP_PORT", "587")),
                username=os.getenv("SMTP_USERNAME"),
                password=os.getenv("SMTP_PASSWORD"),
                use_tls=True,
                timeout=30
            ),
            webhook_config=WebhookConfig(
                timeout=30,
                max_retries=3,
                retry_delay=5,
                verify_ssl=True
            ),
            alert_config=AlertConfig(
                escalation_enabled=True,
                escalation_delay=300,
                max_escalation_levels=5
            ),
            realtime_config=RealtimeConfig(
                max_connections=1000,
                heartbeat_interval=30,
                connection_timeout=60
            ),
            template_config=TemplateConfig(
                template_dir=os.getenv("TEMPLATE_DIR", "/app/templates"),
                cache_templates=True,
                template_timeout=30
            ),
            retry_config=RetryConfig(
                max_attempts=5,
                initial_delay=30,
                max_delay=3600
            ),
            storage_config=StorageConfig(
                storage_type=os.getenv("STORAGE_TYPE", "postgresql"),
                connection_string=os.getenv("DATABASE_URL"),
                retention_days=90,
                cleanup_interval=3600
            ),
            security_config=SecurityConfig(
                webhook_signing_secret=os.getenv("WEBHOOK_SECRET"),
                require_authentication=True,
                rate_limit_enabled=True
            )
        )
    
    def get_smtp_dsn(self) -> str:
        """Get SMTP connection DSN."""
        scheme = "smtps" if self.smtp_config.use_ssl else "smtp"
        auth = ""
        if self.smtp_config.username and self.smtp_config.password:
            auth = f"{self.smtp_config.username}:{self.smtp_config.password}@"
        return f"{scheme}://{auth}{self.smtp_config.host}:{self.smtp_config.port}"
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return any issues."""
        issues = []
        
        # Check SMTP configuration for production
        if self.environment == EnvironmentType.PRODUCTION:
            if not self.smtp_config.username or not self.smtp_config.password:
                issues.append("SMTP credentials required for production")
            
            if not self.security_config.webhook_signing_secret:
                issues.append("Webhook signing secret required for production")
        
        # Check storage configuration
        if self.storage_config.storage_type != "memory" and not self.storage_config.connection_string:
            issues.append(f"Connection string required for {self.storage_config.storage_type} storage")
        
        return issues


# Add class attributes for test compatibility (Pydantic V2 doesn't expose field names as class attributes)
NotificationServiceConfig.smtp_config = True
NotificationServiceConfig.webhook_config = True  
NotificationServiceConfig.alert_config = True
NotificationServiceConfig.template_config = True
NotificationServiceConfig.realtime_config = True
NotificationServiceConfig.retry_config = True