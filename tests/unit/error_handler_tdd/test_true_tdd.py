"""
Comprehensive TDD Test Suite for Error Handler Service

This test suite follows true Test-Driven Development (TDD) methodology.
Tests are written first based on requirements derived from:
1. Current error_handler usage patterns across the codebase
2. Component integration requirements
3. Microservice architecture requirements
4. Business requirements for centralized error handling

These tests define the interface and behavior that ErrorHandlerServiceTDD must implement.
All tests should FAIL initially (RED phase) until implementation is created.

Test Categories:
1. Error Classification and Categorization
2. Context Tracking and Enrichment  
3. Centralized Logging System
4. Notification and Alert System
5. Recovery and Retry Mechanisms
6. Error Statistics and Analytics
7. Service Health Monitoring
8. Configuration Management
9. Async Error Handling Support
10. Performance and Volume Handling
"""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, List, Any, Optional
import json
import tempfile
import os


# Test Fixtures
@pytest.fixture
def error_handler_config():
    """Configuration for ErrorHandlerServiceTDD."""
    return {
        "service_name": "error_handler_tdd",
        "log_level": "INFO",
        "enable_file_logging": True,
        "enable_database_logging": True,
        "enable_notifications": True,
        "notification_channels": ["email", "webhook"],
        "max_retries": 3,
        "retry_delay_seconds": 1.0,
        "error_retention_days": 30,
        "enable_metrics": True,
        "max_errors_per_minute": 1000,
        "alert_threshold": 100,
        "webhook_url": "https://example.com/webhook",
        "admin_email": "admin@example.com"
    }


@pytest.fixture
def sample_error_context():
    """Sample error context as used throughout the codebase."""
    return {
        "component": "resume_uploader",
        "method": "upload_resume", 
        "file_path": "/path/to/file.pdf",
        "user_id": "user123",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": "req-123-456"
    }


class TestErrorClassificationAndCategorization:
    """Test error classification by type, severity, and category."""
    
    @pytest.mark.asyncio
    async def test_classify_error_by_exception_type(self, error_handler_config):
        """Test error classification based on exception type."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Test different exception types get proper classification
            value_error = ValueError("Invalid input value")
            file_error = FileNotFoundError("File not found")
            connection_error = ConnectionError("Network unavailable")
            timeout_error = TimeoutError("Operation timed out")
            
            # Each should be classified differently
            value_result = await service.handle_error(value_error, {})
            file_result = await service.handle_error(file_error, {})
            connection_result = await service.handle_error(connection_error, {})
            timeout_result = await service.handle_error(timeout_error, {})
            
            # Verify proper classification
            assert value_result.error_type == "ValueError"
            assert value_result.category == "validation"
            assert value_result.severity == "medium"
            
            assert file_result.error_type == "FileNotFoundError"
            assert file_result.category == "system"
            assert file_result.severity == "medium"
            
            assert connection_result.error_type == "ConnectionError"
            assert connection_result.category == "network"
            assert connection_result.severity == "high"
            
            assert timeout_result.error_type == "TimeoutError"
            assert timeout_result.category == "performance"
            assert timeout_result.severity == "high"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_classify_error_by_context_component(self, error_handler_config, sample_error_context):
        """Test error classification based on component context."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            error = Exception("Test error")
            
            # Test different component contexts
            resume_context = {"component": "resume_uploader", "method": "upload_resume"}
            llm_context = {"component": "llm_provider", "method": "generate_completion"}
            scraping_context = {"component": "scraping_service", "method": "scrape_jobs"}
            
            resume_result = await service.handle_error(error, resume_context)
            llm_result = await service.handle_error(error, llm_context)
            scraping_result = await service.handle_error(error, scraping_context)
            
            # Verify component-specific classification
            assert resume_result.component_category == "file_processing"
            assert llm_result.component_category == "ai_service"
            assert scraping_result.component_category == "data_collection"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_auto_assign_severity_levels(self, error_handler_config):
        """Test automatic severity level assignment."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Test severity assignment based on error patterns
            critical_error = Exception("Database connection failed")
            warning_error = Exception("Cache miss occurred") 
            info_error = Exception("User cancelled operation")
            
            critical_result = await service.handle_error(critical_error, {"component": "database"})
            warning_result = await service.handle_error(warning_error, {"component": "cache"})
            info_result = await service.handle_error(info_error, {"user_action": "cancel"})
            
            assert critical_result.severity == "critical"
            assert warning_result.severity == "warning"
            assert info_result.severity == "info"
            
        finally:
            await service.stop()


class TestContextTrackingAndEnrichment:
    """Test context preservation and enrichment capabilities."""
    
    @pytest.mark.asyncio
    async def test_preserve_original_context(self, error_handler_config, sample_error_context):
        """Test that original context is preserved exactly."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            error = Exception("Test error")
            result = await service.handle_error(error, sample_error_context)
            
            # Original context should be preserved
            assert result.original_context == sample_error_context
            assert result.component == "resume_uploader"
            assert result.method == "upload_resume"
            assert result.file_path == "/path/to/file.pdf"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_enrich_context_with_system_info(self, error_handler_config):
        """Test context enrichment with system information."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            error = Exception("Test error")
            context = {"component": "test"}
            
            result = await service.handle_error(error, context)
            
            # Should be enriched with system info
            assert result.enriched_context is not None
            assert "hostname" in result.enriched_context
            assert "process_id" in result.enriched_context
            assert "memory_usage" in result.enriched_context
            assert "timestamp" in result.enriched_context
            assert "error_id" in result.enriched_context
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio 
    async def test_track_error_chain_and_stack_trace(self, error_handler_config):
        """Test tracking of error chains and stack traces."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Create nested exception chain
            try:
                try:
                    raise ValueError("Original error")
                except ValueError as e:
                    raise FileNotFoundError("File error") from e
            except FileNotFoundError as e:
                result = await service.handle_error(e, {"component": "test"})
            
            # Should track the full error chain
            assert result.error_chain is not None
            assert len(result.error_chain) == 2
            assert result.error_chain[0]["type"] == "FileNotFoundError"
            assert result.error_chain[1]["type"] == "ValueError"
            assert result.stack_trace is not None
            
        finally:
            await service.stop()


