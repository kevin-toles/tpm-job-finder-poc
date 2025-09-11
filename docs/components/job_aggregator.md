# Job Aggregator Service

The JobAggregatorService is the central orchestration service that coordinates multi-source job collection, intelligent deduplication, and workflow automation. It serves as the primary interface for collecting jobs from both API sources and browser scrapers.

## Architecture Overview

The job aggregator follows a microservice-inspired architecture with clear separation of concerns:

```
job_aggregator/
├── main.py                      # JobAggregatorService - central orchestrator
├── aggregators/                 # API-based job sources
│   ├── ashby_aggregator.py      # Ashby API integration
│   ├── greenhouse_aggregator.py # Greenhouse API integration
│   ├── lever_aggregator.py      # Lever API integration
│   ├── remoteok_aggregator.py   # RemoteOK API integration
│   ├── smartrecruiters_aggregator.py # SmartRecruiters API
│   └── workable_aggregator.py   # Workable API integration
├── cache/                       # Deduplication and caching
├── controllers/                 # Request handlers and API endpoints
├── scrapers/                    # Browser scraper integration
├── services/                    # Supporting services
└── data/                        # Data management and storage
```

## Core Features

### 1. Multi-Source Job Collection
- **API Sources**: RemoteOK, Greenhouse, Lever, Ashby, Workable, SmartRecruiters
- **Browser Scrapers**: Indeed, LinkedIn, ZipRecruiter, Greenhouse (via scraping_service_v2)
- **Unified Interface**: Single interface for all job sources
- **Async Processing**: Concurrent job collection for performance

### 2. Intelligent Deduplication
- **SQLite-based Caching**: Persistent deduplication across sessions
- **Fuzzy Matching**: Handle variations in job titles and descriptions
- **Cross-Source Detection**: Identify duplicates across different platforms
- **Applied Job Tracking**: Track jobs already applied to

### 3. Health Monitoring
- **Service Status**: Real-time health checks for all sources
- **Error Tracking**: Comprehensive error logging and recovery
- **Performance Metrics**: Collection speed and success rates
- **Rate Limit Management**: Respect API and scraping limits

### 4. Configuration Management
- **Flexible Configuration**: JSON-based configuration system
- **Source Selection**: Enable/disable specific job sources
- **Rate Limiting**: Configurable limits per source
- **Output Customization**: Multiple output formats and destinations

## JobAggregatorService API

### Basic Usage

```python
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService

# Initialize service
service = JobAggregatorService()

# Collect jobs with basic parameters
jobs = await service.collect_jobs(
    keywords=["product manager", "technical product manager"],
    location="Remote",
    max_jobs_per_source=50
)

# Health check
health_status = await service.health_check()
```

### Advanced Configuration

```python
# Custom configuration
config = {
    "sources": {
        "api_sources": ["remoteok", "greenhouse", "lever"],
        "scraping_sources": ["indeed", "linkedin"],
        "disabled_sources": ["ziprecruiter"]
    },
    "limits": {
        "max_jobs_per_source": 25,
        "total_max_jobs": 200,
        "timeout_seconds": 300
    },
    "deduplication": {
        "enabled": True,
        "similarity_threshold": 0.8,
        "cache_expiry_hours": 24
    }
}

service = JobAggregatorService(config=config)
```

## API Aggregators

### 1. RemoteOK Aggregator (`aggregators/remoteok_aggregator.py`)
**Features:**
- Real-time job feed access
- Location and technology filtering
- Salary information extraction
- Company metadata collection

**Configuration:**
```json
{
  "remoteok": {
    "enabled": true,
    "api_key": "your-api-key",
    "rate_limit": 60,
    "timeout": 30,
    "tags": ["product-manager", "technical-manager"]
  }
}
```

### 2. Greenhouse Aggregator (`aggregators/greenhouse_aggregator.py`)
**Features:**
- Public job board API access
- Department and location filtering
- Company-specific board scraping
- Rich job metadata

**Configuration:**
```json
{
  "greenhouse": {
    "enabled": true,
    "companies": ["airbnb", "stripe", "slack"],
    "rate_limit": 30,
    "include_closed": false
  }
}
```

### 3. Lever Aggregator (`aggregators/lever_aggregator.py`)
**Features:**
- Public postings API
- Team and commitment filtering
- Location-based search
- Application link extraction

### 4. Additional Aggregators
- **Ashby**: Modern ATS with GraphQL API
- **Workable**: Job board API with advanced filtering
- **SmartRecruiters**: Enterprise recruiting platform API

## Browser Scraper Integration

The JobAggregatorService integrates with the scraping_service_v2 for browser-based job collection:

### Supported Platforms
- **Indeed**: Job search and extraction
- **LinkedIn**: Professional network job scraping
- **ZipRecruiter**: Job board scraping
- **Greenhouse**: Company career pages

### Integration Example
```python
# Service automatically coordinates API and scraping sources
jobs = await service.collect_jobs(
    keywords=["senior product manager"],
    location="San Francisco",
    sources={
        "api_sources": ["remoteok", "lever"],
        "scraping_sources": ["indeed", "linkedin"]
    }
)
```

## Deduplication System

### Cache-Based Deduplication
The system uses SQLite-based caching for intelligent job deduplication:

```python
from tpm_job_finder_poc.job_aggregator.cache import DedupeCache

cache = DedupeCache()

# Check if job is duplicate
is_duplicate = cache.is_duplicate(job_data)

# Add job to cache
cache.add_job(job_data)

# Get cache statistics
stats = cache.get_statistics()
```

