"""
Comprehensive TDD unit tests for Notification Service.

This test suite follows TDD methodology (RED → GREEN → REFACTOR) and defines
all requirements for the notification service including:
- Email notifications with SMTP integration
- Webhook delivery with retry logic
- Alert management with priority levels
- Real-time updates via WebSocket/SSE
- Template engine for dynamic messages
- Delivery tracking and confirmation
- Multi-channel configuration
- Integration with health monitoring and audit logging

Test Structure:
1. Interface and Contract Tests (Service contracts)
2. Core Service Implementation Tests (Business logic)  
3. Delivery Channel Tests (Email, Webhook, WebSocket)
4. Template Engine Tests (Message templating)
5. Alert Management Tests (Priority and escalation)
6. Configuration Tests (Multi-channel configuration)
7. Integration Tests (Health, audit, auth integration)
8. API Tests (FastAPI REST endpoints)
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import json
import uuid

# Test Configuration
pytest_plugins = ['pytest_asyncio']

class TestNotificationServiceInterface:
    """Test notification service interface and contracts (TDD RED Phase)."""
    
    def test_notification_service_interface_exists(self):
        """Test that NotificationService interface exists with required methods."""
        from tpm_job_finder_poc.notification_service.service import NotificationService
        
        # Check service class exists
        assert hasattr(NotificationService, '__init__')
        
        # Check core notification methods
        assert hasattr(NotificationService, 'send_email')
        assert hasattr(NotificationService, 'send_webhook')
        assert hasattr(NotificationService, 'send_alert')
        assert hasattr(NotificationService, 'send_realtime_update')
        
        # Check template methods
        assert hasattr(NotificationService, 'render_template')
        assert hasattr(NotificationService, 'register_template')
        
        # Check delivery tracking methods
        assert hasattr(NotificationService, 'track_delivery')
        assert hasattr(NotificationService, 'get_delivery_status')
        assert hasattr(NotificationService, 'retry_failed_delivery')
        
        # Check configuration methods
        assert hasattr(NotificationService, 'configure_channel')
        assert hasattr(NotificationService, 'get_channel_config')
        
        # Check batch operations
        assert hasattr(NotificationService, 'send_bulk_notifications')
        assert hasattr(NotificationService, 'schedule_notification')

    def test_data_models_exist(self):
        """Test that required data models exist."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationResponse, DeliveryStatus,
            EmailConfig, WebhookConfig, AlertConfig, TemplateConfig,
            NotificationChannel, NotificationPriority, NotificationTemplate,
            DeliveryAttempt, NotificationMetrics
        )
        
        # Check all required models exist
        assert NotificationRequest is not None
        assert NotificationResponse is not None
        assert DeliveryStatus is not None
        assert EmailConfig is not None
        assert WebhookConfig is not None
        assert AlertConfig is not None
        assert TemplateConfig is not None
        assert NotificationChannel is not None
        assert NotificationPriority is not None
        assert NotificationTemplate is not None
        assert DeliveryAttempt is not None
        assert NotificationMetrics is not None

    def test_notification_config_interface_exists(self):
        """Test that NotificationServiceConfig interface exists."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        
        # Check config class exists  
        assert hasattr(NotificationServiceConfig, '__init__')
        assert hasattr(NotificationServiceConfig, 'for_testing')
        assert hasattr(NotificationServiceConfig, 'for_production')
        
        # Check configuration properties
        assert hasattr(NotificationServiceConfig, 'smtp_config')
        assert hasattr(NotificationServiceConfig, 'webhook_config')  
        assert hasattr(NotificationServiceConfig, 'alert_config')
        assert hasattr(NotificationServiceConfig, 'template_config')
        assert hasattr(NotificationServiceConfig, 'realtime_config')
        assert hasattr(NotificationServiceConfig, 'retry_config')

    def test_email_provider_interface_exists(self):
        """Test that email provider interface exists."""
        from tpm_job_finder_poc.notification_service.service import EmailProvider
        
        assert hasattr(EmailProvider, 'send_email')
        assert hasattr(EmailProvider, 'validate_config')
        assert hasattr(EmailProvider, 'test_connection')

    def test_webhook_provider_interface_exists(self):
        """Test that webhook provider interface exists."""  
        from tpm_job_finder_poc.notification_service.service import WebhookProvider
        
        assert hasattr(WebhookProvider, 'send_webhook')
        assert hasattr(WebhookProvider, 'validate_endpoint')
        assert hasattr(WebhookProvider, 'verify_signature')

    def test_realtime_provider_interface_exists(self):
        """Test that real-time provider interface exists."""
        from tpm_job_finder_poc.notification_service.service import RealtimeProvider
        
        assert hasattr(RealtimeProvider, 'send_update')
        assert hasattr(RealtimeProvider, 'broadcast_update')
        assert hasattr(RealtimeProvider, 'manage_connections')


class TestNotificationServiceImplementation:
    """Test notification service core implementation."""
    
    @pytest.fixture
    async def notification_service(self):
        """Create notification service for testing."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        from tpm_job_finder_poc.notification_service.service import NotificationService
        
        config = NotificationServiceConfig.for_testing()
        service = NotificationService(config)
        await service.initialize()
        return service

    async def test_service_initialization(self, notification_service):
        """Test notification service initializes correctly."""
        from tpm_job_finder_poc.notification_service.service import NotificationService
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        
        config = NotificationServiceConfig.for_testing()
        service = NotificationService(config)
        await service.initialize()
        
        assert service.config is not None
        assert service.email_provider is not None
        assert service.webhook_provider is not None
        assert service.realtime_provider is not None
        assert service.template_engine is not None
        assert service.delivery_tracker is not None
        assert service.is_initialized is True

    async def test_email_notification_success(self, notification_service):
        """Test successful email notification sending."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test Subject",
            message="Test message content",
            priority=NotificationPriority.NORMAL,
            template_name="default_email",
            context={"user_name": "John Doe"}
        )
        
        result = await notification_service.send_email(request)
        
        assert result.success is True
        assert result.notification_id is not None
        assert result.channel == NotificationChannel.EMAIL
        assert result.status == "sent"
        assert result.delivery_attempts == 1
        assert result.sent_at is not None

    async def test_email_notification_failure(self, notification_service):
        """Test email notification failure handling."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        # Invalid email configuration to trigger failure
        request = NotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="invalid-email-format",
            subject="Test Subject", 
            message="Test message",
            priority=NotificationPriority.NORMAL
        )
        
        result = await notification_service.send_email(request)
        
        assert result.success is False
        assert result.error_message is not None
        assert "invalid email" in result.error_message.lower()
        assert result.status == "failed"

    async def test_webhook_notification_success(self, notification_service):
        """Test successful webhook notification sending."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.WEBHOOK,
            recipient="https://api.example.com/webhook",
            message="Test webhook payload",
            priority=NotificationPriority.HIGH,
            context={"event_type": "job_found", "job_id": "12345"}
        )
        
        result = await notification_service.send_webhook(request)
        
        assert result.success is True
        assert result.notification_id is not None
        assert result.channel == NotificationChannel.WEBHOOK
        assert result.status == "sent"
        assert result.webhook_response_code == 200

    async def test_webhook_notification_retry_logic(self, notification_service):
        """Test webhook notification retry logic on failure."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.WEBHOOK,
            recipient="https://api.example.com/failing-webhook",
            message="Test webhook payload",
            priority=NotificationPriority.HIGH,
            retry_count=3
        )
        
        result = await notification_service.send_webhook(request)
        
        # Should retry failed webhooks
        assert result.delivery_attempts > 1
        assert result.delivery_attempts <= 4  # Initial + 3 retries

    async def test_alert_notification_with_escalation(self, notification_service):
        """Test alert notification with priority escalation."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        # Enable escalation for this test
        notification_service.config.alert_config.escalation_enabled = True
        
        request = NotificationRequest(
            channel=NotificationChannel.ALERT,
            recipient="system-admin@example.com",
            subject="Critical System Alert",
            message="Database connection failed",
            priority=NotificationPriority.CRITICAL,
            escalation_levels=["admin", "oncall", "manager"],
            escalation_delay=300  # 5 minutes
        )
        
        result = await notification_service.send_alert(request)
        
        assert result.success is True
        assert result.notification_id is not None
        assert result.priority == NotificationPriority.CRITICAL
        assert result.escalation_scheduled is True

    async def test_realtime_notification_broadcast(self, notification_service):
        """Test real-time notification broadcasting."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.REALTIME,
            recipient="all_connected_users",
            message="New job posting available",
            priority=NotificationPriority.NORMAL,
            broadcast_type="job_update",
            context={"job_id": "12345", "title": "Senior Developer"}
        )
        
        result = await notification_service.send_realtime_update(request)
        
        assert result.success is True
        assert result.notification_id is not None
        assert result.channel == NotificationChannel.REALTIME
        assert result.connected_clients_count >= 0

    async def test_template_rendering(self, notification_service):
        """Test notification template rendering."""
        from tpm_job_finder_poc.notification_service.service import NotificationTemplate, NotificationChannel
        
        template = NotificationTemplate(
            name="job_alert_email",
            subject_template="New {{job_type}} Job: {{job_title}}",
            content_template="Hello {{user_name}}, we found a {{job_type}} position: {{job_title}} at {{company}}.",
            channel=NotificationChannel.EMAIL
        )
        
        await notification_service.register_template(template)
        
        context = {
            "user_name": "John Doe",
            "job_type": "Python Developer", 
            "job_title": "Senior Python Engineer",
            "company": "TechCorp"
        }
        
        rendered = await notification_service.render_template("job_alert_email", context)
        
        assert rendered.subject == "New Python Developer Job: Senior Python Engineer"
        assert "Hello John Doe" in rendered.content
        assert "TechCorp" in rendered.content

    async def test_delivery_status_tracking(self, notification_service):
        """Test notification delivery status tracking."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Test Tracking",
            message="Test message",
            priority=NotificationPriority.NORMAL
        )
        
        result = await notification_service.send_email(request)
        notification_id = result.notification_id
        
        # Track delivery status
        status = await notification_service.get_delivery_status(notification_id)
        
        assert status.notification_id == notification_id
        assert status.status in ["sent", "delivered", "failed", "pending"]
        assert status.channel == NotificationChannel.EMAIL
        assert status.recipient == "test@example.com"
        assert status.created_at is not None

    async def test_bulk_notification_sending(self, notification_service):
        """Test bulk notification sending."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        requests = [
            NotificationRequest(
                channel=NotificationChannel.EMAIL,
                recipient=f"user{i}@example.com",
                subject="Bulk Test",
                message=f"Test message {i}",
                priority=NotificationPriority.NORMAL
            )
            for i in range(1, 6)  # 5 notifications
        ]
        
        results = await notification_service.send_bulk_notifications(requests)
        
        assert len(results) == 5
        for result in results:
            assert result.notification_id is not None
            assert result.channel == NotificationChannel.EMAIL

    async def test_scheduled_notification(self, notification_service):
        """Test scheduled notification functionality."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        import datetime
        
        scheduled_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        
        request = NotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Scheduled Test",
            message="This is a scheduled notification",
            priority=NotificationPriority.NORMAL,
            scheduled_for=scheduled_time
        )
        
        result = await notification_service.schedule_notification(request)
        
        assert result.success is True
        assert result.notification_id is not None
        assert result.status == "scheduled"
        assert result.scheduled_for == scheduled_time

    async def test_retry_failed_delivery(self, notification_service):
        """Test retrying failed notification delivery."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        # Create a notification that will fail
        request = NotificationRequest(
            channel=NotificationChannel.WEBHOOK,
            recipient="https://invalid-url-that-will-fail.com/webhook",
            message="Test message",
            priority=NotificationPriority.NORMAL
        )
        
        # Send initial notification (should fail)
        result = await notification_service.send_webhook(request)
        notification_id = result.notification_id
        
        # Retry the failed notification
        retry_result = await notification_service.retry_failed_delivery(notification_id)
        
        assert retry_result.notification_id == notification_id
        assert retry_result.delivery_attempts > result.delivery_attempts


