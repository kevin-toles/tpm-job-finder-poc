"""
FastAPI endpoints for Authentication and Authorization Service

REST API implementation providing authentication and authorization endpoints
with OpenAPI documentation, security middleware, and error handling.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

from tpm_job_finder_poc.auth_service.config import AuthServiceConfig
from tpm_job_finder_poc.auth_service.service import AuthenticationService, AuthorizationService
from tpm_job_finder_poc.shared.contracts.auth_service import (
    LoginCredentials, AuthResult, PermissionCheck, AuthorizationResult,
    OperationResult, TokenValidationResult
)

logger = logging.getLogger(__name__)

# Pydantic models for API requests/responses
class RegisterRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str
    mfa_code: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    username: str
    old_password: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class PermissionCheckRequest(BaseModel):
    user_id: str
    resource: str
    action: str
    context: Optional[Dict[str, Any]] = None

class RoleAssignmentRequest(BaseModel):
    user_id: str
    role_name: str

# Create FastAPI app
app = FastAPI(
    title="Authentication & Authorization Service",
    description="Microservice providing authentication, authorization, and user management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global variables for services (will be initialized in create_app)
auth_service: Optional[AuthenticationService] = None
authz_service: Optional[AuthorizationService] = None

# Security scheme
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from token."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    token = credentials.credentials
    validation_result = await auth_service.validate_token(token)
    
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=validation_result.error_message or "Invalid token"
        )
    
    return validation_result.user

# Authentication endpoints
@app.post("/auth/register", response_model=Dict[str, Any])
async def register_user(request: RegisterRequest):
    """Register a new user."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    credentials = LoginCredentials(
        username=request.username,
        email=request.email,
        password=request.password
    )
    
    result = await auth_service.register_user(
        credentials,
        first_name=request.first_name,
        last_name=request.last_name
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error_message
        )
    
    return {
        "message": "User registered successfully",
        "user_id": result.user.id if result.user else None
    }

@app.post("/auth/login", response_model=TokenResponse)
async def login_user(request: LoginRequest):
    """Authenticate user and return tokens."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    credentials = LoginCredentials(
        username=request.username,
        email=request.email,
        password=request.password,
        mfa_code=request.mfa_code
    )
    
    result = await auth_service.authenticate_user(credentials)
    
    if not result.success:
        status_code = status.HTTP_401_UNAUTHORIZED
        if result.requires_mfa:
            status_code = status.HTTP_202_ACCEPTED
        
        raise HTTPException(
            status_code=status_code,
            detail=result.error_message
        )
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in
    )

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    result = await auth_service.refresh_token(request.refresh_token)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error_message
        )
    
    return TokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in
    )

@app.post("/auth/logout")
async def logout_user(current_user=Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout user by revoking token."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    token = credentials.credentials
    result = await auth_service.logout_user(token)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return {"message": "User logged out successfully"}

@app.post("/auth/change-password")
async def change_password(request: ChangePasswordRequest, current_user=Depends(get_current_user)):
    """Change user password."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    result = await auth_service.change_password(
        request.username,
        request.old_password,
        request.new_password
    )
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return {"message": "Password changed successfully"}

@app.get("/auth/validate")
async def validate_token(current_user=Depends(get_current_user)):
    """Validate current token and return user info."""
    return {
        "valid": True,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "roles": current_user.roles
        }
    }

# Authorization endpoints
@app.post("/authz/check", response_model=Dict[str, Any])
async def check_permission(request: PermissionCheckRequest):
    """Check if user has permission for specific action."""
    if not authz_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authorization service not available"
        )
    
    permission_check = PermissionCheck(
        user_id=request.user_id,
        resource=request.resource,
        action=request.action,
        context=request.context
    )
    
    result = await authz_service.authorize_action(permission_check)
    
    return {
        "authorized": result.authorized,
        "reason": result.reason,
        "matched_permissions": result.matched_permissions,
        "user_roles": result.user_roles
    }

@app.get("/authz/permissions/{user_id}")
async def get_user_permissions(user_id: str, current_user=Depends(get_current_user)):
    """Get all permissions for a user."""
    if not authz_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authorization service not available"
        )
    
    permissions = await authz_service.get_user_permissions(user_id)
    
    return {
        "user_id": user_id,
        "permissions": [
            {
                "name": perm.name,
                "resource": perm.resource,
                "action": perm.action,
                "description": perm.description
            }
            for perm in permissions
        ]
    }

@app.post("/authz/roles/assign")
async def assign_role(request: RoleAssignmentRequest, current_user=Depends(get_current_user)):
    """Assign role to user."""
    if not authz_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authorization service not available"
        )
    
    result = await authz_service.assign_role(request.user_id, request.role_name)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return {"message": result.message}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not auth_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    health_status = await auth_service.health_check()
    
    if health_status.get("status") != "healthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )
    
    return health_status

def create_app(config: AuthServiceConfig) -> FastAPI:
    """Create and configure FastAPI application."""
    global auth_service, authz_service
    
    # Create a new FastAPI app instance
    new_app = FastAPI(
        title="Authentication & Authorization Service",
        description="Microservice providing authentication, authorization, and user management",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Copy routes from the base app
    new_app.router = app.router
    
    # Initialize services
    auth_service = AuthenticationService(config)
    authz_service = AuthorizationService(config, auth_service.storage)
    
    # Configure CORS
    if config.security.cors_origins:
        new_app.add_middleware(
            CORSMiddleware,
            allow_origins=config.security.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Add authentication middleware
    auth_middleware = auth_service.create_auth_middleware()
    
    return new_app

# For testing purposes
if __name__ == "__main__":
    import uvicorn
    from tpm_job_finder_poc.auth_service.config import AuthServiceConfig
    
    config = AuthServiceConfig.for_testing()
    app = create_app(config)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)