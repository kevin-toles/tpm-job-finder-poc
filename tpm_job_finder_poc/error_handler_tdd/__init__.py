"""
Error Handler Service TDD Implementation

This module implements a comprehensive error handling service following TDD methodology.
It provides centralized error handling, logging, notification, recovery, and analytics
capabilities as a microservice.

Key Features:
- Error classification and categorization
- Multi-destination logging (file, database, external systems)
- Notification system (email, webhook, alerts)
- Error recovery and retry mechanisms
- Error analytics and pattern detection
- Performance monitoring and health checks
- Configuration management
- Async support for high-volume processing

Main Components:
- ErrorHandlerServiceTDD: Main service implementation
- Error classification and enrichment
- Logging and persistence services
- Notification and alert services
- Recovery and retry services
- Analytics and monitoring services
"""

from .service import ErrorHandlerServiceTDD

__all__ = [
    "ErrorHandlerServiceTDD"
]

__version__ = "1.0.0"