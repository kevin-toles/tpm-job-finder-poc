# Scraping Service

Production-ready, modular browser scraping service for large-scale job data collection across multiple platforms with advanced anti-detection capabilities.

## Overview

The scraping service is a sophisticated browser automation system designed for reliable, large-scale job data collection from major job platforms. It provides intelligent orchestration, anti-detection mechanisms, and comprehensive monitoring to ensure consistent access to job data from sources that don't offer public APIs.

The service supports multiple job platforms including Indeed, LinkedIn, ZipRecruiter, and Greenhouse, with each scraper optimized for platform-specific requirements. Advanced anti-detection features include user agent rotation, request timing, viewport randomization, and JavaScript property masking to maintain reliable access.

Built with production requirements in mind, the service includes health monitoring, rate limiting, error resilience, and resource management to support both development and large-scale deployment scenarios.

## Architecture

```
scraping_service/
├── __init__.py                  # Package exports and public interface
├── demo_phase2.py              # Demo scripts and validation
├── validate_phase2.py          # Validation utilities
├── requirements.txt            # Python dependencies
├── core/                       # Core infrastructure components
│   ├── service_registry.py     # Service discovery and registration
│   ├── orchestrator.py         # Multi-source coordination (Primary API)
│   ├── base_job_source.py      # Base classes and interfaces
│   └── health_monitor.py       # Service health monitoring
└── scrapers/                   # Platform-specific scrapers
    ├── base_scraper.py         # Base browser scraper implementation
    ├── indeed/                 # Indeed.com scraper
    │   ├── __init__.py
    │   └── scraper.py
    ├── linkedin/               # LinkedIn scraper
    │   ├── __init__.py
    │   └── scraper.py
    ├── ziprecruiter/           # ZipRecruiter scraper
    │   ├── __init__.py
    │   └── scraper.py
    └── greenhouse/             # Greenhouse.io scraper
        ├── __init__.py
        └── scraper.py
```

## Public API

### Core Classes

#### ScrapingOrchestrator
Primary coordination service for multi-source job collection and scraper management.

```python
from tpm_job_finder_poc.scraping_service.core.orchestrator import ScrapingOrchestrator
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams

class ScrapingOrchestrator:
    def __init__(self, registry=None, config=None):
        """Initialize orchestrator with service registry and configuration.
        
        Args:
            registry: ServiceRegistry instance for scraper management
            config: Configuration dictionary for global settings
        """
    
    async def collect_jobs(self, 
                          sources: List[str], 
                          params: FetchParams) -> List[JobPosting]:
        """Collect jobs from multiple sources concurrently.
        
        Args:
            sources: List of scraper names ('indeed', 'linkedin', etc.)
            params: Search parameters including keywords, location, limits
            
        Returns:
            List of standardized JobPosting objects
            
        Raises:
            ScrapingError: When scraping fails across all sources
            ValidationError: When search parameters are invalid
        """
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health status of all registered scrapers.
        
        Returns:
            Dictionary with overall status and per-scraper health metrics
        """
```

#### ServiceRegistry
Central registry for scraper discovery and management.

```python
from tpm_job_finder_poc.scraping_service.core.service_registry import ServiceRegistry

class ServiceRegistry:
    def register_scraper(self, name: str, scraper_class: Type[BaseJobSource]):
        """Register a scraper implementation."""
    
    def get_scraper(self, name: str) -> BaseJobSource:
        """Get scraper instance by name."""
    
    def list_available_scrapers(self) -> List[str]:
        """List all registered scraper names."""
```

#### BaseScraper
Base class for all browser-based job scrapers with anti-detection capabilities.

```python
from tpm_job_finder_poc.scraping_service.scrapers.base_scraper import BaseScraper

class BaseScraper(BaseJobSource):
    async def setup_browser(self) -> webdriver.Chrome:
        """Set up browser with anti-detection measures."""
    
    async def apply_anti_detection(self, driver: webdriver.Chrome):
        """Apply stealth measures to browser instance."""
    
    async def fetch_jobs(self, params: FetchParams) -> List[JobPosting]:
        """Fetch jobs using browser automation."""
```

