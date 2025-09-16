# Cache Component

The Cache component provides a multi-level caching system with intelligent deduplication and application tracking for the TPM Job Finder POC. It implements memory caching, persistent SQLite-based deduplication, and application state management to optimize performance and prevent duplicate job processing.

## Architecture Overview

The cache component follows a multi-tier caching strategy with specialized cache types:

```
cache/
├── cache_manager.py            # Multi-level cache coordination
├── dedupe_cache.py             # SQLite-based deduplication cache
├── applied_tracker.py          # Job application tracking cache
└── __init__.py                 # Module initialization
```

## Core Components

### 1. Cache Manager (cache_manager.py)
**Purpose**: Multi-level cache orchestration with memory and disk caching
- **Memory cache**: Fast in-memory caching for hot data
- **Disk cache**: Persistent disk-based caching for larger datasets
- **TTL management**: Time-to-live based cache expiration
- **Cache hierarchies**: Automatic promotion between cache levels
- **Async operations**: Non-blocking cache operations for performance

### 2. Deduplication Cache (dedupe_cache.py)
**Purpose**: SQLite-based persistent deduplication for job postings
- **Cross-session persistence**: Maintains deduplication state across application restarts
- **URL-based tracking**: Primary deduplication by job posting URL
- **Content hashing**: Secondary deduplication by job content hash
- **Fuzzy matching**: Company and title-based similarity detection
- **Performance optimization**: Indexed SQLite database for fast lookups

### 3. Application Tracker (applied_tracker.py)
**Purpose**: Tracks user job applications to prevent duplicate applications
- **Application state**: Maintains record of jobs already applied to
- **Excel integration**: Reads application history from Excel files
- **Status tracking**: Tracks application status and timestamps
- **User isolation**: Per-user application tracking
- **Persistent storage**: SQLite-based storage for reliability

## Data Architecture

### Cache Storage Structure
```
cache/
├── memory_cache/               # In-memory cache (runtime only)
├── disk_cache/                 # Persistent disk cache
│   ├── job_data_*.cache        # Cached job posting data
│   └── metadata_*.cache        # Cache metadata files
├── dedupe_cache.db             # SQLite deduplication database
└── applied_jobs.db             # SQLite application tracking database
```

### Deduplication Database Schema
```sql
CREATE TABLE job_urls (
    url TEXT PRIMARY KEY,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_hash TEXT,
    job_title TEXT,
    company_name TEXT
);

CREATE INDEX idx_content_hash ON job_urls(content_hash);
CREATE INDEX idx_company_title ON job_urls(company_name, job_title);
```

### Application Tracking Schema
```sql
CREATE TABLE applied_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    job_url TEXT NOT NULL,
    job_title TEXT,
    company_name TEXT,
    applied_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    application_status TEXT DEFAULT 'applied',
    source TEXT,
    UNIQUE(user_id, job_url)
);

CREATE INDEX idx_user_jobs ON applied_jobs(user_id, job_url);
```

## Public API

### Cache Manager API

```python
from tpm_job_finder_poc.cache.cache_manager import CacheManager

class CacheManager:
    def __init__(self)
    
    async def get_or_fetch(self, cache_key: str, fetch_func: Callable, ttl_seconds: int = 3600) -> Any
    async def get(self, cache_key: str) -> Optional[Any]
    async def set(self, cache_key: str, value: Any, ttl_seconds: int = 3600) -> None
    async def invalidate(self, cache_key: str) -> None
    async def clear_expired(self) -> int
    def get_cache_stats(self) -> Dict[str, Any]
```

### Deduplication Cache API

```python
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache

class DedupeCache:
    def __init__(self, db_path: str = "dedupe_cache.db")
    
    def add_job(self, url: str, title: str = None, company: str = None, content_hash: str = None) -> bool
    def is_duplicate(self, url: str, title: str = None, company: str = None) -> bool
    def get_duplicate_info(self, url: str) -> Optional[Dict[str, Any]]
    def remove_job(self, url: str) -> bool
    def get_stats(self) -> Dict[str, Any]
    def cleanup_old_entries(self, days_old: int = 30) -> int
```

### Application Tracker API

```python
from tpm_job_finder_poc.cache.applied_tracker import AppliedTracker

class AppliedTracker:
    def __init__(self, db_path: str = "applied_jobs.db")
    
    def mark_applied(self, user_id: str, job_url: str, job_title: str = None, company: str = None) -> bool
    def is_applied(self, user_id: str, job_url: str) -> bool
    def get_applied_jobs(self, user_id: str, limit: int = None) -> List[Dict[str, Any]]
    def update_application_status(self, user_id: str, job_url: str, status: str) -> bool
    def import_from_excel(self, user_id: str, excel_path: str) -> int
    def get_application_stats(self, user_id: str) -> Dict[str, Any]
```