class TestNotificationChannels:
    """Test individual notification channels."""
    
    @pytest.fixture
    async def notification_service(self):
        """Create notification service for testing."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        from tpm_job_finder_poc.notification_service.service import NotificationService
        
        config = NotificationServiceConfig.for_testing()
        service = NotificationService(config)
        await service.initialize()
        return service

    async def test_email_with_attachments(self, notification_service):
        """Test email notifications with file attachments."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority,
            EmailAttachment
        )
        
        attachment = EmailAttachment(
            filename="report.pdf",
            content_type="application/pdf",
            data=b"fake pdf content"
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="Email with Attachment",
            message="Please find the report attached.",
            priority=NotificationPriority.NORMAL,
            attachments=[attachment]
        )
        
        result = await notification_service.send_email(request)
        
        assert result.success is True
        assert result.attachments_count == 1

    async def test_email_html_and_text_content(self, notification_service):
        """Test email with both HTML and text content."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            subject="HTML Email Test",
            message="Plain text version",
            html_content="<h1>HTML Version</h1><p>This is <strong>HTML</strong> content.</p>",
            priority=NotificationPriority.NORMAL
        )
        
        result = await notification_service.send_email(request)
        
        assert result.success is True
        assert result.content_type == "multipart/alternative"

    async def test_webhook_with_authentication(self, notification_service):
        """Test webhook with authentication headers."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority,
            WebhookAuth
        )
        
        auth = WebhookAuth(
            type="bearer",
            token="secret-token-123"
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.WEBHOOK,
            recipient="https://api.example.com/secure-webhook",
            message="Authenticated webhook payload",
            priority=NotificationPriority.HIGH,
            webhook_auth=auth,
            headers={"Custom-Header": "value"}
        )
        
        result = await notification_service.send_webhook(request)
        
        assert result.success is True
        assert result.authenticated is True

    async def test_webhook_signature_verification(self, notification_service):
        """Test webhook signature generation and verification."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        request = NotificationRequest(
            channel=NotificationChannel.WEBHOOK,
            recipient="https://api.example.com/webhook",
            message='{"event": "test", "data": "payload"}',
            priority=NotificationPriority.NORMAL,
            webhook_secret="my-webhook-secret",
            signature_header="X-Signature"
        )
        
        result = await notification_service.send_webhook(request)
        
        assert result.success is True
        assert result.signature_generated is True

    async def test_realtime_connection_management(self, notification_service):
        """Test real-time connection management."""
        from tpm_job_finder_poc.notification_service.service import RealtimeConnection
        
        # Simulate client connections
        connection1 = RealtimeConnection(
            connection_id="conn_123",
            user_id="user_456",
            connection_type="websocket"
        )
        
        connection2 = RealtimeConnection(
            connection_id="conn_789",
            user_id="user_012",
            connection_type="sse"
        )
        
        # Add connections
        await notification_service.realtime_provider.add_connection(connection1)
        await notification_service.realtime_provider.add_connection(connection2)
        
        # Check active connections
        active_connections = await notification_service.realtime_provider.get_active_connections()
        
        assert len(active_connections) == 2
        assert any(conn.connection_id == "conn_123" for conn in active_connections)
        assert any(conn.connection_id == "conn_789" for conn in active_connections)


class TestNotificationTemplates:
    """Test notification template engine."""
    
    @pytest.fixture
    async def notification_service(self):
        """Create notification service for testing.""" 
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        from tpm_job_finder_poc.notification_service.service import NotificationService
        
        config = NotificationServiceConfig.for_testing()
        service = NotificationService(config)
        await service.initialize()
        return service

    async def test_template_registration(self, notification_service):
        """Test template registration and retrieval."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationTemplate, NotificationChannel
        )
        
        template = NotificationTemplate(
            name="welcome_email",
            subject_template="Welcome to {{app_name}}, {{user_name}}!",
            content_template="Hello {{user_name}}, welcome to {{app_name}}. Your account is now active.",
            channel=NotificationChannel.EMAIL,
            description="Welcome email for new users"
        )
        
        result = await notification_service.register_template(template)
        
        assert result.success is True
        assert result.template_name == "welcome_email"
        
        # Retrieve template
        retrieved = await notification_service.get_template("welcome_email")
        assert retrieved.name == "welcome_email"
        assert retrieved.subject_template == template.subject_template

    async def test_template_with_conditionals(self, notification_service):
        """Test template with conditional content."""
        from tpm_job_finder_poc.notification_service.service import NotificationTemplate, NotificationChannel
        
        template = NotificationTemplate(
            name="job_alert_conditional",
            subject_template="{{job_count}} New Job{% if job_count > 1 %}s{% endif %} Found",
            content_template="""
Hello {{user_name}},

{% if if_urgent %}
🚨 URGENT: 
{% endif %}

We found {{job_count}} new job{% if job_count > 1 %}s{% endif %} matching your criteria:

{% for job in jobs %}
- {{job.title}} at {{job.company}} ({{job.salary}})
{% endfor %}

{% if if_remote %}
Note: Some positions offer remote work options.
{% endif %}
            """,
            channel=NotificationChannel.EMAIL
        )
        
        await notification_service.register_template(template)
        
        context = {
            "user_name": "John",
            "job_count": 3,
            "if_multiple": True,
            "if_urgent": False,
            "if_remote": True,
            "jobs": [
                {"title": "Python Developer", "company": "TechCorp", "salary": "$90k"},
                {"title": "Data Scientist", "company": "DataInc", "salary": "$95k"},
                {"title": "DevOps Engineer", "company": "CloudCo", "salary": "$85k"}
            ]
        }
        
        rendered = await notification_service.render_template("job_alert_conditional", context)
        
        assert "3 New Jobs Found" in rendered.subject
        assert "Hello John" in rendered.content
        assert "Python Developer" in rendered.content
        assert "remote work options" in rendered.content

    async def test_template_validation(self, notification_service):
        """Test template validation and error handling."""
        from tpm_job_finder_poc.notification_service.service import NotificationTemplate, NotificationChannel
        
        # Invalid template syntax
        invalid_template = NotificationTemplate(
            name="invalid_template",
            subject_template="Hello {{user_name}",  # Missing closing brace
            content_template="Content with {{invalid_syntax",
            channel=NotificationChannel.EMAIL
        )
        
        result = await notification_service.register_template(invalid_template)
        
        assert result.success is False
        assert "template syntax" in result.error_message.lower()