### Key Methods

#### `collect_jobs(sources, params) -> List[JobPosting]`
- **Purpose**: Coordinate multi-source job collection with concurrent processing
- **Parameters**:
  - `sources`: List of scraper names to use ['indeed', 'linkedin', 'ziprecruiter', 'greenhouse']
  - `params`: FetchParams with keywords, location, date filters, limits
- **Returns**: Deduplicated list of standardized JobPosting objects
- **Example**:
```python
orchestrator = ScrapingOrchestrator()
params = FetchParams(
    keywords=["product manager", "technical product manager"],
    location="Remote",
    limit=50,
    date_posted="pastWeek"
)

jobs = await orchestrator.collect_jobs(
    sources=["indeed", "ziprecruiter"],
    params=params
)

print(f"Collected {len(jobs)} jobs")
```

#### `health_check() -> Dict[str, Any]`
- **Purpose**: Monitor scraper availability and performance metrics
- **Returns**: Health status with success rates, response times, error rates
- **Example**:
```python
health = await orchestrator.health_check()
print(f"Service Status: {health['status']}")
print(f"Available Scrapers: {health['available_scrapers']}")
for scraper, metrics in health['scrapers'].items():
    print(f"{scraper}: {metrics['success_rate']}% success")
```

## Configuration

### Environment Variables
```bash
# Global Scraping Configuration
SCRAPING_HEADLESS=true
SCRAPING_TIMEOUT=30
SCRAPING_MAX_RETRIES=3
SCRAPING_USER_AGENT_ROTATION=true

# Rate Limiting (requests per minute)
INDEED_RATE_LIMIT=10
LINKEDIN_RATE_LIMIT=5
ZIPRECRUITER_RATE_LIMIT=10
GREENHOUSE_RATE_LIMIT=15

# Anti-Detection Settings
ANTI_DETECTION_ENABLED=true
ANTI_DETECTION_DELAY_MIN=1
ANTI_DETECTION_DELAY_MAX=3
VIEWPORT_RANDOMIZATION=true
JAVASCRIPT_PROTECTION=true

# Browser Management
MAX_BROWSER_INSTANCES=5
BROWSER_INSTANCE_TIMEOUT=300
BROWSER_MEMORY_LIMIT=1024
CLEANUP_INTERVAL=60
```

### Configuration Class
```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class ScrapingConfig:
    # Global settings
    headless: bool = True
    timeout: int = 30
    max_retries: int = 3
    user_agent_rotation: bool = True
    
    # Rate limits per platform
    rate_limits: Dict[str, int] = field(default_factory=lambda: {
        "indeed": 10,
        "linkedin": 5,
        "ziprecruiter": 10,
        "greenhouse": 15
    })
    
    # Anti-detection configuration
    anti_detection: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "delay_range": [1, 3],
        "viewport_randomization": True,
        "javascript_protection": True
    })
    
    @classmethod
    def from_env(cls) -> "ScrapingConfig":
        return cls(
            headless=os.environ.get("SCRAPING_HEADLESS", "true").lower() == "true",
            timeout=int(os.environ.get("SCRAPING_TIMEOUT", "30")),
            max_retries=int(os.environ.get("SCRAPING_MAX_RETRIES", "3")),
            # ... other settings
        )
```

## Usage Examples

### Basic Multi-Source Scraping
```python
from tpm_job_finder_poc.scraping_service.core.orchestrator import ScrapingOrchestrator
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams
import asyncio

async def basic_scraping():
    # Initialize orchestrator
    orchestrator = ScrapingOrchestrator()
    
    # Configure search parameters
    params = FetchParams(
        keywords=["data scientist", "machine learning"],
        location="San Francisco",
        limit=25,
        date_posted="pastWeek"
    )
    
    # Collect jobs from multiple sources
    jobs = await orchestrator.collect_jobs(
        sources=["indeed", "ziprecruiter"],
        params=params
    )
    
    # Process results
    for job in jobs:
        print(f"{job.title} at {job.company}")
        print(f"Location: {job.location}")
        print(f"Posted: {job.date_posted}")
        print(f"URL: {job.url}")
        print("-" * 50)
    
    return jobs

# Run the scraping
jobs = asyncio.run(basic_scraping())
```

