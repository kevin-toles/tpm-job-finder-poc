
# Job Normalizer Service

Production-ready job data normalization, validation, and deduplication service with comprehensive error handling and multi-source integration.

## Overview

The Job Normalizer Service is a critical component that standardizes job postings from multiple sources into a unified schema, performs intelligent deduplication, and ensures data quality across the entire job aggregation pipeline.

## Features

### 🔧 Data Normalization
- **Title Standardization**: Consistent job title formatting and classification
- **Salary Parsing**: Intelligent salary range extraction and normalization
- **Location Processing**: Geographic standardization and validation
- **Company Normalization**: Company name standardization and domain extraction

### ✅ Data Validation
- **Schema Validation**: Pydantic-based strict schema enforcement
- **Required Fields**: Comprehensive validation of essential job fields
- **Data Type Validation**: Type checking and conversion with error reporting
- **Business Logic Validation**: Domain-specific validation rules

### 🔍 Deduplication
- **Multi-Level Deduplication**: URL, content hash, and fuzzy matching
- **Company-Title Matching**: Intelligent duplicate detection by company and role
- **Temporal Deduplication**: Time-based duplicate filtering
- **Performance Optimized**: Efficient deduplication with minimal memory footprint

### 📊 Error Handling & Monitoring
- **Comprehensive Logging**: Detailed error tracking and context
- **Validation Reporting**: Structured error reporting for debugging
- **Performance Metrics**: Processing statistics and monitoring
- **Audit Trail**: Complete audit trail for data quality assurance

## Architecture

```
job_normalizer/
├── jobs/
│   ├── JobPosting.md           # Schema documentation
│   ├── normalizer.py           # Core normalization logic
│   ├── parser.py              # Multi-source parsing
│   ├── validator.py           # Data validation
│   └── deduplicator.py        # Deduplication logic
├── tests/
│   ├── unit/                  # Unit tests for individual components
│   ├── integration/           # Integration tests with other services
│   ├── regression/            # Regression tests for data quality
│   └── e2e/                  # End-to-end workflow tests
├── README.md                  # This file
└── requirements.txt           # Service dependencies
```

## Data Schema

### JobPosting Model
```python
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List

class JobPosting(BaseModel):
    # Required Fields
    title: str
    company: str
    description: str
    url: str
    
    # Optional Fields
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    employment_type: Optional[str] = None
    remote_work: Optional[bool] = None
    
    # Metadata
    source: str
    posted_date: Optional[datetime] = None
    scraped_date: datetime
    job_id: Optional[str] = None
    
    # Enrichment Fields
    normalized_title: Optional[str] = None
    company_domain: Optional[str] = None
    location_parsed: Optional[dict] = None
    skills_extracted: Optional[List[str]] = None
    
    # System Fields
    content_hash: Optional[str] = None
    duplicate_group_id: Optional[str] = None
    validation_errors: Optional[List[str]] = None
```

### Schema Validation
```python
@validator('salary_min', 'salary_max')
def validate_salary(cls, v):
    if v is not None and v < 0:
        raise ValueError('Salary cannot be negative')
    return v

@validator('url')
def validate_url(cls, v):
    if not v.startswith(('http://', 'https://')):
        raise ValueError('URL must be a valid HTTP/HTTPS URL')
    return v
```

## Usage

### Basic Normalization
```python
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_job
from tpm_job_finder_poc.job_normalizer.jobs.parser import parse_job

# Parse raw job data
raw_job = {
    'title': 'sr. software engineer',
    'company': 'Example Corp.',
    'description': 'Job description...',
    'url': 'https://example.com/job/123',
    'salary': '$80,000 - $120,000',
    'location': 'San Francisco, CA'
}

# Parse and validate
job = parse_job(raw_job, source="indeed")

# Normalize fields
normalized_job = normalize_job(job)

print(f"Original title: {raw_job['title']}")
print(f"Normalized title: {normalized_job.normalized_title}")
```

