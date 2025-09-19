"""Notification Service package."""

__version__ = "1.0.0"
__author__ = "TPM Job Finder POC"
__description__ = "Comprehensive notification service with email, webhooks, alerts, and real-time updates"

from .service import NotificationService
from .config import NotificationServiceConfig

__all__ = ["NotificationService", "NotificationServiceConfig"]