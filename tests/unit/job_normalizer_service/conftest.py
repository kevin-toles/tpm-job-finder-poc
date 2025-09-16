"""Pytest configuration and fixtures for Job Normalizer Service tests."""

import pytest
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any
from unittest.mock import AsyncMock, Mock

from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig
from tpm_job_finder_poc.shared.contracts.job_normalizer_service import (
    JobNormalizationConfig,
    NormalizationResult,
    NormalizationStatistics
)
from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def service_config():
    """Create default service configuration for testing."""
    return JobNormalizerServiceConfig()


@pytest.fixture
def custom_service_config():
    """Create custom service configuration for testing."""
    return JobNormalizerServiceConfig(
        enable_deduplication=False,
        enable_field_normalization=True,
        max_batch_size=500,
        processing_timeout_seconds=60,
        duplicate_detection_similarity_threshold=0.9
    )


@pytest.fixture
def operation_config():
    """Create default operation configuration for testing."""
    return JobNormalizationConfig()


@pytest.fixture
def custom_operation_config():
    """Create custom operation configuration for testing."""
    return JobNormalizationConfig(
        enable_deduplication=False,
        normalize_titles=False,
        duplicate_detection_method="exact",
        similarity_threshold=0.95
    )


@pytest.fixture
def sample_raw_job():
    """Create sample raw job data for testing."""
    return {
        'id': 'test123',
        'title': 'Software Engineer',
        'company': 'Test Corp',
        'url': 'https://example.com/job/123',
        'date_posted': datetime.now(timezone.utc).isoformat(),
        'location': 'San Francisco, CA',
        'salary': '$100,000',
        'description': 'A great software engineering position.'
    }


@pytest.fixture
def sample_raw_jobs():
    """Create list of sample raw job data for testing."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            'id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp A',
            'url': 'https://example.com/job/1',
            'date_posted': base_time.isoformat(),
            'location': 'San Francisco, CA',
            'salary': '$100,000'
        },
        {
            'id': 'job2',
            'title': 'Product Manager',
            'company': 'Product Corp B',
            'url': 'https://example.com/job/2',
            'date_posted': base_time.isoformat(),
            'location': 'New York, NY',
            'salary': '$120,000'
        },
        {
            'id': 'job3',
            'title': 'Data Scientist',
            'company': 'Data Corp C',
            'url': 'https://example.com/job/3',
            'date_posted': base_time.isoformat(),
            'location': 'Remote',
            'description': 'Work with big data and machine learning.'
        }
    ]


@pytest.fixture
def sample_job_posting():
    """Create sample JobPosting object for testing."""
    return JobPosting(
        id="test123",
        source="indeed",
        company="Test Corp",
        title="Software Engineer",
        url="https://example.com/job/123",
        date_posted=datetime.now(timezone.utc),
        location="San Francisco, CA",
        salary="$100,000",
        description="A great software engineering position."
    )


@pytest.fixture
def sample_job_postings():
    """Create list of sample JobPosting objects for testing."""
    base_time = datetime.now(timezone.utc)
    return [
        JobPosting(
            id="job1",
            source="indeed",
            company="Tech Corp A",
            title="Software Engineer",
            url="https://example.com/job/1",
            date_posted=base_time,
            location="San Francisco, CA",
            salary="$100,000"
        ),
        JobPosting(
            id="job2",
            source="linkedin",
            company="Product Corp B",
            title="Product Manager",
            url="https://example.com/job/2",
            date_posted=base_time,
            location="New York, NY",
            salary="$120,000"
        ),
        JobPosting(
            id="job3",
            source="glassdoor",
            company="Data Corp C",
            title="Data Scientist",
            url="https://example.com/job/3",
            date_posted=base_time,
            location="Remote",
            description="Work with big data and machine learning."
        )
    ]


@pytest.fixture
def duplicate_raw_jobs():
    """Create sample raw jobs with duplicates for testing."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            'id': 'job1',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'url': 'https://example.com/job/1',
            'date_posted': base_time.isoformat()
        },
        {
            'id': 'job2',
            'title': 'Software Engineer',
            'company': 'Tech Corp',  # Same company and title
            'url': 'https://example.com/job/2',
            'date_posted': base_time.isoformat()
        },
        {
            'id': 'job3',
            'title': 'Software Engineer',
            'company': 'Tech Corp',
            'url': 'https://example.com/job/1',  # Same URL as job1
            'date_posted': base_time.isoformat()
        },
        {
            'id': 'job4',
            'title': 'Product Manager',
            'company': 'Different Corp',  # Unique job
            'url': 'https://example.com/job/4',
            'date_posted': base_time.isoformat()
        }
    ]


