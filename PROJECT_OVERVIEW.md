# TPM Job Finder POC: Project Overview

## Purpose
This document provides a comprehensive overview of the TPM Job Finder Proof of Concept (POC) - a production-ready automated job search and aggregation system designed for Technical Product Managers and other professionals. It is intended for new developers, teams with dependencies, and stakeholders who need to understand the system architecture before diving into detailed documentation.

## System Overview
The TPM Job Finder POC is a sophisticated, modular job aggregation system that combines API-based job collection, browser scraping, intelligent deduplication, and LLM-powered enrichment into a unified workflow automation platform.

## Architecture Summary
- **Language & Frameworks:** Python 3.13+, Selenium WebDriver, pytest, asyncio
- **Project Structure:** Modern Python package with microservice-inspired architecture
- **Core Architecture:**
  - **JobAggregatorService**: Central orchestration service for multi-source job collection
  - **Scraping Service v2**: Independent, modular browser scraping service
  - **Enrichment Pipeline**: LLM-powered job analysis and enhancement
  - **CLI Automation**: Complete workflow automation with configuration management
  - **Comprehensive Testing**: 70+ tests with 100% pass rate validation

## Key Features
- **Multi-Source Job Aggregation**: API sources (RemoteOK, Greenhouse, Lever, Ashby, Workable, SmartRecruiters) + Browser scraping (Indeed, LinkedIn, ZipRecruiter, Greenhouse)
- **Intelligent Deduplication**: Advanced SQLite-based caching with fuzzy matching
- **Job Enrichment**: LLM-powered job analysis, scoring, and metadata enhancement
- **Browser Scraping Service**: Modern, modular scraping with anti-detection techniques
- **Health Monitoring**: Comprehensive service health checks and monitoring
- **Audit Logging**: Complete audit trails for all operations
- **Secure Storage**: SecureStorage integration for all file operations
- **Production-Ready**: Full test coverage, error handling, and deployment readiness

## Project Structure

