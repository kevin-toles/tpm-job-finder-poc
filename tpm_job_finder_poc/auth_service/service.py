"""
Authentication and Authorization Service Implementation

Core service implementing authentication, authorization, and user management
with JWT tokens, RBAC, password security, and audit logging.
"""

import asyncio
import logging
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set
import jwt
import bcrypt
from passlib.context import CryptContext

# Import contracts and config
from tpm_job_finder_poc.shared.contracts.auth_service import (
    IAuthenticationService,
    IAuthorizationService,
    User,
    Role,
    Permission,
    AuthToken,
    LoginCredentials,
    AuthResult,
    TokenValidationResult,
    PermissionCheck,
    AuthorizationResult,
    SecurityContext,
    OperationResult,
    UserStatus,
    TokenType,
    AuthenticationMethod,
    PermissionEffect,
    AuthServiceError,
    AuthenticationError,
    AuthorizationError,
    TokenError,
    UserValidationError,
    PermissionError,
    RoleError,
    create_default_roles,
    create_default_permissions
)
from tpm_job_finder_poc.auth_service.config import AuthServiceConfig

# Import audit service for logging
from tpm_job_finder_poc.shared.contracts.audit_service import AuditLevel, AuditCategory


logger = logging.getLogger(__name__)


class InMemoryUserStore:
    """In-memory user storage for development/testing."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.users_by_username: Dict[str, str] = {}  # username -> user_id
        self.users_by_email: Dict[str, str] = {}      # email -> user_id
        self.roles: Dict[str, Role] = {}
        self.permissions: Dict[str, Permission] = {}
        self.revoked_tokens: Set[str] = set()
        
        # Initialize with default roles and permissions
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default roles and permissions."""
        # Create default permissions
        for perm in create_default_permissions():
            self.permissions[perm.name] = perm
        
        # Create default roles
        for role in create_default_roles():
            self.roles[role.name] = role
    
    async def save_user(self, user: User) -> User:
        """Save user to storage."""
        self.users[user.id] = user
        if user.username:
            self.users_by_username[user.username] = user.id
        if user.email:
            self.users_by_email[user.email] = user.id
        return user
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_id = self.users_by_username.get(username)
        return self.users.get(user_id) if user_id else None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_id = self.users_by_email.get(email)
        return self.users.get(user_id) if user_id else None
    
    async def save_role(self, role: Role) -> Role:
        """Save role to storage."""
        self.roles[role.name] = role
        return role
    
    async def get_role(self, role_name: str) -> Optional[Role]:
        """Get role by name."""
        return self.roles.get(role_name)
    
    async def save_permission(self, permission: Permission) -> Permission:
        """Save permission to storage."""
        self.permissions[permission.name] = permission
        return permission
    
    async def get_permission(self, permission_name: str) -> Optional[Permission]:
        """Get permission by name."""
        return self.permissions.get(permission_name)
    
    async def revoke_token(self, token_jti: str):
        """Add token to revocation list."""
        self.revoked_tokens.add(token_jti)
    
    async def is_token_revoked(self, token_jti: str) -> bool:
        """Check if token is revoked."""
        return token_jti in self.revoked_tokens


