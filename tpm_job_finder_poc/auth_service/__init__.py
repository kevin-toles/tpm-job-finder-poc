"""
Authentication and Authorization Service Module

Provides comprehensive authentication and authorization services including:
- User registration and authentication
- JWT token management
- Role-based access control (RBAC)
- Password policies and security
- Multi-factor authentication support
- Audit logging integration
"""

from .config import AuthServiceConfig, JWTConfig, PasswordConfig, SecurityConfig, MFAConfig, AuditConfig
from .service import AuthenticationService, AuthorizationService, InMemoryUserStore

__all__ = [
    "AuthServiceConfig",
    "JWTConfig", 
    "PasswordConfig",
    "SecurityConfig",
    "MFAConfig",
    "AuditConfig",
    "AuthenticationService",
    "AuthorizationService",
    "InMemoryUserStore"
]