```
tpm-job-finder-poc/
├── README.md                     # Main documentation
├── PROJECT_OVERVIEW.md           # This file - architecture overview
├── requirements.txt              # Python dependencies
├── pytest.ini                   # Test configuration
├── CHANGELOG.md                  # Version history
└── llm_keys.txt                  # LLM API keys (gitignored)

# Core Package
tpm_job_finder_poc/               # Main application package
├── __init__.py
├── job_aggregator/               # Job collection orchestration
│   ├── main.py                   # JobAggregatorService - central orchestrator
│   ├── aggregators/              # API-based job sources
│   │   ├── ashby_aggregator.py   # Ashby API integration
│   │   ├── greenhouse_aggregator.py # Greenhouse API
│   │   ├── lever_aggregator.py   # Lever API
│   │   ├── remoteok_aggregator.py # RemoteOK API
│   │   ├── smartrecruiters_aggregator.py # SmartRecruiters API
│   │   └── workable_aggregator.py # Workable API
│   ├── cache/                    # Deduplication cache
│   ├── controllers/              # Request handlers
│   ├── scrapers/                 # Browser scraper integration
│   └── services/                 # Supporting services
├── cli/                          # Command-line interfaces
│   ├── automated_cli.py          # Automated workflow CLI
│   ├── cli.py                    # Manual pipeline CLI
│   └── runner.py                 # Legacy CLI runner
├── cache/                        # Caching infrastructure
│   ├── cache_manager.py          # Cache coordination
│   ├── dedupe_cache.py           # Deduplication logic
│   └── applied_tracker.py        # Application tracking
├── enrichment/                   # Job enhancement pipeline
│   ├── orchestrator.py           # Enrichment orchestration
│   ├── jd_parser.py              # Job description parsing
│   ├── ml_scorer.py              # ML-based job scoring
│   ├── resume_parser.py          # Resume analysis
│   ├── heuristic_scorer.py       # Rule-based scoring
│   └── llm_provider.py           # LLM integration
├── models/                       # Data models
│   ├── job.py                    # Job data model
│   ├── user.py                   # User data model
│   ├── application.py            # Application data model
│   └── resume.py                 # Resume data model
├── llm_provider/                 # LLM service providers
│   ├── base.py                   # Base LLM provider interface
│   ├── openai_provider.py        # OpenAI GPT integration
│   ├── anthropic_provider.py     # Anthropic Claude integration
│   ├── gemini_provider.py        # Google Gemini integration
│   ├── deepseek_provider.py      # DeepSeek integration
│   └── ollama_provider.py        # Ollama local LLM integration
├── storage/                      # Data persistence
├── config/                       # Configuration management
├── secure_storage/               # Secure file operations (moved)
├── error_handler/                # Error handling system (moved)
├── scraping_service/             # Browser scraping engine (moved)
│   ├── core/                     # Core infrastructure
│   │   ├── service_registry.py   # Service discovery and registration
│   │   ├── orchestrator.py       # Multi-source coordination
│   │   ├── base_job_source.py    # Base classes and type definitions
│   │   └── health_monitor.py     # Service health checking
│   └── scrapers/                 # Browser-based scrapers
│       ├── base_scraper.py       # Base scraper implementation
│       ├── indeed/               # Indeed.com scraper
│       │   ├── scraper.py        # Indeed scraping logic
│       │   └── __init__.py
│       ├── linkedin/             # LinkedIn scraper
│       │   ├── scraper.py        # LinkedIn scraping logic
│       │   └── __init__.py
│       ├── ziprecruiter/         # ZipRecruiter scraper
│       │   ├── scraper.py        # ZipRecruiter scraping logic
│       │   └── __init__.py
│       └── greenhouse/           # Greenhouse.io scraper
│           ├── scraper.py        # Greenhouse scraping logic
│           └── __init__.py
└── webhook/                      # Webhook handling

# Comprehensive Testing
tests/                            # Test suite (70+ tests)
├── unit/                         # Unit tests (45+ tests)
│   ├── test_job_aggregator/      # JobAggregatorService tests
│   ├── test_scrapers/            # Scraper tests
│   ├── test_enrichment/          # Enrichment pipeline tests
│   ├── test_cli/                 # CLI tests
│   ├── test_cache/               # Cache system tests
│   ├── test_models/              # Data model tests
│   └── test_llm_provider/        # LLM provider tests
├── integration/                  # Integration tests (15+ tests)
│   ├── test_connectors_integration.py
│   └── test_service_integration.py
├── e2e/                          # End-to-end tests (5+ tests)
│   └── test_connectors_e2e.py
└── regression/                   # Regression tests (5+ tests)
    └── test_regression_workflows.py

# Supporting Infrastructure
audit_logger/                     # Audit logging system
├── __init__.py
├── audit_trail.py                # Audit trail implementation
└── logger.py                     # Audit logger
health_monitor/                   # System health monitoring
config/                           # Configuration management
docs/                            # Sphinx documentation
scripts/                         # Utility scripts
output/                          # Default output directory
```

## Core Services

### 1. JobAggregatorService (`tpm_job_finder_poc/job_aggregator/main.py`)
Central orchestration service that coordinates all job collection activities:

**Features:**
- Multi-source job collection (API + browser scraping)
- Intelligent deduplication with SQLite caching
- Health monitoring and service status tracking
- Async processing for concurrent job collection
- Comprehensive error handling and retry logic

**Integration Points:**
- API Aggregators: RemoteOK, Greenhouse, Lever, Ashby, Workable, SmartRecruiters
- Browser Scrapers: Indeed, LinkedIn, ZipRecruiter, Greenhouse
- Cache System: Deduplication and applied job tracking
- Enrichment Pipeline: Job enhancement and scoring

### 2. Scraping Service (`tpm_job_finder_poc/scraping_service/`)
Independent, production-ready browser scraping service:

