"""
Integration tests for the Greenhouse adapter.
"""
import pytest
import json
from datetime import datetime
from aiohttp import ClientSession, web
from tpm_job_finder_poc.scraping_service.adapters.greenhouse import GreenhouseAdapter
from tpm_job_finder_poc.scraping_service.base_adapter import (
    ScrapingConfig, RateLimitError, AuthenticationError
)

# Sample job data for testing
SAMPLE_JOBS = {
    'jobs': [
        {
            'id': '123',
            'title': 'Senior TPM',
            'company_name': 'Test Company',
            'location': {'name': 'Remote'},
            'content': '<div>Job description here</div>',
            'absolute_url': 'https://example.com/job/123',
            'updated_at': '2025-09-09T12:00:00.000Z'
        }
    ]
}

async def test_greenhouse_job_fetching(aiohttp_client):
    """Test fetching jobs from Greenhouse."""
    # Set up mock Greenhouse API
    async def mock_jobs(request):
        return web.json_response(SAMPLE_JOBS)
    
    app = web.Application()
    app.router.add_get('/v1/boards/{company}/jobs', mock_jobs)
    
    # Create test client
    client = await aiohttp_client(app)
    
    # Create adapter with test config
    adapter = GreenhouseAdapter(ScrapingConfig(
        backend='local',
        timeout=5
    ))
    
    # Test job fetching
    jobs = await adapter.fetch_jobs({'company_ids': ['test-company']})
    
    assert len(jobs) == 1
    job = jobs[0]
    assert job.title == 'Senior TPM'
    assert job.company == 'Test Company'
    assert job.location == 'Remote'
    assert 'Job description here' in job.description
    assert job.source == 'greenhouse'
    assert isinstance(job.posted_date, datetime)

async def test_greenhouse_rate_limit_handling(aiohttp_client):
    """Test handling of rate limit responses."""
    async def mock_rate_limit(request):
        return web.Response(status=429)
    
    app = web.Application()
    app.router.add_get('/v1/boards/{company}/jobs', mock_rate_limit)
    
    client = await aiohttp_client(app)
    adapter = GreenhouseAdapter(ScrapingConfig(backend='local'))
    
    with pytest.raises(RateLimitError):
        await adapter.fetch_jobs({'company_ids': ['test-company']})

async def test_greenhouse_auth_error_handling(aiohttp_client):
    """Test handling of authentication errors."""
    async def mock_auth_error(request):
        return web.Response(status=401)
    
    app = web.Application()
    app.router.add_get('/v1/boards/{company}/jobs', mock_auth_error)
    
    client = await aiohttp_client(app)
    adapter = GreenhouseAdapter(ScrapingConfig(backend='local'))
    
    with pytest.raises(AuthenticationError):
        await adapter.fetch_jobs({'company_ids': ['test-company']})

async def test_greenhouse_job_parsing():
    """Test parsing of Greenhouse job data."""
    adapter = GreenhouseAdapter(ScrapingConfig(backend='local'))
    
    jobs = adapter._parse_jobs(SAMPLE_JOBS['jobs'], 'test-company')
    
    assert len(jobs) == 1
    job = jobs[0]
    assert job.job_id == 'greenhouse_test-company_123'
    assert job.title == 'Senior TPM'
    assert job.company == 'Test Company'
    assert job.location == 'Remote'
    assert job.source == 'greenhouse'
    assert job.raw_data == SAMPLE_JOBS['jobs'][0]

async def test_greenhouse_health_check(aiohttp_client):
    """Test health check functionality."""
    async def mock_health(request):
        return web.json_response({'status': 'ok'})
    
    app = web.Application()
    app.router.add_get('/v1/boards/{company}/jobs', mock_health)
    
    client = await aiohttp_client(app)
    adapter = GreenhouseAdapter(ScrapingConfig(backend='local'))
    
    status = await adapter.health_check()
    assert status['status'] == 'ok'
