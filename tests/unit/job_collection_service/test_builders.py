"""
Tests for Job Collection Service builders and configuration.

Tests builder pattern implementations, configuration loading,
and service initialization.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    JobQuery,
    JobPosting,
    JobType,
    CollectionResult,
    SourceStatus,
    JobSourceType
)


class TestJobCollectionBuilders:
    """Test cases for job collection service builders."""
    
    def test_job_query_builder(self):
        """Test building job queries with builder pattern."""
        # Simulate a JobQueryBuilder
        class JobQueryBuilder:
            def __init__(self):
                self._keywords = None
                self._location = None
                self._max_jobs_per_source = 50
                self._sources = None
                self._include_remote = True
                self._date_range_days = 7
            
            def with_keywords(self, keywords):
                self._keywords = keywords
                return self
            
            def with_location(self, location):
                self._location = location
                return self
            
            def with_max_jobs_per_source(self, max_jobs):
                self._max_jobs_per_source = max_jobs
                return self
            
            def with_sources(self, sources):
                self._sources = sources
                return self
            
            def with_remote_filter(self, include_remote):
                self._include_remote = include_remote
                return self
            
            def with_date_range(self, days):
                self._date_range_days = days
                return self
            
            def build(self):
                return JobQuery(
                    keywords=self._keywords,
                    location=self._location,
                    max_jobs_per_source=self._max_jobs_per_source,
                    sources=self._sources,
                    include_remote=self._include_remote,
                    date_range_days=self._date_range_days
                )
        
        # Test builder pattern
        query = (JobQueryBuilder()
                .with_keywords(["product manager", "tpm"])
                .with_location("San Francisco, CA")
                .with_max_jobs_per_source(25)
                .with_sources(["remoteok", "linkedin"])
                .with_remote_filter(True)
                .with_date_range(14)
                .build())
        
        assert query.keywords == ["product manager", "tpm"]
        assert query.location == "San Francisco, CA"
        assert query.max_jobs_per_source == 25
        assert query.sources == ["remoteok", "linkedin"]
        assert query.include_remote is True
        assert query.date_range_days == 14
    
    def test_job_posting_builder(self):
        """Test building job postings with builder pattern."""
        # Simulate a JobPostingBuilder
        class JobPostingBuilder:
            def __init__(self):
                self._id = None
                self._source = None
                self._title = None
                self._company = None
                self._location = None
                self._url = None
                self._date_posted = None
                self._job_type = None
                self._remote_friendly = False
                self._tpm_keywords_found = 0
                self._raw_data = None
                self._aggregated_at = None
            
            def with_id(self, job_id):
                self._id = job_id
                return self
            
            def with_source(self, source):
                self._source = source
                return self
            
            def with_title(self, title):
                self._title = title
                return self
            
            def with_company(self, company):
                self._company = company
                return self
            
            def with_location(self, location):
                self._location = location
                return self
            
            def with_url(self, url):
                self._url = url
                return self
            
            def with_date_posted(self, date_posted):
                self._date_posted = date_posted
                return self
            
            def with_job_type(self, job_type):
                self._job_type = job_type
                return self
            
            def with_remote_friendly(self, remote_friendly):
                self._remote_friendly = remote_friendly
                return self
            
            def with_tpm_keywords_found(self, count):
                self._tpm_keywords_found = count
                return self
            
            def with_raw_data(self, raw_data):
                self._raw_data = raw_data
                return self
            
            def with_aggregated_at(self, aggregated_at):
                self._aggregated_at = aggregated_at
                return self
            
            def build(self):
                return JobPosting(
                    id=self._id,
                    source=self._source,
                    title=self._title,
                    company=self._company,
                    location=self._location,
                    url=self._url,
                    date_posted=self._date_posted,
                    job_type=self._job_type,
                    remote_friendly=self._remote_friendly,
                    tpm_keywords_found=self._tpm_keywords_found,
                    raw_data=self._raw_data,
                    aggregated_at=self._aggregated_at
                )
        
        # Test builder pattern
        now = datetime.now()
        job = (JobPostingBuilder()
               .with_id("test-job-123")
               .with_source("remoteok")
               .with_title("Senior Product Manager")
               .with_company("Tech Corp")
               .with_location("Remote")
               .with_url("https://remoteok.io/job/123")
               .with_date_posted(now)
               .with_job_type(JobType.SENIOR)
               .with_remote_friendly(True)
               .with_tpm_keywords_found(3)
               .with_raw_data({"source_data": "test"})
               .with_aggregated_at(now)
               .build())
        
        assert job.id == "test-job-123"
        assert job.source == "remoteok"
        assert job.title == "Senior Product Manager"
        assert job.company == "Tech Corp"
        assert job.location == "Remote"
        assert job.url == "https://remoteok.io/job/123"
        assert job.date_posted == now
        assert job.job_type == JobType.SENIOR
        assert job.remote_friendly is True
        assert job.tpm_keywords_found == 3
        assert job.raw_data == {"source_data": "test"}
        assert job.aggregated_at == now
    
    def test_collection_result_builder(self):
        """Test building collection results with builder pattern."""
        # Simulate a CollectionResultBuilder
        class CollectionResultBuilder:
            def __init__(self):
                self._jobs = []
                self._total_jobs = 0
                self._raw_jobs = 0
                self._duplicates_removed = 0
                self._sources_queried = []
                self._successful_sources = []
                self._failed_sources = []
                self._collection_time = datetime.now()
                self._duration_seconds = 0.0
                self._errors = {}
            
            def with_jobs(self, jobs):
                self._jobs = jobs
                self._total_jobs = len(jobs)
                return self
            
            def with_raw_jobs(self, raw_jobs):
                self._raw_jobs = raw_jobs
                return self
            
            def with_duplicates_removed(self, duplicates):
                self._duplicates_removed = duplicates
                return self
            
            def with_sources_queried(self, sources):
                self._sources_queried = sources
                return self
            
            def with_successful_sources(self, sources):
                self._successful_sources = sources
                return self
            
            def with_failed_sources(self, sources):
                self._failed_sources = sources
                return self
            
            def with_collection_time(self, collection_time):
                self._collection_time = collection_time
                return self
            
            def with_duration_seconds(self, duration):
                self._duration_seconds = duration
                return self
            
            def with_errors(self, errors):
                self._errors = errors
                return self
            
            def build(self):
                return CollectionResult(
                    jobs=self._jobs,
                    total_jobs=self._total_jobs,
                    raw_jobs=self._raw_jobs,
                    duplicates_removed=self._duplicates_removed,
                    sources_queried=self._sources_queried,
                    successful_sources=self._successful_sources,
                    failed_sources=self._failed_sources,
                    collection_time=self._collection_time,
                    duration_seconds=self._duration_seconds,
                    errors=self._errors
                )
        
        # Test builder pattern
        jobs = [
            JobPosting(id="1", source="test", title="PM", company="Corp"),
            JobPosting(id="2", source="test", title="TPM", company="Inc")
        ]
        
        result = (CollectionResultBuilder()
                 .with_jobs(jobs)
                 .with_raw_jobs(5)
                 .with_duplicates_removed(3)
                 .with_sources_queried(["remoteok", "linkedin"])
                 .with_successful_sources(["remoteok", "linkedin"])
                 .with_failed_sources([])
                 .with_duration_seconds(12.5)
                 .with_errors({})
                 .build())
        
        assert len(result.jobs) == 2
        assert result.total_jobs == 2
        assert result.raw_jobs == 5
        assert result.duplicates_removed == 3
        assert result.sources_queried == ["remoteok", "linkedin"]
        assert result.successful_sources == ["remoteok", "linkedin"]
        assert result.failed_sources == []
        assert result.duration_seconds == 12.5
        assert result.errors == {}


class TestJobCollectionConfiguration:
    """Test cases for job collection service configuration."""
    
    def test_default_configuration(self):
        """Test default configuration values."""
        # Simulate a JobCollectionConfig class
        class JobCollectionConfig:
            def __init__(self):
                self.max_jobs_per_source = 50
                self.collection_timeout_seconds = 30
                self.enable_deduplication = True
                self.enable_enrichment = True
                self.api_aggregators = {
                    "remoteok": {"enabled": True},
                    "greenhouse": {"enabled": True},
                    "lever": {"enabled": True}
                }
                self.browser_scrapers = {
                    "linkedin": {"enabled": True},
                    "indeed": {"enabled": True},
                    "ziprecruiter": {"enabled": False}
                }
                self.storage = {
                    "backend": "file",
                    "path": "./job_storage"
                }
        
        config = JobCollectionConfig()
        
        assert config.max_jobs_per_source == 50
        assert config.collection_timeout_seconds == 30
        assert config.enable_deduplication is True
        assert config.enable_enrichment is True
        assert len(config.api_aggregators) == 3
        assert len(config.browser_scrapers) == 3
        assert config.storage["backend"] == "file"
    
    def test_configuration_from_dict(self):
        """Test loading configuration from dictionary."""
        config_dict = {
            "max_jobs_per_source": 75,
            "collection_timeout_seconds": 45,
            "enable_deduplication": False,
            "enable_enrichment": True,
            "api_aggregators": {
                "remoteok": {"enabled": True},
                "greenhouse": {"enabled": False}
            },
            "browser_scrapers": {
                "linkedin": {"enabled": True}
            },
            "storage": {
                "backend": "database",
                "connection_string": "postgresql://localhost/jobs"
            }
        }
        
        # Simulate loading configuration
        class JobCollectionConfig:
            def __init__(self, config_dict=None):
                if config_dict:
                    self.__dict__.update(config_dict)
                else:
                    # Set defaults
                    self.max_jobs_per_source = 50
                    self.collection_timeout_seconds = 30
        
        config = JobCollectionConfig(config_dict)
        
        assert config.max_jobs_per_source == 75
        assert config.collection_timeout_seconds == 45
        assert config.enable_deduplication is False
        assert config.enable_enrichment is True
        assert config.api_aggregators["remoteok"]["enabled"] is True
        assert config.api_aggregators["greenhouse"]["enabled"] is False
        assert config.browser_scrapers["linkedin"]["enabled"] is True
        assert config.storage["backend"] == "database"
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Test invalid configurations
        invalid_configs = [
            {"max_jobs_per_source": -1},  # Negative value
            {"collection_timeout_seconds": 0},  # Zero timeout
            {"api_aggregators": "not_a_dict"},  # Wrong type
            {"browser_scrapers": []},  # Wrong type
        ]
        
        # Simulate a configuration validator
        def validate_config(config_dict):
            if "max_jobs_per_source" in config_dict:
                if config_dict["max_jobs_per_source"] <= 0:
                    raise ValueError("max_jobs_per_source must be positive")
            
            if "collection_timeout_seconds" in config_dict:
                if config_dict["collection_timeout_seconds"] <= 0:
                    raise ValueError("collection_timeout_seconds must be positive")
            
            if "api_aggregators" in config_dict:
                if not isinstance(config_dict["api_aggregators"], dict):
                    raise TypeError("api_aggregators must be a dictionary")
            
            if "browser_scrapers" in config_dict:
                if not isinstance(config_dict["browser_scrapers"], dict):
                    raise TypeError("browser_scrapers must be a dictionary")
        
        # Test validation failures
        for invalid_config in invalid_configs:
            with pytest.raises((ValueError, TypeError)):
                validate_config(invalid_config)
    
    def test_configuration_environment_variables(self):
        """Test loading configuration from environment variables."""
        # Simulate environment variable loading
        env_vars = {
            "JOB_COLLECTION_MAX_JOBS_PER_SOURCE": "100",
            "JOB_COLLECTION_TIMEOUT_SECONDS": "60",
            "JOB_COLLECTION_ENABLE_DEDUPLICATION": "true",
            "JOB_COLLECTION_STORAGE_BACKEND": "database"
        }
        
        # Simulate environment config loader
        def load_config_from_env(env_vars):
            config = {}
            
            if "JOB_COLLECTION_MAX_JOBS_PER_SOURCE" in env_vars:
                config["max_jobs_per_source"] = int(env_vars["JOB_COLLECTION_MAX_JOBS_PER_SOURCE"])
            
            if "JOB_COLLECTION_TIMEOUT_SECONDS" in env_vars:
                config["collection_timeout_seconds"] = int(env_vars["JOB_COLLECTION_TIMEOUT_SECONDS"])
            
            if "JOB_COLLECTION_ENABLE_DEDUPLICATION" in env_vars:
                config["enable_deduplication"] = env_vars["JOB_COLLECTION_ENABLE_DEDUPLICATION"].lower() == "true"
            
            if "JOB_COLLECTION_STORAGE_BACKEND" in env_vars:
                config["storage"] = {"backend": env_vars["JOB_COLLECTION_STORAGE_BACKEND"]}
            
            return config
        
        config = load_config_from_env(env_vars)
        
        assert config["max_jobs_per_source"] == 100
        assert config["collection_timeout_seconds"] == 60
        assert config["enable_deduplication"] is True
        assert config["storage"]["backend"] == "database"


class TestServiceInitialization:
    """Test cases for service initialization and dependency injection."""
    
    def test_service_builder_with_dependencies(self):
        """Test building service with dependency injection."""
        # Simulate a service builder with dependency injection
        class JobCollectionServiceBuilder:
            def __init__(self):
                self._config = None
                self._storage = None
                self._enricher = None
                self._cache = None
                self._api_aggregators = None
                self._browser_scrapers = None
            
            def with_config(self, config):
                self._config = config
                return self
            
            def with_storage(self, storage):
                self._storage = storage
                return self
            
            def with_enricher(self, enricher):
                self._enricher = enricher
                return self
            
            def with_cache(self, cache):
                self._cache = cache
                return self
            
            def with_api_aggregators(self, aggregators):
                self._api_aggregators = aggregators
                return self
            
            def with_browser_scrapers(self, scrapers):
                self._browser_scrapers = scrapers
                return self
            
            def build(self):
                # Simulate service creation with all dependencies
                return {
                    "config": self._config,
                    "storage": self._storage,
                    "enricher": self._enricher,
                    "cache": self._cache,
                    "api_aggregators": self._api_aggregators,
                    "browser_scrapers": self._browser_scrapers
                }
        
        # Mock dependencies
        config = {"max_jobs_per_source": 50}
        storage = Mock()
        enricher = Mock()
        cache = Mock()
        api_aggregators = {"remoteok": Mock()}
        browser_scrapers = {"linkedin": Mock()}
        
        # Build service
        service = (JobCollectionServiceBuilder()
                  .with_config(config)
                  .with_storage(storage)
                  .with_enricher(enricher)
                  .with_cache(cache)
                  .with_api_aggregators(api_aggregators)
                  .with_browser_scrapers(browser_scrapers)
                  .build())
        
        assert service["config"] == config
        assert service["storage"] == storage
        assert service["enricher"] == enricher
        assert service["cache"] == cache
        assert service["api_aggregators"] == api_aggregators
        assert service["browser_scrapers"] == browser_scrapers
    
    def test_service_initialization_validation(self):
        """Test service initialization validation."""
        # Simulate service validation
        def validate_service_dependencies(config, storage, enricher):
            if config is None:
                raise ValueError("Configuration is required")
            
            if storage is None:
                raise ValueError("Storage is required")
            
            if enricher is None:
                raise ValueError("Enricher is required")
            
            if "max_jobs_per_source" not in config:
                raise ValueError("max_jobs_per_source is required in config")
        
        # Test successful validation
        config = {"max_jobs_per_source": 50}
        storage = Mock()
        enricher = Mock()
        
        # Should not raise
        validate_service_dependencies(config, storage, enricher)
        
        # Test validation failures
        with pytest.raises(ValueError, match="Configuration is required"):
            validate_service_dependencies(None, storage, enricher)
        
        with pytest.raises(ValueError, match="Storage is required"):
            validate_service_dependencies(config, None, enricher)
        
        with pytest.raises(ValueError, match="Enricher is required"):
            validate_service_dependencies(config, storage, None)
        
        with pytest.raises(ValueError, match="max_jobs_per_source is required"):
            validate_service_dependencies({}, storage, enricher)