"""
Authentication Service Configuration

Configuration models for the authentication and authorization microservice
with validation, security settings, and environment-specific overrides.
"""

from datetime import timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator, SecretStr, ConfigDict
from pathlib import Path
import os


class DatabaseConfig(BaseModel):
    """Database configuration for user storage."""
    
    # Database connection
    url: str = Field(
        default="sqlite:///./auth_service.db",
        description="Database connection URL"
    )
    echo: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )
    pool_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Database connection pool size"
    )
    max_overflow: int = Field(
        default=20,
        ge=0,
        le=100,
        description="Maximum connection pool overflow"
    )
    pool_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Database connection timeout in seconds"
    )


class JWTConfig(BaseModel):
    """JWT token configuration."""
    
    # JWT signing
    secret_key: SecretStr = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token signing (min 32 chars)"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    issuer: str = Field(
        default="tpm-job-finder-auth",
        description="JWT token issuer"
    )
    
    # Token expiration
    access_token_expire_minutes: int = Field(
        default=30,
        ge=5,
        le=1440,  # 24 hours max
        description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        ge=1,
        le=30,  # 30 days max
        description="Refresh token expiration in days"
    )
    reset_token_expire_minutes: int = Field(
        default=15,
        ge=5,
        le=60,
        description="Password reset token expiration in minutes"
    )
    verification_token_expire_hours: int = Field(
        default=24,
        ge=1,
        le=168,  # 7 days max
        description="Email verification token expiration in hours"
    )
    
    @field_validator('algorithm')
    @classmethod
    def validate_algorithm(cls, v):
        """Validate JWT algorithm."""
        allowed_algorithms = ['HS256', 'HS384', 'HS512', 'RS256', 'RS384', 'RS512']
        if v not in allowed_algorithms:
            raise ValueError(f"Algorithm must be one of: {allowed_algorithms}")
        return v


class PasswordConfig(BaseModel):
    """Password policy configuration."""
    
    # Password requirements
    min_length: int = Field(
        default=8,
        ge=6,
        le=128,
        description="Minimum password length"
    )
    max_length: int = Field(
        default=128,
        ge=8,
        le=512,
        description="Maximum password length"
    )
    require_uppercase: bool = Field(
        default=True,
        description="Require at least one uppercase letter"
    )
    require_lowercase: bool = Field(
        default=True,
        description="Require at least one lowercase letter"
    )
    require_numbers: bool = Field(
        default=True,
        description="Require at least one number"
    )
    require_special_chars: bool = Field(
        default=True,
        description="Require at least one special character"
    )
    special_chars: str = Field(
        default="!@#$%^&*()_+-=[]{}|;:,.<>?",
        description="Allowed special characters"
    )
    
    # Password history
    history_count: int = Field(
        default=5,
        ge=0,
        le=24,
        description="Number of previous passwords to remember (0 to disable)"
    )
    
    # Hashing
    bcrypt_rounds: int = Field(
        default=12,
        ge=4,  # Allow lower for testing
        le=15,
        description="BCrypt hashing rounds (higher = more secure but slower)"
    )
    
    @field_validator('max_length')
    @classmethod
    def validate_max_length(cls, v, info):
        """Ensure max_length >= min_length."""
        if info.data and 'min_length' in info.data and v < info.data['min_length']:
            raise ValueError("max_length must be >= min_length")
        return v


