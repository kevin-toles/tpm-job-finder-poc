# Job Aggregator Component

The Job Aggregator is a comprehensive orchestration service that coordinates multi-source job collection from APIs and browser scrapers. It serves as the central hub for collecting, normalizing, deduplicating, and enriching job postings from diverse sources into a unified pipeline.

## Architecture Overview

The job_aggregator follows a microservice-inspired architecture with clear separation of concerns:

```
job_aggregator/
├── main.py                      # JobAggregatorService - central orchestrator
├── aggregators/                 # API-based job sources
│   ├── adzuna.py                # Adzuna API integration
│   ├── ashby.py                 # Ashby ATS API integration
│   ├── careerjet.py             # Careerjet API integration
│   ├── greenhouse.py            # Greenhouse API integration
│   ├── jooble.py                # Jooble API integration
│   ├── lever.py                 # Lever API integration
│   ├── recruitee.py             # Recruitee API integration
│   ├── remoteok.py              # RemoteOK API integration
│   ├── smartrecruiters.py       # SmartRecruiters API integration
│   ├── usajobs.py               # USAJobs API integration
│   └── workable.py              # Workable API integration
├── cache/                       # Deduplication and caching logic
├── controllers/                 # Request handlers and API endpoints
├── data/                        # Data management and storage
├── scrapers/                    # Browser scraper integration
├── services/                    # Supporting services
│   └── job_aggregation_service.py  # Core aggregation logic
├── health.py                    # Health monitoring and metrics
├── requirements.txt             # Component dependencies
└── Dockerfile                   # Containerization config
```

## Core Components

### 1. JobAggregatorService (main.py)
**Purpose**: Central orchestration service coordinating all job collection activities
- **Multi-source coordination**: Manages both API and scraping sources
- **Async processing**: Concurrent job collection for optimal performance
- **Data normalization**: Standardizes job data across all sources
- **Intelligent deduplication**: SQLite-based cross-source duplicate detection
- **Enrichment integration**: Adds metadata and classification to job postings

### 2. API Aggregators (aggregators/)
**Purpose**: Connector implementations for job board APIs
- **RemoteOK**: Remote job board with high-quality tech positions
- **Greenhouse**: ATS integration for companies like Airbnb, Stripe, Slack
- **Lever**: Modern ATS with clean APIs (Shopify, Netflix, Uber)
- **Ashby**: Next-gen ATS with detailed job metadata
- **Workable**: SMB company job boards
- **SmartRecruiters**: Enterprise job aggregation platform
- **Additional APIs**: Adzuna, Careerjet, Jooble, USAJobs, Recruitee

### 3. Browser Scraper Integration (scrapers/)
**Purpose**: Coordinates with scraping_service for comprehensive coverage
- **Indeed**: Largest job board with 50M+ listings
- **LinkedIn**: Professional network job scraping
- **ZipRecruiter**: Aggregated postings with salary data
- **Glassdoor**: Company insights with job listings

### 4. Deduplication System (cache/)
**Purpose**: Cross-source duplicate detection and caching
- **SQLite persistence**: Maintains deduplication state across sessions
- **Fuzzy matching**: Handles variations in job titles and descriptions
- **Applied job tracking**: Prevents re-processing of already applied positions

### 5. Job Aggregation Service (services/)
**Purpose**: Core business logic for multi-source job collection
- **API connector management**: Initializes and coordinates API sources
- **Scraping service integration**: Manages browser-based collection
- **Error handling**: Robust error recovery and logging
- **Result consolidation**: Combines and normalizes results from all sources

## Public API

### JobAggregatorService

```python
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService

class JobAggregatorService:
    def __init__(self, config: Optional[Dict[str, Any]] = None)
    
    async def run_daily_aggregation(self, 
                                   search_params: Dict[str, Any],
                                   max_jobs_per_source: int = 50) -> List[Dict[str, Any]]
    
    async def collect_jobs(self,
                          keywords: List[str],
                          location: Optional[str] = None,
                          experience_level: Optional[str] = None,
                          max_jobs_per_source: int = 50,
                          sources: Optional[List[str]] = None) -> List[Dict[str, Any]]
    
    def _deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    
    def _enrich_job_data(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]
```

### JobAggregationService

```python
from tpm_job_finder_poc.job_aggregator.services.job_aggregation_service import JobAggregationService

class JobAggregationService:
    def __init__(self,
                 search_terms: List[str],
                 location: Optional[str] = None,
                 api_config: Optional[dict] = None,
                 scraping_sources: Optional[List[str]] = None)
    
    async def fetch_all_jobs(self) -> List[Dict[str, Any]]
    
    def deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]
```