### Applied Job Tracking
Track jobs that have been applied to prevent re-application:

```python
from tpm_job_finder_poc.cache.applied_tracker import AppliedTracker

tracker = AppliedTracker()

# Mark job as applied
tracker.mark_applied(job_id, application_date)

# Check if already applied
already_applied = tracker.is_applied(job_id)
```

## Configuration Files

### Main Configuration (`config/job_aggregator_config.json`)
```json
{
  "sources": {
    "api_sources": {
      "remoteok": {
        "enabled": true,
        "rate_limit": 60,
        "timeout": 30
      },
      "greenhouse": {
        "enabled": true,
        "rate_limit": 30,
        "companies": ["default"]
      },
      "lever": {
        "enabled": true,
        "rate_limit": 30
      }
    },
    "scraping_sources": {
      "indeed": {
        "enabled": true,
        "rate_limit": 10
      },
      "linkedin": {
        "enabled": true,
        "rate_limit": 5,
        "auth_required": false
      }
    }
  },
  "deduplication": {
    "enabled": true,
    "similarity_threshold": 0.8,
    "cache_database": "dedupe_cache.db"
  },
  "output": {
    "formats": ["json", "excel"],
    "directory": "./output/",
    "include_metadata": true
  }
}
```

### Scraper-Specific Configuration
Integration with scraping_service_v2 configuration:

```json
{
  "scraping_service": {
    "rate_limits": {
      "indeed": 10,
      "linkedin": 5,
      "ziprecruiter": 10,
      "greenhouse": 15
    },
    "browser_config": {
      "headless": true,
      "timeout": 30,
      "user_agent_rotation": true
    },
    "anti_detection": {
      "enabled": true,
      "delay_range": [1, 3],
      "viewport_randomization": true
    }
  }
}
```

## Health Monitoring

### Service Health Checks
```python
# Check overall service health
health = await service.health_check()
print(f"Status: {health.status}")
print(f"Sources: {health.sources}")
print(f"Errors: {health.errors}")

# Check individual source health
api_health = await service.check_api_sources()
scraper_health = await service.check_scraping_sources()
```

### Monitoring Metrics
- **Collection Rate**: Jobs collected per minute
- **Success Rate**: Percentage of successful requests
- **Error Rate**: Request failures and types
- **Deduplication Rate**: Percentage of duplicates found
- **Source Availability**: API and scraper uptime

## Usage Examples

### 1. Basic Job Collection
```bash
# CLI usage
python -m tpm_job_finder_poc.job_aggregator.main \
  --keywords "product manager" "technical product manager" \
  --location "Remote" \
  --max-jobs-per-source 25 \
  --output jobs.json
```

### 2. Programmatic Usage
```python
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService

async def collect_tpm_jobs():
    service = JobAggregatorService()
    
    jobs = await service.collect_jobs(
        keywords=["technical product manager", "senior PM"],
        location="San Francisco Bay Area",
        experience_level="senior",
        max_jobs_per_source=50,
        sources=["remoteok", "greenhouse", "indeed", "linkedin"]
    )
    
    print(f"Collected {len(jobs)} jobs")
    return jobs
```

### 3. Integration with Enrichment
```python
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
from tpm_job_finder_poc.enrichment.orchestrator import EnrichmentOrchestrator

async def collect_and_enrich():
    # Collect jobs
    aggregator = JobAggregatorService()
    jobs = await aggregator.collect_jobs(keywords=["product manager"])
    
    # Enrich jobs
    enricher = EnrichmentOrchestrator()
    enriched_jobs = []
    
    for job in jobs:
        enriched_job = await enricher.enrich_job(job)
        enriched_jobs.append(enriched_job)
    
    return enriched_jobs
```

## Error Handling

### Retry Logic
```python
# Built-in retry logic for failed requests
config = {
    "retry": {
        "max_attempts": 3,
        "backoff_factor": 2,
        "retry_on": ["timeout", "connection_error", "rate_limit"]
    }
}
```

### Error Recovery
```python
# Graceful handling of source failures
try:
    jobs = await service.collect_jobs(keywords=["PM"])
except SourceUnavailableError as e:
    print(f"Source {e.source} unavailable, continuing with others")
    jobs = await service.collect_jobs(
        keywords=["PM"], 
        exclude_sources=[e.source]
    )
```

## Performance Optimization

### Async Processing
- Concurrent collection from multiple sources
- Non-blocking I/O for API requests
- Parallel processing of job batches

### Caching Strategy
- SQLite-based job deduplication cache
- Response caching for API calls
- Intelligent cache invalidation

### Rate Limiting
- Respectful rate limiting for all sources
- Burst protection and smoothing
- Adaptive rate adjustment based on response times

## Testing

### Unit Tests
```bash
# Run aggregator-specific tests
python -m pytest tests/unit/test_job_aggregator/ -v
```

### Integration Tests
```bash
# Test API integrations
python -m pytest tests/integration/test_api_aggregators.py -v

# Test scraper integrations
python -m pytest tests/integration/test_scraper_integration.py -v
```

### End-to-End Tests
```bash
# Test complete workflows
python -m pytest tests/e2e/test_job_collection_e2e.py -v
```

## Future Enhancements

- **Machine Learning**: Smart job ranking and recommendation
- **Real-Time Processing**: Stream processing for live job updates
- **Advanced Analytics**: Detailed job market analytics
- **Company Intelligence**: Enhanced company data and insights
- **Custom Sources**: Framework for adding new job sources

---

_Last updated: January 2025 - Production-ready job aggregation service with 70+ tests passing_