class SecurityConfig(BaseModel):
    """Security and rate limiting configuration."""
    
    # Account lockout
    max_login_attempts: int = Field(
        default=5,
        ge=3,
        le=20,
        description="Maximum failed login attempts before lockout"
    )
    account_lockout_duration_minutes: int = Field(
        default=15,
        ge=1,
        le=1440,  # 24 hours max
        description="Account lockout duration in minutes"
    )
    progressive_lockout: bool = Field(
        default=True,
        description="Enable progressive lockout (longer lockouts for repeated failures)"
    )
    
    # Rate limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_requests_per_minute: int = Field(
        default=60,
        ge=10,
        le=1000,
        description="Maximum requests per minute per IP"
    )
    rate_limit_login_per_minute: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Maximum login attempts per minute per IP"
    )
    
    # Session security
    secure_cookies: bool = Field(
        default=True,
        description="Use secure cookies (HTTPS only)"
    )
    same_site_cookies: str = Field(
        default="lax",
        description="SameSite cookie policy"
    )
    session_timeout_minutes: int = Field(
        default=480,  # 8 hours
        ge=30,
        le=1440,  # 24 hours max
        description="Session timeout in minutes"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(
        default=True,
        description="Allow CORS credentials"
    )
    
    @field_validator('same_site_cookies')
    @classmethod
    def validate_same_site(cls, v):
        """Validate SameSite cookie policy."""
        allowed_values = ['strict', 'lax', 'none']
        if v.lower() not in allowed_values:
            raise ValueError(f"same_site_cookies must be one of: {allowed_values}")
        return v.lower()


class MFAConfig(BaseModel):
    """Multi-factor authentication configuration."""
    
    # MFA settings
    enable_mfa: bool = Field(
        default=False,
        description="Enable multi-factor authentication"
    )
    mfa_required_for_admin: bool = Field(
        default=True,
        description="Require MFA for admin users"
    )
    totp_issuer: str = Field(
        default="TPM Job Finder",
        description="TOTP issuer name"
    )
    totp_period: int = Field(
        default=30,
        ge=15,
        le=300,
        description="TOTP time period in seconds"
    )
    totp_digits: int = Field(
        default=6,
        ge=6,
        le=8,
        description="Number of TOTP digits"
    )
    
    # Backup codes
    backup_codes_count: int = Field(
        default=10,
        ge=5,
        le=20,
        description="Number of backup codes to generate"
    )


class AuditConfig(BaseModel):
    """Audit logging configuration."""
    
    # Audit settings
    enable_audit_logging: bool = Field(
        default=True,
        description="Enable audit event logging"
    )
    audit_service_url: Optional[str] = Field(
        default=None,
        description="URL of the audit service (if external)"
    )
    log_successful_logins: bool = Field(
        default=True,
        description="Log successful login events"
    )
    log_failed_logins: bool = Field(
        default=True,
        description="Log failed login events"
    )
    log_password_changes: bool = Field(
        default=True,
        description="Log password change events"
    )
    log_permission_changes: bool = Field(
        default=True,
        description="Log permission and role changes"
    )
    log_token_operations: bool = Field(
        default=False,
        description="Log token creation and validation (can be noisy)"
    )


class EmailConfig(BaseModel):
    """Email configuration for notifications."""
    
    # SMTP settings
    smtp_host: str = Field(
        default="localhost",
        description="SMTP server host"
    )
    smtp_port: int = Field(
        default=587,
        ge=1,
        le=65535,
        description="SMTP server port"
    )
    smtp_use_tls: bool = Field(
        default=True,
        description="Use TLS for SMTP connection"
    )
    smtp_username: Optional[str] = Field(
        default=None,
        description="SMTP username"
    )
    smtp_password: Optional[SecretStr] = Field(
        default=None,
        description="SMTP password"
    )
    
    # Email settings
    from_email: str = Field(
        default="auth@tpm-job-finder.com",
        description="From email address"
    )
    from_name: str = Field(
        default="TPM Job Finder Authentication",
        description="From name for emails"
    )
    
    # Email templates
    welcome_email_enabled: bool = Field(
        default=True,
        description="Send welcome email on registration"
    )
    password_reset_email_enabled: bool = Field(
        default=True,
        description="Send password reset emails"
    )
    verification_email_enabled: bool = Field(
        default=True,
        description="Send email verification emails"
    )


class AuthServiceConfig(BaseModel):
    """Main configuration for the authentication service."""
    
    # Service settings
    service_name: str = Field(
        default="auth_service",
        description="Name of the service"
    )
    service_version: str = Field(
        default="1.0.0",
        description="Version of the service"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    testing: bool = Field(
        default=False,
        description="Enable testing mode"
    )
    
    # Component configurations
    database: DatabaseConfig = Field(
        default_factory=DatabaseConfig,
        description="Database configuration"
    )
    jwt: JWTConfig = Field(
        ...,
        description="JWT configuration"
    )
    password: PasswordConfig = Field(
        default_factory=PasswordConfig,
        description="Password policy configuration"
    )
    security: SecurityConfig = Field(
        default_factory=SecurityConfig,
        description="Security configuration"
    )
    mfa: MFAConfig = Field(
        default_factory=MFAConfig,
        description="Multi-factor authentication configuration"
    )
    audit: AuditConfig = Field(
        default_factory=AuditConfig,
        description="Audit logging configuration"
    )
    email: EmailConfig = Field(
        default_factory=EmailConfig,
        description="Email configuration"
    )
    
    # Feature flags
    enable_rbac: bool = Field(
        default=True,
        description="Enable role-based access control"
    )
    enable_resource_permissions: bool = Field(
        default=True,
        description="Enable resource-level permissions"
    )
    enable_user_registration: bool = Field(
        default=True,
        description="Allow user self-registration"
    )
    enable_password_reset: bool = Field(
        default=True,
        description="Enable password reset functionality"
    )
    enable_email_verification: bool = Field(
        default=True,
        description="Require email verification for new accounts"
    )
    
    # Default roles
    default_user_role: str = Field(
        default="user",
        description="Default role for new users"
    )
    admin_role: str = Field(
        default="admin",
        description="Admin role name"
    )
    
    # Cache settings
    enable_caching: bool = Field(
        default=True,
        description="Enable permission and role caching"
    )
    cache_ttl_seconds: int = Field(
        default=300,  # 5 minutes
        ge=60,
        le=3600,  # 1 hour max
        description="Cache TTL in seconds"
    )
    
    model_config = ConfigDict(
        env_prefix="AUTH_",
        case_sensitive=False,
        validate_assignment=True
    )
        
    @classmethod
    def from_env(cls) -> 'AuthServiceConfig':
        """Create configuration from environment variables."""
        # Load JWT secret from environment
        jwt_secret = os.getenv('AUTH_JWT_SECRET_KEY')
        if not jwt_secret:
            # Generate a random secret for development (NOT for production)
            import secrets
            jwt_secret = secrets.token_urlsafe(32)
            if not os.getenv('AUTH_TESTING'):
                print("WARNING: No JWT secret key found. Generated temporary key. Set AUTH_JWT_SECRET_KEY in production!")
        
        return cls(
            jwt=JWTConfig(secret_key=jwt_secret),
            debug=os.getenv('AUTH_DEBUG', 'false').lower() == 'true',
            testing=os.getenv('AUTH_TESTING', 'false').lower() == 'true'
        )
    
    @classmethod
    def for_testing(cls) -> 'AuthServiceConfig':
        """Create configuration optimized for testing."""
        return cls(
            jwt=JWTConfig(
                secret_key="test-secret-key-for-testing-only-do-not-use-in-production",
                access_token_expire_minutes=5,  # Short expiration for testing
                refresh_token_expire_days=1
            ),
            database=DatabaseConfig(
                url="sqlite:///:memory:",  # In-memory database for testing
                echo=False
            ),
            password=PasswordConfig(
                bcrypt_rounds=4,  # Faster hashing for tests
                history_count=2   # Shorter history for tests
            ),
            security=SecurityConfig(
                max_login_attempts=3,
                account_lockout_duration_minutes=1,  # Short lockout for tests
                rate_limit_enabled=False  # Disable rate limiting in tests
            ),
            audit=AuditConfig(
                enable_audit_logging=False  # Disable audit for unit tests
            ),
            email=EmailConfig(
                welcome_email_enabled=False,  # Disable emails in tests
                password_reset_email_enabled=False,
                verification_email_enabled=False
            ),
            debug=True,
            testing=True,
            enable_email_verification=False  # Skip email verification in tests
        )
    
    def get_database_url(self) -> str:
        """Get the database URL with any environment overrides."""
        env_url = os.getenv('AUTH_DATABASE_URL')
        return env_url if env_url else self.database.url
    
    def get_jwt_secret(self) -> str:
        """Get JWT secret key as plain string."""
        return self.jwt.secret_key.get_secret_value()
    
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug and not self.testing
    
    def get_token_expiry_timedelta(self, token_type: str = "access") -> timedelta:
        """Get token expiry as timedelta object."""
        if token_type == "access":
            return timedelta(minutes=self.jwt.access_token_expire_minutes)
        elif token_type == "refresh":
            return timedelta(days=self.jwt.refresh_token_expire_days)
        elif token_type == "reset":
            return timedelta(minutes=self.jwt.reset_token_expire_minutes)
        elif token_type == "verification":
            return timedelta(hours=self.jwt.verification_token_expire_hours)
        else:
            raise ValueError(f"Unknown token type: {token_type}")


# Helper functions for configuration loading
def load_config_from_file(config_path: Path) -> AuthServiceConfig:
    """Load configuration from a YAML or JSON file."""
    import yaml
    import json
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            data = yaml.safe_load(f)
        elif config_path.suffix.lower() == '.json':
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")
    
    return AuthServiceConfig(**data)


def create_development_config() -> AuthServiceConfig:
    """Create configuration suitable for development."""
    return AuthServiceConfig(
        jwt=JWTConfig(
            secret_key="development-secret-key-not-for-production-use",
            access_token_expire_minutes=60  # Longer expiration for development
        ),
        database=DatabaseConfig(
            url="sqlite:///./dev_auth_service.db",
            echo=True  # Show SQL queries in development
        ),
        security=SecurityConfig(
            rate_limit_enabled=False,  # Disable rate limiting for development
            secure_cookies=False,      # Allow HTTP cookies in development
            cors_origins=["*"]         # Allow all origins in development
        ),
        debug=True,
        testing=False
    )


def create_production_config() -> AuthServiceConfig:
    """Create configuration template for production (requires environment variables)."""
    return AuthServiceConfig.from_env()