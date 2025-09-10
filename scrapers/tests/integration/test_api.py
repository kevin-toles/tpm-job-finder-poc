"""Integration tests for scraper service API."""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.config import Settings

@pytest.fixture
async def client():
    """Test client fixture."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_search_jobs(client):
    """Test job search endpoint."""
    response = await client.post("/jobs/search", json={
        "source": "linkedin",
        "search_terms": ["Technical Program Manager"],
        "location": "San Francisco",
        "max_results": 5
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert len(data["jobs"]) <= 5
    
    for job in data["jobs"]:
        assert all(key in job for key in ["title", "company", "location"])

@pytest.mark.asyncio
async def test_batch_search(client):
    """Test batch job search across multiple sources."""
    response = await client.post("/api/v1/scrapers/batch", json={
        "sources": ["linkedin", "indeed"],
        "search_terms": ["TPM"],
        "location": "Remote",
        "max_results": 3
    })
    
    assert response.status_code == 200
    data = response.json()
    assert all(source in data for source in ["linkedin", "indeed"])
    
    for source, result in data.items():
        if "error" not in result:
            assert "jobs" in result
            assert len(result["jobs"]) <= 3

@pytest.mark.asyncio
async def test_scraper_health(client):
    """Test scraper health check endpoint."""
    response = await client.get("/api/v1/scrapers/linkedin/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "response_time" in data

@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Test metrics endpoint."""
    # Make some requests to generate metrics
    await client.post("/jobs/search", json={
        "source": "linkedin",
        "search_terms": ["TPM"],
        "max_results": 1
    })
    
    response = await client.get("/metrics")
    assert response.status_code == 200
    metrics = response.text
    
    # Check for expected metric types
    assert "scraper_requests_total" in metrics
    assert "scraper_request_duration_seconds" in metrics
    assert "jobs_found_total" in metrics

@pytest.mark.asyncio
async def test_configure_scraper(client):
    """Test scraper configuration endpoint."""
    new_config = {
        "requests_per_minute": 5,
        "cache_enabled": True,
        "cache_max_age": 7200
    }
    
    response = await client.post(
        "/api/v1/scrapers/linkedin/configure",
        json=new_config
    )
    
    assert response.status_code == 200
    
    # Verify configuration was updated
    response = await client.get("/config/scrapers")
    data = response.json()
    linkedin_config = next(
        s["config"] for s in data["scrapers"]
        if s["name"] == "linkedin"
    )
    
    assert linkedin_config["requests_per_minute"] == new_config["requests_per_minute"]
    assert linkedin_config["cache_enabled"] == new_config["cache_enabled"]
    assert linkedin_config["cache_max_age"] == new_config["cache_max_age"]