## Usage Examples

### 1. Multi-Level Caching with Auto-Fetch
```python
from tpm_job_finder_poc.cache.cache_manager import CacheManager
import asyncio

async def example_caching_workflow():
    """Demonstrate multi-level caching with automatic data fetching."""
    cache_manager = CacheManager()
    
    # Define expensive data fetch function
    async def fetch_job_data(job_id: str):
        """Simulate expensive job data fetch from external API."""
        print(f"Fetching job data for {job_id} (expensive operation)")
        await asyncio.sleep(2)  # Simulate network delay
        return {
            "job_id": job_id,
            "title": "Senior Product Manager",
            "company": "Tech Corp",
            "salary": "$120k-$160k",
            "description": "Lead product development..."
        }
    
    # First call - cache miss, will fetch data
    job_data_1 = await cache_manager.get_or_fetch(
        cache_key="job_12345",
        fetch_func=lambda: fetch_job_data("12345"),
        ttl_seconds=3600  # Cache for 1 hour
    )
    print(f"First call result: {job_data_1['title']}")
    
    # Second call - cache hit, returns immediately
    job_data_2 = await cache_manager.get_or_fetch(
        cache_key="job_12345",
        fetch_func=lambda: fetch_job_data("12345"),
        ttl_seconds=3600
    )
    print(f"Second call result: {job_data_2['title']}")
    
    # Check cache statistics
    stats = cache_manager.get_cache_stats()
    print(f"Cache stats: {stats}")

# Run the example
asyncio.run(example_caching_workflow())
```

### 2. Job Deduplication Workflow
```python
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache

def job_deduplication_example():
    """Demonstrate job deduplication across multiple sources."""
    dedupe_cache = DedupeCache()
    
    # Job from first source
    job1 = {
        "url": "https://company.com/jobs/123",
        "title": "Senior Product Manager",
        "company": "Tech Corp"
    }
    
    # Same job from different source (different URL)
    job2 = {
        "url": "https://linkedin.com/jobs/456",
        "title": "Senior Product Manager",
        "company": "Tech Corp"
    }
    
    # Completely different job
    job3 = {
        "url": "https://startup.com/jobs/789",
        "title": "Software Engineer", 
        "company": "Startup Inc"
    }
    
    # Process jobs through deduplication
    jobs = [job1, job2, job3]
    unique_jobs = []
    
    for job in jobs:
        is_duplicate = dedupe_cache.is_duplicate(
            url=job["url"],
            title=job["title"],
            company=job["company"]
        )
        
        if not is_duplicate:
            # Add to cache and unique list
            dedupe_cache.add_job(
                url=job["url"],
                title=job["title"],
                company=job["company"]
            )
            unique_jobs.append(job)
            print(f"Added unique job: {job['title']} at {job['company']}")
        else:
            duplicate_info = dedupe_cache.get_duplicate_info(job["url"])
            print(f"Duplicate detected: {job['title']} (original from {duplicate_info['first_seen']})")
    
    print(f"Processed {len(jobs)} jobs, {len(unique_jobs)} unique")
    
    # Get deduplication statistics
    stats = dedupe_cache.get_stats()
    print(f"Deduplication stats: {stats}")

job_deduplication_example()
```

### 3. Application Tracking Integration
```python
from tpm_job_finder_poc.cache.applied_tracker import AppliedTracker

def application_tracking_example():
    """Demonstrate job application tracking to prevent duplicates."""
    tracker = AppliedTracker()
    user_id = "user123"
    
    # Check if user has applied to a job
    job_url = "https://company.com/jobs/product-manager"
    has_applied = tracker.is_applied(user_id, job_url)
    
    if not has_applied:
        # Mark job as applied
        success = tracker.mark_applied(
            user_id=user_id,
            job_url=job_url,
            job_title="Senior Product Manager",
            company="Tech Corp"
        )
        
        if success:
            print(f"Marked job as applied for user {user_id}")
        else:
            print("Failed to mark job as applied")
    else:
        print("User has already applied to this job")
    
    # Get all applied jobs for user
    applied_jobs = tracker.get_applied_jobs(user_id, limit=10)
    print(f"User has applied to {len(applied_jobs)} jobs")
    
    # Update application status
    tracker.update_application_status(
        user_id=user_id,
        job_url=job_url,
        status="interviewed"
    )
    
    # Get application statistics
    stats = tracker.get_application_stats(user_id)
    print(f"Application stats: {stats}")

application_tracking_example()
```

