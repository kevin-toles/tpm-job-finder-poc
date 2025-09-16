# Job Collection Service

A production-ready microservice for collecting job postings from multiple sources including API aggregators and browser scrapers.

## Features

- **Multi-Source Collection**: Supports API aggregators (RemoteOK, Greenhouse, Lever) and browser scrapers (Indeed, LinkedIn)
- **Job Enrichment**: Automatic job classification, remote detection, TPM scoring, and market analysis
- **Deduplication**: Smart deduplication based on title, company, and URL similarity
- **Flexible Storage**: File-based JSON storage with search indexing and statistics
- **REST API**: Complete FastAPI-based REST API with async support
- **CLI Interface**: Rich command-line interface for all operations
- **Health Monitoring**: Source health checks and collection statistics
- **Configuration Management**: Environment variables, file-based, and programmatic configuration
- **Production Ready**: Comprehensive error handling, logging, and monitoring

## Architecture

```
job_collection_service/
├── service.py          # Core service implementation
├── storage.py          # File-based JSON storage
├── enricher.py         # Job metadata enrichment
├── config.py           # Configuration management
├── api.py              # REST API endpoints
├── builders.py         # Dependency injection
├── main.py             # CLI interface
└── __init__.py         # Module exports
```

## Quick Start

### Using the Service Programmatically

```python
from tpm_job_finder_poc.job_collection_service import create_development_service
from tpm_job_finder_poc.shared.contracts.job_collection_service import JobQuery

# Create service
service = create_development_service(enable_sources=['remoteok'])

# Collect jobs
query = JobQuery(
    keywords="Technical Project Manager",
    location="San Francisco",
    remote_only=True,
    max_results=50
)

result = await service.collect_jobs(query=query)
print(f"Collected {len(result.jobs)} jobs")
```

### Using the CLI

```bash
# Collect jobs
python -m tpm_job_finder_poc.job_collection_service.main collect "Technical Project Manager" --remote-only --max-jobs 50

# Search stored jobs
python -m tpm_job_finder_poc.job_collection_service.main search --query "project manager" --remote-only

# Check source status
python -m tpm_job_finder_poc.job_collection_service.main sources

# Start API server
python -m tpm_job_finder_poc.job_collection_service.main serve --port 8000
```

### Using the REST API

```bash
# Start the API server
python -m tpm_job_finder_poc.job_collection_service.main serve

# Collect jobs via API
curl -X POST "http://localhost:8000/collect" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Technical Project Manager",
    "remote_only": true,
    "max_jobs": 50
  }'

# Get stored jobs
curl "http://localhost:8000/jobs?remote_only=true&limit=10"

# Check health
curl "http://localhost:8000/health"
```

## Configuration

### Environment Variables

```bash
# General settings
export JOB_COLLECTION_MAX_JOBS_PER_SOURCE=50
export JOB_COLLECTION_TIMEOUT_SECONDS=30
export JOB_COLLECTION_ENABLE_DEDUPLICATION=true
export JOB_COLLECTION_ENABLE_ENRICHMENT=true

# Storage
export JOB_COLLECTION_STORAGE_BACKEND=file
export JOB_COLLECTION_STORAGE_PATH=./job_storage

# Sources
export JOB_COLLECTION_ENABLE_REMOTEOK=true
export JOB_COLLECTION_ENABLE_GREENHOUSE=false
export JOB_COLLECTION_ENABLE_INDEED=false
```

### Configuration File (JSON)

```json
{
  "max_jobs_per_source": 50,
  "collection_timeout_seconds": 30,
  "enable_deduplication": true,
  "enable_enrichment": true,
  "api_aggregators": {
    "remoteok": {"enabled": true},
    "greenhouse": {"enabled": false},
    "lever": {"enabled": false}
  },
  "browser_scrapers": {
    "indeed": {"enabled": false},
    "linkedin": {"enabled": false}
  },
  "storage": {
    "backend": "file",
    "path": "./job_storage"
  },
  "enrichment": {
    "enable_job_classification": true,
    "enable_remote_detection": true,
    "enable_tpm_scoring": true
  }
}
```

