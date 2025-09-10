"""Main FastAPI application for the scraper service."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from src.core.factory import ScraperFactory
from src.models.job import JobRequest, JobResponse
from src.core.config import Settings
from src.core.metrics import MetricsCollector
from .management import router as management_router
import time

app = FastAPI(
    title="Job Scraper Service",
    description="Microservice for scraping job postings from various job boards",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include management routes
app.include_router(management_router)

# Load settings
settings = Settings()
scraper_factory = ScraperFactory(settings)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    all_healthy = True
    status = {}
    
    for source in settings.scrapers:
        try:
            health = await management_router.check_scraper_health(source)
            status[source] = health["status"]
            all_healthy &= health["status"] == "healthy"
        except HTTPException:
            status[source] = "unhealthy"
            all_healthy = False
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "scrapers": status
    }

@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.post("/jobs/search", response_model=JobResponse)
async def search_jobs(request: JobRequest):
    """Search for jobs across configured job boards."""
    try:
        start = time.time()
        scraper = scraper_factory.get_scraper(request.source)
        
        async with scraper:
            jobs = await scraper.fetch_jobs(
                search_terms=request.search_terms,
                location=request.location,
                max_results=request.max_results
            )
            
        duration = time.time() - start
        MetricsCollector.record_request(request.source, "success")
        MetricsCollector.record_request_duration(request.source, duration)
        MetricsCollector.record_jobs_found(request.source, len(jobs))
        
        return JobResponse(jobs=jobs)
    except Exception as e:
        MetricsCollector.record_request(request.source, "error")
        MetricsCollector.record_error(request.source, type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/config/scrapers")
async def list_scrapers():
    """List available scrapers and their configurations."""
    return {
        "scrapers": scraper_factory.list_scrapers(),
        "config": settings.dict()
    }