class AuthenticationService(IAuthenticationService):
    """Authentication service implementation."""
    
    def __init__(self, config: AuthServiceConfig, storage: Optional[InMemoryUserStore] = None):
        self.config = config
        self.storage = storage or InMemoryUserStore()
        
        # Initialize password hashing
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=config.password.bcrypt_rounds
        )
        
        # Mock audit service for logging
        self.audit_service = None
        
        logger.info(f"Authentication service initialized with config: {config.service_name}")
    
    async def register_user(self, credentials: LoginCredentials, **kwargs) -> AuthResult:
        """Register a new user in the system."""
        try:
            # Validate credentials
            if not credentials.username and not credentials.email:
                return AuthResult(
                    success=False,
                    error_message="Username or email is required"
                )
            
            # Validate password strength
            password_validation = self._validate_password_strength(credentials.password)
            if not password_validation.success:
                return AuthResult(
                    success=False,
                    error_message=password_validation.message
                )
            
            # Check if user already exists
            existing_user = None
            if credentials.username:
                existing_user = await self.storage.get_user_by_username(credentials.username)
            if not existing_user and credentials.email:
                existing_user = await self.storage.get_user_by_email(credentials.email)
            
            if existing_user:
                return AuthResult(
                    success=False,
                    error_message="User already exists"
                )
            
            # Create new user
            password_hash = self.pwd_context.hash(credentials.password)
            
            user = User(
                username=credentials.username or "",
                email=credentials.email or "",
                password_hash=password_hash,
                roles=[self.config.default_user_role],
                status=UserStatus.ACTIVE,
                is_verified=not self.config.enable_email_verification,
                **kwargs
            )
            
            # Save user
            saved_user = await self.storage.save_user(user)
            
            # Log audit event
            await self._log_audit_event("user_registered", saved_user.id, {
                "username": saved_user.username,
                "email": saved_user.email
            })
            
            return AuthResult(
                success=True,
                user=saved_user
            )
            
        except Exception as e:
            logger.error(f"User registration failed: {e}")
            return AuthResult(
                success=False,
                error_message="Registration failed"
            )
    
    async def authenticate_user(self, credentials: LoginCredentials) -> AuthResult:
        """Authenticate a user with their credentials."""
        try:
            # Find user
            user = None
            if credentials.username:
                user = await self.storage.get_user_by_username(credentials.username)
            elif credentials.email:
                user = await self.storage.get_user_by_email(credentials.email)
            
            if not user:
                await self._log_audit_event("login_failed", None, {
                    "reason": "user_not_found",
                    "username": credentials.username,
                    "email": credentials.email
                })
                return AuthResult(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # Check account status
            if user.status == UserStatus.LOCKED:
                if user.locked_until and datetime.now(timezone.utc) > user.locked_until:
                    # Unlock account
                    user.status = UserStatus.ACTIVE
                    user.failed_login_attempts = 0
                    user.locked_until = None
                    await self.storage.save_user(user)
                else:
                    await self._log_audit_event("login_failed", user.id, {
                        "reason": "account_locked",
                        "username": user.username
                    })
                    return AuthResult(
                        success=False,
                        error_message="Account is locked. Please try again later."
                    )
            
            if user.status != UserStatus.ACTIVE:
                return AuthResult(
                    success=False,
                    error_message="Account is not active"
                )
            
            # Verify password
            if not user.password_hash or not self.pwd_context.verify(credentials.password, user.password_hash):
                # Increment failed attempts
                user.failed_login_attempts += 1
                
                # Check if account should be locked
                if user.failed_login_attempts >= self.config.security.max_login_attempts:
                    user.status = UserStatus.LOCKED
                    user.locked_until = datetime.now(timezone.utc) + timedelta(
                        minutes=self.config.security.account_lockout_duration_minutes
                    )
                    
                    await self._log_audit_event("account_locked", user.id, {
                        "reason": "too_many_failed_attempts",
                        "username": user.username
                    })
                    
                    await self.storage.save_user(user)
                    return AuthResult(
                        success=False,
                        error_message="Too many failed attempts. Account has been locked."
                    )
                
                await self.storage.save_user(user)
                await self._log_audit_event("login_failed", user.id, {
                    "reason": "invalid_password",
                    "username": user.username,
                    "attempts": user.failed_login_attempts
                })
                
                return AuthResult(
                    success=False,
                    error_message="Invalid credentials"
                )
            
            # Check MFA if enabled
            if user.mfa_enabled and not credentials.mfa_code:
                return AuthResult(
                    success=False,
                    requires_mfa=True,
                    error_message="MFA code required"
                )
            
            # Reset failed attempts on successful authentication
            user.failed_login_attempts = 0
            user.last_login = datetime.now(timezone.utc)
            await self.storage.save_user(user)
            
            # Generate tokens
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)
            
            await self._log_audit_event("login_success", user.id, {
                "username": user.username,
                "method": "password"
            })
            
            return AuthResult(
                success=True,
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="Bearer",
                expires_in=self.config.jwt.access_token_expire_minutes * 60
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return AuthResult(
                success=False,
                error_message="Authentication failed"
            )
    
    async def validate_token(self, token: str, token_type: TokenType = TokenType.ACCESS) -> TokenValidationResult:
        """Validate a JWT token."""
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.config.get_jwt_secret(),
                algorithms=[self.config.jwt.algorithm],
                issuer=self.config.jwt.issuer
            )
            
            # Check token type
            if payload.get("type") != token_type.value:
                return TokenValidationResult(
                    is_valid=False,
                    error_message=f"Invalid token type. Expected {token_type.value}"
                )
            
            # Check if token is revoked
            token_jti = payload.get("jti")
            if token_jti and await self.storage.is_token_revoked(token_jti):
                return TokenValidationResult(
                    is_valid=False,
                    error_message="Token has been revoked"
                )
            
            # Get user
            user_id = payload.get("sub")
            if not user_id:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="Invalid token: missing user ID"
                )
            
            user = await self.storage.get_user(user_id)
            if not user:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="User not found"
                )
            
            if user.status != UserStatus.ACTIVE:
                return TokenValidationResult(
                    is_valid=False,
                    error_message="User account is not active"
                )
            
            # Create AuthToken object
            auth_token = AuthToken(
                token=token,
                token_type=token_type,
                user_id=user_id,
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
                scopes=payload.get("scopes", [])
            )
            
            return TokenValidationResult(
                is_valid=True,
                user=user,
                token=auth_token,
                expires_at=auth_token.expires_at,
                scopes=auth_token.scopes
            )
            
        except jwt.ExpiredSignatureError:
            return TokenValidationResult(
                is_valid=False,
                error_message="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            return TokenValidationResult(
                is_valid=False,
                error_message=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return TokenValidationResult(
                is_valid=False,
                error_message="Token validation failed"
            )
    
    async def refresh_token(self, refresh_token: str) -> AuthResult:
        """Refresh an access token using a refresh token."""
        try:
            # Validate refresh token
            validation_result = await self.validate_token(refresh_token, TokenType.REFRESH)
            
            if not validation_result.is_valid:
                return AuthResult(
                    success=False,
                    error_message="Invalid refresh token"
                )
            
            user = validation_result.user
            if not user:
                return AuthResult(
                    success=False,
                    error_message="User not found"
                )
            
            # Generate new tokens
            new_access_token = self._generate_access_token(user)
            new_refresh_token = self._generate_refresh_token(user)
            
            await self._log_audit_event("token_refreshed", user.id, {
                "username": user.username
            })
            
            return AuthResult(
                success=True,
                user=user,
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="Bearer",
                expires_in=self.config.jwt.access_token_expire_minutes * 60
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            return AuthResult(
                success=False,
                error_message="Token refresh failed"
            )
    
    async def logout_user(self, token: str) -> OperationResult:
        """Logout a user by revoking their token."""
        try:
            # Decode token to get JTI
            payload = jwt.decode(
                token,
                self.config.get_jwt_secret(),
                algorithms=[self.config.jwt.algorithm],
                options={"verify_exp": False}  # Don't verify expiration for logout
            )
            
            token_jti = payload.get("jti")
            user_id = payload.get("sub")
            
            if token_jti:
                await self.storage.revoke_token(token_jti)
            
            await self._log_audit_event("logout", user_id, {
                "method": "token_revocation"
            })
            
            return OperationResult(
                success=True,
                message="User logged out successfully"
            )
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return OperationResult(
                success=False,
                message="Logout failed"
            )
    
    async def change_password(self, username: str, old_password: str, new_password: str) -> OperationResult:
        """Change a user's password."""
        try:
            # Find user
            user = await self.storage.get_user_by_username(username)
            if not user:
                return OperationResult(
                    success=False,
                    message="User not found"
                )
            
            # Verify old password
            if not user.password_hash or not self.pwd_context.verify(old_password, user.password_hash):
                return OperationResult(
                    success=False,
                    message="Current password is incorrect"
                )
            
            # Validate new password
            password_validation = self._validate_password_strength(new_password)
            if not password_validation.success:
                return OperationResult(
                    success=False,
                    message=password_validation.message
                )
            
            # Update password
            new_password_hash = self.pwd_context.hash(new_password)
            user.password_hash = new_password_hash
            user.updated_at = datetime.now(timezone.utc)
            
            await self.storage.save_user(user)
            
            await self._log_audit_event("password_changed", user.id, {
                "username": user.username
            })
            
            return OperationResult(
                success=True,
                message="Password changed successfully"
            )
            
        except Exception as e:
            logger.error(f"Password change failed: {e}")
            return OperationResult(
                success=False,
                message="Password change failed"
            )
    
    async def reset_password(self, email: str) -> OperationResult:
        """Initiate password reset process."""
        try:
            user = await self.storage.get_user_by_email(email)
            if not user:
                # Don't reveal if email exists or not
                return OperationResult(
                    success=True,
                    message="If the email exists, a reset link has been sent"
                )
            
            # Generate reset token (simplified for this implementation)
            reset_token = self._generate_reset_token(user)
            
            await self._log_audit_event("password_reset_requested", user.id, {
                "email": email
            })
            
            # In a real implementation, you would send an email here
            logger.info(f"Password reset token for {email}: {reset_token}")
            
            return OperationResult(
                success=True,
                message="If the email exists, a reset link has been sent"
            )
            
        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            return OperationResult(
                success=False,
                message="Password reset failed"
            )
    
    async def enable_mfa(self, user_id: str) -> OperationResult:
        """Enable multi-factor authentication for a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user:
                return OperationResult(
                    success=False,
                    message="User not found"
                )
            
            if user.mfa_enabled:
                return OperationResult(
                    success=False,
                    message="MFA is already enabled"
                )
            
            # Generate MFA secret
            mfa_secret = secrets.token_urlsafe(32)
            user.mfa_secret = mfa_secret
            user.mfa_enabled = True
            user.updated_at = datetime.now(timezone.utc)
            
            await self.storage.save_user(user)
            
            await self._log_audit_event("mfa_enabled", user.id, {
                "username": user.username
            })
            
            return OperationResult(
                success=True,
                message="MFA enabled successfully",
                data={"mfa_secret": mfa_secret}
            )
            
        except Exception as e:
            logger.error(f"MFA enable failed: {e}")
            return OperationResult(
                success=False,
                message="Failed to enable MFA"
            )
    
    async def verify_mfa(self, user_id: str, mfa_code: str) -> OperationResult:
        """Verify MFA code for a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user or not user.mfa_enabled:
                return OperationResult(
                    success=False,
                    message="MFA not enabled for user"
                )
            
            # In a real implementation, you would verify TOTP here
            # For this demo, we'll accept any 6-digit code
            if len(mfa_code) == 6 and mfa_code.isdigit():
                return OperationResult(
                    success=True,
                    message="MFA code verified"
                )
            
            return OperationResult(
                success=False,
                message="Invalid MFA code"
            )
            
        except Exception as e:
            logger.error(f"MFA verification failed: {e}")
            return OperationResult(
                success=False,
                message="MFA verification failed"
            )
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.storage.get_user(user_id)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the authentication service."""
        try:
            # Check storage connection
            user_count = len(self.storage.users)
            
            # Check JWT key
            jwt_key_loaded = bool(self.config.get_jwt_secret())
            
            # Check configuration
            config_valid = self.config.jwt.secret_key is not None
            
            return {
                "status": "healthy",
                "service": self.config.service_name,
                "version": self.config.service_version,
                "database_connection": True,  # Always true for in-memory storage
                "jwt_key_loaded": jwt_key_loaded,
                "config_valid": config_valid,
                "user_count": user_count,
                "roles_count": len(self.storage.roles),
                "permissions_count": len(self.storage.permissions),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def create_auth_middleware(self):
        """Create authentication middleware for web frameworks."""
        async def auth_middleware(request, call_next):
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                # Return unauthorized response
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            token = auth_header.split(" ")[1]
            validation_result = await self.validate_token(token)
            
            if not validation_result.is_valid:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=validation_result.error_message
                )
            
            # Add user to request state
            request.state.user = validation_result.user
            request.state.token = validation_result.token
            
            return await call_next(request)
        
        return auth_middleware
    
    def _generate_access_token(self, user: User) -> str:
        """Generate JWT access token for user."""
        now = datetime.now(timezone.utc)
        expires = now + self.config.get_token_expiry_timedelta("access")
        
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "type": TokenType.ACCESS.value,
            "iat": now,
            "exp": expires,
            "iss": self.config.jwt.issuer,
            "jti": secrets.token_urlsafe(16)  # JWT ID for revocation
        }
        
        return jwt.encode(
            payload,
            self.config.get_jwt_secret(),
            algorithm=self.config.jwt.algorithm
        )
    
    def _generate_refresh_token(self, user: User) -> str:
        """Generate JWT refresh token for user."""
        now = datetime.now(timezone.utc)
        expires = now + self.config.get_token_expiry_timedelta("refresh")
        
        payload = {
            "sub": user.id,
            "type": TokenType.REFRESH.value,
            "iat": now,
            "exp": expires,
            "iss": self.config.jwt.issuer,
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(
            payload,
            self.config.get_jwt_secret(),
            algorithm=self.config.jwt.algorithm
        )
    
    def _generate_reset_token(self, user: User) -> str:
        """Generate password reset token for user."""
        now = datetime.now(timezone.utc)
        expires = now + self.config.get_token_expiry_timedelta("reset")
        
        payload = {
            "sub": user.id,
            "type": TokenType.RESET.value,
            "iat": now,
            "exp": expires,
            "iss": self.config.jwt.issuer
        }
        
        return jwt.encode(
            payload,
            self.config.get_jwt_secret(),
            algorithm=self.config.jwt.algorithm
        )
    
    def _validate_password_strength(self, password: str) -> OperationResult:
        """Validate password against policy."""
        if len(password) < self.config.password.min_length:
            return OperationResult(
                success=False,
                message=f"Password must be at least {self.config.password.min_length} characters long"
            )
        
        if len(password) > self.config.password.max_length:
            return OperationResult(
                success=False,
                message=f"Password must be no more than {self.config.password.max_length} characters long"
            )
        
        if self.config.password.require_uppercase and not any(c.isupper() for c in password):
            return OperationResult(
                success=False,
                message="Password must contain at least one uppercase letter"
            )
        
        if self.config.password.require_lowercase and not any(c.islower() for c in password):
            return OperationResult(
                success=False,
                message="Password must contain at least one lowercase letter"
            )
        
        if self.config.password.require_numbers and not any(c.isdigit() for c in password):
            return OperationResult(
                success=False,
                message="Password must contain at least one number"
            )
        
        if self.config.password.require_special_chars:
            if not any(c in self.config.password.special_chars for c in password):
                return OperationResult(
                    success=False,
                    message=f"Password must contain at least one special character: {self.config.password.special_chars}"
                )
        
        return OperationResult(success=True, message="Password is valid")
    
    async def _log_audit_event(self, action: str, user_id: Optional[str], details: Dict[str, Any]):
        """Log audit event (mock implementation)."""
        # In a real implementation, this would call the audit service
        logger.info(f"AUDIT: {action} - User: {user_id} - Details: {details}")


class AuthorizationService(IAuthorizationService):
    """Authorization service implementation."""
    
    def __init__(self, config: AuthServiceConfig, storage: Optional[InMemoryUserStore] = None):
        self.config = config
        self.storage = storage or InMemoryUserStore()
        self.audit_service = None
        
        logger.info(f"Authorization service initialized with config: {config.service_name}")
    
    async def authorize_action(self, check: PermissionCheck) -> AuthorizationResult:
        """Check if a user is authorized to perform an action."""
        try:
            user = await self.storage.get_user(check.user_id)
            if not user:
                return AuthorizationResult(
                    authorized=False,
                    reason="User not found"
                )
            
            if user.status != UserStatus.ACTIVE:
                return AuthorizationResult(
                    authorized=False,
                    reason="User account is not active"
                )
            
            # Get user permissions
            user_permissions = await self.get_user_permissions(check.user_id)
            user_roles = await self.get_user_roles(check.user_id)
            
            # Check for admin role (has all permissions)
            if self.config.admin_role in [role.name for role in user_roles]:
                return AuthorizationResult(
                    authorized=True,
                    reason="User has admin role",
                    matched_permissions=["admin_access"],
                    user_roles=[role.name for role in user_roles]
                )
            
            # Check specific permissions
            matched_permissions = []
            for permission in user_permissions:
                if self._permission_matches(permission, check):
                    matched_permissions.append(permission.name)
            
            authorized = len(matched_permissions) > 0
            
            await self._log_audit_event("authorization_check", check.user_id, {
                "resource": check.resource,
                "action": check.action,
                "authorized": authorized,
                "matched_permissions": matched_permissions
            })
            
            return AuthorizationResult(
                authorized=authorized,
                reason="Permission granted" if authorized else "Permission denied",
                matched_permissions=matched_permissions,
                user_roles=[role.name for role in user_roles]
            )
            
        except Exception as e:
            logger.error(f"Authorization check failed: {e}")
            return AuthorizationResult(
                authorized=False,
                reason="Authorization check failed"
            )
    
    async def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user:
                return []
            
            permissions = []
            
            # Get permissions from all user roles
            for role_name in user.roles:
                role = await self.storage.get_role(role_name)
                if role:
                    for perm_name in role.permissions:
                        # Handle wildcard permissions (admin)
                        if perm_name == "*":
                            # Add all available permissions
                            permissions.extend(self.storage.permissions.values())
                            break
                        else:
                            permission = await self.storage.get_permission(perm_name)
                            if permission:
                                permissions.append(permission)
            
            # Remove duplicates
            unique_permissions = []
            seen_names = set()
            for perm in permissions:
                if perm.name not in seen_names:
                    unique_permissions.append(perm)
                    seen_names.add(perm.name)
            
            return unique_permissions
            
        except Exception as e:
            logger.error(f"Failed to get user permissions: {e}")
            return []
    
    async def get_user_roles(self, user_id: str) -> List[Role]:
        """Get all roles for a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user:
                return []
            
            roles = []
            for role_name in user.roles:
                role = await self.storage.get_role(role_name)
                if role:
                    roles.append(role)
            
            return roles
            
        except Exception as e:
            logger.error(f"Failed to get user roles: {e}")
            return []
    
    async def assign_role(self, user_id: str, role_name: str) -> OperationResult:
        """Assign a role to a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user:
                return OperationResult(
                    success=False,
                    message="User not found"
                )
            
            role = await self.storage.get_role(role_name)
            if not role:
                return OperationResult(
                    success=False,
                    message="Role not found"
                )
            
            if role_name in user.roles:
                return OperationResult(
                    success=False,
                    message="User already has this role"
                )
            
            user.roles.append(role_name)
            user.updated_at = datetime.now(timezone.utc)
            await self.storage.save_user(user)
            
            await self._log_audit_event("role_assigned", user_id, {
                "role": role_name,
                "username": user.username
            })
            
            return OperationResult(
                success=True,
                message=f"Role '{role_name}' assigned successfully"
            )
            
        except Exception as e:
            logger.error(f"Role assignment failed: {e}")
            return OperationResult(
                success=False,
                message="Role assignment failed"
            )
    
    async def revoke_role(self, user_id: str, role_name: str) -> OperationResult:
        """Revoke a role from a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user:
                return OperationResult(
                    success=False,
                    message="User not found"
                )
            
            if role_name not in user.roles:
                return OperationResult(
                    success=False,
                    message="User does not have this role"
                )
            
            user.roles.remove(role_name)
            user.updated_at = datetime.now(timezone.utc)
            await self.storage.save_user(user)
            
            await self._log_audit_event("role_revoked", user_id, {
                "role": role_name,
                "username": user.username
            })
            
            return OperationResult(
                success=True,
                message=f"Role '{role_name}' revoked successfully"
            )
            
        except Exception as e:
            logger.error(f"Role revocation failed: {e}")
            return OperationResult(
                success=False,
                message="Role revocation failed"
            )
    
    async def create_role(self, role: Role) -> OperationResult:
        """Create a new role."""
        try:
            existing_role = await self.storage.get_role(role.name)
            if existing_role:
                return OperationResult(
                    success=False,
                    message="Role already exists"
                )
            
            saved_role = await self.storage.save_role(role)
            
            await self._log_audit_event("role_created", None, {
                "role_name": role.name,
                "permissions": role.permissions
            })
            
            return OperationResult(
                success=True,
                message="Role created successfully",
                role=saved_role
            )
            
        except Exception as e:
            logger.error(f"Role creation failed: {e}")
            return OperationResult(
                success=False,
                message="Role creation failed"
            )
    
    async def create_permission(self, permission: Permission) -> OperationResult:
        """Create a new permission."""
        try:
            existing_permission = await self.storage.get_permission(permission.name)
            if existing_permission:
                return OperationResult(
                    success=False,
                    message="Permission already exists"
                )
            
            saved_permission = await self.storage.save_permission(permission)
            
            await self._log_audit_event("permission_created", None, {
                "permission_name": permission.name,
                "resource": permission.resource,
                "action": permission.action
            })
            
            return OperationResult(
                success=True,
                message="Permission created successfully",
                permission=saved_permission
            )
            
        except Exception as e:
            logger.error(f"Permission creation failed: {e}")
            return OperationResult(
                success=False,
                message="Permission creation failed"
            )
    
    async def check_resource_access(self, check: PermissionCheck) -> AuthorizationResult:
        """Check access to a specific resource."""
        # For resource-specific checks, we need to consider context
        user = await self.storage.get_user(check.user_id)
        if not user:
            return AuthorizationResult(
                authorized=False,
                reason="User not found"
            )
        
        # Check if user owns the resource (for owner_only permissions)
        if check.context and check.context.get("owner_id") == check.user_id:
            return AuthorizationResult(
                authorized=True,
                reason="User owns the resource",
                matched_permissions=["owner_access"]
            )
        
        # Fall back to regular authorization check
        return await self.authorize_action(check)
    
    async def get_security_context(self, user_id: str) -> Optional[SecurityContext]:
        """Get complete security context for a user."""
        try:
            user = await self.storage.get_user(user_id)
            if not user:
                return None
            
            permissions = await self.get_user_permissions(user_id)
            roles = await self.get_user_roles(user_id)
            
            return SecurityContext(
                user=user,
                permissions=permissions,
                roles=roles
            )
            
        except Exception as e:
            logger.error(f"Failed to get security context: {e}")
            return None
    
    def _permission_matches(self, permission: Permission, check: PermissionCheck) -> bool:
        """Check if a permission matches the requested action."""
        # Check resource match
        if permission.resource != "*" and permission.resource != check.resource:
            return False
        
        # Check action match
        if permission.action != "*" and permission.action != check.action:
            return False
        
        # Check permission effect (allow vs deny)
        if permission.effect != PermissionEffect.ALLOW:
            return False
        
        # Check conditions (if any)
        if permission.conditions:
            # Handle owner_only condition
            if permission.conditions.get("owner_only") and check.context:
                owner_id = check.context.get("owner_id")
                if owner_id and owner_id != check.user_id:
                    return False
        
        return True
    
    async def _log_audit_event(self, action: str, user_id: Optional[str], details: Dict[str, Any]):
        """Log audit event (mock implementation)."""
        # In a real implementation, this would call the audit service
        logger.info(f"AUDIT: {action} - User: {user_id} - Details: {details}")