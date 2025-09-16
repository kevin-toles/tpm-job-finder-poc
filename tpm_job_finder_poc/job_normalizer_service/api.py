"""REST API for Job Normalizer Service.

This module implements the FastAPI REST endpoints for the Job Normalizer Service,
providing HTTP access to all service functionality.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

from tpm_job_finder_poc.job_normalizer_service.service import JobNormalizerService
from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig
from tpm_job_finder_poc.shared.contracts.job_normalizer_service import (
    JobNormalizationConfig,
    NormalizationResult,
    NormalizationStatistics,
    ServiceNotStartedError,
    NormalizationError,
    ServiceError
)

logger = logging.getLogger(__name__)

# Global service instance
_service: Optional[JobNormalizerService] = None


# Request/Response Models
class NormalizeJobsRequest(BaseModel):
    """Request model for normalize-jobs endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    jobs: List[Dict[str, Any]] = Field(
        description="List of raw job dictionaries to normalize"
    )
    source: str = Field(
        description="Source identifier for the jobs (e.g., 'indeed', 'linkedin')"
    )
    config: Optional[JobNormalizationConfig] = Field(
        default=None,
        description="Optional operation-specific configuration"
    )


class ValidateJobRequest(BaseModel):
    """Request model for validate-job endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    job: Dict[str, Any] = Field(
        description="Raw job dictionary to validate"
    )
    source: str = Field(
        description="Source identifier for the job"
    )


class ValidateJobResponse(BaseModel):
    """Response model for validate-job endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    is_valid: bool = Field(
        description="Whether the job is valid"
    )
    validation_errors: List[str] = Field(
        default_factory=list,
        description="List of validation error messages if job is invalid"
    )


class ServiceStatusResponse(BaseModel):
    """Response model for service status endpoints."""
    model_config = ConfigDict(extra='forbid')
    
    message: str = Field(
        description="Status message"
    )
    is_running: bool = Field(
        description="Whether the service is currently running"
    )


class ResetStatisticsResponse(BaseModel):
    """Response model for reset statistics endpoint."""
    model_config = ConfigDict(extra='forbid')
    
    message: str = Field(
        default="Statistics reset successfully",
        description="Confirmation message"
    )


# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    global _service
    
    # Startup
    try:
        config = JobNormalizerServiceConfig()
        _service = JobNormalizerService(config)
        await _service.start()
        logger.info("JobNormalizerService started successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to start JobNormalizerService: {e}")
        raise
    finally:
        # Shutdown
        if _service and _service.is_running():
            await _service.stop()
            logger.info("JobNormalizerService stopped successfully")


# FastAPI app configuration
app = FastAPI(
    title="Job Normalizer Service",
    description="Microservice for normalizing, validating, and deduplicating job postings",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# Dependency to get service instance
def get_service() -> JobNormalizerService:
    """Get the current service instance.
    
    Returns:
        JobNormalizerService instance
        
    Raises:
        HTTPException: If service is not available
    """
    if _service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service not available"
        )
    return _service


# Health check endpoint
@app.get("/health", response_model=Dict[str, Any])
async def health_check(service: JobNormalizerService = Depends(get_service)):
    """Get service health status.
    
    Returns:
        Health status information including uptime, operation count, and error rates
    """
    try:
        health_status = await service.get_health_status()
        
        if health_status.get("status") == "healthy":
            return health_status
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health_status
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "is_running": False,
                "error": str(e)
            }
        )


# Job normalization endpoint
@app.post("/normalize-jobs", response_model=NormalizationResult)
async def normalize_jobs(
    request: NormalizeJobsRequest,
    service: JobNormalizerService = Depends(get_service)
):
    """Normalize a batch of job postings.
    
    Args:
        request: Request containing jobs, source, and optional configuration
        
    Returns:
        NormalizationResult with processing details and normalized jobs
        
    Raises:
        HTTPException: For various error conditions
    """
    try:
        result = await service.normalize_jobs(
            raw_jobs=request.jobs,
            source=request.source,
            config=request.config
        )
        return result
        
    except ServiceNotStartedError as e:
        logger.error(f"Service not started error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
        
    except NormalizationError as e:
        logger.error(f"Normalization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during normalization: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal service error: {str(e)}"
        )


# Job validation endpoint
@app.post("/validate-job", response_model=ValidateJobResponse)
async def validate_job(
    request: ValidateJobRequest,
    service: JobNormalizerService = Depends(get_service)
):
    """Validate a single job posting.
    
    Args:
        request: Request containing job data and source
        
    Returns:
        ValidateJobResponse indicating if job is valid
        
    Raises:
        HTTPException: For service errors
    """
    try:
        is_valid = await service.validate_job(
            raw_job=request.job,
            source=request.source
        )
        
        response = ValidateJobResponse(
            is_valid=is_valid,
            validation_errors=[] if is_valid else ["Job validation failed"]
        )
        
        return response
        
    except ServiceNotStartedError as e:
        logger.error(f"Service not started error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal service error: {str(e)}"
        )


# Statistics endpoints
@app.get("/statistics", response_model=NormalizationStatistics)
async def get_statistics(service: JobNormalizerService = Depends(get_service)):
    """Get current processing statistics.
    
    Returns:
        NormalizationStatistics with current processing metrics
        
    Raises:
        HTTPException: For service errors
    """
    try:
        statistics = await service.get_statistics()
        return statistics
        
    except ServiceNotStartedError as e:
        logger.error(f"Service not started error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Unexpected error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal service error: {str(e)}"
        )


@app.post("/statistics/reset", response_model=ResetStatisticsResponse)
async def reset_statistics(service: JobNormalizerService = Depends(get_service)):
    """Reset all processing statistics.
    
    Returns:
        Confirmation message
        
    Raises:
        HTTPException: For service errors
    """
    try:
        await service.reset_statistics()
        return ResetStatisticsResponse()
        
    except ServiceNotStartedError as e:
        logger.error(f"Service not started error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
        
    except Exception as e:
        logger.error(f"Unexpected error resetting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal service error: {str(e)}"
        )


# Service management endpoints
@app.post("/service/start", response_model=ServiceStatusResponse)
async def start_service(service: JobNormalizerService = Depends(get_service)):
    """Start the service (if not already running).
    
    Returns:
        Service status response
        
    Raises:
        HTTPException: For service errors
    """
    try:
        await service.start()
        return ServiceStatusResponse(
            message="Service started successfully",
            is_running=service.is_running()
        )
        
    except Exception as e:
        logger.error(f"Error starting service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start service: {str(e)}"
        )


@app.post("/service/stop", response_model=ServiceStatusResponse)
async def stop_service(service: JobNormalizerService = Depends(get_service)):
    """Stop the service.
    
    Returns:
        Service status response
        
    Raises:
        HTTPException: For service errors
    """
    try:
        await service.stop()
        return ServiceStatusResponse(
            message="Service stopped successfully",
            is_running=service.is_running()
        )
        
    except Exception as e:
        logger.error(f"Error stopping service: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop service: {str(e)}"
        )


# Error handlers
@app.exception_handler(ServiceNotStartedError)
async def service_not_started_handler(request, exc):
    """Handle ServiceNotStartedError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)}
    )


@app.exception_handler(NormalizationError)
async def normalization_error_handler(request, exc):
    """Handle NormalizationError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(ServiceError)
async def service_error_handler(request, exc):
    """Handle ServiceError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Job Normalizer Service",
        "version": "1.0.0",
        "description": "Microservice for normalizing, validating, and deduplicating job postings",
        "docs": "/docs",
        "health": "/health"
    }