# Scraper Service Refactoring Plan

## Overview
Refactor the current scraper functionality into an independent, microservice-based architecture where each scraper becomes a standalone, pluggable component.

## Current Architecture Analysis

### Existing Structure
```
tpm_job_finder_poc/job_aggregator/
├── aggregators/           # API-based connectors (Greenhouse, Lever, etc.)
├── scrapers/             # Browser-based scrapers (Indeed, LinkedIn, etc.)
├── services/
├── controllers/
└── main.py

scraping_service/         # Newer async architecture (partial)
├── adapters/
├── base_adapter.py
└── scrapers/

src/poc/aggregators/      # Legacy connectors (to be migrated)
```

### Current Components Identified
1. **API Connectors** (11 total):
   - Greenhouse, Lever, Ashby, Recruitee, Workable, SmartRecruiters
   - Adzuna, RemoteOK, USAJobs, Jooble
   
2. **Browser Scrapers** (3 total):
   - Indeed, LinkedIn, ZipRecruiter

3. **Infrastructure Components**:
   - Rate limiting, proxy rotation, caching, retry logic
   - Browser simulation, CAPTCHA handling
   - Selector maintenance and health monitoring

## Proposed New Architecture

### 1. Core Service Structure
```
scraping_service/
├── core/                          # Core service infrastructure
│   ├── __init__.py
│   ├── base_scraper.py           # Abstract base for all scrapers
│   ├── service_registry.py        # Dynamic scraper registration
│   ├── orchestrator.py           # Job coordination and routing
│   └── health_monitor.py         # Service health checking
├── connectors/                    # API-based job sources
│   ├── __init__.py
│   ├── base_connector.py
│   ├── greenhouse/
│   ├── lever/
│   ├── ashby/
│   ├── recruitee/
│   ├── workable/
│   ├── smartrecruiters/
│   ├── adzuna/
│   ├── remoteok/
│   ├── usajobs/
│   └── jooble/
├── scrapers/                      # Browser-based scrapers
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── indeed/
│   ├── linkedin/
│   └── ziprecruiter/
├── infrastructure/                # Shared utilities
│   ├── __init__.py
│   ├── rate_limiter.py
│   ├── proxy_rotator.py
│   ├── response_cache.py
│   ├── retry_handler.py
│   ├── browser_manager.py
│   ├── captcha_solver.py
│   └── selector_manager.py
├── api/                          # REST API for the service
│   ├── __init__.py
│   ├── routes.py
│   ├── middleware.py
│   └── schemas.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── connector_configs/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── Dockerfile
├── requirements.txt
└── main.py
```

### 2. Individual Connector Architecture
Each connector becomes a self-contained module:

```
connectors/greenhouse/
├── __init__.py
├── connector.py              # Main connector class
├── config.py                 # Connector-specific config
├── schemas.py               # Data schemas
├── rate_limits.py           # Rate limit definitions
├── transformers.py          # Data transformation logic
├── exceptions.py            # Custom exceptions
└── tests/
    ├── test_connector.py
    ├── test_transformers.py
    └── fixtures/
```

### 3. Scraper Module Architecture
```
scrapers/indeed/
├── __init__.py
├── scraper.py               # Main scraper class
├── selectors.py             # CSS/XPath selectors
├── config.py                # Scraper configuration
├── page_handlers.py         # Page-specific logic
├── data_extractors.py       # Data extraction utilities
├── anti_detection.py        # Anti-bot measures
└── tests/
```

## Implementation Plan

### Phase 1: Core Infrastructure Setup (Week 1)
1. **Create base service structure**
   - Set up new scraping_service directory structure
   - Implement base classes and interfaces
   - Create service registry and orchestrator

2. **Migrate infrastructure utilities**
   - Move and refactor existing utilities
   - Implement common interfaces
   - Add comprehensive error handling

### Phase 2: API Connector Migration (Week 1-2)
1. **Migrate existing API connectors** (Priority Order):
   - Greenhouse (most stable)
   - Lever (well-tested)
   - RemoteOK (simple API)
   - Ashby, Recruitee, Workable
   - Adzuna, USAJobs, Jooble, SmartRecruiters