### Programmatic Configuration

```python
from tpm_job_finder_poc.job_collection_service import JobCollectionConfig, create_job_collection_service

# Create configuration
config = JobCollectionConfig(
    max_jobs_per_source=100,
    enable_deduplication=True,
    enable_enrichment=True
)

# Enable specific sources
config.enable_source('remoteok')
config.enable_source('greenhouse')

# Create service with config
service = create_job_collection_service(config_dict=config.to_dict())
```

## API Endpoints

### Job Collection

- `POST /collect` - Collect jobs based on query
- `GET /jobs` - Get stored jobs with filtering
- `GET /jobs/{job_id}` - Get specific job by ID
- `POST /background-collect` - Start background collection
- `DELETE /jobs` - Clear all stored jobs

### Source Management

- `GET /sources` - List available sources and status
- `PUT /sources/{source_name}` - Configure a source

### Monitoring

- `GET /health` - Health check with source status
- `GET /statistics` - Collection statistics

### API Documentation

When running the API server, visit `http://localhost:8000/docs` for interactive API documentation.

## Job Enrichment

The service automatically enriches collected jobs with:

- **Job Classification**: Categorizes jobs (Engineering, Management, Sales, etc.)
- **Remote Detection**: Identifies remote work opportunities
- **TPM Scoring**: Scores relevance for Technical Project Manager roles
- **Market Analysis**: Provides market insights and trends

## Storage

Jobs are stored in JSON format with the following structure:

```
job_storage/
├── jobs/           # Individual job files
├── indices/        # Search indices
└── metadata/       # Collection metadata
```

## Health Monitoring

The service provides comprehensive health monitoring:

- **Source Health**: Individual source availability and performance
- **Collection Statistics**: Success rates, error counts, timing metrics
- **System Health**: Overall service status

## Error Handling

The service includes robust error handling:

- **Source Errors**: Graceful handling of individual source failures
- **Network Errors**: Retry logic with exponential backoff
- **Configuration Errors**: Validation and helpful error messages
- **Storage Errors**: Fallback mechanisms and data integrity checks

## Development

### Running Tests

```bash
# Run all tests
pytest tests/unit/job_collection_service/

# Run specific test
pytest tests/unit/job_collection_service/test_service.py

# Run with coverage
pytest tests/unit/job_collection_service/ --cov
```

### Development Setup

```python
from tpm_job_finder_poc.job_collection_service import create_development_service

# Create development service with minimal sources
service = create_development_service(
    enable_sources=['remoteok'],
    storage_path='./dev_storage'
)
```

### Production Deployment

```python
from tpm_job_finder_poc.job_collection_service import create_production_service

# Create production service (uses environment variables)
service = create_production_service()

# Or with configuration file
service = create_production_service(config_file_path='/etc/job_collection/config.json')
```

## Integration

### With Job Aggregator

The service integrates with the existing job aggregator:

```python
from tpm_job_finder_poc.job_aggregator.main import UnifiedJobAggregator
from tpm_job_finder_poc.job_collection_service import JobCollectionService

# The service uses the unified aggregator internally
# No additional integration required
```

### With Scraping Service

Browser scraping is handled through the scraping service:

```python
# Browser scrapers are automatically integrated
# Enable via configuration
config.enable_source('indeed')
config.enable_source('linkedin')
```

## Monitoring and Observability

### Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('tpm_job_finder_poc.job_collection_service')
```

### Metrics

The service exposes metrics through the `/statistics` endpoint:

- Collection counts by source
- Success/failure rates
- Response times
- Storage statistics

### Health Checks

Use the `/health` endpoint for monitoring:

```bash
# Check health
curl http://localhost:8000/health

# Use in monitoring systems
if curl -f http://localhost:8000/health; then
  echo "Service healthy"
else
  echo "Service unhealthy"
fi
```

## Contributing

1. Follow the established patterns from the audit service
2. Add comprehensive tests for new features
3. Update documentation
4. Ensure all tests pass

## License

This service is part of the TPM Job Finder POC project.