## Configuration

### API Configuration
```python
api_config = {
    "remoteok": {
        "api_key": "your-api-key",
        "rate_limit": 60,
        "timeout": 30
    },
    "greenhouse": {
        "companies": ["airbnb", "stripe", "slack"],
        "rate_limit": 30
    },
    "adzuna": {
        "app_id": "your-app-id",
        "app_key": "your-app-key"
    },
    "careerjet": {
        "affiliate_id": "your-affiliate-id",
        "locales": ["en_US", "en_GB", "en_CA"]
    },
    "jooble": {
        "api_key": "your-jooble-key"
    },
    "usajobs": {
        "user_agent": "your-app-name",
        "api_key": "your-usajobs-key"
    },
    "smartrecruiters": {
        "companies": ["company1", "company2"]
    },
    "ashby": {
        "board_names": ["board1", "board2"]
    },
    "workable": {
        "subdomains": ["company1", "company2"]
    },
    "recruitee": {
        "subdomains": ["company1", "company2"]
    }
}
```

### Service Configuration
```python
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
```

## Usage Examples

### 1. Basic Job Collection
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

# CLI usage
python -m tpm_job_finder_poc.job_aggregator.main \
  --keywords "product manager" "technical product manager" \
  --location "Remote" \
  --max-jobs-per-source 25 \
  --output jobs.json
```

### 2. Daily Aggregation Workflow
```python
async def run_daily_search():
    service = JobAggregatorService()
    
    search_params = {
        "keywords": ["technical product manager", "TPM"],
        "location": "Remote",
        "experience_level": "senior"
    }
    
    jobs = await service.run_daily_aggregation(
        search_params=search_params,
        max_jobs_per_source=25
    )
    
    # Jobs are automatically deduplicated and enriched
    return jobs
```

### 3. Custom Source Configuration
```python
# API-only collection
api_service = JobAggregationService(
    search_terms=["product manager"],
    location="San Francisco",
    api_config={
        "remoteok": {"api_key": "key"},
        "greenhouse": {"companies": ["stripe"]}
    }
)

api_jobs = await api_service.fetch_all_jobs()

# Scraping-only collection
scraping_service = JobAggregationService(
    search_terms=["product manager"],
    location="San Francisco",
    scraping_sources=["indeed", "linkedin"]
)

scraped_jobs = await scraping_service.fetch_all_jobs()
```

### 4. Integration with Enrichment System
```python
from tpm_job_finder_poc.enrichment.orchestrators.multi_resume_intelligence_orchestrator import MultiResumeIntelligenceOrchestrator

async def collect_and_analyze_jobs():
    # Collect jobs
    aggregator = JobAggregatorService()
    jobs = await aggregator.collect_jobs(
        keywords=["technical product manager"],
        location="Remote"
    )
    
    # Enrich with intelligence
    orchestrator = MultiResumeIntelligenceOrchestrator()
    enriched_jobs = await orchestrator.process_jobs(jobs)
    
    return enriched_jobs
```

## Architecture Decisions

### 1. Multi-Source Strategy
- **API-first approach**: Prioritize structured data from APIs when available
- **Scraping fallback**: Use browser automation for comprehensive coverage
- **Unified interface**: Single service coordinates both collection methods
- **Async processing**: Concurrent collection for optimal performance

### 2. Deduplication Architecture
- **Cross-source detection**: Identify duplicates across different platforms
- **Fuzzy matching**: Handle variations in job titles and company names
- **Persistent caching**: SQLite-based storage maintains state across sessions
- **Applied job tracking**: Prevent re-processing of already applied positions

### 3. Error Handling Strategy
- **Graceful degradation**: Continue processing if individual sources fail
- **Comprehensive logging**: Track all errors for debugging and monitoring
- **Rate limit respect**: Built-in rate limiting for all API sources
- **Retry mechanisms**: Automatic retry for transient failures

### 4. Data Normalization
- **Standard schema**: Convert all job data to unified format
- **Enrichment integration**: Add classification and metadata
- **Quality scoring**: Basic job quality assessment
- **Source attribution**: Maintain source tracking for quality analysis

## Performance Characteristics

### Throughput
- **API Sources**: 500-2000 jobs/minute (depending on rate limits)
- **Scraping Sources**: 50-200 jobs/minute (browser-limited)
- **Concurrent Processing**: 5-10 parallel API connections
- **Deduplication**: <100ms per job using SQLite indexing

### Scalability
- **Horizontal scaling**: Independent API connectors
- **Memory efficiency**: Streaming job processing
- **Cache optimization**: SQLite with optimized indexing
- **Rate limit management**: Built-in backoff and throttling

## Error Handling

### Common Error Scenarios
```python
# API rate limiting
try:
    jobs = await aggregator.collect_jobs(keywords=["PM"])