### Batch Processing
```python
from tpm_job_finder_poc.job_normalizer.jobs.deduplicator import dedupe_jobs

# Process multiple jobs
raw_jobs = [job1, job2, job3, ...]
parsed_jobs = [parse_job(job, source) for job in raw_jobs]
normalized_jobs = [normalize_job(job) for job in parsed_jobs]

# Deduplicate
unique_jobs = dedupe_jobs(normalized_jobs)

print(f"Original count: {len(raw_jobs)}")
print(f"After deduplication: {len(unique_jobs)}")
```

### Advanced Validation
```python
from tpm_job_finder_poc.job_normalizer.jobs.validator import JobValidator

validator = JobValidator()

# Validate single job
validation_result = validator.validate_job(job)
if not validation_result.is_valid:
    print(f"Validation errors: {validation_result.errors}")

# Batch validation
validation_results = validator.validate_jobs(jobs)
valid_jobs = [job for job, result in zip(jobs, validation_results) if result.is_valid]
```

## API Reference

### Core Functions

#### parse_job(raw_data: dict, source: str) -> JobPosting
Parses raw job data into a standardized JobPosting object.

**Parameters:**
- `raw_data`: Raw job dictionary from source
- `source`: Source identifier (e.g., 'indeed', 'linkedin')

**Returns:** Validated JobPosting object

**Raises:** ValidationError for invalid data

#### normalize_job(job: JobPosting) -> JobPosting
Normalizes job fields including title, salary, location, and company.

**Parameters:**
- `job`: JobPosting object to normalize

**Returns:** JobPosting with normalized fields

#### dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]
Removes duplicate jobs using multiple deduplication strategies.

**Parameters:**
- `jobs`: List of JobPosting objects

**Returns:** Deduplicated list of jobs

### Normalization Functions

#### normalize_title(title: str) -> str
Standardizes job titles with consistent formatting.

```python
# Examples
normalize_title("sr. software engineer") # -> "Senior Software Engineer"
normalize_title("FE Developer") # -> "Frontend Developer"
normalize_title("ML Eng.") # -> "Machine Learning Engineer"
```

#### normalize_salary(salary_str: str) -> dict
Parses salary strings into structured data.

```python
# Examples
normalize_salary("$80k - $120k") 
# -> {'min': 80000, 'max': 120000, 'currency': 'USD'}

normalize_salary("€50,000/year")
# -> {'min': 50000, 'max': 50000, 'currency': 'EUR'}
```

#### normalize_location(location: str) -> dict
Parses and standardizes location information.

```python
# Examples
normalize_location("San Francisco, CA")
# -> {'city': 'San Francisco', 'state': 'CA', 'country': 'US'}

normalize_location("Remote")
# -> {'remote': True, 'city': None, 'state': None}
```

#### normalize_company(company: str) -> dict
Standardizes company names and extracts metadata.

```python
# Examples
normalize_company("Google Inc.")
# -> {'name': 'Google', 'domain': 'google.com', 'type': 'Corporation'}
```

## Integration

### JobAggregatorService Integration
```python
from tpm_job_finder_poc.job_aggregator.service import JobAggregatorService
from tpm_job_finder_poc.job_normalizer.jobs.normalizer import normalize_job

class JobAggregatorService:
    def process_jobs(self, raw_jobs: List[dict]) -> List[JobPosting]:
        """Process and normalize collected jobs"""
        processed_jobs = []
        
        for raw_job in raw_jobs:
            try:
                # Parse raw job data
                job = parse_job(raw_job, source=raw_job.get('source'))
                
                # Normalize job fields
                normalized_job = normalize_job(job)
                
                processed_jobs.append(normalized_job)
                
            except ValidationError as e:
                self.logger.warning(f"Job validation failed: {e}")
                continue
        
        # Deduplicate across all jobs
        return dedupe_jobs(processed_jobs)
```

