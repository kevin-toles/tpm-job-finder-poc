# Scraping Service v2

A production-ready, modular browser scraping service designed for large-scale job data collection across multiple platforms. Built with anti-detection capabilities, service orchestration, and comprehensive health monitoring.

## Architecture Overview

The scraping service follows a modular, plugin-based architecture with clear separation of concerns:

```
scraping_service_v2/
├── __init__.py                  # Main package exports
├── core/                        # Core infrastructure
│   ├── service_registry.py      # Service discovery and registration
│   ├── orchestrator.py          # Multi-source coordination
│   ├── base_job_source.py       # Base classes and type definitions
│   └── health_monitor.py        # Service health checking
└── scrapers/                    # Browser-based scrapers
    ├── base_scraper.py          # Base scraper implementation
    ├── indeed/                  # Indeed.com scraper
    │   ├── __init__.py
    │   └── scraper.py
    ├── linkedin/                # LinkedIn scraper
    │   ├── __init__.py
    │   └── scraper.py
    ├── ziprecruiter/            # ZipRecruiter scraper
    │   ├── __init__.py
    │   └── scraper.py
    └── greenhouse/              # Greenhouse.io scraper
        ├── __init__.py
        └── scraper.py
```

## Key Features

### 1. Multi-Platform Support
- **Indeed.com**: Job search and extraction with pagination
- **LinkedIn**: Professional network job scraping (authenticated and guest modes)
- **ZipRecruiter**: Job board scraping with salary information
- **Greenhouse.io**: Company career pages and job board scraping

### 2. Production-Ready Architecture
- **Modular Design**: Plugin-based scraper system with service registry
- **Anti-Detection**: Advanced anti-bot detection avoidance
- **Service Orchestration**: Coordinated multi-source data collection
- **Health Monitoring**: Real-time service health checks and monitoring
- **Error Resilience**: Comprehensive error handling and recovery

### 3. Advanced Anti-Detection
- **User Agent Rotation**: Randomized browser fingerprints
- **Request Delays**: Intelligent timing between requests
- **Viewport Randomization**: Varied browser window sizes
- **JavaScript Anti-Detection**: Property masking and protection
- **Proxy Support**: Built-in proxy rotation capability

### 4. Performance Optimization
- **Async Processing**: Non-blocking concurrent scraping
- **Rate Limiting**: Respectful rate limiting per platform
- **Resource Management**: Efficient browser instance management
- **Caching**: Intelligent response caching for efficiency

## Core Components

### 1. Service Registry (`core/service_registry.py`)
Central service discovery and registration system:

```python
from scraping_service_v2.core.service_registry import ServiceRegistry

# Initialize registry
registry = ServiceRegistry()

# Register scrapers
registry.register_default_scrapers()

# Get available scrapers
scrapers = registry.get_available_scrapers()

# Get specific scraper
indeed_scraper = registry.get_scraper('indeed')
```

### 2. Orchestrator (`core/orchestrator.py`)
Multi-source coordination and workflow management:

```python
from scraping_service_v2 import ScrapingOrchestrator
from scraping_service_v2.core.base_job_source import FetchParams

orchestrator = ScrapingOrchestrator()

# Configure search parameters
params = FetchParams(
    keywords=['product manager', 'technical product manager'],
    location='Remote',
    limit=100,
    date_posted='pastWeek'
)

# Collect jobs from multiple sources
jobs = await orchestrator.collect_jobs(
    sources=['indeed', 'linkedin', 'ziprecruiter'],
    params=params
)

print(f"Collected {len(jobs)} jobs from {len(jobs)} sources")
```

### 3. Base Scraper (`scrapers/base_scraper.py`)
Foundation class for all scrapers with common functionality:

```python
from scraping_service_v2.scrapers.base_scraper import BaseScraper

class CustomScraper(BaseScraper):
    source_name = "custom_site"
    base_url = "https://custom-site.com"
    
    async def fetch_jobs(self, params: FetchParams) -> List[JobResult]:
        # Implement custom scraping logic
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        # Implement health check logic
        pass
```

## Individual Scrapers

### 1. Indeed Scraper (`scrapers/indeed/scraper.py`)
**Features:**
- Comprehensive job search with pagination
- Salary range extraction
- Company rating and review data
- Job description and requirements parsing
- Anti-bot detection handling

**Configuration:**
```python
indeed_config = {
    "rate_limit": 10,  # requests per minute
    "max_pages": 5,    # maximum pages to scrape
    "headless": True,  # run in headless mode
    "timeout": 30      # request timeout in seconds
}
```

**Usage:**
```python
from scraping_service_v2.scrapers.indeed import IndeedScraper

scraper = IndeedScraper(config=indeed_config)
jobs = await scraper.fetch_jobs(params)
```

### 2. LinkedIn Scraper (`scrapers/linkedin/scraper.py`)
**Features:**
- Authentication-aware scraping with email/password support
- Guest mode fallback for unauthenticated access
- Advanced anti-bot detection handling
- LinkedIn-specific overlay and popup management
- Relative date parsing ("1 hour ago" format)

