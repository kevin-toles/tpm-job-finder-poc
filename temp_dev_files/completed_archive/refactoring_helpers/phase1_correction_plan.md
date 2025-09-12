# Phase 1 Correction Plan: Browser Scrapers Focus

## Issue Identified
**Misunderstanding**: Initially built architecture for API connectors when the actual need is for browser scrapers only.

## Correct Scope
- **API Connectors**: Stay in existing `job_aggregator/aggregators/` (NO CHANGES)
- **Browser Scrapers**: Need refactoring into independent service (4 scrapers total)

## Architecture Correction Required

### Current (Incorrect) Structure
```
scraping_service_v2/
├── connectors/              # ❌ Not needed - API connectors stay in place
│   ├── base_connector.py    # ❌ Remove
│   └── greenhouse/          # ❌ Remove (API should stay in aggregators)
```

### Correct Structure Needed
```
scraping_service_v2/
├── core/                          # ✅ Keep - base infrastructure is good
│   ├── base_job_source.py        # ✅ Keep but adjust for scrapers
│   ├── service_registry.py       # ✅ Keep
│   └── orchestrator.py           # ✅ Keep
├── scrapers/                      # 🔄 Need BaseScraper + 4 implementations
│   ├── base_scraper.py           # 🆕 Browser scraper base class
│   ├── indeed/                   # 🔄 Migrate from existing
│   ├── linkedin/                 # 🔄 Migrate from existing  
│   ├── ziprecruiter/             # 🔄 Migrate from existing
│   └── greenhouse/               # 🆕 New browser scraper
├── infrastructure/                # 🔄 Migrate existing browser utilities
│   ├── browser_manager.py        # From browser_simulator.py
│   ├── rate_limiter.py           # Migrate existing
│   ├── proxy_rotator.py          # Migrate existing
│   ├── captcha_solver.py         # From captcha_handler.py
│   └── selector_manager.py       # From selector_* files
└── api/                          # ✅ Keep for scraper service REST API
```

## What to Keep from Phase 1
- ✅ Core infrastructure (BaseJobSource, ServiceRegistry, Orchestrator)
- ✅ Service architecture and patterns
- ✅ Health monitoring and error handling
- ✅ Resource management and cleanup

## What to Change
- ❌ Remove BaseConnector and connector implementations
- 🔄 Create BaseScraper for browser-based scraping
- 🔄 Focus on Selenium/Playwright integration
- 🔄 Migrate existing browser infrastructure utilities

## Action Plan
1. **Create BaseScraper class** for browser automation
2. **Remove connector-focused code** 
3. **Migrate browser infrastructure** (rate limiter, browser simulator, etc.)
4. **Create first scraper implementation** as proof of concept
5. **Update demo script** to show browser scraping workflow

## Browser Scraper Requirements
- Selenium/Playwright integration
- Anti-detection measures (user agents, delays, mouse simulation)
- Selector management and health monitoring
- CAPTCHA handling
- Proxy rotation
- Rate limiting per domain
- Session management and cookies
