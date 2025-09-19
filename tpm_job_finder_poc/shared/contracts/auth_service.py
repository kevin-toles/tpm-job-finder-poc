"""
Authentication/Authorization Service Contract

Defines the API interfaces and data models for authentication and authorization microservice.
This contract ensures type safety and clear boundaries between the auth service and its consumers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
import uuid


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"


class TokenType(str, Enum):
    """JWT token types."""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET = "reset"
    VERIFICATION = "verification"


class AuthenticationMethod(str, Enum):
    """Authentication methods supported."""
    PASSWORD = "password"
    MFA_TOTP = "mfa_totp"
    MFA_SMS = "mfa_sms"
    API_KEY = "api_key"
    OAUTH = "oauth"


class PermissionEffect(str, Enum):
    """Permission effect types."""
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class Permission:
    """Represents a permission for a specific action on a resource."""
    name: str
    resource: str
    action: str
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = field(default_factory=dict)
    effect: PermissionEffect = PermissionEffect.ALLOW
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Validate permission data."""
        if not self.name:
            raise ValueError("Permission name is required")
        if not self.resource:
            raise ValueError("Permission resource is required")
        if not self.action:
            raise ValueError("Permission action is required")


@dataclass(frozen=True)
class Role:
    """Represents a role with associated permissions."""
    name: str
    description: Optional[str] = None
    permissions: List[str] = field(default_factory=list)  # Permission names
    is_system_role: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate role data."""
        if not self.name:
            raise ValueError("Role name is required")


@dataclass
class User:
    """User entity with authentication and profile information."""
    id: str = field(default_factory=lambda: str(uuid4()))
    username: str = ""
    email: str = ""
    password_hash: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: List[str] = field(default_factory=list)
    status: UserStatus = UserStatus.ACTIVE
    is_verified: bool = False
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    api_keys: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    
    @property
    def is_active(self) -> bool:
        """Check if user is active (for backwards compatibility)."""
        return self.status == UserStatus.ACTIVE


@dataclass(frozen=True)
class AuthToken:
    """Represents an authentication token."""
    token: str
    token_type: TokenType
    user_id: str
    expires_at: datetime
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    scopes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_revoked: bool = False
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)."""
        return not self.is_expired and not self.is_revoked


@dataclass
class LoginCredentials:
    """Represents login credentials."""
    username: Optional[str] = None
    email: Optional[str] = None
    password: str = ""
    mfa_code: Optional[str] = None
    remember_me: bool = False
    
    def __post_init__(self):
        """Validate credentials."""
        if not self.username and not self.email:
            raise ValueError("Either username or email is required for login")
        if not self.password:
            raise ValueError("Password is required for login")


@dataclass
class AuthResult:
    """Result of authentication operation."""
    success: bool
    user: Optional[User] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: Optional[int] = None  # seconds
    error_message: Optional[str] = None
    requires_mfa: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TokenValidationResult:
    """Result of token validation."""
    is_valid: bool
    user: Optional[User] = None
    token: Optional[AuthToken] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


@dataclass
class PermissionCheck:
    """Request for permission check."""
    user_id: str
    resource: str
    action: str
    resource_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizationResult:
    """Result of authorization check."""
    authorized: bool
    reason: Optional[str] = None
    matched_permissions: List[str] = field(default_factory=list)
    user_roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityContext:
    """Security context for authenticated requests."""
    user: User
    permissions: List[Permission]
    roles: List[Role]
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class OperationResult:
    """Generic result for service operations."""
    success: bool
    message: Optional[str] = None
    error_code: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    
    # Specific result types
    user: Optional[User] = None
    role: Optional[Role] = None
    permission: Optional[Permission] = None
    token: Optional[AuthToken] = None


# Exceptions
class AuthServiceError(Exception):
    """Base exception for authentication service errors."""
    pass


class AuthenticationError(AuthServiceError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AuthServiceError):
    """Raised when authorization fails."""
    pass


class TokenError(AuthServiceError):
    """Raised when token operations fail."""
    pass


class UserValidationError(AuthServiceError):
    """Raised when user validation fails."""
    pass


class PermissionError(AuthServiceError):
    """Raised when permission operations fail."""
    pass


class RoleError(AuthServiceError):
    """Raised when role operations fail."""
    pass