### Cache Integration
```python
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache

class JobNormalizer:
    def __init__(self):
        self.cache = DedupeCache()
    
    def process_with_cache(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """Process jobs with cache-based deduplication"""
        new_jobs = []
        
        for job in jobs:
            # Check cache for duplicates
            if not self.cache.is_duplicate(job):
                new_jobs.append(job)
                self.cache.add_job(job)
        
        return new_jobs
```

### Enrichment Pipeline Integration
```python
from tpm_job_finder_poc.enrichment.orchestrator import EnrichmentOrchestrator

# Normalize before enrichment
normalized_jobs = [normalize_job(job) for job in raw_jobs]

# Enrich normalized jobs
orchestrator = EnrichmentOrchestrator()
enriched_jobs = orchestrator.enrich_jobs(normalized_jobs)
```

## Error Handling

### Validation Errors
```python
from pydantic import ValidationError

try:
    job = parse_job(raw_data, source="indeed")
except ValidationError as e:
    # Handle validation errors gracefully
    logger.error(f"Job validation failed: {e}")
    
    # Extract error details
    for error in e.errors():
        field = error['loc'][0]
        message = error['msg']
        logger.error(f"Field '{field}': {message}")
```

### Data Quality Monitoring
```python
from tpm_job_finder_poc.job_normalizer.jobs.validator import DataQualityMonitor

monitor = DataQualityMonitor()

# Track validation statistics
stats = monitor.get_validation_stats()
print(f"Validation success rate: {stats['success_rate']:.2f}%")
print(f"Common errors: {stats['common_errors']}")
```

### Error Recovery
```python
def robust_parse_job(raw_data: dict, source: str) -> Optional[JobPosting]:
    """Parse job with error recovery"""
    try:
        return parse_job(raw_data, source)
    except ValidationError as e:
        # Attempt to fix common issues
        fixed_data = fix_common_issues(raw_data)
        try:
            return parse_job(fixed_data, source)
        except ValidationError:
            # Log and skip job
            logger.warning(f"Unable to parse job from {source}: {e}")
            return None
```

## Testing

### Test Categories
- **Unit Tests**: Individual function validation
- **Integration Tests**: Service integration validation
- **Regression Tests**: Data quality regression prevention
- **Performance Tests**: Processing speed and memory usage

### Running Tests
```bash
# Run all normalizer tests
python -m pytest tpm_job_finder_poc/job_normalizer/tests/ -v

# Run specific test categories
python -m pytest tpm_job_finder_poc/job_normalizer/tests/unit/ -v
python -m pytest tpm_job_finder_poc/job_normalizer/tests/integration/ -v

# Run with coverage
python -m pytest tpm_job_finder_poc/job_normalizer/tests/ --cov=job_normalizer --cov-report=html
```

### Test Examples
```python
def test_normalize_title():
    """Test title normalization"""
    assert normalize_title("sr. software engineer") == "Senior Software Engineer"
    assert normalize_title("FE Developer") == "Frontend Developer"

def test_salary_parsing():
    """Test salary parsing"""
    result = normalize_salary("$80k - $120k")
    assert result['min'] == 80000
    assert result['max'] == 120000
    assert result['currency'] == 'USD'

def test_deduplication():
    """Test job deduplication"""
    job1 = create_test_job(title="Engineer", company="Google")
    job2 = create_test_job(title="Engineer", company="Google")  # Duplicate
    
    unique_jobs = dedupe_jobs([job1, job2])
    assert len(unique_jobs) == 1
```

## Performance Optimization

### Batch Processing
```python
# Process jobs in batches for memory efficiency
def process_jobs_in_batches(raw_jobs: List[dict], batch_size: int = 1000):
    for i in range(0, len(raw_jobs), batch_size):
        batch = raw_jobs[i:i + batch_size]
        processed_batch = [parse_job(job, source) for job in batch]
        yield processed_batch
```

