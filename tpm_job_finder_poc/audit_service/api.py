"""
Audit Service REST API

FastAPI-based REST interface for audit service operations.
Provides endpoints for event logging, querying, and health monitoring.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import uvicorn

from tpm_job_finder_poc.shared.contracts.audit_service import (
    AuditEvent,
    AuditQuery,
    AuditQueryResult,
    AuditLevel,
    AuditCategory,
    IAuditService,
    AuditServiceError,
    AuditEventValidationError
)


# Request/Response Models
class AuditEventRequest(BaseModel):
    """Request model for audit event logging."""
    level: AuditLevel
    category: AuditCategory
    action: str
    service_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    message: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    duration_ms: Optional[float] = None


class AuditEventResponse(BaseModel):
    """Response model for audit event operations."""
    event_id: str
    timestamp: datetime
    level: AuditLevel
    category: AuditCategory
    action: str
    service_name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    message: str
    metadata: Dict[str, Any]
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    duration_ms: Optional[float] = None

    @classmethod
    def from_audit_event(cls, event: AuditEvent) -> "AuditEventResponse":
        """Convert audit event to response model."""
        return cls(
            event_id=event.event_id,
            timestamp=event.timestamp,
            level=event.level,
            category=event.category,
            action=event.action,
            service_name=event.service_name,
            user_id=event.user_id,
            session_id=event.session_id,
            request_id=event.request_id,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            message=event.message,
            metadata=event.metadata,
            error_code=event.error_code,
            error_message=event.error_message,
            stack_trace=event.stack_trace,
            duration_ms=event.duration_ms
        )


class AuditQueryRequest(BaseModel):
    """Request model for audit event queries."""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    service_names: Optional[List[str]] = None
    user_ids: Optional[List[str]] = None
    levels: Optional[List[AuditLevel]] = None
    categories: Optional[List[AuditCategory]] = None
    actions: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    resource_ids: Optional[List[str]] = None
    message_contains: Optional[str] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    order_by: str = Field(default="timestamp")
    order_desc: bool = Field(default=True)


class AuditQueryResponse(BaseModel):
    """Response model for audit event queries."""
    events: List[AuditEventResponse]
    total_count: int
    has_more: bool
    query_duration_ms: float

    @classmethod
    def from_query_result(cls, result: AuditQueryResult) -> "AuditQueryResponse":
        """Convert query result to response model."""
        return cls(
            events=[AuditEventResponse.from_audit_event(event) for event in result.events],
            total_count=result.total_count,
            has_more=result.has_more,
            query_duration_ms=result.query_duration_ms
        )


class BatchAuditEventRequest(BaseModel):
    """Request model for batch audit event logging."""
    events: List[AuditEventRequest]


class BatchAuditEventResponse(BaseModel):
    """Response model for batch audit event operations."""
    events_logged: int
    event_ids: List[str]


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    service: Dict[str, Any]
    storage: Dict[str, Any]


# Global service instance
_audit_service: Optional[IAuditService] = None


def get_audit_service() -> IAuditService:
    """Dependency to get audit service instance."""
    if _audit_service is None:
        raise HTTPException(status_code=500, detail="Audit service not initialized")
    return _audit_service


def set_audit_service(service: IAuditService) -> None:
    """Set the global audit service instance."""
    global _audit_service
    _audit_service = service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger = logging.getLogger(__name__)
    
    # Startup
    if _audit_service:
        await _audit_service.start()
        logger.info("Audit service started")
    
    yield
    
    # Shutdown
    if _audit_service:
        await _audit_service.stop()
        logger.info("Audit service stopped")


# Create FastAPI app
app = FastAPI(
    title="Audit Service API",
    description="REST API for audit event logging and querying",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/events", response_model=AuditEventResponse)
async def log_event(
    request: AuditEventRequest,
    service: IAuditService = Depends(get_audit_service)
) -> AuditEventResponse:
    """Log a single audit event."""
    try:
        # Create event using builder
        builder = service.create_event_builder()
        event = (builder
                .set_level(request.level)
                .set_category(request.category)
                .set_action(request.action)
                .set_service_name(request.service_name)
                .set_message(request.message))
        
        # Set optional fields
        if request.user_id:
            event = event.set_user_id(request.user_id)
        if request.session_id:
            event = event.set_session_id(request.session_id)
        if request.request_id:
            event = event.set_request_id(request.request_id)
        if request.resource_type:
            event = event.set_resource_type(request.resource_type)
        if request.resource_id:
            event = event.set_resource_id(request.resource_id)
        if request.metadata:
            event = event.set_metadata(request.metadata)
        if request.error_code:
            event = event.set_error_code(request.error_code)
        if request.error_message:
            event = event.set_error_message(request.error_message)
        if request.stack_trace:
            event = event.set_stack_trace(request.stack_trace)
        if request.duration_ms is not None:
            event = event.set_duration_ms(request.duration_ms)
        
        # Build and log event
        audit_event = event.build()
        await service.log_event(audit_event)
        
        return AuditEventResponse.from_audit_event(audit_event)
        
    except AuditEventValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuditServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/batch", response_model=BatchAuditEventResponse)
async def log_events_batch(
    request: BatchAuditEventRequest,
    service: IAuditService = Depends(get_audit_service)
) -> BatchAuditEventResponse:
    """Log multiple audit events in batch."""
    try:
        if not request.events:
            raise HTTPException(status_code=400, detail="No events provided")
        
        if len(request.events) > 100:  # Reasonable batch size limit
            raise HTTPException(status_code=400, detail="Too many events (max 100)")
        
        # Convert requests to events
        events = []
        for event_req in request.events:
            builder = service.create_event_builder()
            event = (builder
                    .set_level(event_req.level)
                    .set_category(event_req.category)
                    .set_action(event_req.action)
                    .set_service_name(event_req.service_name)
                    .set_message(event_req.message))
            
            # Set optional fields
            if event_req.user_id:
                event = event.set_user_id(event_req.user_id)
            if event_req.session_id:
                event = event.set_session_id(event_req.session_id)
            if event_req.request_id:
                event = event.set_request_id(event_req.request_id)
            if event_req.resource_type:
                event = event.set_resource_type(event_req.resource_type)
            if event_req.resource_id:
                event = event.set_resource_id(event_req.resource_id)
            if event_req.metadata:
                event = event.set_metadata(event_req.metadata)
            if event_req.error_code:
                event = event.set_error_code(event_req.error_code)
            if event_req.error_message:
                event = event.set_error_message(event_req.error_message)
            if event_req.stack_trace:
                event = event.set_stack_trace(event_req.stack_trace)
            if event_req.duration_ms is not None:
                event = event.set_duration_ms(event_req.duration_ms)
            
            events.append(event.build())
        
        # Log events
        await service.log_events(events)
        
        return BatchAuditEventResponse(
            events_logged=len(events),
            event_ids=[event.event_id for event in events]
        )
        
    except AuditEventValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AuditServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events", response_model=AuditQueryResponse)
async def query_events(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    service_names: Optional[str] = Query(None),
    user_ids: Optional[str] = Query(None),
    levels: Optional[str] = Query(None),
    categories: Optional[str] = Query(None),
    actions: Optional[str] = Query(None),
    resource_types: Optional[str] = Query(None),
    resource_ids: Optional[str] = Query(None),
    message_contains: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    order_by: str = Query("timestamp"),
    order_desc: bool = Query(True),
    service: IAuditService = Depends(get_audit_service)
) -> AuditQueryResponse:
    """Query audit events."""
    try:
        # Parse comma-separated lists
        service_names_list = service_names.split(",") if service_names else None
        user_ids_list = user_ids.split(",") if user_ids else None
        levels_list = [AuditLevel(level.strip()) for level in levels.split(",")] if levels else None
        categories_list = [AuditCategory(cat.strip()) for cat in categories.split(",")] if categories else None
        actions_list = actions.split(",") if actions else None
        resource_types_list = resource_types.split(",") if resource_types else None
        resource_ids_list = resource_ids.split(",") if resource_ids else None
        
        # Create query
        query = AuditQuery(
            start_time=start_time,
            end_time=end_time,
            service_names=service_names_list,
            user_ids=user_ids_list,
            levels=levels_list,
            categories=categories_list,
            actions=actions_list,
            resource_types=resource_types_list,
            resource_ids=resource_ids_list,
            message_contains=message_contains,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_desc=order_desc
        )
        
        # Execute query
        result = await service.query_events(query)
        
        return AuditQueryResponse.from_query_result(result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter: {e}")
    except AuditServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/events/query", response_model=AuditQueryResponse)
async def query_events_post(
    request: AuditQueryRequest,
    service: IAuditService = Depends(get_audit_service)
) -> AuditQueryResponse:
    """Query audit events using POST body."""
    try:
        # Create query
        query = AuditQuery(
            start_time=request.start_time,
            end_time=request.end_time,
            service_names=request.service_names,
            user_ids=request.user_ids,
            levels=request.levels,
            categories=request.categories,
            actions=request.actions,
            resource_types=request.resource_types,
            resource_ids=request.resource_ids,
            message_contains=request.message_contains,
            limit=request.limit,
            offset=request.offset,
            order_by=request.order_by,
            order_desc=request.order_desc
        )
        
        # Execute query
        result = await service.query_events(query)
        
        return AuditQueryResponse.from_query_result(result)
        
    except AuditServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events/{event_id}", response_model=AuditEventResponse)
async def get_event(
    event_id: str,
    service: IAuditService = Depends(get_audit_service)
) -> AuditEventResponse:
    """Get a specific audit event by ID."""
    try:
        event = await service.get_event(event_id)
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return AuditEventResponse.from_audit_event(event)
        
    except AuditServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/flush")
async def flush_events(
    service: IAuditService = Depends(get_audit_service)
) -> Dict[str, str]:
    """Manually flush buffered events."""
    try:
        await service.flush()
        return {"status": "flushed"}
        
    except AuditServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health_check(
    service: IAuditService = Depends(get_audit_service)
) -> HealthResponse:
    """Check service health."""
    try:
        health = await service.health_check()
        return HealthResponse(**health)
        
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            service={"error": str(e)},
            storage={"error": "health check failed"}
        )


def create_app(audit_service: IAuditService) -> FastAPI:
    """
    Create configured FastAPI app with audit service.
    
    Args:
        audit_service: Audit service instance
        
    Returns:
        Configured FastAPI application
    """
    set_audit_service(audit_service)
    return app


def run_server(audit_service: IAuditService,
               host: str = "0.0.0.0",
               port: int = 8000,
               log_level: str = "info") -> None:
    """
    Run the audit service API server.
    
    Args:
        audit_service: Audit service instance
        host: Server host
        port: Server port
        log_level: Logging level
    """
    set_audit_service(audit_service)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level
    )