@pytest.fixture
def invalid_raw_jobs():
    """Create sample invalid raw jobs for testing."""
    return [
        {
            'id': 'valid_job',
            'title': 'Software Engineer',
            'company': 'Test Corp',
            'url': 'https://example.com/job/valid',
            'date_posted': datetime.now(timezone.utc).isoformat()
        },
        {
            # Missing required 'id' field
            'title': 'Invalid Job 1',
            'company': 'Test Corp',
            'url': 'https://example.com/job/invalid1',
            'date_posted': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': 'invalid_job_2',
            'title': 'Invalid Job 2',
            'company': 'Test Corp',
            'url': 'not-a-valid-url',  # Invalid URL
            'date_posted': datetime.now(timezone.utc).isoformat()
        },
        {
            'id': 'invalid_job_3',
            'title': 'Invalid Job 3',
            'company': 'Test Corp',
            'url': 'https://example.com/job/invalid3'
            # Missing required 'date_posted' field
        }
    ]


@pytest.fixture
def sample_normalization_result():
    """Create sample NormalizationResult for testing."""
    return NormalizationResult(
        total_input_jobs=10,
        successful_normalizations=8,
        failed_normalizations=2,
        validation_errors=1,
        duplicates_removed=3,
        normalized_jobs=[],  # Simplified for testing
        processing_time_seconds=2.5,
        jobs_per_second=4.0,
        validation_error_details=[
            "Job at index 5: Missing required field 'id'",
            "Job at index 8: Invalid URL format"
        ]
    )


@pytest.fixture
def sample_normalization_statistics():
    """Create sample NormalizationStatistics for testing."""
    return NormalizationStatistics(
        total_jobs_processed=1000,
        total_successful_normalizations=950,
        total_failed_normalizations=50,
        total_duplicates_removed=150,
        jobs_by_source={
            "indeed": 400,
            "linkedin": 300,
            "glassdoor": 200,
            "ziprecruiter": 100
        },
        average_processing_time=1.5,
        average_throughput=66.67,
        first_processing_time=datetime.now(timezone.utc),
        last_processing_time=datetime.now(timezone.utc)
    )


@pytest.fixture
def mock_service():
    """Create mock JobNormalizerService for testing."""
    mock = AsyncMock()
    mock.is_running.return_value = True
    return mock


@pytest.fixture
def large_job_dataset():
    """Create large dataset of jobs for performance testing."""
    jobs = []
    base_time = datetime.now(timezone.utc)
    
    for i in range(100):
        jobs.append({
            'id': f'job_{i}',
            'title': f'Software Engineer {i}',
            'company': f'Tech Corp {i % 20}',  # 20 different companies
            'url': f'https://example.com/job/{i}',
            'date_posted': base_time.isoformat(),
            'location': ['San Francisco, CA', 'New York, NY', 'Remote', 'Seattle, WA'][i % 4],
            'salary': f'${80000 + (i * 1000)}'
        })
    
    return jobs


@pytest.fixture
def performance_test_config():
    """Create configuration optimized for performance testing."""
    return JobNormalizerServiceConfig(
        max_batch_size=1000,
        processing_timeout_seconds=60,
        enable_statistics=True
    )