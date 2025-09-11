"""
Comprehensive test suite configuration and utilities.

Provides shared test fixtures, utilities, and configuration for the entire test suite.
Ensures consistent test execution across unit, integration, regression, and E2E tests.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

# Ensure deterministic CWD in tests that use relative file paths
@pytest.fixture(scope="session", autouse=True)
def _set_cwd_to_repo_root():
    os.chdir(Path(__file__).resolve().parent.parent)  # repo/tests -> repo

# Common paths for samples/fixtures (adjust if yours differ)
@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

@pytest.fixture(scope="session")
def fixtures_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures"

# Example convenience paths used by CLI/regression tests
@pytest.fixture
def sample_jobs(fixtures_dir: Path) -> Path:
    return fixtures_dir / "remoteok_sample.json"

@pytest.fixture
def sample_resume(fixtures_dir: Path) -> Path:
    return fixtures_dir / "sample_resume.txt"

@pytest.fixture
def sample_applied(fixtures_dir: Path) -> Path:
    return fixtures_dir / "sample_applied.xlsx"

# Audit logger specific fixtures
@pytest.fixture
def audit_log_path(tmp_path):
    """Provide temporary audit log path."""
    return tmp_path / "test_audit.jsonl"

# CLI runner fixtures  
@pytest.fixture
def sample_config():
    """Provide sample configuration for CLI tests."""
    return {
        "input_file": "sample_jobs.json",
        "resume_file": "sample_resume.txt",
        "output_format": "json"
    }

@pytest.fixture(scope="session")
def test_workspace():
    """Create a temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp(prefix="job_finder_test_")
    workspace = Path(temp_dir)
    
    # Create directory structure
    directories = [
        "config",
        "output", 
        "cache",
        "logs",
        "resume_store/resume",
        "scraping_service_v2/logs",
        "job_aggregator/data"
    ]
    
    for directory in directories:
        (workspace / directory).mkdir(parents=True, exist_ok=True)
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_job_data():
    """Provide sample job data for testing."""
    return {
        "id": "test_job_123",
        "source": "indeed",
        "title": "Senior Software Engineer",
        "company": "Tech Innovations Corp",
        "location": "San Francisco, CA", 
        "url": "https://indeed.com/job/123456",
        "date_posted": datetime.now(timezone.utc),
        "salary": "$120,000 - $150,000",
        "description": "We are seeking an experienced software engineer to join our team...",
        "raw_data": {
            "job_type": "Full-time",
            "experience_level": "Senior",
            "benefits": ["Health Insurance", "401k", "Remote Work"]
        }
    }

@pytest.fixture
def mock_job_posting():
    """Create a mock job posting object."""
    job = Mock()
    job.id = "mock_job_456"
    job.source = "test_source"
    job.title = "Test Engineer"
    job.company = "Mock Company"
    job.location = "Test City"
    job.url = "https://test.example.com/job/456"
    job.date_posted = datetime.now(timezone.utc)
    job.salary = "$90,000"
    job.description = "Mock job description for testing purposes."
    return job

@pytest.fixture
def mock_scraper():
    """Create a mock scraper for testing."""
    scraper = Mock()
    scraper.name = "test_scraper"
    scraper.source_type = "BROWSER_SCRAPER"
    scraper.enabled = True
    
    # Mock async methods
    scraper.fetch_jobs = AsyncMock(return_value=[])
    scraper.health_check = AsyncMock(return_value=Mock(
        status="HEALTHY",
        message="OK",
        timestamp=datetime.now(timezone.utc),
        response_time_ms=150.0
    ))
    scraper.initialize = AsyncMock(return_value=True)
    scraper.cleanup = AsyncMock()
    
    # Mock sync methods
    scraper.get_search_url = Mock(return_value="https://test.example.com/search")
    scraper.get_selectors = Mock(return_value={"job_title": ".job-title"})
    scraper.get_supported_params = Mock(return_value={"q": {"type": "string"}})
    scraper.get_rate_limits = Mock(return_value=Mock(
        requests_per_minute=10,
        requests_per_hour=100
    ))
    
    return scraper

# Test markers for categorizing tests
pytest_markers = [
    "unit: Unit tests for individual components",
    "integration: Integration tests for component interactions", 
    "regression: Regression tests to prevent breaking changes",
    "e2e: End-to-end tests for complete workflows",
    "performance: Performance and load tests",
    "slow: Tests that take longer to execute"
]

# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    for marker in pytest_markers:
        config.addinivalue_line("markers", marker)

# Test collection filters
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file paths."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "regression" in str(item.fspath):
            item.add_marker(pytest.mark.regression)  
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
            
        # Mark slow tests
        if "performance" in item.name.lower() or "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)

# Async test utilities
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