2. **Standardize connector interfaces**
   - Common authentication patterns
   - Unified data transformation
   - Consistent error handling

### Phase 3: Browser Scraper Migration (Week 2)
1. **Migrate browser-based scrapers**:
   - Indeed (complex, high-value)
   - LinkedIn (authentication heavy)
   - ZipRecruiter (moderate complexity)

2. **Enhance anti-detection measures**
   - Advanced browser simulation
   - Dynamic selector management
   - CAPTCHA solving integration

### Phase 4: Service Integration (Week 3)
1. **Build REST API layer**
   - Job fetching endpoints
   - Health check endpoints
   - Configuration management

2. **Implement orchestration logic**
   - Multi-source job aggregation
   - Deduplication and normalization
   - Rate limiting coordination

### Phase 5: Testing & Deployment (Week 3-4)
1. **Comprehensive testing**
   - Unit tests for all components
   - Integration tests for workflows
   - End-to-end testing with real sources

2. **Performance optimization**
   - Async/await optimization
   - Caching strategies
   - Resource management

## Technical Specifications

### Base Interfaces
```python
# Abstract base for all job sources
class BaseJobSource(ABC):
    @abstractmethod
    async def fetch_jobs(self, params: Dict[str, Any]) -> List[JobPosting]:
        pass
    
    @abstractmethod
    async def health_check(self) -> HealthStatus:
        pass
    
    @abstractmethod
    def get_rate_limits(self) -> RateLimitConfig:
        pass

# Connector-specific interface (API-based)
class BaseConnector(BaseJobSource):
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    def transform_response(self, raw_data: Dict) -> List[JobPosting]:
        pass

# Scraper-specific interface (Browser-based)
class BaseScraper(BaseJobSource):
    @abstractmethod
    async def setup_browser(self) -> Browser:
        pass
    
    @abstractmethod
    def get_selectors(self) -> Dict[str, str]:
        pass
    
    @abstractmethod
    async def handle_anti_detection(self) -> None:
        pass
```

### Configuration Management
```python
# Dynamic configuration per source
@dataclass
class ConnectorConfig:
    name: str
    enabled: bool
    rate_limit: RateLimitConfig
    authentication: AuthConfig
    endpoints: Dict[str, str]
    retry_policy: RetryConfig
    timeout: int
    
@dataclass
class ScraperConfig:
    name: str
    enabled: bool
    base_url: str
    selectors: Dict[str, str]
    browser_config: BrowserConfig
    anti_detection: AntiDetectionConfig
    rate_limit: RateLimitConfig
```

## Migration Strategy

### Data Migration
1. **Preserve existing functionality** during migration
2. **Gradual cutover** - connector by connector
3. **Backward compatibility** with existing job_aggregator interface
4. **Comprehensive testing** at each migration step

### Deployment Strategy
1. **Docker containerization** for each service component
2. **Independent scaling** of different scraper types
3. **Health monitoring** and automatic failover
4. **Configuration hot-reloading** for dynamic updates

## Success Metrics
1. **Performance**: 50% reduction in job fetch time through parallelization
2. **Reliability**: 99% uptime for individual scrapers
3. **Maintainability**: Isolated failures, easier debugging
4. **Scalability**: Independent scaling of popular sources
5. **Extensibility**: New scrapers can be added in <2 hours

## Risks & Mitigation
1. **Breaking changes**: Comprehensive testing and gradual migration
2. **Performance degradation**: Benchmarking and optimization
3. **Complex debugging**: Enhanced logging and monitoring
4. **Resource usage**: Efficient connection pooling and resource management

## Timeline Summary
- **Week 1**: Core infrastructure + API connector migration
- **Week 2**: Browser scraper migration
- **Week 3**: Service integration + API development  
- **Week 4**: Testing, optimization, deployment

## Next Steps
1. Begin with Phase 1: Core Infrastructure Setup
2. Create base classes and service registry
3. Start with Greenhouse connector migration as proof of concept
