"""
LLM Provider Service FastAPI Application
HTTP API endpoints for LLM provider management and request processing
"""

from fastapi import FastAPI, HTTPException, status
from typing import List, Dict, Any
import logging

from .service import LLMProviderService
from ..shared.contracts.llm_provider_service import (
    LLMRequest, 
    LLMResponse, 
    ProviderInfo,
    ProviderType,
    LLMProviderError,
    ProviderUnavailableError,
    InvalidRequestError,
    RateLimitExceededError
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LLM Provider Service",
    description="Microservice for LLM provider management and request processing",
    version="1.0.0"
)

# Initialize service
llm_service = LLMProviderService()


@app.exception_handler(LLMProviderError)
async def llm_provider_error_handler(request, exc: LLMProviderError):
    """Handle LLM provider specific errors"""
    if isinstance(exc, ProviderUnavailableError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        )
    elif isinstance(exc, InvalidRequestError):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )
    elif isinstance(exc, RateLimitExceededError):
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc)
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal LLM provider error"
        )


@app.post("/llm/signals", response_model=LLMResponse)
async def get_signals(request: LLMRequest) -> LLMResponse:
    """Get structured signals from LLM provider"""
    try:
        result = await llm_service.get_signals(request)
        return result
    except LLMProviderError as e:
        # Re-raise to be handled by exception handler
        raise e
    except Exception as e:
        logger.error(f"Unexpected error processing LLM request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/providers", response_model=List[ProviderInfo])
async def get_providers() -> List[ProviderInfo]:
    """Get list of available providers"""
    try:
        return await llm_service.get_providers()
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving providers"
        )


@app.post("/providers", status_code=status.HTTP_201_CREATED)
async def add_provider(provider: ProviderInfo) -> Dict[str, Any]:
    """Add new provider"""
    try:
        success = await llm_service.add_provider(provider)
        if success:
            return {"message": f"Provider '{provider.name}' added successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add provider"
            )
    except Exception as e:
        logger.error(f"Error adding provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding provider"
        )


@app.delete("/providers/{provider_type}")
async def remove_provider(provider_type: ProviderType) -> Dict[str, Any]:
    """Remove provider"""
    try:
        success = await llm_service.remove_provider(provider_type)
        if success:
            return {"message": f"Provider '{provider_type.value}' removed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider '{provider_type.value}' not found"
            )
    except Exception as e:
        logger.error(f"Error removing provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing provider"
        )


@app.get("/providers/{provider_type}", response_model=ProviderInfo)
async def get_provider_status(provider_type: ProviderType) -> ProviderInfo:
    """Get status of specific provider"""
    try:
        provider = await llm_service.get_provider_status(provider_type)
        return provider
    except ProviderUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_type.value}' not found"
        )
    except Exception as e:
        logger.error(f"Error getting provider status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving provider status"
        )


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        health_status = await llm_service.health_check()
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.post("/admin/reset-rate-limits")
async def reset_rate_limits() -> Dict[str, Any]:
    """Reset rate limits for all providers"""
    try:
        success = await llm_service.reset_rate_limits()
        if success:
            return {"message": "Rate limits reset successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reset rate limits"
            )
    except Exception as e:
        logger.error(f"Error resetting rate limits: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error resetting rate limits"
        )