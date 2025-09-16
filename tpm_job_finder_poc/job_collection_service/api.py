"""
Job Collection Service - REST API endpoints.

Provides HTTP API for job collection operations.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import asdict
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

from .service import JobCollectionService
from .config import JobCollectionConfig
from ..shared.contracts.job_collection_service import (
    JobPosting, 
    JobQuery, 
    CollectionResult,
    SourceStatus,
    JobCollectionError,
    SourceNotFoundError,
    ValidationError
)

logger = logging.getLogger(__name__)


# Request/Response models
class CollectJobsRequest(BaseModel):
    """Request model for job collection."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "Technical Project Manager",
                "sources": ["remoteok", "greenhouse"],
                "max_jobs": 100,
                "location": "San Francisco",
                "remote_only": True
            }
        }
    )
    
    query: str = Field(..., description="Job search query")
    sources: Optional[List[str]] = Field(None, description="Specific sources to search")
    max_jobs: Optional[int] = Field(None, description="Maximum number of jobs to collect")
    location: Optional[str] = Field(None, description="Job location filter")
    remote_only: Optional[bool] = Field(None, description="Filter for remote jobs only")


class CollectionResponse(BaseModel):
    """Response model for job collection."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Successfully collected 45 jobs",
                "total_jobs": 45,
                "jobs_by_source": {"remoteok": 25, "greenhouse": 20},
                "collection_time_seconds": 15.3,
                "jobs": []
            }
        }
    )
    
    success: bool
    message: str
    total_jobs: int
    jobs_by_source: Dict[str, int]
    collection_time_seconds: float
    jobs: List[Dict[str, Any]]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    source_statuses: Dict[str, Dict[str, Any]]
    collection_stats: Dict[str, Any]


class SourceConfigRequest(BaseModel):
    """Request model for source configuration."""
    enabled: bool = Field(..., description="Whether to enable the source")
    config: Optional[Dict[str, Any]] = Field(None, description="Additional source configuration")


class JobCollectionAPI:
    """REST API for job collection service."""
    
    def __init__(self, service: JobCollectionService, config: JobCollectionConfig):
        """
        Initialize API.
        
        Args:
            service: Job collection service instance
            config: Service configuration
        """
        self.service = service
        self.config = config
        self.app = FastAPI(
            title="Job Collection Service",
            description="Microservice for collecting job postings from multiple sources",
            version="1.0.0"
        )
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/", response_model=Dict[str, str])
        async def root():
            """Root endpoint."""
            return {
                "service": "Job Collection Service",
                "version": "1.0.0",
                "status": "running"
            }
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            try:
                source_statuses = await self.service.get_source_statuses()
                collection_stats = await self.service.get_collection_statistics()
                
                # Determine overall status
                failed_sources = [
                    name for name, status in source_statuses.items()
                    if not status.is_healthy
                ]
                
                overall_status = "healthy" if not failed_sources else "degraded"
                if len(failed_sources) >= len(source_statuses) / 2:
                    overall_status = "unhealthy"
                
                return HealthResponse(
                    status=overall_status,
                    timestamp=datetime.utcnow().isoformat(),
                    source_statuses={
                        name: asdict(status) for name, status in source_statuses.items()
                    },
                    collection_stats=collection_stats
                )
                
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return HealthResponse(
                    status="unhealthy",
                    timestamp=datetime.utcnow().isoformat(),
                    source_statuses={},
                    collection_stats={}
                )
        
        @self.app.post("/collect", response_model=CollectionResponse)
        async def collect_jobs(request: CollectJobsRequest):
            """
            Collect jobs based on query.
            
            Args:
                request: Collection request
                
            Returns:
                Collection response with jobs
            """
            try:
                start_time = datetime.utcnow()
                
                # Create job query
                job_query = JobQuery(
                    keywords=request.query,
                    location=request.location,
                    remote_only=request.remote_only or False,
                    max_results=request.max_jobs or self.config.max_jobs_per_source
                )
                
                # Collect jobs
                result = await self.service.collect_jobs(
                    query=job_query,
                    sources=request.sources
                )
                
                collection_time = (datetime.utcnow() - start_time).total_seconds()
                
                return CollectionResponse(
                    success=result.success,
                    message=result.message,
                    total_jobs=len(result.jobs),
                    jobs_by_source=result.jobs_by_source,
                    collection_time_seconds=collection_time,
                    jobs=[asdict(job) for job in result.jobs]
                )
                
            except JobCollectionError as e:
                logger.error(f"Job collection error: {e}")
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                logger.error(f"Unexpected error during job collection: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        @self.app.get("/jobs", response_model=List[Dict[str, Any]])
        async def get_jobs(
            query: Optional[str] = Query(None, description="Search query"),
            source: Optional[str] = Query(None, description="Job source filter"),
            location: Optional[str] = Query(None, description="Location filter"),
            remote_only: Optional[bool] = Query(None, description="Remote jobs only"),
            limit: int = Query(100, description="Maximum number of jobs to return"),
            offset: int = Query(0, description="Number of jobs to skip")
        ):
            """
            Get stored jobs with optional filters.
            
            Args:
                query: Search query
                source: Source filter
                location: Location filter
                remote_only: Remote only filter
                limit: Result limit
                offset: Result offset
                
            Returns:
                List of job postings
            """
            try:
                filters = {}
                if query:
                    filters['query'] = query
                if source:
                    filters['source'] = source
                if location:
                    filters['location'] = location
                if remote_only is not None:
                    filters['remote_only'] = remote_only
                
                jobs = await self.service.search_jobs(
                    filters=filters,
                    limit=limit,
                    offset=offset
                )
                
                return [asdict(job) for job in jobs]
                
            except Exception as e:
                logger.error(f"Error retrieving jobs: {e}")
                raise HTTPException(status_code=500, detail="Error retrieving jobs")
        
        @self.app.get("/jobs/{job_id}", response_model=Dict[str, Any])
        async def get_job(job_id: str):
            """
            Get specific job by ID.
            
            Args:
                job_id: Job identifier
                
            Returns:
                Job posting details
            """
            try:
                job = await self.service.get_job_by_id(job_id)
                if not job:
                    raise HTTPException(status_code=404, detail="Job not found")
                
                return asdict(job)
                
            except Exception as e:
                logger.error(f"Error retrieving job {job_id}: {e}")
                raise HTTPException(status_code=500, detail="Error retrieving job")
        
        @self.app.get("/sources", response_model=Dict[str, Any])
        async def get_sources():
            """
            Get available job sources and their status.
            
            Returns:
                Dictionary of sources and their configuration
            """
            try:
                source_statuses = await self.service.get_source_statuses()
                
                # Combine configuration with status
                sources = {}
                
                # API aggregators
                for name, config in self.config.api_aggregators.items():
                    status = source_statuses.get(name)
                    sources[name] = {
                        "type": "api_aggregator",
                        "enabled": config.get('enabled', False),
                        "config": config,
                        "status": asdict(status) if status else None
                    }
                
                # Browser scrapers
                for name, config in self.config.browser_scrapers.items():
                    status = source_statuses.get(name)
                    sources[name] = {
                        "type": "browser_scraper",
                        "enabled": config.get('enabled', False),
                        "config": config,
                        "status": asdict(status) if status else None
                    }
                
                return sources
                
            except Exception as e:
                logger.error(f"Error retrieving sources: {e}")
                raise HTTPException(status_code=500, detail="Error retrieving sources")
        
        @self.app.put("/sources/{source_name}", response_model=Dict[str, str])
        async def configure_source(source_name: str, request: SourceConfigRequest):
            """
            Configure a job source.
            
            Args:
                source_name: Name of the source
                request: Configuration request
                
            Returns:
                Configuration result
            """
            try:
                success = False
                
                if request.enabled:
                    success = self.config.enable_source(source_name)
                else:
                    success = self.config.disable_source(source_name)
                
                if not success:
                    raise HTTPException(status_code=404, detail="Source not found")
                
                # Apply additional configuration if provided
                if request.config:
                    if source_name in self.config.api_aggregators:
                        self.config.api_aggregators[source_name].update(request.config)
                    elif source_name in self.config.browser_scrapers:
                        self.config.browser_scrapers[source_name].update(request.config)
                
                return {
                    "message": f"Source {source_name} configured successfully",
                    "enabled": request.enabled
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error configuring source {source_name}: {e}")
                raise HTTPException(status_code=500, detail="Error configuring source")
        
        @self.app.get("/statistics", response_model=Dict[str, Any])
        async def get_statistics():
            """
            Get collection statistics.
            
            Returns:
                Collection statistics and metrics
            """
            try:
                stats = await self.service.get_collection_statistics()
                return stats
                
            except Exception as e:
                logger.error(f"Error retrieving statistics: {e}")
                raise HTTPException(status_code=500, detail="Error retrieving statistics")
        
        @self.app.post("/background-collect", response_model=Dict[str, str])
        async def start_background_collection(
            background_tasks: BackgroundTasks,
            request: CollectJobsRequest
        ):
            """
            Start background job collection.
            
            Args:
                background_tasks: FastAPI background tasks
                request: Collection request
                
            Returns:
                Task started confirmation
            """
            try:
                job_query = JobQuery(
                    keywords=request.query,
                    location=request.location,
                    remote_only=request.remote_only or False,
                    max_results=request.max_jobs or self.config.max_jobs_per_source
                )
                
                # Add background task
                background_tasks.add_task(
                    self._background_collect,
                    job_query,
                    request.sources
                )
                
                return {
                    "message": "Background collection started",
                    "query": request.query
                }
                
            except Exception as e:
                logger.error(f"Error starting background collection: {e}")
                raise HTTPException(status_code=500, detail="Error starting background collection")
        
        @self.app.delete("/jobs", response_model=Dict[str, str])
        async def clear_jobs(
            confirm: bool = Query(False, description="Confirmation required")
        ):
            """
            Clear all stored jobs.
            
            Args:
                confirm: Confirmation flag
                
            Returns:
                Clear operation result
            """
            if not confirm:
                raise HTTPException(
                    status_code=400, 
                    detail="Clear operation requires confirmation. Add ?confirm=true"
                )
            
            try:
                await self.service.clear_all_jobs()
                return {"message": "All jobs cleared successfully"}
                
            except Exception as e:
                logger.error(f"Error clearing jobs: {e}")
                raise HTTPException(status_code=500, detail="Error clearing jobs")
    
    async def _background_collect(self, query: JobQuery, sources: Optional[List[str]]):
        """
        Background job collection task.
        
        Args:
            query: Job query
            sources: Optional source filter
        """
        try:
            logger.info(f"Starting background collection for query: {query.keywords}")
            result = await self.service.collect_jobs(query=query, sources=sources)
            logger.info(f"Background collection completed: {result.message}")
            
        except Exception as e:
            logger.error(f"Background collection failed: {e}")
    
    def get_app(self) -> FastAPI:
        """
        Get FastAPI application.
        
        Returns:
            FastAPI application instance
        """
        return self.app


def create_job_collection_api(
    service: JobCollectionService,
    config: JobCollectionConfig
) -> FastAPI:
    """
    Create job collection API application.
    
    Args:
        service: Job collection service
        config: Service configuration
        
    Returns:
        FastAPI application
    """
    api = JobCollectionAPI(service, config)
    return api.get_app()