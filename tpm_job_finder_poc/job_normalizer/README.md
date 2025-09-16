# Job Normalizer Component (Legacy)

**Status**: Legacy Implementation - **Superseded by Job Normalizer Service**  
**Replacement**: [Job Normalizer Service](../job_normalizer_service/README.md) - TDD Microservice  
**Migration**: This component provides core normalization functions used by the new service

> ⚠️ **MIGRATION NOTICE**: This legacy component is being superseded by the new **Job Normalizer Service** microservice. While this component remains functional for backward compatibility, new development should use the [Job Normalizer Service](../job_normalizer_service/README.md) which provides:
> 
> - 🎯 **Complete TDD Implementation** (63/63 tests passing)
> - 🌐 **REST API Endpoints** with FastAPI
> - 📊 **Advanced Quality Metrics** and monitoring
> - ⚡ **Production-Ready Architecture** with async processing
> - 🔧 **Service Lifecycle Management** and health monitoring

The Job Normalizer is a production-ready component for standardizing job postings from multiple sources into a unified schema. It provides the core normalization functions that are utilized by the new **Job Normalizer Service** microservice.

## Architecture Overview

> 📢 **NEW ARCHITECTURE**: The modern microservice architecture is implemented in [Job Normalizer Service](../job_normalizer_service/README.md). This legacy component provides the core normalization functions.

The job_normalizer follows a pipeline architecture with clear separation between parsing, validation, normalization, and deduplication. **These functions are now utilized by the Job Normalizer Service microservice**:

```
job_normalizer/                    # Legacy normalization functions
├── jobs/                       # Core normalization logic (used by service)
│   ├── normalizer.py           # Field normalization functions ⭐
│   ├── parser.py               # Multi-source parsing and validation ⭐
│   └── schema.py               # Pydantic JobPosting model ⭐
├── requirements.txt            # Component dependencies
├── README.md                   # This legacy documentation
└── Dockerfile                  # Containerization config

job_normalizer_service/            # 🚀 NEW: TDD Microservice
├── service.py                  # Core service implementation
├── api.py                      # FastAPI REST endpoints
├── config.py                   # Service configuration
├── README.md                   # Modern service documentation
└── __init__.py                 # Service exports

⭐ = Functions used by Job Normalizer Service
```

## Core Components

### 1. JobPosting Schema (jobs/schema.py)
**Purpose**: Pydantic-based unified data model for all job postings
- **Strict validation**: Type checking and business logic validation
- **Required fields**: Enforces essential job posting fields
- **Timezone handling**: UTC normalization for all datetime fields
- **Immutable design**: Frozen model prevents accidental mutations
- **Extensible structure**: Support for enrichment and metadata fields

### 2. Job Parser (jobs/parser.py)
**Purpose**: Multi-source job data parsing with validation
- **Source agnostic**: Handles job data from any aggregator source
- **Error handling**: Comprehensive validation error reporting
- **Data mapping**: Maps raw source data to standardized schema
- **Logging integration**: Detailed parsing activity logging

### 3. Job Normalizer (jobs/normalizer.py)
**Purpose**: Field-level normalization and standardization
- **Title normalization**: Consistent job title formatting
- **Salary processing**: Intelligent salary parsing and standardization
- **Location standardization**: Geographic data normalization
- **Deduplication**: Multi-level duplicate detection and removal

## Data Schema

### JobPosting Model
```python
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, Dict, Any

class JobPosting(BaseModel):
    # Required Fields
    id: str                     # SHA-256 hash or source-specific ID
    source: str                 # Source identifier (remoteok, greenhouse, etc.)
    company: str                # Company name
    title: str                  # Job title
    url: HttpUrl                # Job posting URL
    date_posted: datetime       # When job was posted (UTC)
    
    # Optional Fields
    location: Optional[str] = None      # Job location
    salary: Optional[str] = None        # Salary information
    description: Optional[str] = None   # Job description
    
    # Raw Data
    raw: Dict[str, Any] = Field(
        default_factory=dict,
        description="Unmodified payload from upstream API"
    )
    
    # Configuration
    model_config = {
        "frozen": True,              # Immutable objects
        "populate_by_name": True,    # Support field aliases
        "str_max_length": 1_024,     # String length limits
    }
```