# Service Interfaces
class IAuthenticationService(ABC):
    """
    Abstract interface for the authentication service.
    
    This interface defines all authentication operations including
    user registration, login, token management, and security features.
    """
    
    @abstractmethod
    async def register_user(self, credentials: LoginCredentials, **kwargs) -> AuthResult:
        """
        Register a new user in the system.
        
        Args:
            credentials: User registration credentials
            **kwargs: Additional user metadata
            
        Returns:
            AuthResult with success status and user info
            
        Raises:
            UserValidationError: If user data is invalid
            AuthenticationError: If registration fails
        """
        pass
    
    @abstractmethod
    async def authenticate_user(self, credentials: LoginCredentials) -> AuthResult:
        """
        Authenticate a user with their credentials.
        
        Args:
            credentials: User login credentials
            
        Returns:
            AuthResult with tokens if successful
            
        Raises:
            AuthenticationError: If authentication fails
        """
        pass
    
    @abstractmethod
    async def validate_token(self, token: str, token_type: TokenType = TokenType.ACCESS) -> TokenValidationResult:
        """
        Validate a JWT token.
        
        Args:
            token: JWT token to validate
            token_type: Type of token being validated
            
        Returns:
            TokenValidationResult with validation status
            
        Raises:
            TokenError: If token validation fails
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            AuthResult with new access token
            
        Raises:
            TokenError: If refresh fails
        """
        pass
    
    @abstractmethod
    async def logout_user(self, token: str) -> OperationResult:
        """
        Logout a user by revoking their token.
        
        Args:
            token: Access token to revoke
            
        Returns:
            OperationResult indicating success
            
        Raises:
            TokenError: If logout fails
        """
        pass
    
    @abstractmethod
    async def change_password(self, username: str, old_password: str, new_password: str) -> OperationResult:
        """
        Change a user's password.
        
        Args:
            username: Username of the user
            old_password: Current password
            new_password: New password
            
        Returns:
            OperationResult indicating success
            
        Raises:
            AuthenticationError: If old password is incorrect
            UserValidationError: If new password is invalid
        """
        pass
    
    @abstractmethod
    async def reset_password(self, email: str) -> OperationResult:
        """
        Initiate password reset process.
        
        Args:
            email: Email address for password reset
            
        Returns:
            OperationResult indicating if reset was initiated
        """
        pass
    
    @abstractmethod
    async def enable_mfa(self, user_id: str) -> OperationResult:
        """
        Enable multi-factor authentication for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            OperationResult with MFA setup information
        """
        pass
    
    @abstractmethod
    async def verify_mfa(self, user_id: str, mfa_code: str) -> OperationResult:
        """
        Verify MFA code for a user.
        
        Args:
            user_id: ID of the user
            mfa_code: MFA code to verify
            
        Returns:
            OperationResult indicating verification success
        """
        pass
    
    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            User object or None if not found
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of the authentication service.
        
        Returns:
            Dictionary with health status information
        """
        pass
    
    @abstractmethod
    def create_auth_middleware(self):
        """
        Create authentication middleware for web frameworks.
        
        Returns:
            Middleware function/class for request authentication
        """
        pass


class IAuthorizationService(ABC):
    """
    Abstract interface for the authorization service.
    
    This interface defines all authorization operations including
    permission checks, role management, and access control.
    """
    
    @abstractmethod
    async def authorize_action(self, check: PermissionCheck) -> AuthorizationResult:
        """
        Check if a user is authorized to perform an action.
        
        Args:
            check: Permission check request
            
        Returns:
            AuthorizationResult with authorization decision
            
        Raises:
            AuthorizationError: If authorization check fails
        """
        pass
    
    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of permissions for the user
        """
        pass
    
    @abstractmethod
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """
        Get all roles for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List of roles for the user
        """
        pass
    
    @abstractmethod
    async def assign_role(self, user_id: str, role_name: str) -> OperationResult:
        """
        Assign a role to a user.
        
        Args:
            user_id: ID of the user
            role_name: Name of the role to assign
            
        Returns:
            OperationResult indicating success
            
        Raises:
            RoleError: If role assignment fails
        """
        pass
    
    @abstractmethod
    async def revoke_role(self, user_id: str, role_name: str) -> OperationResult:
        """
        Revoke a role from a user.
        
        Args:
            user_id: ID of the user
            role_name: Name of the role to revoke
            
        Returns:
            OperationResult indicating success
            
        Raises:
            RoleError: If role revocation fails
        """
        pass
    
    @abstractmethod
    async def create_role(self, role: Role) -> OperationResult:
        """
        Create a new role.
        
        Args:
            role: Role to create
            
        Returns:
            OperationResult with created role
            
        Raises:
            RoleError: If role creation fails
        """
        pass
    
    @abstractmethod
    async def create_permission(self, permission: Permission) -> OperationResult:
        """
        Create a new permission.
        
        Args:
            permission: Permission to create
            
        Returns:
            OperationResult with created permission
            
        Raises:
            PermissionError: If permission creation fails
        """
        pass
    
    @abstractmethod
    async def check_resource_access(self, check: PermissionCheck) -> AuthorizationResult:
        """
        Check access to a specific resource.
        
        Args:
            check: Resource access check request
            
        Returns:
            AuthorizationResult with access decision
        """
        pass
    
    @abstractmethod
    async def get_security_context(self, user_id: str) -> Optional[SecurityContext]:
        """
        Get complete security context for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            SecurityContext with user, roles, and permissions
        """
        pass


# Convenience Functions
def create_admin_user(username: str, email: str, password_hash: str) -> User:
    """Create an admin user with default admin role."""
    return User(
        username=username,
        email=email,
        password_hash=password_hash,
        roles=["admin"],
        status=UserStatus.ACTIVE,
        is_verified=True
    )


def create_default_roles() -> List[Role]:
    """Create default system roles."""
    return [
        Role(
            name="admin",
            description="System administrator with full access",
            permissions=["*"],
            is_system_role=True
        ),
        Role(
            name="user",
            description="Standard user with basic permissions",
            permissions=["read_own_profile", "update_own_profile"],
            is_system_role=True
        ),
        Role(
            name="moderator",
            description="Content moderator with limited admin permissions",
            permissions=["read_content", "moderate_content", "ban_user"],
            is_system_role=True
        )
    ]


def create_default_permissions() -> List[Permission]:
    """Create default system permissions."""
    return [
        Permission(name="read_own_profile", resource="user_profile", action="read", description="Read own user profile"),
        Permission(name="update_own_profile", resource="user_profile", action="update", description="Update own user profile"),
        Permission(name="read_content", resource="content", action="read", description="Read content"),
        Permission(name="create_content", resource="content", action="create", description="Create content"),
        Permission(name="update_content", resource="content", action="update", description="Update content"),
        Permission(name="delete_content", resource="content", action="delete", description="Delete content"),
        Permission(name="moderate_content", resource="content", action="moderate", description="Moderate content"),
        Permission(name="ban_user", resource="user", action="ban", description="Ban users"),
        Permission(name="admin_access", resource="admin", action="*", description="Full admin access"),
    ]