### Advanced Configuration with Custom Settings
```python
# Custom configuration for production environment
production_config = {
    "global": {
        "headless": True,
        "timeout": 60,
        "max_retries": 5,
        "user_agent_rotation": True,
        "javascript_protection": True
    },
    "rate_limits": {
        "indeed": 8,    # Conservative for production
        "linkedin": 3,  # Very conservative for LinkedIn
        "ziprecruiter": 12,
        "greenhouse": 20
    },
    "anti_detection": {
        "enabled": True,
        "delay_range": [2, 5],  # Longer delays
        "viewport_randomization": True,
        "proxy_rotation": True
    },
    "browser_management": {
        "max_instances": 3,
        "instance_timeout": 600,
        "memory_limit": "512MB",
        "cleanup_interval": 120
    }
}

orchestrator = ScrapingOrchestrator(config=production_config)
```

### Parallel Processing with Error Handling
```python
import asyncio
from typing import List, Dict, Any

async def parallel_scraping_with_monitoring():
    """Advanced parallel scraping with health monitoring"""
    orchestrator = ScrapingOrchestrator()
    
    # Define multiple search queries
    search_queries = [
        FetchParams(keywords=["python developer"], location="Remote", limit=20),
        FetchParams(keywords=["react developer"], location="New York", limit=20),
        FetchParams(keywords=["product manager"], location="San Francisco", limit=20)
    ]
    
    # Check health before starting
    health = await orchestrator.health_check()
    available_scrapers = health['available_scrapers']
    print(f"Available scrapers: {available_scrapers}")
    
    # Process queries concurrently
    tasks = []
    for i, params in enumerate(search_queries):
        task = orchestrator.collect_jobs(available_scrapers, params)
        tasks.append(task)
    
    try:
        # Execute all tasks with timeout
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=300  # 5 minute timeout
        )
        
        # Process results
        all_jobs = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Query {i} failed: {result}")
            else:
                all_jobs.extend(result)
                print(f"Query {i}: {len(result)} jobs")
        
        return all_jobs
        
    except asyncio.TimeoutError:
        print("Scraping timeout exceeded")
        return []

# Run with monitoring
jobs = asyncio.run(parallel_scraping_with_monitoring())
```

### Individual Scraper Usage
```python
from tpm_job_finder_poc.scraping_service.scrapers.indeed.scraper import IndeedScraper

async def use_individual_scraper():
    """Use a specific scraper directly"""
    scraper = IndeedScraper()
    
    params = FetchParams(
        keywords=["software engineer"],
        location="Austin, TX",
        limit=30
    )
    
    try:
        jobs = await scraper.fetch_jobs(params)
        print(f"Indeed returned {len(jobs)} jobs")
        return jobs
    except Exception as e:
        print(f"Scraping failed: {e}")
        return []

jobs = asyncio.run(use_individual_scraper())
```

## Architecture Decisions

### Key Design Choices

1. **Plugin-Based Architecture**: Service registry pattern enables easy addition of new scrapers
   - Each platform has dedicated scraper with platform-specific optimizations
   - Registry manages scraper lifecycle and discovery
   - Consistent interface across all scrapers via BaseJobSource

2. **Advanced Anti-Detection Strategy**: Multi-layered approach to avoid bot detection
   - User agent rotation with realistic browser fingerprints
   - Intelligent request timing with randomized delays
   - Viewport and browser property randomization
   - JavaScript property masking and automation trace removal