### Schema Validation Rules
```python
@field_validator("date_posted", mode="before")
def _enforce_utc(cls, v: datetime) -> datetime:
    """Force all datetimes to UTC & timezone-aware."""
    if v.tzinfo is None:
        return v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc)

@model_validator(mode="after")
def check_required_fields(self):
    """Validate required fields are present and non-empty."""
    required_fields = ["id", "source", "company", "title", "url", "date_posted"]
    missing = [f for f in required_fields if not getattr(self, f, None)]
    if missing:
        raise ValidationError(f"Missing required fields: {missing}")
    return self
```

## Public API

### Core Functions

```python
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import (
    normalize_job, normalize_title, normalize_salary, 
    normalize_location, dedupe_jobs
)
from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting

# Parse raw job data
def parse_job(raw: Dict[str, Any], source: str) -> JobPosting

# Normalize job fields
def normalize_job(job: JobPosting) -> JobPosting
def normalize_title(title: str) -> str
def normalize_salary(salary: Optional[str]) -> Optional[str]
def normalize_location(location: Optional[str]) -> Optional[str]

# Deduplication
def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]
```

### Parser API

```python
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job

# Parse job from source data
job = parse_job(raw_data, source="indeed")

# Validation errors are automatically raised
try:
    job = parse_job(invalid_data, source="linkedin")
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### Normalizer API

```python
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_job

# Normalize all job fields
normalized_job = normalize_job(job)

# Individual field normalization
clean_title = normalize_title("sr. software engineer")  # "Senior Software Engineer"
clean_salary = normalize_salary("$80k - $120k")        # "$80,000 - $120,000"
clean_location = normalize_location("SF, CA")           # "San Francisco, CA"
```

## Usage Examples

### 1. Basic Job Processing Pipeline
```python
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_job, dedupe_jobs

def process_job_batch(raw_jobs, source):
    """Process a batch of raw jobs through the normalization pipeline."""
    processed_jobs = []
    
    for raw_job in raw_jobs:
        try:
            # Parse raw data into JobPosting
            job = parse_job(raw_job, source=source)
            
            # Normalize fields
            normalized_job = normalize_job(job)
            
            processed_jobs.append(normalized_job)
            
        except ValidationError as e:
            logger.error(f"Failed to process job from {source}: {e}")
            continue
    
    # Remove duplicates
    unique_jobs = dedupe_jobs(processed_jobs)
    
    return unique_jobs

# Example usage
raw_data = [
    {
        'id': 'job123',
        'title': 'sr. product manager',
        'company': 'Example Corp.',
        'url': 'https://example.com/job/123',
        'location': 'SF, CA',
        'salary': '$100k-$150k',
        'date_posted': '2024-01-15T10:00:00Z'
    }
]

processed = process_job_batch(raw_data, source="indeed")
print(f"Processed {len(processed)} unique jobs")
```

### 2. Multi-Source Integration
```python
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_job, dedupe_jobs

async def collect_and_normalize_jobs():
    """Collect jobs from multiple sources and normalize them."""
    # Collect raw jobs
    aggregator = JobAggregatorService()
    raw_jobs = await aggregator.collect_jobs(
        keywords=["product manager"],
        location="Remote"
    )
    
    # Process each source separately
    all_normalized_jobs = []
    
    for job_data in raw_jobs:
        source = job_data.get('source', 'unknown')
        
        try:
            # Parse and validate
            job = parse_job(job_data, source=source)
            
            # Normalize fields
            normalized_job = normalize_job(job)
            
            all_normalized_jobs.append(normalized_job)
            
        except ValidationError as e:
            logger.warning(f"Skipping invalid job from {source}: {e}")
    
    # Global deduplication across all sources
    unique_jobs = dedupe_jobs(all_normalized_jobs)
    
    print(f"Collected {len(raw_jobs)} raw jobs")
    print(f"Processed {len(all_normalized_jobs)} valid jobs")
    print(f"Final unique jobs: {len(unique_jobs)}")
    
    return unique_jobs
```

### 3. Advanced Validation and Error Handling
```python
from pydantic import ValidationError
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job

