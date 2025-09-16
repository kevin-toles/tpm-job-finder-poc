"""
Test configuration for scraping service TDD tests.

Provides shared fixtures and test configuration for the scraping service
TDD test suite.
"""

import pytest
import os
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, List

# Import our contracts and models
from tpm_job_finder_poc.shared.contracts.scraping_service import (
    IScrapingService,
    ScrapingConfig,
    ScrapingQuery,
    ScrapingResult,
    ScrapingStatistics,
    SourceHealth
)
from tpm_job_finder_poc.scraping_service.core.base_job_source import JobPosting


@pytest.fixture
def sample_config():
    """Sample scraping configuration for testing."""
    return ScrapingConfig(
        headless=True,
        timeout_seconds=30,
        max_retries=3,
        user_agent_rotation=True,
        enable_anti_detection=True,
        delay_min_seconds=1.0,
        delay_max_seconds=3.0,
        max_browser_instances=3,
        max_concurrent_scrapers=2,
        indeed_rate_limit=10,
        linkedin_rate_limit=5
    )


@pytest.fixture
def sample_query():
    """Sample scraping query for testing."""
    return ScrapingQuery(
        keywords=["python developer", "software engineer"],
        location="Remote",
        date_posted="week",
        max_results=50,
        sources=["indeed", "ziprecruiter"]
    )


@pytest.fixture
def sample_job_posting():
    """Sample job posting for testing."""
    return JobPosting(
        id="test_job_123",
        source="indeed",
        company="Tech Corp",
        title="Senior Python Developer",
        location="Remote",
        salary="$100,000 - $120,000",
        url="https://indeed.com/job/123",
        date_posted=datetime.now(timezone.utc),
        description="Exciting Python developer role..."
    )


@pytest.fixture
def sample_job_postings(sample_job_posting):
    """List of sample job postings for testing."""
    return [
        sample_job_posting,
        JobPosting(
            id="test_job_456",
            source="ziprecruiter",
            company="Startup Inc",
            title="Python Engineer",
            location="San Francisco, CA",
            url="https://ziprecruiter.com/job/456",
            date_posted=datetime.now(timezone.utc)
        )
    ]


@pytest.fixture
def mock_browser():
    """Mock browser instance for testing."""
    mock = Mock()
    mock.get = AsyncMock()
    mock.quit = AsyncMock()
    mock.find_elements = Mock(return_value=[])
    mock.page_source = "<html><body>Test page</body></html>"
    return mock


@pytest.fixture
def mock_scraping_orchestrator():
    """Mock scraping orchestrator for testing."""
    mock = AsyncMock()
    mock.fetch_all_sources = AsyncMock()
    mock.health_check_sources = AsyncMock()
    mock.get_source_capabilities = AsyncMock()
    return mock


@pytest.fixture
def mock_service_registry():
    """Mock service registry for testing."""
    mock = Mock()
    mock.list_sources = Mock(return_value=["indeed", "linkedin", "ziprecruiter"])
    mock.enable_source = Mock(return_value=True)
    mock.disable_source = Mock(return_value=True)
    mock.get_source = Mock()
    return mock


# Test utilities
class MockScrapingService:
    """Mock implementation of IScrapingService for testing."""
    
    def __init__(self):
        self.running = False
        self.statistics = ScrapingStatistics()
        self.available_sources = ["indeed", "linkedin", "ziprecruiter", "greenhouse"]
        
    async def start(self):
        self.running = True
        
    async def stop(self):
        self.running = False
        
    def is_running(self):
        return self.running
        
    async def scrape_jobs(self, query, config=None):
        return ScrapingResult(
            jobs=[],
            query=query,
            total_jobs_found=0,
            jobs_after_deduplication=0,
            duplicates_removed=0,
            sources_queried=len(query.sources) if query.sources else len(self.available_sources),
            successful_sources=0,
            failed_sources=0,
            processing_time_seconds=1.0,
            average_response_time_ms=500.0,
            source_results={},
            errors={},
            scraped_at=datetime.now(timezone.utc)
        )
        
    async def get_available_sources(self):
        return self.available_sources
        
    async def get_statistics(self):
        return self.statistics


# Environment setup
def pytest_configure(config):
    """Configure test environment."""
    # Ensure we don't accidentally hit real websites during tests
    os.environ["SCRAPING_TEST_MODE"] = "1"
    
    
def pytest_unconfigure(config):
    """Clean up test environment."""
    if "SCRAPING_TEST_MODE" in os.environ:
        del os.environ["SCRAPING_TEST_MODE"]