3. **Async-First Design**: Non-blocking concurrent processing for performance
   - All I/O operations are async for maximum throughput
   - Concurrent scraping across multiple platforms
   - Resource pooling for browser instances

4. **Health Monitoring Integration**: Real-time monitoring and error tracking
   - Per-scraper health metrics (success rate, response time, error rate)
   - Overall service health aggregation
   - Graceful degradation when scrapers fail

### Dependencies

**Internal Dependencies:**
- `models.job` - JobPosting data structures
- `secure_storage` - File management and audit trails
- `config` - Configuration management

**External Dependencies:**
- `selenium` - Browser automation framework
- `webdriver-manager` - Automatic WebDriver management
- `aiohttp` - Async HTTP client for API calls
- `beautifulsoup4` - HTML parsing and extraction
- `fake-useragent` - User agent rotation
- `asyncio` - Async programming support

**Optional Dependencies:**
- `proxy-rotation` - Proxy management for large-scale scraping
- `captcha-solver` - CAPTCHA solving integration
- `redis` - Distributed caching and rate limiting

### Interfaces

**Implements:**
- `BaseJobSource` - Standard interface for all job sources
- `IHealthMonitor` - Health checking and metrics interface
- `IServiceRegistry` - Service discovery and management

**Provides Services:**
- Multi-platform job data collection
- Browser automation with anti-detection
- Health monitoring and metrics
- Service orchestration and coordination

**Consumes Services:**
- Secure storage for audit logging
- Configuration management for settings
- Job aggregator for data pipeline integration

## Error Handling

### Exception Types
```python
class ScrapingError(Exception):
    """Base exception for scraping service errors."""
    
class BrowserSetupError(ScrapingError):
    """Browser initialization and configuration failures."""
    
class AntiDetectionError(ScrapingError):
    """Anti-detection mechanism failures."""
    
class RateLimitExceededError(ScrapingError):
    """Rate limiting violations."""
    
class ScraperUnavailableError(ScrapingError):
    """Scraper service unavailable or failing."""
    
class ValidationError(ScrapingError):
    """Search parameter validation failures."""
```

### Error Recovery

**Retry Logic:**
- Exponential backoff for temporary failures (3 attempts default)
- Browser restart on WebDriver crashes
- Service registry failover to available scrapers
- Graceful degradation with partial results

**Fallback Strategies:**
- Switch to available scrapers when others fail
- API fallback for platforms with public APIs
- Cached results when live scraping fails
- Empty results with detailed error logging

**Circuit Breaker Pattern:**
- Automatic scraper disabling after consecutive failures
- Health check recovery with exponential backoff
- Service-level circuit breaking for resource protection

## Testing

### Test Structure
```
tests/
├── unit/
│   ├── test_orchestrator.py
│   ├── test_service_registry.py
│   ├── test_base_scraper.py
│   └── scrapers/
│       ├── test_indeed_scraper.py
│       ├── test_linkedin_scraper.py
│       └── test_ziprecruiter_scraper.py
├── integration/
│   ├── test_scraping_integration.py
│   └── test_multi_source_collection.py
└── fixtures/
    ├── mock_browsers.py
    ├── sample_html_responses/
    └── test_job_data.py
```

### Running Tests
```bash
# Unit tests for scraping service
pytest tests/unit/test_*scraping* -v

# Integration tests (requires browser setup)
pytest tests/integration/test_scraping_integration.py -v

# Scraper-specific tests
pytest tests/unit/scrapers/ -v

# Full scraping test suite with coverage
pytest -k "scraping" --cov=tpm_job_finder_poc.scraping_service
```

### Mock Testing Setup
```python
# Mock browser for testing without actual browser instances
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_browser():
    """Mock WebDriver for testing"""
    mock_driver = Mock()
    mock_driver.get.return_value = None
    mock_driver.find_elements.return_value = []
    mock_driver.quit.return_value = None
    return mock_driver

@patch('selenium.webdriver.Chrome')
async def test_scraper_with_mock(mock_chrome, mock_browser):
    mock_chrome.return_value = mock_browser
    scraper = IndeedScraper()
    # Test scraper logic without browser overhead
```