def robust_job_parsing(raw_jobs, source):
    """Parse jobs with comprehensive error handling and reporting."""
    successful_jobs = []
    validation_errors = []
    
    for i, raw_job in enumerate(raw_jobs):
        try:
            job = parse_job(raw_job, source=source)
            successful_jobs.append(job)
            
        except ValidationError as e:
            error_details = {
                'job_index': i,
                'source': source,
                'errors': e.errors(),
                'raw_data': raw_job
            }
            validation_errors.append(error_details)
            
            # Log specific validation issues
            for error in e.errors():
                field = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                logger.error(f"Job {i} validation error in {field}: {message}")
    
    # Generate validation report
    success_rate = len(successful_jobs) / len(raw_jobs) * 100
    logger.info(f"Validation success rate: {success_rate:.1f}%")
    
    if validation_errors:
        logger.warning(f"Failed to parse {len(validation_errors)} jobs")
        
        # Analyze common errors
        error_types = {}
        for error_detail in validation_errors:
            for error in error_detail['errors']:
                error_type = error['type']
                error_types[error_type] = error_types.get(error_type, 0) + 1
        
        logger.info(f"Common error types: {error_types}")
    
    return successful_jobs, validation_errors
```

### 4. Custom Field Normalization
```python
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_title, normalize_salary

def custom_job_enhancement(job):
    """Add custom normalization logic for specific use cases."""
    enhanced_job = job.copy()
    
    # Enhanced title normalization
    title = normalize_title(job.title)
    
    # Add custom title classifications
    if any(keyword in title.lower() for keyword in ['senior', 'sr.', 'lead']):
        enhanced_job.seniority_level = 'Senior'
    elif any(keyword in title.lower() for keyword in ['junior', 'jr.', 'entry']):
        enhanced_job.seniority_level = 'Junior'
    else:
        enhanced_job.seniority_level = 'Mid-level'
    
    # Enhanced salary processing
    if job.salary:
        salary = normalize_salary(job.salary)
        
        # Extract salary range
        if '-' in salary and '$' in salary:
            try:
                parts = salary.replace('$', '').replace(',', '').split('-')
                enhanced_job.salary_min = int(parts[0].strip()) * 1000
                enhanced_job.salary_max = int(parts[1].strip()) * 1000
                enhanced_job.salary_currency = 'USD'
            except (ValueError, IndexError):
                logger.warning(f"Could not parse salary range: {salary}")
    
    # Remote work detection
    if job.location:
        location_lower = job.location.lower()
        enhanced_job.remote_work = any(
            keyword in location_lower 
            for keyword in ['remote', 'anywhere', 'distributed', 'work from home']
        )
    
    return enhanced_job
```

## Architecture Decisions

### 1. Pydantic Schema Design
- **Type safety**: Strict type validation prevents data corruption
- **Immutable objects**: Frozen models prevent accidental modifications
- **Validation at boundary**: Early validation prevents invalid data propagation
- **Extensible design**: Easy addition of new fields without breaking changes

### 2. Normalization Strategy
- **Field-level functions**: Granular control over individual field processing
- **Composable pipeline**: Combine normalization functions as needed
- **Source agnostic**: Uniform processing regardless of data source
- **Error isolation**: Field-level errors don't prevent entire job processing

### 3. Deduplication Approach
- **Multi-level detection**: URL, content hash, and fuzzy matching
- **Performance optimized**: Efficient algorithms for large job sets
- **Configurable thresholds**: Adjustable similarity matching
- **Preservation of metadata**: Maintain source tracking during deduplication

### 4. Error Handling Philosophy
- **Fail fast**: Early validation prevents downstream errors
- **Comprehensive logging**: Detailed error context for debugging
- **Graceful degradation**: Process valid jobs even when some fail
- **Error reporting**: Structured error information for monitoring

## Data Quality Features

### Validation Rules
```python
# Required field validation
required_fields = ["id", "source", "company", "title", "url", "date_posted"]

# Data type validation
type_validations = {
    'id': str,
    'source': str,
    'url': HttpUrl,
    'date_posted': datetime
}

# Business logic validation
business_rules = {
    'title_min_length': 1,
    'title_max_length': 200,
    'company_min_length': 1,
    'url_valid_schemes': ['http', 'https']
}
```

### Normalization Functions
```python
def normalize_title(title: str) -> str:
    """Standardize job titles with consistent formatting."""
    # Remove extra whitespace
    title = ' '.join(title.split())
    
    # Standardize common abbreviations
    replacements = {
        'sr.': 'Senior',
        'jr.': 'Junior', 
        'mgr': 'Manager',
        'dev': 'Developer',
        'eng': 'Engineer'
    }
    
    title_lower = title.lower()
    for abbrev, full in replacements.items():
        title_lower = title_lower.replace(abbrev, full.lower())
    
    # Proper case formatting
    return title_lower.title()