class TestCentralizedLoggingSystem:
    """Test centralized logging to multiple destinations."""
    
    @pytest.mark.asyncio
    async def test_log_to_file_system(self, error_handler_config):
        """Test logging errors to file system."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        # Configure file logging
        config = error_handler_config.copy()
        config["enable_file_logging"] = True
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            error = Exception("Test file logging error")
            context = {"component": "test", "method": "test_method"}
            
            result = await service.handle_error(error, context)
            
            # Should confirm file logging
            assert result.logged_to_file is True
            assert result.log_file_path is not None
            
            # Verify log file exists and contains error
            log_files = await service.get_log_files()
            assert len(log_files) > 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_log_to_database(self, error_handler_config):
        """Test logging errors to database."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["enable_database_logging"] = True
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            error = Exception("Test database logging error") 
            context = {"component": "test", "method": "test_method"}
            
            result = await service.handle_error(error, context)
            
            # Should confirm database logging
            assert result.logged_to_database is True
            assert result.error_id is not None
            
            # Verify error can be retrieved from database
            stored_error = await service.get_error_by_id(result.error_id)
            assert stored_error is not None
            assert stored_error.message == "Test database logging error"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_structured_logging_format(self, error_handler_config):
        """Test structured logging format consistency."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            error = Exception("Test structured logging")
            context = {"component": "test", "user_id": "user123"}
            
            result = await service.handle_error(error, context)
            
            # Should have consistent structured format
            log_entry = result.structured_log_entry
            assert "timestamp" in log_entry
            assert "level" in log_entry
            assert "message" in log_entry
            assert "error_type" in log_entry
            assert "component" in log_entry
            assert "context" in log_entry
            assert "stack_trace" in log_entry
            
            # Should be valid JSON
            json_str = json.dumps(log_entry)
            parsed = json.loads(json_str)
            assert parsed == log_entry
            
        finally:
            await service.stop()


class TestNotificationAndAlertSystem:
    """Test notification and alert capabilities."""
    
    @pytest.mark.asyncio
    async def test_email_notifications_for_critical_errors(self, error_handler_config):
        """Test email notifications for critical errors."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["enable_notifications"] = True
        config["notification_channels"] = ["email"]
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            # Critical error should trigger email
            critical_error = Exception("Critical system failure")
            context = {"component": "database", "severity": "critical"}
            
            result = await service.handle_error(critical_error, context, notify=True)
            
            assert result.notification_sent is True
            assert "email" in result.notification_channels
            assert result.notification_status["email"] == "sent"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_webhook_notifications(self, error_handler_config):
        """Test webhook notifications for error events."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["enable_notifications"] = True
        config["notification_channels"] = ["webhook"]
        config["webhook_url"] = "https://example.com/webhook"
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            error = Exception("Test webhook notification")
            context = {"component": "test"}
            
            result = await service.handle_error(error, context, notify=True)
            
            assert result.notification_sent is True
            assert "webhook" in result.notification_channels
            assert result.webhook_payload is not None
            assert "error_id" in result.webhook_payload
            assert "timestamp" in result.webhook_payload
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_alert_threshold_monitoring(self, error_handler_config):
        """Test alert threshold monitoring and escalation."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["alert_threshold"] = 5  # Low threshold for testing
        config["enable_notifications"] = True
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            # Generate errors to exceed threshold
            for i in range(6):
                error = Exception(f"Test error {i}")
                await service.handle_error(error, {"component": "test"})
            
            # Should trigger threshold alert
            alert_status = await service.get_alert_status()
            assert alert_status.threshold_exceeded is True
            assert alert_status.error_count >= 5
            assert alert_status.alert_sent is True
            
        finally:
            await service.stop()


