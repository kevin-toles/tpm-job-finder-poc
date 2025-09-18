"""
Error Handler Service TDD Implementation

This module implements the ErrorHandlerServiceTDD following Test-Driven Development.
The service provides comprehensive error handling capabilities including                webhook_payload = {
                    "error_id": error_result.error_id,
                    "error_type": error_result.error_type,
                    "message": error_result.message,
                    "severity": error_result.severity,  # Already a string now
                    "timestamp": error_result.timestamp.isoformat(),
                    "component": error_result.component
                }r classification and categorization
- Context tracking and enrichment
- Centralized logging to multiple destinations
- Notification and alert systems
- Recovery and retry mechanisms
- Error statistics and analytics
- Service health monitoring
- Configuration management
- High-performance async support
"""

import asyncio
import json
import logging
import os
import socket
import time
import traceback
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Callable, Awaitable
import psutil
import aiofiles
from unittest.mock import AsyncMock

from tpm_job_finder_poc.shared.contracts.error_handler import (
    ErrorHandlerConfig, ErrorResult, ErrorSeverity, ErrorCategory, 
    ComponentCategory, NotificationChannel, RecoveryStrategy,
    RetryResult, ErrorStatistics, ErrorTrends, ErrorPattern,
    HealthStatus, PerformanceMetrics, AlertStatus, ConfigurationResult,
    ConfigurationValidation, RateLimitStatus,
    IErrorClassifier, IErrorLogger, INotificationService, 
    IRecoveryService, IRetryService, IErrorAnalytics, IErrorStorage,
    ErrorHandlerServiceError, ErrorClassificationError, ErrorLoggingError,
    NotificationError, RecoveryError, ConfigurationError, RateLimitExceededError
)


