"""
LLM Provider Service TDD REST API

FastAPI REST endpoints for the LLM Provider Service microservice,
providing HTTP access to all TDD-implemented functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

from .service import LLMProviderService
from ..shared.contracts.llm_provider_service_tdd import (
    LLMRequest,
    LLMResponse,
    LLMProviderConfig,
    ProviderType,
    ProviderInfo,
    ProviderHealth,
    LLMServiceStatistics,
    # Exception Classes
    LLMProviderError,
    ServiceNotStartedError,
    ProviderNotFoundError,
    ProviderUnavailableError,
    RateLimitExceededError,
    InvalidRequestError,
    ModelNotFoundError,
    LLMTimeoutError,
    ConfigurationError,
    AuthenticationError,
)

logger = logging.getLogger(__name__)

# Global service instance
_service: Optional[LLMProviderService] = None


# Request/Response Models
class ProcessBatchRequest(BaseModel):
    """Request model for batch processing endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    requests: List[LLMRequest] = Field(
        description="List of LLM requests to process"
    )


class UsageReportRequest(BaseModel):
    """Request model for usage report endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    start_date: Optional[datetime] = Field(
        default=None,
        description="Start date for report period"
    )
    end_date: Optional[datetime] = Field(
        default=None,
        description="End date for report period"
    )
    provider: Optional[ProviderType] = Field(
        default=None,
        description="Filter by specific provider"
    )


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    status: str = Field(description="Overall health status")
    service_status: str = Field(description="Service operational status")
    uptime_seconds: float = Field(description="Service uptime in seconds")
    enabled_providers: int = Field(description="Number of enabled providers")
    memory_usage: Optional[Dict[str, float]] = Field(
        default=None,
        description="Memory usage information"
    )
    resources: Optional[Dict[str, float]] = Field(
        default=None,
        description="Resource utilization"
    )
    providers: List[Dict[str, Any]] = Field(
        description="Individual provider health status"
    )


# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage service lifecycle"""
    global _service
    
    # Startup
    try:
        # Initialize with default configuration
        # In production, this would load from environment/config files
        config = LLMProviderConfig(
            openai_config={"api_key": "mock", "models": ["gpt-4", "gpt-3.5-turbo"]},
            enable_fallback=True,
            enable_cost_tracking=True,
            enable_usage_analytics=True
        )
        
        _service = LLMProviderService(config)
        await _service.start()
        logger.info("LLM Provider Service started successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to start LLM Provider Service: {e}")
        raise
    finally:
        # Shutdown
        if _service:
            try:
                await _service.stop()
                logger.info("LLM Provider Service stopped gracefully")
            except Exception as e:
                logger.error(f"Error during service shutdown: {e}")


# Initialize FastAPI app
app = FastAPI(
    title="LLM Provider Service TDD",
    description="Test-Driven Development implementation of LLM Provider microservice",
    version="1.0.0",
    lifespan=lifespan
)


# Dependency injection
async def get_service() -> LLMProviderService:
    """Get the service instance"""
    if _service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not available"
        )
    return _service


# Exception handlers
@app.exception_handler(LLMProviderError)
async def llm_provider_error_handler(request, exc: LLMProviderError):
    """Handle LLM provider specific errors"""
    error_mappings = {
        ServiceNotStartedError: (status.HTTP_503_SERVICE_UNAVAILABLE, "Service not started"),
        ProviderNotFoundError: (status.HTTP_404_NOT_FOUND, "Provider not found"),
        ProviderUnavailableError: (status.HTTP_503_SERVICE_UNAVAILABLE, "Provider unavailable"),
        RateLimitExceededError: (status.HTTP_429_TOO_MANY_REQUESTS, "Rate limit exceeded"),
        InvalidRequestError: (status.HTTP_400_BAD_REQUEST, "Invalid request"),
        ModelNotFoundError: (status.HTTP_404_NOT_FOUND, "Model not found"),
        LLMTimeoutError: (status.HTTP_408_REQUEST_TIMEOUT, "Request timeout"),
        ConfigurationError: (status.HTTP_400_BAD_REQUEST, "Configuration error"),
        AuthenticationError: (status.HTTP_401_UNAUTHORIZED, "Authentication failed"),
    }
    
    status_code, default_detail = error_mappings.get(
        type(exc), 
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal server error")
    )
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": str(exc) if str(exc) else default_detail,
            "error_type": type(exc).__name__
        }
    )


# Health and Status Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check(service: LLMProviderService = Depends(get_service)):
    """Get service health status"""
    try:
        health_data = await service.get_health()
        return HealthResponse(**health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )


@app.get("/status")
async def get_service_status(service: LLMProviderService = Depends(get_service)):
    """Get basic service status"""
    return {
        "status": "running" if service.is_running() else "stopped",
        "timestamp": datetime.utcnow().isoformat()
    }


