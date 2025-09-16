"""
Job Aggregator Service - FastAPI HTTP endpoints.

Provides REST API for job aggregation operations including
multi-source collection, source status monitoring, and health checks.
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from .service import JobAggregatorService
from ..shared.contracts.job_aggregator_service import (
    SearchParams,
    AggregationResult,
    SourceStatus,
    ValidationError,
    JobAggregatorError,
    SourceUnavailableError,
    RateLimitError
)

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Job Aggregator Service",
    description="Multi-source job collection and aggregation service",
    version="1.0.0"
)

# Initialize service (will be configured in main.py)
job_aggregator_service: Optional[JobAggregatorService] = None


def get_service() -> JobAggregatorService:
    """Get the job aggregator service instance."""
    if job_aggregator_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    return job_aggregator_service


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        service = get_service()
        health_data = await service.health_check()
        return JSONResponse(content=health_data)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.post("/aggregate", response_model=Dict[str, Any])
async def aggregate_jobs(
    keywords: Optional[str] = Query(None, description="Job search keywords"),
    location: Optional[str] = Query(None, description="Job location"),
    remote_only: bool = Query(False, description="Filter for remote jobs only"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    company: Optional[str] = Query(None, description="Company filter"),
    max_age_days: int = Query(7, description="Maximum job age in days"),
    max_jobs_per_source: int = Query(50, description="Maximum jobs per source")
):
    """
    Aggregate jobs from all configured sources.
    
    Args:
        keywords: Job search keywords
        location: Job location
        remote_only: Filter for remote jobs only
        job_type: Job type filter (entry_level, mid_level, senior, management)
        company: Company filter
        max_age_days: Maximum job age in days
        max_jobs_per_source: Maximum jobs to collect per source
        
    Returns:
        AggregationResult with collected jobs and metadata
    """
    try:
        service = get_service()
        
        # Create search parameters
        search_params = SearchParams(
            keywords=keywords,
            location=location,
            remote_only=remote_only,
            job_type=job_type,
            company=company,
            max_age_days=max_age_days
        )
        
        # Perform aggregation
        result = await service.aggregate_jobs(search_params, max_jobs_per_source)
        
        # Return as dictionary
        return result.to_dict()
        
    except ValidationError as e:
        logger.error(f"Validation error in aggregate_jobs: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except JobAggregatorError as e:
        logger.error(f"Aggregation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in aggregate_jobs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/sources", response_model=List[Dict[str, Any]])
async def get_sources():
    """
    Get enabled sources by type.
    
    Returns:
        Dictionary mapping source types to source names
    """
    try:
        service = get_service()
        sources = service.get_enabled_sources()
        return sources
        
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sources")


@app.get("/sources/status", response_model=List[Dict[str, Any]])
async def get_source_statuses():
    """
    Get health status of all configured sources.
    
    Returns:
        List of source status information
    """
    try:
        service = get_service()
        statuses = await service.get_source_statuses()
        
        # Convert to dictionaries
        return [status.to_dict() for status in statuses]
        
    except Exception as e:
        logger.error(f"Error getting source statuses: {e}")
        raise HTTPException(status_code=500, detail="Failed to get source statuses")


@app.post("/aggregate/background")
async def aggregate_jobs_background(
    background_tasks: BackgroundTasks,
    keywords: Optional[str] = Query(None, description="Job search keywords"),
    location: Optional[str] = Query(None, description="Job location"),
    remote_only: bool = Query(False, description="Filter for remote jobs only"),
    job_type: Optional[str] = Query(None, description="Job type filter"),
    company: Optional[str] = Query(None, description="Company filter"),
    max_age_days: int = Query(7, description="Maximum job age in days"),
    max_jobs_per_source: int = Query(50, description="Maximum jobs per source")
):
    """
    Start job aggregation in the background.
    
    Args:
        background_tasks: FastAPI background tasks
        keywords: Job search keywords
        location: Job location
        remote_only: Filter for remote jobs only
        job_type: Job type filter
        company: Company filter
        max_age_days: Maximum job age in days
        max_jobs_per_source: Maximum jobs per source
        
    Returns:
        Task acceptance confirmation
    """
    try:
        service = get_service()
        
        # Create search parameters
        search_params = SearchParams(
            keywords=keywords,
            location=location,
            remote_only=remote_only,
            job_type=job_type,
            company=company,
            max_age_days=max_age_days
        )
        
        # Add background task
        background_tasks.add_task(
            _background_aggregation,
            service,
            search_params,
            max_jobs_per_source
        )
        
        return {
            "message": "Job aggregation started in background",
            "search_params": search_params.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
    except ValidationError as e:
        logger.error(f"Validation error in background aggregation: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting background aggregation: {e}")
        raise HTTPException(status_code=500, detail="Failed to start background aggregation")


async def _background_aggregation(
    service: JobAggregatorService,
    search_params: SearchParams,
    max_jobs_per_source: int
):
    """Execute job aggregation in background."""
    try:
        result = await service.aggregate_jobs(search_params, max_jobs_per_source)
        logger.info(f"Background aggregation completed: {result.total_deduplicated} jobs collected")
    except Exception as e:
        logger.error(f"Background aggregation failed: {e}")


@app.get("/stats")
async def get_aggregation_stats():
    """
    Get aggregation statistics.
    
    Returns:
        Aggregation statistics and metrics
    """
    try:
        service = get_service()
        
        # Get current source information
        sources = service.get_enabled_sources()
        statuses = await service.get_source_statuses()
        
        # Calculate stats
        total_sources = len(sources.get("api_aggregators", [])) + len(sources.get("browser_scrapers", []))
        healthy_sources = len([s for s in statuses if s.status.value == "healthy"])
        
        stats = {
            "total_sources": total_sources,
            "healthy_sources": healthy_sources,
            "unhealthy_sources": total_sources - healthy_sources,
            "api_aggregators": len(sources.get("api_aggregators", [])),
            "browser_scrapers": len(sources.get("browser_scrapers", [])),
            "last_update": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting aggregation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get aggregation stats")


# Error handlers
@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )


@app.exception_handler(SourceUnavailableError)
async def source_unavailable_handler(request, exc):
    """Handle source unavailable errors."""
    return JSONResponse(
        status_code=503,
        content={"error": "Source Unavailable", "detail": str(exc)}
    )


@app.exception_handler(RateLimitError)
async def rate_limit_handler(request, exc):
    """Handle rate limit errors."""
    return JSONResponse(
        status_code=429,
        content={"error": "Rate Limit Exceeded", "detail": str(exc)}
    )


@app.exception_handler(JobAggregatorError)
async def job_aggregator_error_handler(request, exc):
    """Handle general job aggregator errors."""
    return JSONResponse(
        status_code=500,
        content={"error": "Job Aggregator Error", "detail": str(exc)}
    )


# Function to set service instance (called from main.py)
def set_service(service: JobAggregatorService):
    """Set the job aggregator service instance."""
    global job_aggregator_service
    job_aggregator_service = service