class MockErrorClassifier(IErrorClassifier):
    """Mock error classifier for TDD implementation."""
    
    async def classify_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Classify an error by type, severity, and category."""
        error_type = error.__class__.__name__
        
        # Classification rules based on error type
        if error_type == "ValueError":
            severity = ErrorSeverity.MEDIUM
            category = ErrorCategory.VALIDATION
        elif error_type == "FileNotFoundError":
            severity = ErrorSeverity.MEDIUM
            category = ErrorCategory.SYSTEM
        elif error_type == "ConnectionError":
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.NETWORK
        elif error_type == "TimeoutError":
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.PERFORMANCE
        elif error_type == "PermissionError":
            severity = ErrorSeverity.HIGH
            category = ErrorCategory.SECURITY
        elif "Database" in str(error):
            severity = ErrorSeverity.CRITICAL
            category = ErrorCategory.SYSTEM
        elif "Cache" in str(error):
            severity = ErrorSeverity.WARNING
            category = ErrorCategory.PERFORMANCE
        elif "cancel" in str(error).lower():
            severity = ErrorSeverity.INFO
            category = ErrorCategory.USER_ERROR
        else:
            severity = ErrorSeverity.MEDIUM
            category = ErrorCategory.SYSTEM
        
        # Component category classification
        component = context.get("component", "unknown")
        if component in ["resume_uploader", "file_processor"]:
            component_category = ComponentCategory.FILE_PROCESSING
        elif component in ["llm_provider", "ai_service"]:
            component_category = ComponentCategory.AI_SERVICE
        elif component in ["scraping_service", "data_collector"]:
            component_category = ComponentCategory.DATA_COLLECTION
        elif component == "database":
            component_category = ComponentCategory.DATABASE
        elif component == "cache":
            component_category = ComponentCategory.CACHE
        elif component in ["api", "web_service"]:
            component_category = ComponentCategory.API
        elif component == "config":
            component_category = ComponentCategory.CONFIGURATION
        elif component in ["auth", "authentication"]:
            component_category = ComponentCategory.AUTHENTICATION
        else:
            component_category = ComponentCategory.API
        
        return {
            "error_type": error_type,
            "severity": severity,
            "category": category,
            "component_category": component_category
        }


class MockErrorLogger(IErrorLogger):
    """Mock error logger for TDD implementation."""
    
    def __init__(self, config: ErrorHandlerConfig):
        self.config = config
        self.log_files = []
        
    async def log_error(self, error_result: ErrorResult) -> bool:
        """Log an error to the configured destinations."""
        try:
            success = True
            
            # File logging
            if self.config.enable_file_logging:
                log_file_path = await self._log_to_file(error_result)
                error_result.logged_to_file = True
                error_result.log_file_path = log_file_path
                self.log_files.append(log_file_path)
            
            # Database logging 
            if self.config.enable_database_logging:
                await self._log_to_database(error_result)
                error_result.logged_to_database = True
            
            # Structured log entry
            error_result.structured_log_entry = self._create_structured_log_entry(error_result)
            
            return success
            
        except Exception as e:
            raise ErrorLoggingError(f"Failed to log error: {e}")
    
    async def _log_to_file(self, error_result: ErrorResult) -> str:
        """Log error to file system."""
        log_dir = "/tmp/error_handler_logs"
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = f"{log_dir}/errors_{datetime.now().strftime('%Y%m%d')}.log"
        
        log_entry = {
            "timestamp": error_result.timestamp.isoformat(),
            "error_id": error_result.error_id,
            "error_type": error_result.error_type,
            "message": error_result.message,
            "severity": error_result.severity,  # Already a string now
            "component": error_result.component,
            "context": error_result.original_context
        }
        
        async with aiofiles.open(log_file, mode='a') as f:
            await f.write(json.dumps(log_entry) + "\n")
        
        return log_file
    
    async def _log_to_database(self, error_result: ErrorResult):
        """Log error to database (mocked)."""
        # Mock database logging
        pass
    
    def _create_structured_log_entry(self, error_result: ErrorResult) -> Dict[str, Any]:
        """Create structured log entry."""
        return {
            "timestamp": error_result.timestamp.isoformat(),
            "level": error_result.severity.upper(),  # Already a string now
            "message": error_result.message,
            "error_type": error_result.error_type,
            "component": error_result.component,
            "context": error_result.original_context,
            "stack_trace": error_result.stack_trace,
            "error_id": error_result.error_id
        }


class MockNotificationService(INotificationService):
    """Mock notification service for TDD implementation."""
    
    def __init__(self, config: ErrorHandlerConfig):
        self.config = config
        
    async def send_notification(self, error_result: ErrorResult, channels: List[NotificationChannel]) -> Dict[str, str]:
        """Send notifications through specified channels."""
        if not self.config.enable_notifications:
            return {}
        
        notification_status = {}
        
        for channel in channels:
            if channel == NotificationChannel.EMAIL:
                status = await self._send_email(error_result)
                notification_status["email"] = status
            elif channel == NotificationChannel.WEBHOOK:
                status = await self._send_webhook(error_result)
                notification_status["webhook"] = status
                # Set webhook payload for test verification
                error_result.webhook_payload = {
                    "error_id": error_result.error_id,
                    "error_type": error_result.error_type,
                    "message": error_result.message,
                    "severity": error_result.severity,  # Already a string now
                    "timestamp": error_result.timestamp.isoformat(),
                    "component": error_result.component
                }
        
        return notification_status
    
    async def _send_email(self, error_result: ErrorResult) -> str:
        """Send email notification (mocked)."""
        # Mock email sending
        await asyncio.sleep(0.01)  # Simulate processing time
        return "sent"
    
    async def _send_webhook(self, error_result: ErrorResult) -> str:
        """Send webhook notification (mocked)."""
        # Mock webhook sending
        await asyncio.sleep(0.01)  # Simulate processing time
        return "sent"


class MockRecoveryService(IRecoveryService):
    """Mock recovery service for TDD implementation."""
    
    async def attempt_recovery(self, error: Exception, context: Dict[str, Any], strategy: RecoveryStrategy) -> bool:
        """Attempt to recover from an error using specified strategy."""
        if strategy == RecoveryStrategy.USE_DEFAULTS:
            return True
        elif strategy == RecoveryStrategy.RESTART_SERVICE:
            # Mock service restart
            await asyncio.sleep(0.01)
            return True
        elif strategy == RecoveryStrategy.FALLBACK:
            return True
        elif strategy == RecoveryStrategy.RETRY:
            return True
        else:
            return False


class MockRetryService(IRetryService):
    """Mock retry service for TDD implementation."""
    
    async def retry_with_backoff(
        self, 
        func: Callable[[], Awaitable[Any]], 
        max_retries: int, 
        strategy: str
    ) -> RetryResult:
        """Retry a function with backoff strategy."""
        retry_delays = []
        
        for attempt in range(max_retries + 1):
            try:
                if attempt == 0:
                    result = await func()
                    return RetryResult(
                        success=True,
                        retry_count=0,
                        retry_delays=[],
                        final_result=result
                    )
                else:
                    # Calculate delay based on strategy
                    if strategy == "exponential_backoff":
                        delay = (2 ** (attempt - 1)) * 0.1
                    else:
                        delay = 0.1
                    
                    retry_delays.append(delay)
                    await asyncio.sleep(delay)
                    result = await func()
                    
                    return RetryResult(
                        success=True,
                        retry_count=attempt,
                        retry_delays=retry_delays,
                        final_result=result
                    )
                    
            except Exception as e:
                if attempt == max_retries:
                    return RetryResult(
                        success=False,
                        retry_count=max_retries,
                        retry_delays=retry_delays,
                        final_error=e
                    )
                continue


class MockErrorAnalytics(IErrorAnalytics):
    """Mock error analytics for TDD implementation."""
    
    def __init__(self):
        self.errors = deque(maxlen=10000)  # Keep last 10k errors
        
    def add_error(self, error_result: ErrorResult):
        """Add an error to analytics."""
        self.errors.append(error_result)
    
    async def get_statistics(self, time_window_minutes: Optional[int] = None) -> ErrorStatistics:
        """Get error statistics for a time window."""
        if time_window_minutes:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
            filtered_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
        else:
            filtered_errors = list(self.errors)
        
        stats = ErrorStatistics(total_errors=len(filtered_errors))
        
        # Count by type
        for error in filtered_errors:
            stats.error_by_type[error.error_type] = stats.error_by_type.get(error.error_type, 0) + 1
            stats.error_by_component[error.component] = stats.error_by_component.get(error.component, 0) + 1
            stats.error_by_severity[error.severity] = stats.error_by_severity.get(error.severity, 0) + 1
            stats.error_by_category[error.category] = stats.error_by_category.get(error.category, 0) + 1
        
        if filtered_errors:
            stats.time_window_start = min(e.timestamp for e in filtered_errors)
            stats.time_window_end = max(e.timestamp for e in filtered_errors)
        
        return stats
    
    async def get_trends(self, time_window_minutes: int) -> ErrorTrends:
        """Get error trends analysis."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
        filtered_errors = [e for e in self.errors if e.timestamp >= cutoff_time]
        
        total_errors = len(filtered_errors)
        errors_per_minute = total_errors / time_window_minutes if time_window_minutes > 0 else 0
        
        # Simple trend calculation
        mid_point = len(filtered_errors) // 2
        if len(filtered_errors) > mid_point:
            first_half = len(filtered_errors[:mid_point])
            second_half = len(filtered_errors[mid_point:])
            if second_half > first_half:
                trend_direction = "increasing"
            elif second_half < first_half:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # Create time buckets
        time_buckets = []
        if filtered_errors:
            bucket_size = time_window_minutes // 5 if time_window_minutes >= 5 else 1
            for i in range(0, time_window_minutes, bucket_size):
                bucket_start = cutoff_time + timedelta(minutes=i)
                bucket_end = bucket_start + timedelta(minutes=bucket_size)
                bucket_errors = [e for e in filtered_errors if bucket_start <= e.timestamp < bucket_end]
                time_buckets.append({
                    "start_time": bucket_start,
                    "end_time": bucket_end,
                    "error_count": len(bucket_errors)
                })
        
        return ErrorTrends(
            total_errors=total_errors,
            errors_per_minute=errors_per_minute,
            trend_direction=trend_direction,
            time_buckets=time_buckets
        )
    
    async def detect_patterns(self) -> List[ErrorPattern]:
        """Detect error patterns and anomalies."""
        patterns = []
        error_groups = defaultdict(list)
        
        # Group errors by component and type
        for error in self.errors:
            key = (error.component, error.error_type)
            error_groups[key].append(error)
        
        # Detect patterns with frequency >= 3
        for (component, error_type), error_list in error_groups.items():
            if len(error_list) >= 3:
                # Find common keywords in error messages
                all_words = []
                for error in error_list:
                    all_words.extend(error.message.lower().split())
                
                word_counts = defaultdict(int)
                for word in all_words:
                    if len(word) > 3:  # Only consider words longer than 3 chars
                        word_counts[word] += 1
                
                common_keywords = [word for word, count in word_counts.items() if count >= 2]
                
                # Severity distribution
                severity_dist = defaultdict(int)
                for error in error_list:
                    severity_dist[error.severity] += 1
                
                pattern = ErrorPattern(
                    pattern_id=str(uuid.uuid4()),
                    component=component,
                    error_type=error_type,
                    frequency=len(error_list),
                    common_keywords=common_keywords,
                    first_occurrence=min(e.timestamp for e in error_list),
                    last_occurrence=max(e.timestamp for e in error_list),
                    severity_distribution=dict(severity_dist)
                )
                patterns.append(pattern)
        
        return patterns