class TestRecoveryAndRetryMechanisms:
    """Test error recovery and retry mechanisms."""
    
    @pytest.mark.asyncio
    async def test_automatic_retry_for_transient_errors(self, error_handler_config):
        """Test automatic retry for transient errors."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["max_retries"] = 3
        config["retry_delay_seconds"] = 0.1  # Fast for testing
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            # Mock a function that fails then succeeds
            call_count = 0
            async def failing_function():
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise ConnectionError("Temporary network issue")
                return "success"
            
            # Should retry and eventually succeed
            result = await service.handle_error_with_retry(
                failing_function, 
                context={"component": "test"}
            )
            
            assert result.success is True
            assert result.retry_count == 2
            assert result.final_result == "success"
            assert call_count == 3
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_retry_strategy(self, error_handler_config):
        """Test exponential backoff retry strategy."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        import time
        
        config = error_handler_config.copy()
        config["max_retries"] = 3
        config["retry_strategy"] = "exponential_backoff"
        config["base_retry_delay"] = 0.1
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            async def always_failing_function():
                raise Exception("Always fails")
            
            start_time = time.time()
            result = await service.handle_error_with_retry(
                always_failing_function,
                context={"component": "test"}
            )
            end_time = time.time()
            
            # Should use exponential backoff timing
            assert result.success is False
            assert result.retry_count == 3
            assert len(result.retry_delays) == 3
            
            # Verify exponential backoff pattern
            assert result.retry_delays[1] > result.retry_delays[0]
            assert result.retry_delays[2] > result.retry_delays[1]
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_error_recovery_strategies(self, error_handler_config):
        """Test different error recovery strategies."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Test fallback strategy
            file_error = FileNotFoundError("Config file missing")
            result = await service.handle_error(
                file_error, 
                {"component": "config", "recovery_strategy": "use_defaults"}
            )
            
            assert result.recovery_attempted is True
            assert result.recovery_strategy == "use_defaults"
            assert result.recovery_successful is True
            
            # Test service restart strategy
            service_error = Exception("Service crashed")
            result = await service.handle_error(
                service_error,
                {"component": "llm_provider", "recovery_strategy": "restart_service"}
            )
            
            assert result.recovery_attempted is True
            assert result.recovery_strategy == "restart_service"
            
        finally:
            await service.stop()


class TestErrorStatisticsAndAnalytics:
    """Test error statistics and analytics capabilities."""
    
    @pytest.mark.asyncio
    async def test_error_frequency_tracking(self, error_handler_config):
        """Test tracking error frequency by type and component."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Generate various errors
            await service.handle_error(ValueError("Error 1"), {"component": "comp1"})
            await service.handle_error(ValueError("Error 2"), {"component": "comp1"}) 
            await service.handle_error(FileNotFoundError("Error 3"), {"component": "comp2"})
            await service.handle_error(ValueError("Error 4"), {"component": "comp2"})
            
            # Get statistics
            stats = await service.get_error_statistics()
            
            assert stats.total_errors == 4
            assert stats.error_by_type["ValueError"] == 3
            assert stats.error_by_type["FileNotFoundError"] == 1
            assert stats.error_by_component["comp1"] == 2
            assert stats.error_by_component["comp2"] == 2
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_error_trend_analysis(self, error_handler_config):
        """Test error trend analysis over time."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Generate errors over time
            for i in range(10):
                await service.handle_error(Exception(f"Error {i}"), {"component": "test"})
                await asyncio.sleep(0.01)  # Small delay
            
            # Get trend analysis
            trends = await service.get_error_trends(time_window_minutes=1)
            
            assert trends.total_errors == 10
            assert trends.errors_per_minute > 0
            assert trends.trend_direction in ["increasing", "stable", "decreasing"]
            assert len(trends.time_buckets) > 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_error_pattern_detection(self, error_handler_config):
        """Test detection of error patterns and anomalies."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Create pattern of similar errors
            for i in range(5):
                await service.handle_error(
                    ConnectionError("Database timeout"),
                    {"component": "database", "query": f"SELECT {i}"}
                )
            
            # Analyze patterns
            patterns = await service.detect_error_patterns()
            
            assert len(patterns) > 0
            db_pattern = next(p for p in patterns if p.component == "database")
            assert db_pattern.error_type == "ConnectionError"
            assert db_pattern.frequency >= 5
            assert "timeout" in db_pattern.common_keywords
            
        finally:
            await service.stop()