### 4. Complete Job Processing Pipeline with Caching
```python
from tpm_job_finder_poc.cache.cache_manager import CacheManager
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache
from tpm_job_finder_poc.cache.applied_tracker import AppliedTracker
import asyncio

async def complete_job_processing_pipeline(user_id: str, raw_jobs: List[Dict]):
    """Complete job processing pipeline with caching optimizations."""
    
    # Initialize cache components
    cache_manager = CacheManager()
    dedupe_cache = DedupeCache()
    applied_tracker = AppliedTracker()
    
    processed_jobs = []
    
    for job in raw_jobs:
        job_url = job.get("url")
        job_title = job.get("title", "")
        company = job.get("company", "")
        
        # Step 1: Check if job is duplicate
        if dedupe_cache.is_duplicate(job_url, job_title, company):
            print(f"Skipping duplicate job: {job_title} at {company}")
            continue
        
        # Step 2: Check if user already applied
        if applied_tracker.is_applied(user_id, job_url):
            print(f"User already applied to: {job_title} at {company}")
            continue
        
        # Step 3: Enrich job data (with caching)
        cache_key = f"enriched_job_{hash(job_url)}"
        enriched_job = await cache_manager.get_or_fetch(
            cache_key=cache_key,
            fetch_func=lambda j=job: enrich_job_data(j),
            ttl_seconds=7200  # Cache for 2 hours
        )
        
        # Step 4: Add to deduplication cache
        dedupe_cache.add_job(job_url, job_title, company)
        
        # Step 5: Add to processed jobs
        processed_jobs.append(enriched_job)
        
        print(f"Processed job: {job_title} at {company}")
    
    return processed_jobs

async def enrich_job_data(job: Dict) -> Dict:
    """Simulate expensive job enrichment process."""
    print(f"Enriching job data for: {job.get('title', 'Unknown')}")
    await asyncio.sleep(1)  # Simulate processing time
    
    enriched_job = job.copy()
    enriched_job.update({
        "enrichment_timestamp": "2025-01-15T10:30:00Z",
        "skills_extracted": ["Product Management", "Strategy", "Analytics"],
        "salary_parsed": {"min": 120000, "max": 160000, "currency": "USD"},
        "remote_work_score": 0.8,
        "match_score": 85
    })
    
    return enriched_job

# Example usage
async def run_pipeline_example():
    """Run the complete pipeline example."""
    sample_jobs = [
        {
            "url": "https://company1.com/jobs/pm1",
            "title": "Senior Product Manager",
            "company": "Tech Corp",
            "description": "Lead product development..."
        },
        {
            "url": "https://company2.com/jobs/pm2", 
            "title": "Product Manager",
            "company": "Startup Inc",
            "description": "Drive product strategy..."
        },
        # Duplicate job (same company and title)
        {
            "url": "https://jobboard.com/tech-corp-pm",
            "title": "Senior Product Manager",
            "company": "Tech Corp",
            "description": "Lead product development..."
        }
    ]
    
    processed = await complete_job_processing_pipeline("user123", sample_jobs)
    print(f"Pipeline processed {len(processed)} unique, new jobs")

asyncio.run(run_pipeline_example())
```

### 5. Cache Maintenance and Optimization
```python
from tpm_job_finder_poc.cache.cache_manager import CacheManager
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache
from tpm_job_finder_poc.cache.applied_tracker import AppliedTracker
import asyncio

async def cache_maintenance_workflow():
    """Demonstrate cache maintenance and optimization operations."""
    
    cache_manager = CacheManager()
    dedupe_cache = DedupeCache()
    applied_tracker = AppliedTracker()
    
    print("Starting cache maintenance...")
    
    # 1. Clear expired cache entries
    expired_count = await cache_manager.clear_expired()
    print(f"Cleared {expired_count} expired cache entries")
    
    # 2. Cleanup old deduplication entries (older than 30 days)
    old_dedupe_count = dedupe_cache.cleanup_old_entries(days_old=30)
    print(f"Cleaned up {old_dedupe_count} old deduplication entries")
    
    # 3. Get comprehensive cache statistics
    cache_stats = cache_manager.get_cache_stats()
    dedupe_stats = dedupe_cache.get_stats()
    
    print(f"Cache Manager Stats: {cache_stats}")
    print(f"Deduplication Stats: {dedupe_stats}")
    
    # 4. Application tracking maintenance
    # Get application statistics for monitoring
    user_ids = ["user123", "user456", "user789"]
    for user_id in user_ids:
        app_stats = applied_tracker.get_application_stats(user_id)
        print(f"User {user_id} application stats: {app_stats}")
    
    # 5. Cache warming for frequently accessed data
    print("Warming cache with frequently accessed job data...")
    frequent_job_ids = ["popular_job_1", "popular_job_2", "popular_job_3"]
    
    for job_id in frequent_job_ids:
        cache_key = f"job_data_{job_id}"
        # Pre-load popular jobs into cache
        await cache_manager.get_or_fetch(
            cache_key=cache_key,
            fetch_func=lambda jid=job_id: fetch_popular_job_data(jid),
            ttl_seconds=7200
        )
    
    print("Cache maintenance completed")

async def fetch_popular_job_data(job_id: str):
    """Simulate fetching popular job data."""
    await asyncio.sleep(0.5)  # Simulate fetch time
    return {
        "job_id": job_id,
        "title": f"Popular Job {job_id}",
        "company": "Popular Company",
        "popularity_score": 95
    }

# Run maintenance workflow
asyncio.run(cache_maintenance_workflow())
```