**Configuration:**
```python
linkedin_config = {
    "rate_limit": 5,              # conservative rate limit
    "auth_required": False,       # use guest mode
    "email": "your@email.com",    # for authenticated access
    "password": "your_password",  # for authenticated access
    "headless": True
}
```

**Authentication Modes:**
```python
# Guest mode (no authentication)
scraper = LinkedInScraper(config={"auth_required": False})

# Authenticated mode
scraper = LinkedInScraper(config={
    "auth_required": True,
    "email": "your@email.com",
    "password": "your_password"
})
```

### 3. ZipRecruiter Scraper (`scrapers/ziprecruiter/scraper.py`)
**Features:**
- Clean job board structure parsing
- Higher rate limits due to more permissive platform
- Pagination support for multiple pages
- Salary information extraction
- Job description snippet capture

**Configuration:**
```python
ziprecruiter_config = {
    "rate_limit": 10,    # requests per minute
    "max_pages": 3,      # pages to scrape
    "include_salary": True,
    "headless": True
}
```

### 4. Greenhouse Scraper (`scrapers/greenhouse/scraper.py`)
**Features:**
- Multi-company discovery mode
- Support for both subdomain and custom domain boards
- Company-specific board scraping
- Dynamic load-more functionality
- Pre-configured list of known Greenhouse companies

**Configuration:**
```python
greenhouse_config = {
    "rate_limit": 15,
    "companies": ["airbnb", "stripe", "slack"],  # specific companies
    "discovery_mode": True,   # discover multiple companies
    "load_more_pages": 3      # additional pages to load
}
```

## Integration with JobAggregatorService

The scraping service is designed to integrate seamlessly with the main JobAggregatorService:

```python
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService

# JobAggregatorService automatically uses scraping_service_v2
service = JobAggregatorService()

jobs = await service.collect_jobs(
    keywords=["product manager"],
    sources={
        "api_sources": ["remoteok", "greenhouse"],
        "scraping_sources": ["indeed", "linkedin", "ziprecruiter"]
    }
)
```

## Health Monitoring

### Service Health Checks
```python
from scraping_service_v2 import ScrapingOrchestrator

orchestrator = ScrapingOrchestrator()

# Check overall health
health = await orchestrator.health_check()
print(f"Service Status: {health['status']}")
print(f"Available Scrapers: {health['available_scrapers']}")

# Check individual scraper health
indeed_health = await orchestrator.check_scraper_health('indeed')
linkedin_health = await orchestrator.check_scraper_health('linkedin')
```

### Health Monitoring Metrics
- **Scraper Availability**: Real-time status of each scraper
- **Success Rate**: Percentage of successful scraping attempts
- **Response Time**: Average response time per scraper
- **Error Rate**: Rate of errors and failures
- **Rate Limit Status**: Current rate limit utilization

## Configuration Management

### Global Configuration
```python
# Configure all scrapers
scraping_config = {
    "global": {
        "headless": True,
        "timeout": 30,
        "max_retries": 3,
        "user_agent_rotation": True
    },
    "rate_limits": {
        "indeed": 10,
        "linkedin": 5,
        "ziprecruiter": 10,
        "greenhouse": 15
    },
    "anti_detection": {
        "enabled": True,
        "delay_range": [1, 3],
        "viewport_randomization": True,
        "javascript_protection": True
    }
}
```

### Per-Scraper Configuration
```python
# Configure individual scrapers
scraper_configs = {
    "indeed": {
        "rate_limit": 10,
        "max_pages": 5,
        "include_salary": True
    },
    "linkedin": {
        "rate_limit": 5,
        "auth_required": False,
        "guest_fallback": True
    }
}
```

## Error Handling & Resilience

### Retry Logic
```python
# Built-in retry logic for failed requests
retry_config = {
    "max_attempts": 3,
    "backoff_factor": 2,
    "retry_on": [
        "timeout",
        "connection_error", 
        "captcha_detected",
        "rate_limit_exceeded"
    ]
}
```

### Error Recovery
```python
# Graceful handling of scraper failures
try:
    jobs = await orchestrator.collect_jobs(['indeed', 'linkedin'], params)
except ScraperUnavailableError as e:
    print(f"Scraper {e.scraper} unavailable, continuing with others")
    available_scrapers = orchestrator.get_available_scrapers()
    jobs = await orchestrator.collect_jobs(available_scrapers, params)
```

### Common Error Scenarios
- **CAPTCHA Detection**: Automatic detection and graceful handling
- **Rate Limiting**: Automatic backoff and retry
- **Authentication Failures**: Fallback to guest mode (LinkedIn)
- **Page Structure Changes**: Robust selector fallback systems
- **Network Issues**: Comprehensive retry logic

## Advanced Features

### 1. Custom Selectors
```python
# Override default selectors for sites that change frequently
custom_selectors = {
    "indeed": {
        "job_card": "div[data-jk]",
        "job_title": "h2.jobTitle",
        "company": "span.companyName",
        "location": "div.companyLocation"
    }
}

scraper = IndeedScraper(selectors=custom_selectors["indeed"])
```