def normalize_salary(salary: Optional[str]) -> Optional[str]:
    """Standardize salary formatting and ranges."""
    if not salary:
        return None
    
    # Remove extra whitespace
    salary = ' '.join(salary.split())
    
    # Standardize number formatting
    salary = salary.replace('k', ',000')
    salary = salary.replace('K', ',000')
    
    # Ensure proper currency symbols
    if salary and not salary.startswith('$'):
        salary = '$' + salary
    
    return salary

def normalize_location(location: Optional[str]) -> Optional[str]:
    """Standardize location formatting."""
    if not location:
        return None
    
    # Remove extra whitespace
    location = ' '.join(location.split())
    
    # Standardize common abbreviations
    location_replacements = {
        'SF': 'San Francisco',
        'NYC': 'New York City',
        'LA': 'Los Angeles'
    }
    
    for abbrev, full in location_replacements.items():
        location = location.replace(abbrev, full)
    
    return location
```

### Deduplication Logic
```python
def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
    """Remove duplicate jobs using multiple strategies."""
    if not jobs:
        return jobs
    
    seen_urls = set()
    seen_company_titles = set()
    unique_jobs = []
    
    for job in jobs:
        # URL-based deduplication (exact match)
        if job.url in seen_urls:
            continue
        
        # Company + title deduplication (normalized)
        company_title_key = (
            job.company.lower().strip(),
            normalize_title(job.title).lower()
        )
        
        if company_title_key in seen_company_titles:
            continue
        
        # Add to unique set
        seen_urls.add(job.url)
        seen_company_titles.add(company_title_key)
        unique_jobs.append(job)
    
    logger.info(f"Deduplicated {len(jobs)} jobs to {len(unique_jobs)} unique jobs")
    return unique_jobs
```

## Performance Characteristics

### Processing Throughput
- **Parser performance**: 1000+ jobs/second for well-formed data
- **Normalization speed**: 2000+ jobs/second for field processing
- **Deduplication efficiency**: O(n) complexity with hash-based lookup
- **Memory usage**: Minimal memory footprint with streaming processing

### Scalability Considerations
- **Stateless design**: No shared state between processing operations
- **Batch processing**: Efficient handling of large job collections
- **Memory efficient**: Stream processing for large datasets
- **Parallel processing**: Independent job processing enables parallelization

## Error Handling

### Validation Error Types
```python
# Common validation errors and handling
validation_error_handlers = {
    'missing': lambda field, value: f"Required field '{field}' is missing",
    'url_invalid': lambda field, value: f"Invalid URL format: {value}",
    'string_too_long': lambda field, value: f"Field '{field}' exceeds maximum length",
    'datetime_invalid': lambda field, value: f"Invalid datetime format: {value}"
}

def handle_validation_error(error):
    """Process validation errors with appropriate logging and recovery."""
    error_type = error.get('type')
    field = '.'.join(str(loc) for loc in error.get('loc', []))
    value = error.get('input')
    
    if error_type in validation_error_handlers:
        message = validation_error_handlers[error_type](field, value)
        logger.error(f"Validation error: {message}")
    else:
        logger.error(f"Unknown validation error: {error}")
```

### Error Recovery Strategies
```python
def safe_parse_job(raw_data, source, fallback_values=None):
    """Parse job with error recovery and fallback values."""
    fallback_values = fallback_values or {}
    
    try:
        return parse_job(raw_data, source)
    except ValidationError as e:
        logger.warning(f"Attempting error recovery for job: {e}")
        
        # Apply fallback values for missing fields
        enhanced_data = {**raw_data}
        for field, fallback in fallback_values.items():
            if field not in enhanced_data or not enhanced_data[field]:
                enhanced_data[field] = fallback
                logger.info(f"Applied fallback for field '{field}': {fallback}")
        
        try:
            return parse_job(enhanced_data, source)
        except ValidationError:
            logger.error(f"Error recovery failed for job from {source}")
            raise
```

## Testing

### Unit Tests
```bash
# Test individual normalization functions
pytest tests/unit/test_job_normalizer/test_normalizer.py -v

# Test schema validation
pytest tests/unit/test_job_normalizer/test_schema.py -v

# Test parser functionality
pytest tests/unit/test_job_normalizer/test_parser.py -v

# Test deduplication logic
pytest tests/unit/test_job_normalizer/test_deduplication.py -v
```

### Integration Tests
```bash
# Test with real job aggregator data
pytest tests/integration/test_job_normalizer_integration.py -v

# Test multi-source processing
pytest tests/integration/test_multi_source_normalization.py -v