class TestServiceHealthMonitoring:
    """Test service health monitoring capabilities."""
    
    @pytest.mark.asyncio
    async def test_service_health_status(self, error_handler_config):
        """Test overall service health status reporting."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            health = await service.get_health_status()
            
            assert health.service_name == "error_handler_tdd"
            assert health.status == "healthy"
            assert health.uptime_seconds > 0
            assert health.total_errors_handled >= 0
            assert health.memory_usage_mb > 0
            assert health.errors_per_minute >= 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, error_handler_config):
        """Test performance metrics collection."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Generate some load
            for i in range(10):
                await service.handle_error(Exception(f"Test {i}"), {"component": "test"})
            
            metrics = await service.get_performance_metrics()
            
            assert metrics.average_processing_time_ms > 0
            assert metrics.errors_processed >= 10
            assert metrics.throughput_per_second > 0
            assert metrics.memory_usage_trend is not None
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_dependency_health_checks(self, error_handler_config):
        """Test health checks for service dependencies."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            dependency_health = await service.check_dependencies()
            
            # Should check key dependencies
            assert "file_system" in dependency_health
            assert "logging_system" in dependency_health
            assert dependency_health["file_system"]["status"] in ["healthy", "unhealthy"]
            assert dependency_health["logging_system"]["status"] in ["healthy", "unhealthy"]
            
            if "database" in dependency_health:
                assert dependency_health["database"]["status"] in ["healthy", "unhealthy"]
                assert "response_time_ms" in dependency_health["database"]
            
        finally:
            await service.stop()


class TestConfigurationManagement:
    """Test configuration management capabilities."""
    
    @pytest.mark.asyncio
    async def test_runtime_configuration_updates(self, error_handler_config):
        """Test runtime configuration updates."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Initial configuration
            initial_config = await service.get_configuration()
            assert initial_config["max_retries"] == 3
            
            # Update configuration
            new_config = {"max_retries": 5, "retry_delay_seconds": 2.0}
            result = await service.update_configuration(new_config)
            
            assert result.success is True
            
            # Verify changes applied
            updated_config = await service.get_configuration()
            assert updated_config["max_retries"] == 5
            assert updated_config["retry_delay_seconds"] == 2.0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_configuration_validation(self, error_handler_config):
        """Test configuration validation."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Test invalid configuration
            invalid_config = {"max_retries": -1, "retry_delay_seconds": "invalid"}
            
            result = await service.validate_configuration(invalid_config)
            
            assert result.valid is False
            assert len(result.errors) > 0
            assert any("max_retries" in error for error in result.errors)
            assert any("retry_delay_seconds" in error for error in result.errors)
            
            # Test valid configuration
            valid_config = {"max_retries": 5, "retry_delay_seconds": 1.5}
            result = await service.validate_configuration(valid_config)
            
            assert result.valid is True
            assert len(result.errors) == 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_environment_variable_configuration(self):
        """Test configuration from environment variables."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        # Test environment variable loading
        with patch.dict(os.environ, {
            "ERROR_HANDLER_MAX_RETRIES": "5",
            "ERROR_HANDLER_LOG_LEVEL": "DEBUG", 
            "ERROR_HANDLER_ENABLE_NOTIFICATIONS": "true"
        }):
            config = ErrorHandlerServiceTDD.load_config_from_env()
            
            assert config["max_retries"] == 5
            assert config["log_level"] == "DEBUG"
            assert config["enable_notifications"] is True