**Architecture:**
- **Modular Design**: Plugin-based scraper system with service registry
- **Anti-Detection**: Rotating user agents, delays, fingerprint masking
- **Service Registry**: Dynamic scraper registration and discovery
- **Health Monitoring**: Service health checks and error reporting
- **Orchestration**: Multi-source coordination with error handling

**Supported Platforms:**
- Indeed.com: Job search and extraction
- LinkedIn: Professional network job scraping
- ZipRecruiter: Job board scraping
- Greenhouse.io: Company career pages

### 3. Enrichment Pipeline (`tpm_job_finder_poc/enrichment/`)
LLM-powered job analysis and enhancement system:

**Components:**
- **Job Description Parser**: Extract skills, requirements, compensation
- **ML Scorer**: Compatibility scoring based on user profile
- **Heuristic Scorer**: Rule-based job evaluation
- **Resume Parser**: Parse and analyze candidate profiles
- **LLM Integration**: Multi-provider LLM support for enhancement

**LLM Providers:**
- OpenAI GPT (GPT-3.5, GPT-4)
- Anthropic Claude
- Google Gemini
- DeepSeek
- Ollama (Local LLM support)

### 4. CLI Automation (`tpm_job_finder_poc/cli/`)
Complete workflow automation with configuration management:

**Interfaces:**
- **Automated CLI**: Configuration-driven automated workflows
- **Manual CLI**: Interactive job processing pipeline
- **Legacy Runner**: Backward compatibility support

**Features:**
- Configuration file support
- Multi-format output (JSON, Excel, CSV)
- Verbose logging and progress tracking
- Error handling and recovery

## Data Flow Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Sources   │    │ Browser Scrapers │    │  Configuration  │
│  (6 providers)  │    │  (4 platforms)   │    │     Files       │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬───────┘
          │                      │                       │
          └──────────────────────┼───────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  JobAggregatorService   │
                    │   (Central Orchestra)   │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Deduplication        │
                    │   (SQLite Cache)        │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │  Enrichment Pipeline    │
                    │    (LLM Enhancement)    │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │      Output             │
                    │ (JSON/Excel/CSV)        │
                    └─────────────────────────┘
```

## Testing Strategy

### Test Coverage (70+ Tests, 100% Pass Rate)
- **Unit Tests (45+ tests)**: Core functionality validation
  - JobAggregatorService functionality
  - Individual scraper implementations
  - Enrichment pipeline components
  - CLI interface operations
  - Cache system operations
  - Data model validation
  - LLM provider integrations

- **Integration Tests (15+ tests)**: Service-to-service communication
  - API aggregator integrations
  - Scraper service integration
  - Cache system integration
  - LLM provider integration

- **End-to-End Tests (5+ tests)**: Complete workflow validation
  - Full job collection workflows
  - Complete enrichment pipelines
  - End-to-end CLI operations

- **Regression Tests (5+ tests)**: Stability and performance monitoring
  - Performance regression detection
  - API compatibility validation
  - Data format consistency

### Test Features
- **Automatic API Key Handling**: LLM provider tests skip gracefully if API keys not configured
- **Secure Testing**: All file operations use SecureStorage
- **Comprehensive Coverage**: Tests validate all major components and workflows
- **Continuous Validation**: Test suite ensures production readiness

## Security & Compliance

### API Key Management
- **Local Development**: `llm_keys.txt` file (gitignored)
- **Production**: Environment variables
- **Security**: Never store keys in code or version control

### File Security
- **SecureStorage**: All file operations use secure storage layer
- **Path Validation**: Secure path handling for all file operations
- **Permission Management**: Proper file permissions and access control

### Network Security
- **Request Timeouts**: All external requests use timeouts
- **Input Validation**: Subprocess calls are validated for safety
- **Error Handling**: Comprehensive error handling and logging

## Usage Examples

### 1. Automated Job Search Workflow
```bash
python -m tpm_job_finder_poc.cli.automated_cli \
  --config config/automation_config.json \
  --keywords "product manager" "technical product manager" \
  --location "Remote" \
  --max-jobs 100 \
  --output results.xlsx \
  --verbose
