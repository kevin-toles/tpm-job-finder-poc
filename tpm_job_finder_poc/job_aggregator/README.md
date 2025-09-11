# Job Aggregator

Job aggregation system that fetches Technical Program Manager positions from multiple sources including major job boards and ATS platforms.

## Features

### Job Board Scrapers
- LinkedIn
- Indeed
- ZipRecruiter

### ATS Connectors
- RemoteOK
- Greenhouse
- Lever

### Advanced Features
- Rate limiting
- Browser simulation
- CAPTCHA handling
- Response caching
- Proxy rotation
- Automatic selector maintenance
- Health monitoring

## Configuration

### Scraper Configuration
Each job board scraper can be individually configured using the `scraper_config.json` file:

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
  },
  "indeed": {
    "enabled": true,
    "requests_per_minute": 10,
    "cache_enabled": true,
    "cache_max_age": 3600,
    "proxy_enabled": false,
    "browser_simulation_enabled": true,
    "captcha_service_enabled": false
  },
  "ziprecruiter": {
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

### Configuration Options

Each scraper supports the following configuration options:

- `enabled`: Toggle the scraper on/off
- `requests_per_minute`: Rate limit for requests
- `cache_enabled`: Enable response caching
- `cache_max_age`: Cache TTL in seconds
- `proxy_enabled`: Use proxy rotation
- `browser_simulation_enabled`: Enable anti-bot measures
- `captcha_service_enabled`: Use CAPTCHA solving service
- `captcha_service_url`: CAPTCHA service endpoint (optional)
- `captcha_api_key`: CAPTCHA service API key (optional)

### Usage Examples

1. Using a custom configuration file:
```python
from job_aggregator.scrapers import LinkedInScraper

scraper = LinkedInScraper(
    search_terms=["Technical Program Manager"],
    config_file="/path/to/custom/config.json"
)
```

2. Programmatically controlling scrapers:
```python
from job_aggregator.scrapers.config import JobScraperConfig

# Get the config manager
config = JobScraperConfig()

# Disable LinkedIn scraper
config.disable_scraper('linkedin')

# Enable Indeed scraper with custom settings
config.config['indeed'].requests_per_minute = 5
config.config['indeed'].cache_max_age = 7200
config.save_config()
```

3. Environment configuration:
```bash
# Use custom config file
export SCRAPER_CONFIG=/path/to/config.json

# Use custom cache directory
export SCRAPER_CACHE_DIR=/path/to/cache
```

### Default Behavior

If no configuration is provided:
- All scrapers are enabled by default
- Conservative rate limits are applied
- Response caching is enabled with 1-hour TTL
- Browser simulation is enabled
- Proxy rotation and CAPTCHA services are disabled

## API

### Job Board Scrapers
```python
async with LinkedInScraper(search_terms=["TPM"]) as scraper:
    jobs = await scraper.fetch_all_jobs()
```

### ATS Connectors
```python
# Fetch jobs from the last 7 days
jobs = await RemoteOKConnector.fetch_since(days=7)
jobs = await GreenhouseConnector.fetch_since(days=7)
jobs = await LeverConnector.fetch_since(days=7)
```

## Output Format

All sources return normalized `JobPosting` objects with:
- Job title
- Company name
- Location
- Description
- Salary (if available)
- Application URL
- Posted date
- Source identifier
- Original data

## Testing
Run the test suite:
```bash
PYTHONPATH=. pytest cross_component_tests/aggregators/
```
