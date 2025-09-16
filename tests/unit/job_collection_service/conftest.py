"""
Test configuration for job collection service tests.

Sets up fixtures and utilities needed across all job collection service tests.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from unittest.mock import AsyncMock, Mock

from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    JobPosting,
    JobQuery,
    JobType,
    CollectionResult,
    SourceStatus,
    JobSourceType,
    IJobCollectionService
)


@pytest.fixture
def sample_job_posting():
    """Create a sample job posting for testing."""
    return JobPosting(
        id="test-job-123",
        source="test_source",
        title="Senior Product Manager",
        company="Tech Corp",
        location="San Francisco, CA",
        url="https://example.com/job/123",
        date_posted=datetime.now(),
        job_type=JobType.SENIOR,
        remote_friendly=True,
        tpm_keywords_found=3,
        raw_data={"test": "data"},
        aggregated_at=datetime.now()
    )


@pytest.fixture
def sample_job_postings():
    """Create multiple sample job postings for testing."""
    now = datetime.now()
    return [
        JobPosting(
            id="job-1",
            source="remoteok",
            title="Product Manager",
            company="Startup Inc",
            location="Remote",
            url="https://remoteok.io/job/1",
            date_posted=now - timedelta(hours=2),
            job_type=JobType.MID_LEVEL,
            remote_friendly=True,
            tpm_keywords_found=2
        ),
        JobPosting(
            id="job-2", 
            source="linkedin",
            title="Technical Program Manager",
            company="Big Tech",
            location="Seattle, WA",
            url="https://linkedin.com/job/2",
            date_posted=now - timedelta(hours=1),
            job_type=JobType.SENIOR,
            remote_friendly=False,
            tpm_keywords_found=4
        ),
        JobPosting(
            id="job-3",
            source="indeed",
            title="Junior Product Owner",
            company="Small Corp",
            location="New York, NY",
            url="https://indeed.com/job/3",
            date_posted=now - timedelta(minutes=30),
            job_type=JobType.ENTRY_LEVEL,
            remote_friendly=False,
            tpm_keywords_found=1
        )
    ]


@pytest.fixture
def sample_job_query():
    """Create a sample job query for testing."""
    return JobQuery(
        keywords=["product manager", "tpm"],
        location="San Francisco, CA",
        max_jobs_per_source=25,
        sources=["remoteok", "linkedin", "indeed"],
        include_remote=True,
        date_range_days=7
    )


@pytest.fixture
def sample_collection_result(sample_job_postings):
    """Create a sample collection result for testing."""
    now = datetime.now()
    return CollectionResult(
        jobs=sample_job_postings,
        total_jobs=len(sample_job_postings),
        raw_jobs=len(sample_job_postings) + 2,  # Simulate duplicates removed
        duplicates_removed=2,
        sources_queried=["remoteok", "linkedin", "indeed"],
        successful_sources=["remoteok", "linkedin", "indeed"],
        failed_sources=[],
        collection_time=now,
        duration_seconds=15.5,
        errors={}
    )


@pytest.fixture
def sample_source_statuses():
    """Create sample source status data for testing."""
    now = datetime.now()
    return [
        SourceStatus(
            name="remoteok",
            type=JobSourceType.API_AGGREGATOR,
            enabled=True,
            healthy=True,
            last_check=now - timedelta(minutes=5),
            jobs_collected_today=45
        ),
        SourceStatus(
            name="linkedin",
            type=JobSourceType.BROWSER_SCRAPER,
            enabled=True,
            healthy=True,
            last_check=now - timedelta(minutes=3),
            jobs_collected_today=32
        ),
        SourceStatus(
            name="indeed",
            type=JobSourceType.BROWSER_SCRAPER,
            enabled=False,
            healthy=False,
            last_check=now - timedelta(hours=1),
            error_message="Connection timeout",
            jobs_collected_today=0
        )
    ]


@pytest.fixture
def mock_job_storage():
    """Create a mock job storage for testing."""
    storage = AsyncMock()
    storage.store_job.return_value = True
    storage.store_jobs.return_value = 3
    storage.get_job.return_value = None
    storage.search_jobs.return_value = []
    storage.delete_job.return_value = True
    storage.get_storage_stats.return_value = {
        "total_jobs": 1250,
        "jobs_today": 45,
        "storage_size_mb": 15.2
    }
    return storage


@pytest.fixture 
def mock_job_enricher():
    """Create a mock job enricher for testing."""
    enricher = Mock()
    enricher.classify_job_type.return_value = JobType.MID_LEVEL
    enricher.detect_remote_work.return_value = True
    enricher.count_tpm_keywords.return_value = 2
    enricher.enrich_job.side_effect = lambda job: job  # Return job unchanged
    return enricher


@pytest.fixture
def mock_dedupe_cache():
    """Create a mock deduplication cache for testing."""
    cache = Mock()
    cache.is_duplicate.return_value = False
    cache.add.return_value = None
    return cache


@pytest.fixture
def mock_api_aggregators():
    """Create mock API aggregators for testing."""
    aggregators = {}
    
    # RemoteOK mock
    remoteok = Mock()
    remoteok.fetch_jobs.return_value = [
        {"id": "remote-1", "position": "Product Manager", "company": "Remote Corp"}
    ]
    aggregators["remoteok"] = remoteok
    
    # Greenhouse mock
    greenhouse = Mock()
    greenhouse.fetch_since.return_value = [
        {"id": "gh-1", "title": "TPM", "company_name": "Greenhouse Co"}
    ]
    aggregators["greenhouse"] = greenhouse
    
    return aggregators


@pytest.fixture
def mock_browser_scrapers():
    """Create mock browser scrapers for testing."""
    scrapers = {}
    
    # LinkedIn mock
    linkedin = AsyncMock()
    linkedin.initialize.return_value = True
    linkedin.fetch_jobs.return_value = [
        Mock(
            id="li-1",
            source="linkedin",
            title="Senior PM",
            company="LinkedIn Corp",
            location="SF",
            url="https://linkedin.com/job/li-1",
            date_posted=datetime.now(),
            raw_data={"source": "linkedin"}
        )
    ]
    linkedin.cleanup.return_value = None
    scrapers["linkedin"] = linkedin
    
    # Indeed mock  
    indeed = AsyncMock()
    indeed.initialize.return_value = True
    indeed.fetch_jobs.return_value = [
        Mock(
            id="indeed-1",
            source="indeed", 
            title="Product Owner",
            company="Indeed Inc",
            location="Austin, TX",
            url="https://indeed.com/job/indeed-1",
            date_posted=datetime.now(),
            raw_data={"source": "indeed"}
        )
    ]
    indeed.cleanup.return_value = None
    scrapers["indeed"] = indeed
    
    return scrapers


@pytest.fixture
def job_collection_config():
    """Create sample configuration for job collection service."""
    return {
        "max_jobs_per_source": 50,
        "collection_timeout_seconds": 30,
        "enable_deduplication": True,
        "enable_enrichment": True,
        "api_aggregators": {
            "remoteok": {"enabled": True},
            "greenhouse": {"enabled": True, "companies": ["test-company"]},
            "lever": {"enabled": False}
        },
        "browser_scrapers": {
            "linkedin": {"enabled": True},
            "indeed": {"enabled": True},
            "ziprecruiter": {"enabled": False}
        },
        "storage": {
            "backend": "file",
            "path": "/tmp/test_jobs"
        }
    }


class MockJobCollectionService:
    """Mock implementation of IJobCollectionService for testing."""
    
    def __init__(self, config=None, storage=None, enricher=None):
        self.config = config or {}
        self.storage = storage
        self.enricher = enricher
        self._enabled_sources = set(["remoteok", "linkedin", "indeed"])
        
    async def collect_jobs(self, query: JobQuery) -> CollectionResult:
        """Mock job collection."""
        # Special case for empty results test
        if query.keywords and "nonexistent-keyword-xyz" in query.keywords:
            now = datetime.now()
            return CollectionResult(
                jobs=[],
                total_jobs=0,
                raw_jobs=0,
                duplicates_removed=0,
                sources_queried=query.sources or list(self._enabled_sources),
                successful_sources=query.sources or list(self._enabled_sources),
                failed_sources=[],
                collection_time=now,
                duration_seconds=1.5,
                errors={}
            )
        
        # Return sample data based on query
        now = datetime.now()
        jobs = [
            JobPosting(
                id=f"mock-{i}",
                source="mock_source",
                title=f"Mock Job {i}",
                company=f"Company {i}",
                location=query.location or "Remote",
                url=f"https://example.com/job/{i}",
                date_posted=now - timedelta(hours=i),
                job_type=JobType.MID_LEVEL,
                remote_friendly=query.include_remote,
                tpm_keywords_found=len(query.keywords) if query.keywords else 0
            )
            for i in range(min(query.max_jobs_per_source, 3))
        ]
        
        return CollectionResult(
            jobs=jobs,
            total_jobs=len(jobs),
            raw_jobs=len(jobs),
            duplicates_removed=0,
            sources_queried=query.sources or list(self._enabled_sources),
            successful_sources=query.sources or list(self._enabled_sources),
            failed_sources=[],
            collection_time=now,
            duration_seconds=1.5,
            errors={}
        )
    
    async def run_daily_aggregation(self, query: JobQuery) -> CollectionResult:
        """Mock daily aggregation."""
        return await self.collect_jobs(query)
    
    async def get_source_statuses(self) -> List[SourceStatus]:
        """Mock source statuses."""
        now = datetime.now()
        return [
            SourceStatus(
                name=source,
                type=JobSourceType.API_AGGREGATOR,
                enabled=source in self._enabled_sources,
                healthy=True,
                last_check=now - timedelta(minutes=5),
                jobs_collected_today=25
            )
            for source in ["remoteok", "linkedin", "indeed"]
        ]
    
    async def enable_source(self, source_name: str) -> bool:
        """Mock enable source."""
        self._enabled_sources.add(source_name)
        return True
    
    async def disable_source(self, source_name: str) -> bool:
        """Mock disable source."""
        self._enabled_sources.discard(source_name)
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Mock health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "sources_enabled": len(self._enabled_sources),
            "sources_healthy": len(self._enabled_sources)
        }
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Mock collection stats."""
        return {
            "total_jobs_collected": 1250,
            "jobs_collected_today": 45,
            "active_sources": len(self._enabled_sources),
            "average_collection_time": 12.5
        }


@pytest.fixture
def mock_job_collection_service(job_collection_config, mock_job_storage, mock_job_enricher):
    """Create a mock job collection service for testing."""
    return MockJobCollectionService(
        config=job_collection_config,
        storage=mock_job_storage,
        enricher=mock_job_enricher
    )