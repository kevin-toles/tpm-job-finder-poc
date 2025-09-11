"""
Unit tests for the scraping service base adapter.
"""
import pytest
from datetime import datetime
from scraping_service.base_adapter import (
    BaseAdapter, JobData, ScrapingConfig, AdapterError,
    RateLimitError, AuthenticationError, ScrapingError
)

class MockAdapter(BaseAdapter):
    """Test implementation of BaseAdapter."""
    async def fetch_jobs(self, params):
        return []
    
    async def validate_credentials(self):
        return True
    
    async def health_check(self):
        return {'status': 'ok'}

def test_job_data_creation():
    """Test creating a JobData object with all fields."""
    job = JobData(
        job_id='test123',
        title='Software Engineer',
        company='Test Co',
        location='Remote',
        description='Test description',
        url='http://example.com/job',
        salary_range='$100k-$150k',
        posted_date=datetime.now(),
        source='test',
        raw_data={'original': 'data'}
    )
    
    assert job.job_id == 'test123'
    assert job.title == 'Software Engineer'
    assert job.company == 'Test Co'
    assert job.location == 'Remote'
    assert job.description == 'Test description'
    assert job.url == 'http://example.com/job'
    assert job.salary_range == '$100k-$150k'
    assert isinstance(job.posted_date, datetime)
    assert job.source == 'test'
    assert job.raw_data == {'original': 'data'}

def test_scraping_config_defaults():
    """Test ScrapingConfig default values."""
    config = ScrapingConfig(backend='local')
    
    assert config.backend == 'local'
    assert config.proxy_enabled is False
    assert config.proxy_config is None
    assert config.rate_limit == 60
    assert config.timeout == 30
    assert config.retries == 3

def test_adapter_error_hierarchy():
    """Test adapter error class hierarchy."""
    base_error = AdapterError("base error")
    assert isinstance(base_error, Exception)
    
    rate_limit_error = RateLimitError("rate limit")
    assert isinstance(rate_limit_error, AdapterError)
    
    auth_error = AuthenticationError("auth error")
    assert isinstance(auth_error, AdapterError)
    
    scraping_error = ScrapingError("scraping error")
    assert isinstance(scraping_error, AdapterError)

@pytest.mark.asyncio
async def test_base_adapter_implementation():
    """Test that BaseAdapter can be implemented."""
    adapter = MockAdapter(ScrapingConfig(backend='local'))
    
    # Test that implementations work
    jobs = await adapter.fetch_jobs({})
    assert jobs == []
    
    valid = await adapter.validate_credentials()
    assert valid is True
    
    status = await adapter.health_check()
    assert status == {'status': 'ok'}
