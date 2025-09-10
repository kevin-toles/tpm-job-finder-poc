"""API endpoints for scraper management."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from ..core.config import Settings
from ..core.factory import ScraperFactory
from ..models.job import JobRequest, JobResponse
from ..core.metrics import MetricsCollector
import time

router = APIRouter(prefix="/api/v1")

@router.get("/scrapers")
async def list_scrapers():
    """List all available scrapers and their configurations."""
    settings = Settings()
    return {
        "scrapers": [
            {
                "name": name,
                "config": config.dict()
            }
            for name, config in settings.scrapers.items()
        ]
    }

@router.get("/scrapers/{source}/health")
async def check_scraper_health(source: str):
    """Check health of a specific scraper."""
    settings = Settings()
    if source not in settings.scrapers:
        raise HTTPException(status_code=404, detail=f"Scraper {source} not found")
    
    try:
        scraper = ScraperFactory(settings).get_scraper(source)
        async with scraper:
            start = time.time()
            jobs = await scraper.fetch_jobs(
                search_terms=["test"],
                max_results=1
            )
            duration = time.time() - start
            
            MetricsCollector.record_request_duration(source, duration)
            MetricsCollector.update_health(source, True)
            
            return {
                "status": "healthy",
                "response_time": duration,
                "found_jobs": len(jobs) > 0
            }
    except Exception as e:
        MetricsCollector.record_error(source, type(e).__name__)
        MetricsCollector.update_health(source, False)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrapers/{source}/configure")
async def configure_scraper(source: str, config: Dict[str, Any]):
    """Update configuration for a specific scraper."""
    settings = Settings()
    if source not in settings.scrapers:
        raise HTTPException(status_code=404, detail=f"Scraper {source} not found")
    
    try:
        settings.scrapers[source] = settings.scrapers[source].copy(update=config)
        settings.save_config()
        return {"status": "success", "message": f"Configuration updated for {source}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics/scraper/{source}")
async def get_scraper_metrics(source: str):
    """Get metrics for a specific scraper."""
    settings = Settings()
    if source not in settings.scrapers:
        raise HTTPException(status_code=404, detail=f"Scraper {source} not found")
    
    return {
        "requests": {
            "total": SCRAPER_REQUESTS.labels(source=source, status="success")._value.get(),
            "errors": SCRAPER_REQUESTS.labels(source=source, status="error")._value.get()
        },
        "performance": {
            "avg_duration": SCRAPER_REQUEST_DURATION.labels(source=source).count._value.get(),
        },
        "cache": {
            "hits": CACHE_HITS.labels(source=source)._value.get(),
            "misses": CACHE_MISSES.labels(source=source)._value.get()
        },
        "jobs_found": JOBS_FOUND.labels(source=source)._value.get(),
        "health_status": SCRAPER_HEALTH.labels(source=source)._value.get()
    }

@router.post("/scrapers/batch")
async def batch_search(
    sources: List[str] = Query(None),
    request: JobRequest = None
) -> Dict[str, JobResponse]:
    """Search for jobs across multiple scrapers in parallel."""
    if not sources:
        settings = Settings()
        sources = list(settings.scrapers.keys())

    factory = ScraperFactory(Settings())
    results = {}
    
    for source in sources:
        try:
            scraper = factory.get_scraper(source)
            async with scraper:
                start = time.time()
                jobs = await scraper.fetch_jobs(
                    search_terms=request.search_terms,
                    location=request.location,
                    max_results=request.max_results
                )
                duration = time.time() - start
                
                MetricsCollector.record_request_duration(source, duration)
                MetricsCollector.record_jobs_found(source, len(jobs))
                
                results[source] = JobResponse(jobs=jobs)
        except Exception as e:
            MetricsCollector.record_error(source, type(e).__name__)
            results[source] = {"error": str(e)}
    
    return results
