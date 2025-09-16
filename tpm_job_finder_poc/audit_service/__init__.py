"""
Audit Service Package

A comprehensive microservice for audit event logging and querying.

This package provides:
- Async audit event logging
- Flexible storage backends
- REST API interface
- Event validation and processing
- Health monitoring

Example usage:
    from tpm_job_finder_poc.audit_service import create_default_audit_service
    
    service = await create_default_audit_service()
    await service.start()
    
    # Log an event
    builder = service.create_event_builder()
    event = (builder
        .set_level(AuditLevel.INFO)
        .set_category(AuditCategory.USER_ACTION)
        .set_action("user_login")
        .set_service_name("auth_service")
        .set_user_id("user123")
        .set_message("User logged in successfully")
        .build())
    
    await service.log_event(event)
"""

from .service import AuditService, create_audit_service
from .storage import JsonFileAuditStorage, create_default_storage
from .builders import AuditEventBuilder
from .api import create_app, run_server
from .config import load_config, AuditServiceConfig
from .main import create_service_from_config

# Re-export contracts
from tpm_job_finder_poc.shared.contracts.audit_service import (
    AuditEvent,
    AuditLevel,
    AuditCategory,
    AuditQuery,
    AuditQueryResult,
    IAuditService,
    IAuditEventBuilder,
    AuditServiceError,
    AuditEventValidationError,
    AuditStorageError
)


__version__ = "1.0.0"


async def create_default_audit_service(base_path=None) -> IAuditService:
    """
    Create a default audit service for development/testing.
    
    Args:
        base_path: Base directory for audit files
        
    Returns:
        Configured audit service instance
    """
    storage = create_default_storage(base_path)
    service = create_audit_service(storage)
    return service


__all__ = [
    # Core service
    "AuditService",
    "create_audit_service",
    "create_default_audit_service",
    
    # Storage
    "JsonFileAuditStorage",
    "create_default_storage",
    
    # Builders
    "AuditEventBuilder",
    
    # API
    "create_app",
    "run_server",
    
    # Configuration
    "load_config",
    "AuditServiceConfig",
    "create_service_from_config",
    
    # Contracts
    "AuditEvent",
    "AuditLevel",
    "AuditCategory",
    "AuditQuery",
    "AuditQueryResult",
    "IAuditService",
    "IAuditEventBuilder",
    "AuditServiceError",
    "AuditEventValidationError",
    "AuditStorageError",
]