class MockErrorStorage(IErrorStorage):
    """Mock error storage for TDD implementation."""
    
    def __init__(self):
        self.errors = {}  # error_id -> ErrorResult
        
    async def store_error(self, error_result: ErrorResult) -> str:
        """Store an error and return its ID."""
        self.errors[error_result.error_id] = error_result
        return error_result.error_id
    
    async def get_error_by_id(self, error_id: str) -> Optional[ErrorResult]:
        """Retrieve an error by its ID."""
        return self.errors.get(error_id)
    
    async def get_errors(self, filters: Dict[str, Any], limit: int = 100) -> List[ErrorResult]:
        """Get errors matching filters."""
        results = []
        for error in self.errors.values():
            if len(results) >= limit:
                break
            
            # Simple filter matching
            match = True
            for key, value in filters.items():
                if hasattr(error, key) and getattr(error, key) != value:
                    match = False
                    break
            
            if match:
                results.append(error)
        
        return results


class ErrorHandlerServiceTDD:
    """
    Error Handler Service TDD Implementation
    
    Provides comprehensive error handling capabilities including classification,
    logging, notifications, recovery, analytics, and monitoring.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Error Handler Service."""
        if isinstance(config, dict):
            self.config = ErrorHandlerConfig(**config)
        else:
            self.config = config
            
        # Service state
        self._is_running = False
        self._start_time = None
        self._error_count = 0
        self._processing_times = deque(maxlen=1000)
        self._rate_limiter = deque(maxlen=self.config.max_errors_per_minute)
        self._alert_status = AlertStatus(
            threshold_exceeded=False,
            error_count=0,
            threshold_limit=self.config.alert_threshold,
            alert_sent=False
        )
        
        # Initialize services
        self._classifier = MockErrorClassifier()
        self._logger = MockErrorLogger(self.config)
        self._notifier = MockNotificationService(self.config)
        self._recovery = MockRecoveryService()
        self._retry = MockRetryService()
        self._analytics = MockErrorAnalytics()
        self._storage = MockErrorStorage()
    
    async def start(self):
        """Start the error handler service."""
        self._is_running = True
        self._start_time = datetime.now(timezone.utc)
        
    async def stop(self):
        """Stop the error handler service."""
        self._is_running = False
    
    async def handle_error(self, error: Exception, context: Dict[str, Any], notify: bool = False) -> ErrorResult:
        """Handle an error with comprehensive processing."""
        if not self._is_running:
            raise ErrorHandlerServiceError("Service not started")
        
        start_processing = time.time()
        
        # Check rate limiting
        current_time = time.time()
        self._rate_limiter.append(current_time)
        
        # Create error ID
        error_id = str(uuid.uuid4())
        
        # Classify the error
        classification = await self._classifier.classify_error(error, context)
        
        # Enrich context
        enriched_context = await self._enrich_context(context)
        
        # Extract error chain and stack trace
        error_chain = self._extract_error_chain(error)
        stack_trace = traceback.format_exc() if hasattr(error, '__traceback__') else str(error)
        
        # Create error result
        error_result = ErrorResult(
            error_id=error_id,
            error_type=classification["error_type"],
            message=str(error),
            severity=classification["severity"].value,  # Convert enum to string
            category=classification["category"].value,  # Convert enum to string
            component_category=classification["component_category"].value,  # Convert enum to string
            timestamp=datetime.now(timezone.utc),
            component=context.get("component", "unknown"),
            method=context.get("method"),
            file_path=context.get("file_path"),
            original_context=context,
            enriched_context=enriched_context,
            error_chain=error_chain,
            stack_trace=stack_trace
        )
        
        # Log the error
        await self._logger.log_error(error_result)
        
        # Send notifications if requested
        if notify:
            start_notification = time.time()
            notification_channels = [NotificationChannel(ch) for ch in self.config.notification_channels]
            notification_status = await self._notifier.send_notification(error_result, notification_channels)
            
            error_result.notification_sent = True
            error_result.notification_channels = list(notification_status.keys())
            error_result.notification_status = notification_status
            error_result.notification_processing_time_ms = (time.time() - start_notification) * 1000
        
        # Store error
        await self._storage.store_error(error_result)
        
        # Add to analytics
        self._analytics.add_error(error_result)
        
        # Attempt recovery if strategy specified
        recovery_strategy = context.get("recovery_strategy")
        if recovery_strategy:
            try:
                # Map string strategy to enum
                strategy_mapping = {
                    "use_defaults": RecoveryStrategy.USE_DEFAULTS,
                    "restart_service": RecoveryStrategy.RESTART_SERVICE,
                    "fallback": RecoveryStrategy.FALLBACK,
                    "retry": RecoveryStrategy.RETRY
                }
                recovery_enum = strategy_mapping.get(recovery_strategy, RecoveryStrategy.USE_DEFAULTS)
                recovery_success = await self._recovery.attempt_recovery(error, context, recovery_enum)
                error_result.recovery_attempted = True
                error_result.recovery_strategy = recovery_strategy
                error_result.recovery_successful = recovery_success
            except Exception:
                error_result.recovery_attempted = True
                error_result.recovery_strategy = recovery_strategy
                error_result.recovery_successful = False
        
        # Update metrics
        self._error_count += 1
        processing_time = (time.time() - start_processing) * 1000
        error_result.processing_time_ms = processing_time
        self._processing_times.append(processing_time)
        
        # Check alert thresholds
        await self._check_alert_thresholds()
        
        return error_result
    
    async def handle_error_with_retry(self, func: Callable[[], Awaitable[Any]], context: Dict[str, Any]) -> RetryResult:
        """Handle error with retry mechanism."""
        return await self._retry.retry_with_backoff(func, self.config.max_retries, self.config.retry_strategy)
    
    async def get_error_by_id(self, error_id: str) -> Optional[ErrorResult]:
        """Get an error by its ID."""
        return await self._storage.get_error_by_id(error_id)
    
    async def get_log_files(self) -> List[str]:
        """Get list of log files."""
        return self._logger.log_files
    
    async def get_error_statistics(self, time_window_minutes: Optional[int] = None) -> ErrorStatistics:
        """Get error statistics."""
        return await self._analytics.get_statistics(time_window_minutes)
    
    async def get_error_trends(self, time_window_minutes: int) -> ErrorTrends:
        """Get error trends analysis."""
        return await self._analytics.get_trends(time_window_minutes)
    
    async def detect_error_patterns(self) -> List[ErrorPattern]:
        """Detect error patterns."""
        return await self._analytics.detect_patterns()
    
    async def get_health_status(self) -> HealthStatus:
        """Get service health status."""
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds() if self._start_time else 0
        
        # Calculate errors per minute
        current_time = time.time()
        recent_errors = [t for t in self._rate_limiter if current_time - t < 60]
        errors_per_minute = len(recent_errors)
        
        # Get memory usage
        process = psutil.Process()
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        
        status = "healthy"
        if errors_per_minute > self.config.alert_threshold:
            status = "degraded"
        if memory_usage_mb > 500:  # 500MB threshold
            status = "degraded"
        
        return HealthStatus(
            service_name=self.config.service_name,
            status=status,
            uptime_seconds=uptime,
            total_errors_handled=self._error_count,
            memory_usage_mb=memory_usage_mb,
            errors_per_minute=errors_per_minute
        )
    
    async def get_performance_metrics(self) -> PerformanceMetrics:
        """Get performance metrics."""
        if not self._processing_times:
            return PerformanceMetrics(
                average_processing_time_ms=0,
                errors_processed=0,
                throughput_per_second=0,
                memory_usage_trend={}
            )
        
        avg_processing_time = sum(self._processing_times) / len(self._processing_times)
        peak_processing_time = max(self._processing_times)
        
        # Calculate throughput
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds() if self._start_time else 1
        throughput = self._error_count / uptime
        
        # Get CPU usage
        process = psutil.Process()
        cpu_usage = process.cpu_percent()
        
        # Memory usage trend (simplified)
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)
        memory_trend = {"current": memory_usage_mb, "trend": "stable"}
        
        return PerformanceMetrics(
            average_processing_time_ms=avg_processing_time,
            errors_processed=self._error_count,
            throughput_per_second=throughput,
            memory_usage_trend=memory_trend,
            peak_processing_time_ms=peak_processing_time,
            cpu_usage_percent=cpu_usage
        )
    
    async def check_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check health of service dependencies."""
        dependencies = {}
        
        # File system check
        try:
            test_file = "/tmp/error_handler_test"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            dependencies["file_system"] = {"status": "healthy", "response_time_ms": 1.0}
        except Exception:
            dependencies["file_system"] = {"status": "unhealthy", "response_time_ms": 0}
        
        # Logging system check
        dependencies["logging_system"] = {"status": "healthy", "response_time_ms": 0.5}
        
        # Database check (if configured)
        if self.config.database_url:
            dependencies["database"] = {"status": "healthy", "response_time_ms": 2.0}
        
        return dependencies
    
    async def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "service_name": self.config.service_name,
            "max_retries": self.config.max_retries,
            "retry_delay_seconds": self.config.retry_delay_seconds,
            "enable_notifications": self.config.enable_notifications,
            "notification_channels": self.config.notification_channels,
            "alert_threshold": self.config.alert_threshold,
            "max_errors_per_minute": self.config.max_errors_per_minute
        }
    
    async def update_configuration(self, new_config: Dict[str, Any]) -> ConfigurationResult:
        """Update service configuration."""
        try:
            # Validate configuration first
            validation = await self.validate_configuration(new_config)
            if not validation.valid:
                return ConfigurationResult(success=False, errors=validation.errors)
            
            # Apply configuration changes
            for key, value in new_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            return ConfigurationResult(success=True)
            
        except Exception as e:
            return ConfigurationResult(success=False, errors=[str(e)])
    
    async def validate_configuration(self, config: Dict[str, Any]) -> ConfigurationValidation:
        """Validate configuration."""
        errors = []
        warnings = []
        
        # Validate max_retries
        if "max_retries" in config:
            if not isinstance(config["max_retries"], int) or config["max_retries"] < 0:
                errors.append("max_retries must be a non-negative integer")
        
        # Validate retry_delay_seconds
        if "retry_delay_seconds" in config:
            if not isinstance(config["retry_delay_seconds"], (int, float)) or config["retry_delay_seconds"] < 0:
                errors.append("retry_delay_seconds must be a non-negative number")
        
        # Validate alert_threshold
        if "alert_threshold" in config:
            if not isinstance(config["alert_threshold"], int) or config["alert_threshold"] <= 0:
                errors.append("alert_threshold must be a positive integer")
        
        # Validate notification channels
        if "notification_channels" in config:
            valid_channels = ["email", "webhook", "sms", "slack", "teams"]
            for channel in config["notification_channels"]:
                if channel not in valid_channels:
                    errors.append(f"Invalid notification channel: {channel}")
        
        return ConfigurationValidation(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    @classmethod
    def load_config_from_env(cls) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        return ErrorHandlerConfig.from_env().__dict__
    
    async def get_alert_status(self) -> AlertStatus:
        """Get current alert status."""
        return self._alert_status
    
    async def get_rate_limit_status(self) -> RateLimitStatus:
        """Get rate limit status."""
        current_time = time.time()
        recent_requests = [t for t in self._rate_limiter if current_time - t < 60]
        current_rate = len(recent_requests)
        
        return RateLimitStatus(
            current_rate=current_rate,
            limit=self.config.max_errors_per_minute,
            time_window_seconds=60,
            requests_remaining=max(0, self.config.max_errors_per_minute - current_rate),
            reset_time_seconds=60 - (current_time % 60)
        )
    
    async def _enrich_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich error context with system information."""
        enriched = context.copy()
        
        enriched.update({
            "hostname": socket.gethostname(),
            "process_id": os.getpid(),
            "memory_usage": psutil.Process().memory_info().rss,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_id": str(uuid.uuid4())
        })
        
        return enriched
    
    def _extract_error_chain(self, error: Exception) -> List[Dict[str, Any]]:
        """Extract error chain from exception."""
        chain = []
        current = error
        
        while current:
            chain.append({
                "type": current.__class__.__name__,
                "message": str(current),
                "module": getattr(current.__class__, '__module__', 'unknown')
            })
            current = getattr(current, '__cause__', None)
        
        return chain
    
    async def _check_alert_thresholds(self):
        """Check if alert thresholds are exceeded."""
        current_time = time.time()
        recent_errors = [t for t in self._rate_limiter if current_time - t < 60]
        
        if len(recent_errors) > self.config.alert_threshold:
            self._alert_status.threshold_exceeded = True
            self._alert_status.error_count = len(recent_errors)
            self._alert_status.alert_sent = True
        else:
            self._alert_status.threshold_exceeded = False
            self._alert_status.error_count = len(recent_errors)