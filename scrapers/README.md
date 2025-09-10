# Job Scrapers

## Overview
This component implements job board scrapers with advanced features like rate limiting, caching, proxy rotation, and anti-bot measures.

## Architecture
```
scrapers/
├── __init__.py
├── base.py               # Base scraper class
├── linkedin.py          # LinkedIn implementation
├── indeed.py            # Indeed implementation
├── ziprecruiter.py      # ZipRecruiter implementation
├── config.py            # Configuration management
├── factory.py           # Scraper factory
├── browser_simulator.py # Anti-bot measures
├── captcha_handler.py   # CAPTCHA handling
├── proxy_rotator.py     # Proxy rotation
├── rate_limiter.py      # Rate limiting
├── response_cache.py    # Response caching
├── retry.py             # Retry logic
├── selector_health.py   # Selector monitoring
├── selector_maintainer.py # Selector maintenance
├── tests/              # Test suite
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   ├── regression/    # Regression tests
│   └── e2e/          # End-to-end tests
└── config/
    ├── scraper_config.json  # Scraper settings
    └── selectors.json       # CSS selectors
```

## Features
- **Rate Limiting**: Configurable requests per minute
- **Browser Simulation**: Anti-bot measures
- **CAPTCHA Handling**: Optional CAPTCHA service integration
- **Response Caching**: Configurable TTL
- **Proxy Rotation**: IP rotation pool
- **Retry Logic**: Exponential backoff
- **Selector Maintenance**: Automated selector updates
- **Health Monitoring**: Selector and response validation

## Configuration
Each scraper can be configured via `scraper_config.json`:
```json
{
  "linkedin": {
    "enabled": true,
    "requests_per_minute": 10,
    "cache_enabled": true,
    "cache_max_age": 3600,
    "proxy_enabled": false,
    "browser_simulation_enabled": true,
    "captcha_service_enabled": false
  }
}
```

## Usage
```python
from scrapers.factory import ScraperFactory
from scrapers.config import ScraperConfig

# Initialize with config
config = ScraperConfig.from_file('config/scraper_config.json')
factory = ScraperFactory(config)

# Get a configured scraper
scraper = factory.get_scraper('linkedin')

# Use the scraper
async with scraper:
    jobs = await scraper.fetch_jobs(
        search_terms=['Technical Program Manager'],
        location='San Francisco'
    )
```

## Integration
The scrapers component integrates with:
- Job Aggregator: Primary consumer of scraper services
- Cache Service: For response caching
- Applied Tracker: For tracking applied jobs

See integration tests for examples.

## Testing
Run tests with:
```bash
# Run all tests
pytest scrapers/tests/

# Run specific test types
pytest scrapers/tests/unit/
pytest scrapers/tests/integration/
pytest scrapers/tests/regression/
pytest scrapers/tests/e2e/
```

## Security
- Rate limiting prevents overloading job boards
- Browser simulation avoids detection
- Proxy rotation distributes requests
- API keys are stored securely
- Input validation prevents injection

## Error Handling
- Automatic retries with backoff
- Detailed error reporting
- Health monitoring alerts
- Selector maintenance automation

## Dependencies
See `requirements.txt` for full list:
- aiohttp
- beautifulsoup4
- requests
- pytest-asyncio

_Last updated: September 9, 2025_