### Caching Optimizations
```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def cached_normalize_title(title: str) -> str:
    """Cache normalized titles for performance"""
    return normalize_title(title)
```

### Memory Management
```python
def memory_efficient_deduplication(jobs: List[JobPosting]) -> List[JobPosting]:
    """Memory-efficient deduplication for large datasets"""
    seen_hashes = set()
    unique_jobs = []
    
    for job in jobs:
        job_hash = calculate_job_hash(job)
        if job_hash not in seen_hashes:
            seen_hashes.add(job_hash)
            unique_jobs.append(job)
    
    return unique_jobs
```

## Monitoring & Metrics

### Processing Metrics
```python
class NormalizationMetrics:
    def __init__(self):
        self.processed_count = 0
        self.validation_errors = 0
        self.duplicates_found = 0
        self.processing_time = 0
    
    def record_processing(self, jobs_count: int, errors: int, time_taken: float):
        self.processed_count += jobs_count
        self.validation_errors += errors
        self.processing_time += time_taken
    
    def get_stats(self) -> dict:
        return {
            'total_processed': self.processed_count,
            'error_rate': self.validation_errors / self.processed_count,
            'avg_processing_time': self.processing_time / self.processed_count
        }
```

### Data Quality Metrics
```python
def calculate_data_quality_score(jobs: List[JobPosting]) -> float:
    """Calculate overall data quality score"""
    total_fields = 0
    complete_fields = 0
    
    for job in jobs:
        for field_name, field_value in job.dict().items():
            total_fields += 1
            if field_value is not None and field_value != "":
                complete_fields += 1
    
    return complete_fields / total_fields if total_fields > 0 else 0.0
```

## Configuration

### Normalization Settings
```python
NORMALIZATION_CONFIG = {
    'title_mapping': {
        'sr.': 'Senior',
        'jr.': 'Junior',
        'fe': 'Frontend',
        'be': 'Backend',
        'ml': 'Machine Learning'
    },
    'company_domains': {
        'Google Inc.': 'google.com',
        'Microsoft Corporation': 'microsoft.com'
    },
    'salary_currencies': ['USD', 'EUR', 'GBP', 'CAD'],
    'location_aliases': {
        'SF': 'San Francisco',
        'NYC': 'New York City',
        'LA': 'Los Angeles'
    }
}
```

### Validation Rules
```python
VALIDATION_RULES = {
    'required_fields': ['title', 'company', 'url'],
    'min_description_length': 50,
    'max_title_length': 200,
    'salary_range_validation': True,
    'url_format_validation': True
}
```

## Troubleshooting

### Common Issues

#### High Validation Error Rate
```python
# Check common validation errors
validator = JobValidator()
error_analysis = validator.analyze_errors(failed_jobs)
print(f"Most common errors: {error_analysis['top_errors']}")
```

#### Performance Issues
```python
# Profile normalization performance
import cProfile

cProfile.run('normalize_jobs(large_job_list)')
```

#### Memory Usage
```python
# Monitor memory usage during processing
import psutil

def monitor_memory_usage():
    process = psutil.Process()
    return process.memory_info().rss / 1024 / 1024  # MB
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('job_normalizer').setLevel(logging.DEBUG)

# Detailed validation logging
job = parse_job(raw_data, source="indeed", debug=True)
```

---

## Version History

- **v1.0.0**: Production-ready normalization service
- **v0.8.0**: Advanced deduplication and validation
- **v0.6.0**: Multi-source parser implementation
- **v0.4.0**: Pydantic schema migration
- **v0.2.0**: Basic normalization functions

---

## Related Documentation

- **[Job Aggregator Service](../job_aggregator/README.md)**: Primary integration point
- **[Enrichment Pipeline](../enrichment/README.md)**: Post-normalization processing
- **[Cache Service](../../cache/README.md)**: Deduplication caching
- **[Models Documentation](../models/README.md)**: Data models and schemas

---

_For detailed API documentation and examples, refer to the test files in `tests/` directory._
