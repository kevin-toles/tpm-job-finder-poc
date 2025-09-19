"""
Health Monitoring Service Configuration

Configuration models and settings for the health monitoring microservice.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import timedelta


@dataclass
class HealthMonitoringConfig:
    """Configuration for the Health Monitoring Service."""
    
    # Core monitoring settings
    check_interval_seconds: int = 30
    concurrent_checks: int = 10
    default_timeout_ms: int = 5000
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    
    # Alert thresholds (default values)
    alert_threshold_error_rate: float = 0.05  # 5% error rate
    alert_threshold_response_time_ms: int = 5000  # 5 seconds
    alert_threshold_cpu_percent: float = 80.0  # 80% CPU usage
    alert_threshold_memory_percent: float = 85.0  # 85% memory usage
    alert_threshold_disk_percent: float = 90.0  # 90% disk usage
    
    # Data retention
    retention_days: int = 7
    max_historical_records: int = 10000
    cleanup_interval_hours: int = 24
    
    # Features
    enable_metrics_collection: bool = True
    enable_alerting: bool = True
    enable_detailed_logging: bool = False
    enable_external_notifications: bool = False
    
    # Services to monitor by default
    services_to_monitor: List[str] = field(default_factory=lambda: [
        "audit_service",
        "job_collection_service",
        "ai_intelligence_service", 
        "web_scraping_service",
        "data_pipeline_service",
        "llm_gateway_service",
        "config_service",
        "storage_service",
        "cache_service"
    ])
    
    # Dependencies to monitor
    dependencies_to_monitor: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "database": {
            "type": "postgresql",
            "check_interval": 300,
            "timeout_ms": 2000
        },
        "redis_cache": {
            "type": "redis", 
            "check_interval": 180,
            "timeout_ms": 1000
        },
        "file_system": {
            "type": "filesystem",
            "check_interval": 600,
            "paths": ["/tmp", "/var/log", "/app/storage"]
        }
    })
    
    # External notification settings
    notification_webhook_url: Optional[str] = None
    notification_email_recipients: List[str] = field(default_factory=list)
    notification_slack_webhook: Optional[str] = None
    
    # Security settings
    health_endpoint_auth_required: bool = False
    api_key_header: str = "X-API-Key"
    trusted_service_ips: List[str] = field(default_factory=list)
    
    # Performance settings
    metrics_collection_interval: int = 60  # seconds
    batch_size_metrics: int = 100
    connection_pool_size: int = 20
    max_concurrent_health_checks: int = 50
    
    # Advanced features
    enable_predictive_alerting: bool = False
    machine_learning_models_enabled: bool = False
    anomaly_detection_enabled: bool = False
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.check_interval_seconds < 10:
            raise ValueError("Check interval must be at least 10 seconds")
        
        if self.retention_days < 1:
            raise ValueError("Retention days must be at least 1")
        
        if self.concurrent_checks < 1:
            raise ValueError("Concurrent checks must be at least 1")
        
        if not 0 < self.alert_threshold_error_rate <= 1:
            raise ValueError("Error rate threshold must be between 0 and 1")
        
        if self.alert_threshold_response_time_ms < 100:
            raise ValueError("Response time threshold must be at least 100ms")


@dataclass
class ServiceMonitoringConfig:
    """Configuration for monitoring a specific service."""
    
    name: str
    health_endpoint: str
    check_interval: int = 60  # seconds
    timeout_ms: int = 5000
    expected_status_codes: List[int] = field(default_factory=lambda: [200])
    headers: Dict[str, str] = field(default_factory=dict)
    
    # Alert thresholds specific to this service
    custom_error_rate_threshold: Optional[float] = None
    custom_response_time_threshold: Optional[int] = None
    
    # Service-specific settings
    critical_service: bool = False  # Higher priority alerts
    maintenance_windows: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    # Monitoring behavior
    fail_fast_on_error: bool = False
    retry_on_failure: bool = True
    escalate_after_failures: int = 3
    
    def __post_init__(self):
        """Validate service configuration."""
        if not self.name:
            raise ValueError("Service name cannot be empty")
        
        if not self.health_endpoint:
            raise ValueError("Health endpoint cannot be empty")
        
        if self.check_interval < 10:
            raise ValueError("Check interval must be at least 10 seconds")


@dataclass 
class DependencyMonitoringConfig:
    """Configuration for monitoring external dependencies."""
    
    name: str
    type: str  # database, redis, filesystem, http_service, etc.
    connection_string: Optional[str] = None
    timeout_ms: int = 2000
    check_interval: int = 300  # seconds
    
    # Type-specific configuration
    database_config: Optional[Dict[str, Any]] = None
    redis_config: Optional[Dict[str, Any]] = None
    filesystem_config: Optional[Dict[str, Any]] = None
    http_config: Optional[Dict[str, Any]] = None
    
    # Monitoring settings
    critical_dependency: bool = True
    alert_on_failure: bool = True
    max_consecutive_failures: int = 3
    
    def __post_init__(self):
        """Validate dependency configuration."""
        if not self.name:
            raise ValueError("Dependency name cannot be empty")
        
        if not self.type:
            raise ValueError("Dependency type cannot be empty")
        
        valid_types = ["database", "redis", "filesystem", "http_service", "message_queue"]
        if self.type not in valid_types:
            raise ValueError(f"Dependency type must be one of: {valid_types}")


@dataclass
class AlertingConfig:
    """Configuration for alerting and notifications."""
    
    # Alert channels
    enable_email_alerts: bool = False
    enable_slack_alerts: bool = False  
    enable_webhook_alerts: bool = False
    enable_sms_alerts: bool = False
    
    # Email settings
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[str] = None
    email_recipients: List[str] = field(default_factory=list)
    
    # Slack settings
    slack_webhook_url: Optional[str] = None
    slack_channel: str = "#alerts"
    slack_username: str = "health-monitor"
    
    # Webhook settings
    webhook_url: Optional[str] = None
    webhook_headers: Dict[str, str] = field(default_factory=dict)
    webhook_timeout_ms: int = 5000
    
    # Alert behavior
    alert_cooldown_minutes: int = 15  # Prevent spam
    escalation_delay_minutes: int = 30
    max_alerts_per_hour: int = 10
    
    # Alert severities
    critical_services: List[str] = field(default_factory=list)
    warning_threshold_minutes: int = 5  # How long before escalating
    critical_threshold_minutes: int = 15  # How long before critical alert
    
    def __post_init__(self):
        """Validate alerting configuration."""
        if self.enable_email_alerts and not self.email_recipients:
            raise ValueError("Email recipients required when email alerts enabled")
        
        if self.enable_slack_alerts and not self.slack_webhook_url:
            raise ValueError("Slack webhook URL required when Slack alerts enabled")
        
        if self.enable_webhook_alerts and not self.webhook_url:
            raise ValueError("Webhook URL required when webhook alerts enabled")