### 2. Proxy Integration
```python
# Use proxy rotation for large-scale scraping
proxy_config = {
    "enabled": True,
    "proxy_list": [
        "http://proxy1:8080",
        "http://proxy2:8080",
        "http://proxy3:8080"
    ],
    "rotation_strategy": "round_robin"
}

orchestrator = ScrapingOrchestrator(proxy_config=proxy_config)
```

### 3. Custom Headers
```python
# Use custom headers for specific requirements
custom_headers = {
    "User-Agent": "Custom Bot 1.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

scraper = IndeedScraper(headers=custom_headers)
```

## Performance Optimization

### 1. Concurrent Processing
```python
# Process multiple scrapers concurrently
import asyncio

async def parallel_scraping():
    scrapers = ['indeed', 'linkedin', 'ziprecruiter']
    
    tasks = [
        orchestrator.collect_jobs([scraper], params)
        for scraper in scrapers
    ]
    
    results = await asyncio.gather(*tasks)
    all_jobs = [job for result in results for job in result]
    
    return all_jobs
```

### 2. Intelligent Caching
```python
# Enable response caching for repeated requests
cache_config = {
    "enabled": True,
    "ttl": 3600,  # 1 hour cache
    "max_entries": 1000,
    "cache_type": "memory"  # or "redis" for distributed caching
}

orchestrator = ScrapingOrchestrator(cache_config=cache_config)
```

### 3. Resource Management
```python
# Optimize browser resource usage
browser_config = {
    "max_instances": 5,      # maximum concurrent browsers
    "instance_timeout": 300, # browser instance timeout
    "memory_limit": "1GB",   # memory limit per instance
    "cleanup_interval": 60   # cleanup interval in seconds
}
```

## Testing & Validation

### Unit Testing
```bash
# Run scraper-specific tests
python -m pytest tests/unit/test_scrapers/ -v

# Test individual scrapers
python -m pytest tests/unit/test_scrapers/test_indeed_scraper.py -v
python -m pytest tests/unit/test_scrapers/test_linkedin_scraper.py -v
```

### Integration Testing
```bash
# Test scraper integration with orchestrator
python -m pytest tests/integration/test_scraping_service.py -v

# Test end-to-end scraping workflows
python -m pytest tests/e2e/test_scraping_e2e.py -v
```

### Live Testing
```python
# Test against live sites (use responsibly)
from scraping_service_v2.validation import validate_scrapers

validation_results = await validate_scrapers(['indeed', 'linkedin'])
for scraper, result in validation_results.items():
    print(f"{scraper}: {result['status']} - {result['jobs_found']} jobs")
```

## Deployment & Production

### Docker Support
```dockerfile
# Dockerfile for scraping service
FROM python:3.13-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy scraping service
COPY scraping_service_v2/ /app/scraping_service_v2/
WORKDIR /app

# Run scraping service
CMD ["python", "-m", "scraping_service_v2"]
```

### Production Configuration
```python
# Production-ready configuration
production_config = {
    "global": {
        "headless": True,
        "timeout": 60,
        "max_retries": 5,
        "user_agent_rotation": True,
        "javascript_protection": True
    },
    "monitoring": {
        "enabled": True,
        "metrics_endpoint": "/metrics",
        "health_check_interval": 60
    },
    "logging": {
        "level": "INFO",
        "format": "json",
        "output": "/var/log/scraping-service.log"
    },
    "rate_limits": {
        "indeed": 10,
        "linkedin": 3,     # more conservative for LinkedIn
        "ziprecruiter": 15,
        "greenhouse": 20
    }
}
```

### Scaling Considerations
- **Horizontal Scaling**: Deploy multiple scraping service instances
- **Load Balancing**: Distribute scraping load across instances
- **Rate Limit Coordination**: Shared rate limiting across instances
- **Proxy Rotation**: Large-scale proxy management
- **Monitoring**: Centralized monitoring and alerting

## Future Enhancements

- **Machine Learning**: Intelligent content extraction using ML
- **Real-Time Scraping**: WebSocket-based real-time job updates
- **API Mode**: RESTful API for scraping service
- **Custom Scrapers**: Framework for easily adding new job sites
- **Advanced Analytics**: Detailed scraping performance analytics
- **Mobile Scraping**: Mobile-optimized scraping capabilities

## Limitations & Considerations

### Known Limitations
- **Site Dependencies**: Subject to changes in target site structures
- **Rate Limits**: Must respect platform-specific rate limits
- **Authentication**: LinkedIn requires careful authentication handling
- **CAPTCHA**: May encounter CAPTCHA challenges under heavy usage
- **Legal Compliance**: Must comply with terms of service and robots.txt

### Best Practices
- **Respectful Scraping**: Always respect rate limits and robots.txt
- **Regular Updates**: Monitor for site structure changes
- **Error Handling**: Implement comprehensive error handling
- **Resource Management**: Properly manage browser resources
- **Legal Review**: Ensure compliance with applicable laws and terms

---

_Last updated: January 2025 - Production-ready browser scraping service with comprehensive anti-detection and monitoring_