```

### 2. Direct JobAggregatorService Usage
```bash
python -m tpm_job_finder_poc.job_aggregator.main \
  --keywords "senior product manager" \
  --location "San Francisco" \
  --max-jobs-per-source 25 \
  --output jobs.json
```

### 3. Independent Browser Scraping
```python
# Updated imports using current package structure
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams

orchestrator = ScrapingOrchestrator()
params = FetchParams(keywords=['python developer'], location='Remote', limit=50)
jobs = await orchestrator.collect_jobs(['indeed', 'linkedin'], params)
```

## Configuration Management

### Automation Configuration (`config/automation_config.json`)
```json
{
  "search_params": {
    "keywords": ["technical product manager", "senior product manager"],
    "location": "Remote",
    "date_posted": "pastWeek",
    "experience_level": "senior"
  },
  "sources": {
    "api_sources": ["remoteok", "greenhouse", "lever"],
    "scraping_sources": ["indeed", "linkedin", "ziprecruiter"]
  },
  "output": {
    "format": "excel",
    "directory": "./output/",
    "filename_template": "jobs_{date}_{keywords}.xlsx"
  },
  "enrichment": {
    "enabled": true,
    "llm_provider": "openai",
    "scoring_enabled": true
  },
  "limits": {
    "max_jobs_per_source": 50,
    "total_max_jobs": 200,
    "timeout_seconds": 300
  }
}
```

## Monitoring & Health

### Service Health Monitoring
- **JobAggregatorService**: Service status and error tracking
- **Scraping Service**: Individual scraper health and performance
- **LLM Providers**: API availability and response times
- **Cache System**: Cache hit rates and performance metrics

### Audit Logging
- **Job Collection Events**: All job collection activities logged
- **Enrichment Operations**: LLM enhancement tracking
- **User Interactions**: CLI usage and configuration changes
- **System Events**: Errors, warnings, and system state changes

### Log Files
- `app.log`: Application logs
- `audit_logger/`: Detailed audit trails
- `webhook.log`: Webhook events
- `cli_runner.log`: CLI execution logs

## Developer Onboarding

### Quick Start
1. **Clone Repository**: `git clone https://github.com/kevin-toles/tpm-job-finder-poc.git`
2. **Setup Environment**: `python -m venv .venv && source .venv/bin/activate`
3. **Install Dependencies**: `pip install -r requirements.txt && pip install -e .`
4. **Configure API Keys**: Create `llm_keys.txt` with your LLM provider keys
5. **Run Tests**: `python -m pytest tests/ -v` (should show 70+ tests passing)
6. **Try Example**: Run automated CLI with sample configuration

### Development Workflow
1. **Feature Development**: Create feature branch
2. **Write Tests**: Add comprehensive tests for new functionality
3. **Run Test Suite**: Ensure all 70+ tests pass
4. **Update Documentation**: Update relevant documentation files
5. **Code Review**: Submit pull request for review

## Change Management

This document is updated whenever major changes are made to:
- System architecture or core services
- Project structure or organization
- Security measures or compliance requirements
- Core features or interfaces
- Testing strategy or coverage
- Configuration management approach

For detailed change logs, see CHANGELOG.md.

## Production Readiness

The TPM Job Finder POC is production-ready with:
- ✅ **Complete Test Coverage**: 70+ tests with 100% pass rate
- ✅ **Production Architecture**: Modular, scalable service design
- ✅ **Comprehensive Monitoring**: Health checks and audit logging
- ✅ **Security Compliance**: Secure storage, API key management, input validation
- ✅ **Documentation**: Complete documentation coverage
- ✅ **Configuration Management**: Flexible configuration system
- ✅ **Error Handling**: Robust error handling and recovery
- ✅ **Performance**: Async processing and optimization

---
_Last updated: January 2025 - Architecture validated through comprehensive test suite (70+ tests passing)_