class TestNotificationConfiguration:
    """Test notification service configuration."""
    
    def test_configuration_creation(self):
        """Test notification service configuration creation."""
        from tpm_job_finder_poc.notification_service.config import (
            NotificationServiceConfig, SMTPConfig, WebhookConfig, 
            AlertConfig, RealtimeConfig
        )
        
        config = NotificationServiceConfig(
            smtp_config=SMTPConfig(
                host="smtp.example.com",
                port=587,
                username="user@example.com",
                password="password",
                use_tls=True
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
                max_escalation_levels=3
            ),
            realtime_config=RealtimeConfig(
                websocket_enabled=True,
                sse_enabled=True,
                max_connections=1000
            )
        )
        
        assert config.smtp_config.host == "smtp.example.com"
        assert config.webhook_config.max_retries == 3
        assert config.alert_config.escalation_enabled is True
        assert config.realtime_config.max_connections == 1000

    def test_testing_configuration(self):
        """Test testing configuration setup."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        
        config = NotificationServiceConfig.for_testing()
        
        assert config.smtp_config.host == "localhost"
        assert config.smtp_config.port == 1025  # Test SMTP port
        assert config.webhook_config.verify_ssl is False  # Relaxed for testing
        assert config.alert_config.escalation_enabled is False  # Disabled for testing

    def test_production_configuration(self):
        """Test production configuration setup."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        
        config = NotificationServiceConfig.for_production()
        
        assert config.smtp_config.use_tls is True
        assert config.webhook_config.verify_ssl is True
        assert config.alert_config.escalation_enabled is True
        assert config.realtime_config.websocket_enabled is True

    async def test_channel_configuration(self):
        """Test individual channel configuration."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        from tpm_job_finder_poc.notification_service.service import NotificationService
        
        config = NotificationServiceConfig.for_testing()
        service = NotificationService(config)
        await service.initialize()
        
        # Configure email channel
        email_result = await service.configure_channel(
            channel="email",
            config={
                "smtp_host": "custom.smtp.com",
                "smtp_port": 465,
                "use_ssl": True
            }
        )
        
        assert email_result.success is True
        
        # Get channel configuration
        email_config = await service.get_channel_config("email")
        assert email_config["smtp_host"] == "custom.smtp.com"


class TestNotificationIntegration:
    """Test notification service integration with other components."""
    
    @pytest.fixture
    async def notification_service(self):
        """Create notification service for testing."""
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        from tpm_job_finder_poc.notification_service.service import NotificationService
        
        config = NotificationServiceConfig.for_testing()
        service = NotificationService(config)
        await service.initialize()
        return service

    async def test_integration_with_audit_logging(self, notification_service):
        """Test integration with audit logging service."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        # Mock audit logger
        with patch('tpm_job_finder_poc.audit_logger.logger.AuditLogger.log_event') as mock_audit:
            request = NotificationRequest(
                channel=NotificationChannel.EMAIL,
                recipient="test@example.com",
                subject="Audit Test",
                message="Test message for audit logging",
                priority=NotificationPriority.NORMAL,
                user_id="user_123"
            )
            
            result = await notification_service.send_email(request)
            
            # Verify audit logging was called
            mock_audit.assert_called()
            call_args = mock_audit.call_args[1]
            assert call_args['event_type'] == 'notification_sent'
            assert call_args['user_id'] == 'user_123'
            assert call_args['event_data']['channel'] == 'email'

    async def test_integration_with_health_monitoring(self, notification_service):
        """Test integration with health monitoring."""
        from tpm_job_finder_poc.notification_service.service import NotificationMetrics
        
        # Check initial health status
        health_status = await notification_service.get_health_status()
        
        assert health_status.service_name == "notification_service"
        assert health_status.status in ["healthy", "degraded", "unhealthy"]
        assert health_status.uptime >= 0
        assert isinstance(health_status.metrics, NotificationMetrics)
        
        # Check metrics
        metrics = health_status.metrics
        assert hasattr(metrics, 'emails_sent')
        assert hasattr(metrics, 'webhooks_sent')
        assert hasattr(metrics, 'alerts_sent')
        assert hasattr(metrics, 'delivery_success_rate')
        assert hasattr(metrics, 'average_delivery_time')

    async def test_integration_with_auth_service(self, notification_service):
        """Test integration with authentication service for user notifications."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        # Mock auth service user lookup
        with patch('tpm_job_finder_poc.auth_service.service.AuthenticationService.get_user') as mock_get_user:
            mock_get_user.return_value = {
                "id": "user_123",
                "username": "johndoe",
                "email": "john@example.com",
                "preferences": {
                    "email_notifications": True,
                    "alert_notifications": True
                }
            }
            
            # Send user-specific notification
            request = NotificationRequest(
                channel=NotificationChannel.EMAIL,
                user_id="user_123",  # Will lookup email from auth service
                subject="User-specific notification",
                message="Hello from integrated service",
                priority=NotificationPriority.NORMAL
            )
            
            result = await notification_service.send_user_notification(request)
            
            assert result.success is True
            assert result.recipient == "john@example.com"
            mock_get_user.assert_called_with("user_123")

    async def test_error_notification_to_health_monitor(self, notification_service):
        """Test automatic error notifications to health monitor."""
        from tpm_job_finder_poc.notification_service.service import (
            NotificationRequest, NotificationChannel, NotificationPriority
        )
        
        # Mock health monitor
        with patch('tpm_job_finder_poc.health_monitor.monitor.HealthMonitor.report_error') as mock_report:
            # Create a notification that will trigger an error
            request = NotificationRequest(
                channel=NotificationChannel.EMAIL,
                recipient="invalid-email",
                subject="Error Test",
                message="This should trigger an error",
                priority=NotificationPriority.NORMAL
            )
            
            result = await notification_service.send_email(request)
            
            # Verify error was reported to health monitor
            assert result.success is False
            mock_report.assert_called()
            call_args = mock_report.call_args[1]
            assert call_args['service'] == 'notification_service'
            assert call_args['error_type'] == 'email_delivery_failed'


class TestNotificationServiceAPI:
    """Test notification service FastAPI endpoints."""
    
    @pytest.fixture
    def api_client(self):
        """Create test API client."""
        from fastapi.testclient import TestClient
        from tpm_job_finder_poc.notification_service.api import create_app
        from tpm_job_finder_poc.notification_service.config import NotificationServiceConfig
        
        config = NotificationServiceConfig.for_testing()
        app = create_app(config)
        return TestClient(app)

    def test_send_notification_endpoint(self, api_client):
        """Test /notifications/send endpoint."""
        notification_data = {
            "channel": "email",
            "recipient": "test@example.com",
            "subject": "API Test",
            "message": "Test message from API",
            "priority": "normal"
        }
        
        response = api_client.post("/notifications/send", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "notification_id" in data
        assert data["status"] == "sent"
        assert data["channel"] == "email"

    def test_get_notification_status_endpoint(self, api_client):
        """Test /notifications/{notification_id}/status endpoint."""
        # First send a notification
        notification_data = {
            "channel": "email",
            "recipient": "test@example.com",
            "subject": "Status Test",
            "message": "Test message",
            "priority": "normal"
        }
        
        send_response = api_client.post("/notifications/send", json=notification_data)
        notification_id = send_response.json()["notification_id"]
        
        # Get notification status
        status_response = api_client.get(f"/notifications/{notification_id}/status")
        assert status_response.status_code == 200
        
        status_data = status_response.json()
        assert status_data["notification_id"] == notification_id
        assert "status" in status_data
        assert "channel" in status_data
        assert "recipient" in status_data

    def test_send_bulk_notifications_endpoint(self, api_client):
        """Test /notifications/bulk endpoint."""
        bulk_data = {
            "notifications": [
                {
                    "channel": "email",
                    "recipient": f"user{i}@example.com",
                    "subject": f"Bulk Test {i}",
                    "message": f"Bulk message {i}",
                    "priority": "normal"
                }
                for i in range(1, 4)
            ]
        }
        
        response = api_client.post("/notifications/bulk", json=bulk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 3
        assert data["total_sent"] == 3

    def test_retry_notification_endpoint(self, api_client):
        """Test /notifications/{notification_id}/retry endpoint."""
        # Create a failed notification to retry
        notification_data = {
            "channel": "webhook",
            "recipient": "https://invalid-url.com/webhook",
            "message": "Test webhook",
            "priority": "normal"
        }
        
        send_response = api_client.post("/notifications/send", json=notification_data)
        notification_id = send_response.json()["notification_id"]
        
        # Retry the notification
        retry_response = api_client.post(f"/notifications/{notification_id}/retry")
        assert retry_response.status_code == 200
        
        retry_data = retry_response.json()
        assert retry_data["notification_id"] == notification_id
        assert "retry_attempt" in retry_data

    def test_get_notification_metrics_endpoint(self, api_client):
        """Test /notifications/metrics endpoint.""" 
        response = api_client.get("/notifications/metrics")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_sent" in data
        assert "success_rate" in data
        assert "channels" in data
        assert "average_delivery_time" in data

    def test_configure_channel_endpoint(self, api_client):
        """Test /notifications/channels/{channel}/config endpoint."""
        config_data = {
            "smtp_host": "custom.smtp.com",
            "smtp_port": 587,
            "use_tls": True
        }
        
        response = api_client.put("/notifications/channels/email/config", json=config_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["channel"] == "email"
        assert data["configured"] is True

    def test_list_templates_endpoint(self, api_client):
        """Test /notifications/templates endpoint."""
        response = api_client.get("/notifications/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)

    def test_create_template_endpoint(self, api_client):
        """Test POST /notifications/templates endpoint."""
        template_data = {
            "name": "api_test_template",
            "subject_template": "API Test: {{subject}}",
            "content_template": "Hello {{name}}, this is a test from API.",
            "channel": "email",
            "description": "Test template created via API"
        }
        
        response = api_client.post("/notifications/templates", json=template_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "api_test_template"
        assert data["created"] is True

    def test_unauthorized_access(self, api_client):
        """Test unauthorized access to protected endpoints."""
        # Test without authentication token
        response = api_client.post("/notifications/send", json={})
        assert response.status_code == 401

    def test_invalid_notification_data(self, api_client):
        """Test validation of invalid notification data."""
        invalid_data = {
            "channel": "invalid_channel",
            "recipient": "",  # Empty recipient
            "subject": "",
            "message": "",
            "priority": "invalid_priority"
        }
        
        response = api_client.post("/notifications/send", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        data = response.json()
        assert "detail" in data