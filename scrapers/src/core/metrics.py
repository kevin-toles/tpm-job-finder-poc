"""Metrics collection for scraper service."""

from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
SCRAPER_REQUESTS = Counter(
    'scraper_requests_total',
    'Total number of scraper requests',
    ['source', 'status']
)

SCRAPER_REQUEST_DURATION = Histogram(
    'scraper_request_duration_seconds',
    'Time spent processing scraper requests',
    ['source']
)

# Job metrics
JOBS_FOUND = Counter(
    'jobs_found_total',
    'Total number of jobs found',
    ['source']
)

# Cache metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['source']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['source']
)

# Rate limiting metrics
RATE_LIMIT_DELAYS = Histogram(
    'rate_limit_delay_seconds',
    'Time spent waiting due to rate limiting',
    ['source']
)

# Error metrics
SCRAPER_ERRORS = Counter(
    'scraper_errors_total',
    'Total number of scraper errors',
    ['source', 'error_type']
)

# Health metrics
SCRAPER_HEALTH = Gauge(
    'scraper_health',
    'Health status of scrapers',
    ['source']
)

class MetricsCollector:
    """Collector for scraper service metrics."""

    @classmethod
    def record_request(cls, source: str, status: str):
        """Record a scraper request."""
        SCRAPER_REQUESTS.labels(source=source, status=status).inc()

    @classmethod
    def record_request_duration(cls, source: str, duration: float):
        """Record request duration."""
        SCRAPER_REQUEST_DURATION.labels(source=source).observe(duration)

    @classmethod
    def record_jobs_found(cls, source: str, count: int):
        """Record number of jobs found."""
        JOBS_FOUND.labels(source=source).inc(count)

    @classmethod
    def record_cache_hit(cls, source: str):
        """Record a cache hit."""
        CACHE_HITS.labels(source=source).inc()

    @classmethod
    def record_cache_miss(cls, source: str):
        """Record a cache miss."""
        CACHE_MISSES.labels(source=source).inc()

    @classmethod
    def record_rate_limit_delay(cls, source: str, delay: float):
        """Record rate limit delay."""
        RATE_LIMIT_DELAYS.labels(source=source).observe(delay)

    @classmethod
    def record_error(cls, source: str, error_type: str):
        """Record a scraper error."""
        SCRAPER_ERRORS.labels(source=source, error_type=error_type).inc()

    @classmethod
    def update_health(cls, source: str, is_healthy: bool):
        """Update scraper health status."""
        SCRAPER_HEALTH.labels(source=source).set(1 if is_healthy else 0)