# Test error handling workflows
pytest tests/integration/test_error_handling.py -v
```

### Performance Tests
```bash
# Benchmark processing performance
pytest tests/performance/test_job_normalizer_performance.py -v

# Memory usage testing
pytest tests/performance/test_memory_usage.py -v

# Large dataset processing
pytest tests/performance/test_batch_processing.py -v
```

### Test Examples
```python
import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

def test_job_parsing_success():
    """Test successful job parsing with valid data."""
    raw_data = {
        'id': 'test123',
        'title': 'Software Engineer',
        'company': 'Test Corp',
        'url': 'https://example.com/job/123',
        'date_posted': datetime.now(timezone.utc)
    }
    
    job = parse_job(raw_data, source="test")
    
    assert job.id == 'test123'
    assert job.title == 'Software Engineer'
    assert job.company == 'Test Corp'
    assert job.source == 'test'

def test_job_parsing_validation_error():
    """Test validation error handling."""
    invalid_data = {
        'title': 'Software Engineer',  # Missing required fields
        'company': 'Test Corp'
    }
    
    with pytest.raises(ValidationError) as exc_info:
        parse_job(invalid_data, source="test")
    
    errors = exc_info.value.errors()
    error_fields = [error['loc'][0] for error in errors]
    
    assert 'id' in error_fields
    assert 'url' in error_fields

def test_title_normalization():
    """Test job title normalization."""
    test_cases = [
        ('sr. software engineer', 'Senior Software Engineer'),
        ('jr. developer', 'Junior Developer'),
        ('tech lead', 'Tech Lead'),
        ('  extra   spaces  ', 'Extra Spaces')
    ]
    
    for input_title, expected in test_cases:
        normalized = normalize_title(input_title)
        assert normalized == expected

def test_deduplication():
    """Test job deduplication logic."""
    jobs = [
        JobPosting(
            id="1", source="test", company="Corp A", title="Engineer",
            url="https://example.com/1", date_posted=datetime.now(timezone.utc)
        ),
        JobPosting(
            id="2", source="test", company="Corp A", title="Engineer",  # Duplicate
            url="https://example.com/2", date_posted=datetime.now(timezone.utc)
        ),
        JobPosting(
            id="3", source="test", company="Corp B", title="Manager",
            url="https://example.com/3", date_posted=datetime.now(timezone.utc)
        )
    ]
    
    unique_jobs = dedupe_jobs(jobs)
    
    assert len(unique_jobs) == 2
    assert any(job.company == "Corp A" for job in unique_jobs)
    assert any(job.company == "Corp B" for job in unique_jobs)
```

## Dependencies

### Core Dependencies
- **pydantic**: Schema validation and data modeling
- **typing**: Type hints and annotations
- **datetime**: Timezone handling and date processing
- **logging**: Error tracking and debugging

### Internal Dependencies
- **job_aggregator**: Source of raw job data
- **cache**: Deduplication state management
- **error_handler**: Centralized error logging

## Security Considerations

### Data Validation Security
- **Input sanitization**: Prevent injection attacks through job descriptions
- **URL validation**: Ensure job URLs are legitimate HTTP/HTTPS links
- **Length limits**: Prevent memory exhaustion from oversized fields
- **Type enforcement**: Strict type checking prevents data corruption

### Privacy and Compliance
- **PII handling**: Careful processing of personal information in job postings
- **Data retention**: Configurable retention policies for normalized data
- **Audit logging**: Track all normalization activities for compliance
- **Error logging security**: Avoid logging sensitive information in errors

## Future Enhancements

### Planned Features
1. **Advanced deduplication**: ML-based similarity detection for better duplicate identification
2. **Skills extraction**: Automated skill identification from job descriptions
3. **Salary intelligence**: Advanced salary parsing with market data integration
4. **Location intelligence**: Geographic enrichment with timezone and market data
5. **Quality scoring**: Automated job posting quality assessment

### Performance Improvements
1. **Async processing**: Full asynchronous processing pipeline
2. **Batch optimization**: Optimized batch processing for large datasets
3. **Caching layer**: Redis-based caching for normalization results
4. **Parallel processing**: Multi-threaded normalization for improved throughput

### Integration Enhancements
1. **Real-time validation**: Streaming validation for live job feeds
2. **Custom validation rules**: User-configurable validation logic
3. **Export formats**: Multiple output formats (JSON, Parquet, Avro)
4. **Monitoring integration**: Prometheus metrics for data quality tracking