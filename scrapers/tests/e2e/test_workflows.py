"""End-to-end tests for scraper service."""

import pytest
import asyncio
from httpx import AsyncClient
from src.api.main import app
from src.core.config import Settings

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_job_search_workflow():
    """Test complete job search workflow from API to storage."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Check service health
        health_response = await client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
        
        # 2. Search for jobs
        search_response = await client.post("/jobs/search", json={
            "source": "linkedin",
            "search_terms": ["Technical Program Manager"],
            "location": "San Francisco",
            "max_results": 5
        })
        assert search_response.status_code == 200
        jobs = search_response.json()["jobs"]
        assert len(jobs) > 0
        
        # 3. Check metrics
        metrics_response = await client.get("/metrics")
        assert metrics_response.status_code == 200
        metrics_text = metrics_response.text
        assert "scraper_requests_total" in metrics_text
        assert "jobs_found_total" in metrics_text

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_multi_source_aggregation():
    """Test job aggregation from multiple sources."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Batch search across sources
        response = await client.post("/api/v1/scrapers/batch", json={
            "sources": ["linkedin", "indeed", "ziprecruiter"],
            "search_terms": ["TPM"],
            "location": "Remote",
            "max_results": 3
        })
        assert response.status_code == 200
        data = response.json()
        
        # 2. Verify results from each source
        for source in ["linkedin", "indeed", "ziprecruiter"]:
            assert source in data
            if "error" not in data[source]:
                jobs = data[source]["jobs"]
                assert len(jobs) <= 3
                for job in jobs:
                    assert all(key in job for key in [
                        "title", "company", "location", "description", "url"
                    ])

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_error_handling_workflow():
    """Test error handling and recovery workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Test invalid source
        response = await client.post("/jobs/search", json={
            "source": "invalid_source",
            "search_terms": ["TPM"]
        })
        assert response.status_code == 404
        
        # 2. Test rate limiting
        tasks = []
        for _ in range(10):
            tasks.append(client.post("/jobs/search", json={
                "source": "linkedin",
                "search_terms": ["TPM"]
            }))
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        assert any(r.status_code == 429 for r in responses if hasattr(r, 'status_code'))
        
        # 3. Verify error metrics
        metrics_response = await client.get("/metrics")
        assert "scraper_errors_total" in metrics_response.text

@pytest.mark.e2e
@pytest.mark.asyncio
async def test_configuration_workflow():
    """Test configuration management workflow."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Get initial configuration
        config_response = await client.get("/config/scrapers")
        initial_config = config_response.json()
        
        # 2. Update configuration
        new_config = {
            "requests_per_minute": 5,
            "cache_enabled": True,
            "cache_max_age": 7200
        }
        update_response = await client.post(
            "/api/v1/scrapers/linkedin/configure",
            json=new_config
        )
        assert update_response.status_code == 200
        
        # 3. Verify configuration was applied
        search_response = await client.post("/jobs/search", json={
            "source": "linkedin",
            "search_terms": ["TPM"],
            "max_results": 2
        })
        assert search_response.status_code == 200
        
        # 4. Verify metrics reflect new configuration
        metrics_response = await client.get("/metrics")
        metrics_text = metrics_response.text
        assert "rate_limit_delay_seconds" in metrics_text