except RateLimitError as e:
    logger.warning(f"Rate limited: {e}, retrying in {e.retry_after}s")
    await asyncio.sleep(e.retry_after)

# Network connectivity issues
except ConnectionError as e:
    logger.error(f"Network error: {e}")
    # Graceful degradation - continue with other sources

# Invalid API configuration
except ConfigurationError as e:
    logger.error(f"Config error: {e}")
    # Fall back to scraping sources only
```

### Error Recovery
- **Source isolation**: Failure of one source doesn't affect others
- **Automatic retry**: Built-in retry logic with exponential backoff
- **Fallback strategies**: Switch to alternative sources when primary fails
- **Health monitoring**: Real-time tracking of source availability

## Testing

### Unit Tests
```bash
# Test individual aggregators
pytest tests/unit/test_job_aggregator/test_aggregators/ -v

# Test core service
pytest tests/unit/test_job_aggregator/test_main.py -v

# Test deduplication
pytest tests/unit/test_job_aggregator/test_cache/ -v
```

### Integration Tests
```bash
# Test API integrations
pytest tests/integration/test_job_aggregator_api.py -v

# Test scraping integration
pytest tests/integration/test_job_aggregator_scraping.py -v

# Test end-to-end workflow
pytest tests/e2e/test_job_aggregator_workflow.py -v
```

### Mock Testing
```python
# Mock API responses for testing
from unittest.mock import patch, MagicMock

@patch('tpm_job_finder_poc.job_aggregator.aggregators.remoteok.RemoteOKConnector')
async def test_api_collection(mock_connector):
    mock_connector.fetch_jobs.return_value = [{"title": "PM", "company": "Test"}]
    
    service = JobAggregatorService()
    jobs = await service.collect_jobs(keywords=["PM"])
    
    assert len(jobs) > 0
    assert jobs[0]["title"] == "PM"
```

## Dependencies

### Core Dependencies
- **asyncio**: Async processing coordination
- **aiohttp**: HTTP client for API integrations
- **sqlite3**: Deduplication cache storage
- **concurrent.futures**: Parallel API processing
- **logging**: Comprehensive error tracking

### Internal Dependencies
- **scraping_service**: Browser automation integration
- **job_normalizer**: Job data standardization
- **cache.dedupe_cache**: Cross-source deduplication
- **models.job**: Job data models

### External APIs
- **RemoteOK API**: Remote job board access
- **Greenhouse API**: ATS job board integration
- **Lever API**: Modern ATS integration
- **Ashby API**: Next-gen ATS access
- **Additional APIs**: Adzuna, Careerjet, Jooble, USAJobs

## Security Considerations

### API Key Management
- **Environment variables**: Store API keys securely
- **Configuration isolation**: Separate dev/prod credentials
- **Rate limit compliance**: Respect API terms of service
- **Error handling**: Don't log sensitive credentials

### Data Privacy
- **PII handling**: Careful processing of personal information in job postings
- **Data retention**: Configurable retention policies
- **Secure transmission**: HTTPS for all API communications
- **Access logging**: Track data access for compliance

## Future Enhancements

### Planned Features
1. **Real-time streaming**: WebSocket-based live job feeds
2. **ML-powered deduplication**: Advanced similarity detection
3. **Quality scoring**: Automated job posting quality assessment
4. **Source health monitoring**: Real-time source availability tracking
5. **Custom aggregator plugins**: Extensible aggregator architecture

### Performance Improvements
1. **Distributed caching**: Redis-based deduplication cache
2. **Async database**: Replace SQLite with async-capable storage
3. **Connection pooling**: Optimized HTTP connection management
4. **Batch processing**: Bulk job processing for efficiency

### Integration Enhancements
1. **Webhook support**: Real-time job notifications
2. **GraphQL API**: Flexible job data querying
3. **Event streaming**: Kafka-based job event distribution
4. **Monitoring integration**: Prometheus metrics export