# Core LLM Processing Endpoints
@app.post("/process", response_model=LLMResponse)
async def process_request(
    request: LLMRequest,
    service: LLMProviderService = Depends(get_service)
):
    """Process a single LLM request"""
    try:
        return await service.process_request(request)
    except LLMProviderError:
        # Re-raise to be handled by exception handler
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing LLM request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.post("/process/batch", response_model=List[LLMResponse])
async def process_batch(
    batch_request: ProcessBatchRequest,
    service: LLMProviderService = Depends(get_service)
):
    """Process multiple LLM requests"""
    try:
        return await service.process_batch(batch_request.requests)
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing batch request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Provider Management Endpoints
@app.get("/providers", response_model=List[ProviderInfo])
async def list_providers(service: LLMProviderService = Depends(get_service)):
    """Get list of available providers"""
    try:
        return await service.list_providers()
    except Exception as e:
        logger.error(f"Error getting providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving providers"
        )


@app.get("/providers/{provider_type}", response_model=ProviderInfo)
async def get_provider_info(
    provider_type: ProviderType,
    service: LLMProviderService = Depends(get_service)
):
    """Get information about a specific provider"""
    try:
        return await service.get_provider_info(provider_type)
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Error getting provider info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving provider information"
        )


@app.post("/providers/{provider_type}/enable")
async def enable_provider(
    provider_type: ProviderType,
    service: LLMProviderService = Depends(get_service)
):
    """Enable a provider"""
    try:
        result = await service.enable_provider(provider_type)
        return {
            "message": f"Provider {provider_type.value} enabled successfully",
            "success": result
        }
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Error enabling provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error enabling provider"
        )


@app.post("/providers/{provider_type}/disable")
async def disable_provider(
    provider_type: ProviderType,
    service: LLMProviderService = Depends(get_service)
):
    """Disable a provider"""
    try:
        result = await service.disable_provider(provider_type)
        return {
            "message": f"Provider {provider_type.value} disabled successfully",
            "success": result
        }
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Error disabling provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error disabling provider"
        )


@app.get("/providers/{provider_type}/health", response_model=ProviderHealth)
async def get_provider_health(
    provider_type: ProviderType,
    service: LLMProviderService = Depends(get_service)
):
    """Get health status of a specific provider"""
    try:
        return await service.get_provider_health(provider_type)
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Error getting provider health: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving provider health"
        )


@app.post("/providers/{provider_type}/test")
async def test_provider(
    provider_type: ProviderType,
    service: LLMProviderService = Depends(get_service)
):
    """Test connectivity and health of a specific provider"""
    try:
        health = await service.test_provider(provider_type)
        return {
            "provider": provider_type.value,
            "status": "healthy" if health.status == "healthy" else "unhealthy",
            "health": health.dict()
        }
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Error testing provider: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error testing provider"
        )


# Statistics and Monitoring Endpoints
@app.get("/statistics", response_model=LLMServiceStatistics)
async def get_statistics(service: LLMProviderService = Depends(get_service)):
    """Get service usage statistics"""
    try:
        return await service.get_statistics()
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving statistics"
        )


@app.post("/statistics/reset")
async def reset_statistics(service: LLMProviderService = Depends(get_service)):
    """Reset service statistics"""
    try:
        await service.reset_statistics()
        return {"message": "Statistics reset successfully"}
    except Exception as e:
        logger.error(f"Error resetting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error resetting statistics"
        )


@app.post("/reports/usage")
async def get_usage_report(
    report_request: UsageReportRequest,
    service: LLMProviderService = Depends(get_service)
):
    """Generate usage report for specified period"""
    try:
        report = await service.get_usage_report(
            start_date=report_request.start_date,
            end_date=report_request.end_date,
            provider=report_request.provider
        )
        return report
    except Exception as e:
        logger.error(f"Error generating usage report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating usage report"
        )


# Configuration Management Endpoints
@app.get("/config", response_model=LLMProviderConfig)
async def get_configuration(service: LLMProviderService = Depends(get_service)):
    """Get current service configuration"""
    try:
        return await service.get_configuration()
    except Exception as e:
        logger.error(f"Error getting configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving configuration"
        )


@app.put("/config")
async def update_configuration(
    config: LLMProviderConfig,
    service: LLMProviderService = Depends(get_service)
):
    """Update service configuration"""
    try:
        result = await service.update_configuration(config)
        return {
            "message": "Configuration updated successfully" if result else "Configuration update failed",
            "success": result
        }
    except LLMProviderError:
        raise
    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating configuration"
        )


# OpenAPI documentation customization
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)