## Performance

### Benchmarks
- **Throughput**: 50-100 jobs/minute per scraper (varies by platform)
- **Concurrent Processing**: 3-5 concurrent browser instances
- **Memory Usage**: ~200-500MB per browser instance
- **Response Time**: 2-10 seconds per page (depends on page complexity)

### Optimization Features
- **Browser Instance Pooling**: Reuse browser instances across requests
- **Intelligent Rate Limiting**: Platform-specific timing optimization
- **Resource Management**: Automatic cleanup and memory management
- **Concurrent Processing**: Parallel scraping across platforms

### Monitoring Metrics
- **Success Rate**: Percentage of successful scraping attempts
- **Response Time**: Average time per scraping operation
- **Error Rate**: Frequency and classification of errors
- **Resource Usage**: Browser memory and CPU consumption
- **Rate Limit Status**: Current usage vs. platform limits

## Security

### Anti-Detection Measures
- **Browser Fingerprinting**: Realistic user agent and viewport combinations
- **Request Timing**: Human-like delays and interaction patterns
- **JavaScript Protection**: Automation property masking and trace removal
- **IP Rotation**: Proxy support for large-scale operations

### Data Protection
- **No Persistent Storage**: Jobs processed in memory, not stored locally
- **Audit Logging**: All scraping activities logged for compliance
- **Secure Configuration**: API keys and credentials managed securely
- **Rate Limiting**: Respectful platform usage to avoid blocking

### Compliance Considerations
- **robots.txt Respect**: Honor platform scraping policies
- **Terms of Service**: Platform-specific usage guidelines
- **Data Usage**: Job data used only for matching purposes
- **Privacy Protection**: No personal data collection or storage

## Development

### Local Setup
```bash
# Install scraping service dependencies
pip install selenium webdriver-manager beautifulsoup4 fake-useragent

# Install browser driver (automatically managed by webdriver-manager)
# ChromeDriver will be downloaded automatically on first use

# Optional: Install development dependencies
pip install pytest pytest-asyncio pytest-cov

# Run validation demo
python -m tpm_job_finder_poc.scraping_service.demo_phase2

# Run component tests
python -m pytest tests/unit/test_*scraping* -v
```

### Development Workflow
```bash
# Run scraping service in development mode
python -c "
import asyncio
from tpm_job_finder_poc.scraping_service.core.orchestrator import ScrapingOrchestrator
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams

async def dev_test():
    orchestrator = ScrapingOrchestrator()
    params = FetchParams(keywords=['test'], location='Remote', limit=5)
    jobs = await orchestrator.collect_jobs(['indeed'], params)
    print(f'Collected {len(jobs)} test jobs')

asyncio.run(dev_test())
"

# Debug with browser visible (non-headless mode)
export SCRAPING_HEADLESS=false
python -m tpm_job_finder_poc.scraping_service.demo_phase2
```

### Contributing Guidelines
- **Code Style**: Follow project Engineering Guidelines for async code and error handling
- **Browser Testing**: Test with both headless and visible browser modes
- **Anti-Detection**: Verify stealth measures don't break functionality
- **Platform Updates**: Monitor for platform changes that affect scraping
- **Performance**: Benchmark any changes affecting scraping speed

## Related Documentation

- **[Job Aggregator Component](../job_aggregator/README.md)**: Integration with scraping service
- **[Scraping Service Phase 2](../../docs/components/scraping_service_phase2.md)**: Advanced features and extensions
- **[Business Process Architecture](../../docs/architecture/BUSINESS_PROCESS_ARCHITECTURE.md)**: Browser automation workflows
- **[Models Documentation](../models/README.md)**: JobPosting data structures
- **[Configuration Guide](../../docs/config.rst)**: Service configuration management

---

*The scraping service provides reliable access to job data from major platforms. For questions about browser automation or anti-detection measures, see the related documentation or create an issue.*