class TestAsyncErrorHandlingSupport:
    """Test async error handling support."""
    
    @pytest.mark.asyncio
    async def test_concurrent_error_handling(self, error_handler_config):
        """Test handling multiple concurrent errors."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            # Generate concurrent errors
            async def generate_error(i):
                return await service.handle_error(
                    Exception(f"Concurrent error {i}"),
                    {"component": "test", "error_id": i}
                )
            
            # Handle 10 concurrent errors
            tasks = [generate_error(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            assert len(results) == 10
            for i, result in enumerate(results):
                assert result.message == f"Concurrent error {i}"
                assert result.component == "test"
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_async_notification_handling(self, error_handler_config):
        """Test async notification handling."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["enable_notifications"] = True
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            error = Exception("Async notification test")
            
            # Should handle notifications asynchronously
            result = await service.handle_error(error, {"component": "test"}, notify=True)
            
            assert result.notification_sent is True
            assert result.notification_processing_time_ms > 0
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_context_preservation_across_async_calls(self, error_handler_config):
        """Test context preservation across async calls."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            async def nested_operation():
                await asyncio.sleep(0.01)
                raise Exception("Nested async error")
            
            context = {"component": "test", "operation": "nested", "correlation_id": "123"}
            
            try:
                await nested_operation()
            except Exception as e:
                result = await service.handle_error(e, context)
            
            # Context should be preserved
            assert result.original_context["correlation_id"] == "123"
            assert result.component == "test"
            
        finally:
            await service.stop()


class TestPerformanceAndVolumeHandling:
    """Test performance under high volume error conditions."""
    
    @pytest.mark.asyncio
    async def test_high_volume_error_processing(self, error_handler_config):
        """Test processing high volume of errors efficiently."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        import time
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            start_time = time.time()
            
            # Process 100 errors
            tasks = []
            for i in range(100):
                task = service.handle_error(
                    Exception(f"Volume test error {i}"),
                    {"component": "test", "batch": "volume_test"}
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            processing_time = end_time - start_time
            throughput = len(results) / processing_time
            
            assert len(results) == 100
            assert throughput > 10  # At least 10 errors per second
            assert all(r.message.startswith("Volume test error") for r in results)
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, error_handler_config):
        """Test memory usage remains stable under load."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        import psutil
        import os
        
        service = ErrorHandlerServiceTDD(error_handler_config)
        await service.start()
        
        try:
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss
            
            # Generate sustained load
            for batch in range(5):
                tasks = []
                for i in range(20):
                    task = service.handle_error(
                        Exception(f"Memory test {batch}-{i}"),
                        {"component": "test", "batch": batch}
                    )
                    tasks.append(task)
                await asyncio.gather(*tasks)
            
            final_memory = process.memory_info().rss
            memory_growth = (final_memory - initial_memory) / initial_memory
            
            # Memory growth should be reasonable (less than 50%)
            assert memory_growth < 0.5
            
        finally:
            await service.stop()
    
    @pytest.mark.asyncio
    async def test_error_rate_limiting(self, error_handler_config):
        """Test error rate limiting functionality."""
        from tpm_job_finder_poc.error_handler_tdd.service import ErrorHandlerServiceTDD
        
        config = error_handler_config.copy()
        config["max_errors_per_minute"] = 50  # Low limit for testing
        
        service = ErrorHandlerServiceTDD(config)
        await service.start()
        
        try:
            # Try to exceed rate limit
            results = []
            for i in range(60):
                try:
                    result = await service.handle_error(
                        Exception(f"Rate limit test {i}"),
                        {"component": "test"}
                    )
                    results.append(result)
                except Exception as e:
                    # Rate limiting might raise exceptions
                    if "rate limit" in str(e).lower():
                        break
            
            # Should either process up to limit or implement backpressure
            rate_limit_status = await service.get_rate_limit_status()
            assert rate_limit_status.current_rate <= config["max_errors_per_minute"]
            
        finally:
            await service.stop()