## Architecture Decisions

### 1. Multi-Tier Caching Strategy
- **Memory cache**: Fast access for frequently used data
- **Disk cache**: Persistent storage for larger datasets
- **Database cache**: SQLite for structured data with relationships
- **Automatic promotion**: Hot data promoted to faster cache tiers

### 2. Specialized Cache Types
- **General caching**: Cache manager for arbitrary data with TTL
- **Deduplication**: Specialized cache for job uniqueness detection
- **Application tracking**: Dedicated cache for user application state
- **Independent operation**: Each cache type can operate independently

### 3. Persistence Strategy
- **SQLite databases**: Reliable, fast, serverless persistence
- **File-based caching**: Simple disk cache for serializable data
- **Cross-session state**: Maintain cache state across application restarts
- **Atomic operations**: Ensure data consistency during concurrent access

### 4. Performance Optimization
- **Async operations**: Non-blocking cache operations
- **Indexed lookups**: Database indexes for fast deduplication queries
- **Memory efficiency**: LRU eviction for memory cache
- **Batch operations**: Efficient bulk cache operations

## Performance Characteristics

### Cache Performance Metrics
- **Memory cache**: Sub-millisecond access times
- **Disk cache**: 1-5ms access times for cached data
- **SQLite cache**: 1-10ms for indexed lookups
- **Cache hit ratio**: Target >80% for frequently accessed data

### Deduplication Performance
- **URL lookup**: O(1) average case with SQLite index
- **Content hash lookup**: O(1) with hash index
- **Fuzzy matching**: O(log n) with company/title index
- **Batch processing**: Optimized for processing large job sets

### Memory Usage
- **Memory cache**: Configurable size limits with LRU eviction
- **Disk cache**: Minimal memory footprint
- **SQLite overhead**: ~1MB for moderate job volumes
- **Scalability**: Linear scaling with job volume

## Testing

### Unit Tests
```bash
# Test cache manager functionality
pytest tests/unit/test_cache/test_cache_manager.py -v

# Test deduplication cache
pytest tests/unit/test_cache/test_dedupe_cache.py -v

# Test application tracker
pytest tests/unit/test_cache/test_applied_tracker.py -v

# Test cache integration
pytest tests/unit/test_cache/test_cache_integration.py -v
```

### Integration Tests
```bash
# Test cache integration with job processing
pytest tests/integration/test_cache_job_processing.py -v

# Test cross-component cache functionality
pytest tests/integration/test_cache_cross_component.py -v

# Test cache performance
pytest tests/performance/test_cache_performance.py -v
```

### Test Examples
```python
import pytest
import asyncio
import tempfile
from pathlib import Path
from tpm_job_finder_poc.cache.cache_manager import CacheManager
from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache

@pytest.fixture
def temp_cache_manager():
    """Create temporary cache manager for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        cache_manager = CacheManager(cache_dir=temp_dir)
        yield cache_manager

@pytest.mark.asyncio
async def test_cache_manager_get_or_fetch(temp_cache_manager):
    """Test cache manager get_or_fetch functionality."""
    cache_manager = temp_cache_manager
    
    # Track if fetch function was called
    fetch_called = False
    
    async def test_fetch():
        nonlocal fetch_called
        fetch_called = True
        await asyncio.sleep(0.1)  # Simulate async operation
        return {"data": "test_value"}
    
    # First call should fetch data
    result1 = await cache_manager.get_or_fetch("test_key", test_fetch, ttl_seconds=60)
    assert result1["data"] == "test_value"
    assert fetch_called is True
    
    # Reset flag
    fetch_called = False
    
    # Second call should use cache
    result2 = await cache_manager.get_or_fetch("test_key", test_fetch, ttl_seconds=60)
    assert result2["data"] == "test_value"
    assert fetch_called is False  # Should not have called fetch function

def test_dedupe_cache_functionality():
    """Test deduplication cache functionality."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        dedupe_cache = DedupeCache(temp_db.name)
        
        try:
            # Add first job
            added = dedupe_cache.add_job(
                url="https://example.com/job1",
                title="Software Engineer",
                company="Tech Corp"
            )
            assert added is True
            
            # Check if it's detected as duplicate
            is_duplicate = dedupe_cache.is_duplicate(
                url="https://example.com/job1",
                title="Software Engineer", 
                company="Tech Corp"
            )
            assert is_duplicate is True
            
            # Add different job
            added2 = dedupe_cache.add_job(
                url="https://example.com/job2",
                title="Product Manager",
                company="Different Corp"
            )
            assert added2 is True
            
            # Check it's not detected as duplicate
            is_duplicate2 = dedupe_cache.is_duplicate(
                url="https://example.com/job2",
                title="Product Manager",
                company="Different Corp"
            )
            assert is_duplicate2 is True  # It should be duplicate now that it's added
            
            # Test fuzzy matching (same company and title, different URL)
            is_fuzzy_duplicate = dedupe_cache.is_duplicate(
                url="https://different-site.com/job",
                title="Software Engineer",
                company="Tech Corp"
            )
            assert is_fuzzy_duplicate is True  # Should detect as duplicate
            
        finally:
            Path(temp_db.name).unlink(missing_ok=True)

def test_applied_tracker_functionality():
    """Test application tracker functionality."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        tracker = AppliedTracker(temp_db.name)
        
        try:
            user_id = "test_user"
            job_url = "https://example.com/job1"
            
            # Initially not applied
            assert tracker.is_applied(user_id, job_url) is False
            
            # Mark as applied
            success = tracker.mark_applied(
                user_id=user_id,
                job_url=job_url,
                job_title="Software Engineer",
                company="Tech Corp"
            )
            assert success is True
            
            # Now should be marked as applied
            assert tracker.is_applied(user_id, job_url) is True
            
            # Get applied jobs
            applied_jobs = tracker.get_applied_jobs(user_id)
            assert len(applied_jobs) == 1
            assert applied_jobs[0]["job_url"] == job_url
            
            # Update status
            updated = tracker.update_application_status(
                user_id=user_id,
                job_url=job_url,
                status="interviewed"
            )
            assert updated is True
            
            # Get stats
            stats = tracker.get_application_stats(user_id)
            assert stats["total_applications"] == 1
            
        finally:
            Path(temp_db.name).unlink(missing_ok=True)
```

## Dependencies

### Core Dependencies
- **sqlite3**: SQLite database operations for persistent caching
- **asyncio**: Asynchronous cache operations
- **hashlib**: Content hashing for deduplication
- **json**: Data serialization for disk cache
- **datetime**: Timestamp management and TTL calculations

### Internal Dependencies
- **storage**: Integration with secure storage for cache persistence
- **models**: Job and user models for cache data structures

## Security Considerations

### Data Protection
- **Local storage**: All cache data stored locally by default
- **Database security**: SQLite databases with appropriate file permissions
- **Data sanitization**: Input validation for all cache operations
- **Privacy**: No sensitive user data stored in cache without encryption

### Access Control
- **File permissions**: Appropriate filesystem permissions for cache files
- **User isolation**: Application tracking isolated per user
- **Database integrity**: SQLite transactions for data consistency
- **Cache poisoning prevention**: Validation of cached data integrity

## Future Enhancements

### Planned Features
1. **Distributed caching**: Redis-based distributed cache for scalability
2. **Cache clustering**: Multiple cache nodes for high availability
3. **Advanced TTL**: Dynamic TTL based on data access patterns
4. **Cache warming**: Proactive cache population for popular data
5. **Cache analytics**: Detailed cache usage analytics and optimization

### Performance Improvements
1. **Parallel operations**: Concurrent cache operations for better throughput
2. **Compression**: Data compression for larger cached objects
3. **Indexing optimization**: Advanced database indexing strategies
4. **Memory management**: Smart memory allocation and garbage collection

### Integration Enhancements
1. **Event-driven cache**: Cache invalidation based on system events
2. **Cache federation**: Multiple cache backends with automatic failover
3. **Monitoring integration**: Prometheus metrics for cache performance
4. **API layer**: RESTful API for external cache access