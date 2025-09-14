# TPM Job Finder POC: Project Overview

## Purpose
This document provides a comprehensive overview of the TPM Job Finder Proof of Concept (POC) - a **production-ready global job intelligence platform** implementing Phase 5+ advanced features. The system combines automated job search, AI-powered assessment, enterprise multi-user capabilities, immigration support, and advanced career modeling into a unified platform designed for Technical Product Managers and professionals seeking global career opportunities. It is intended for new developers, teams with dependencies, and stakeholders who need to understand the complete system architecture before diving into detailed documentation.

## System Overview
The TPM Job Finder POC is a sophisticated, enterprise-grade global job intelligence platform that combines API-based job collection, browser scraping, intelligent deduplication, LLM-powered enrichment, immigration support, enterprise collaboration, and advanced career modeling into a unified workflow automation platform with international expansion capabilities.

## Architecture Summary
- **Language & Frameworks:** Python 3.13+, Selenium WebDriver, pytest, asyncio
- **Project Structure:** Modern Python package with microservice-inspired architecture
- **Core Architecture:**
  - **JobAggregatorService**: Central orchestration service for multi-source job collection
  - **Scraping Service v2**: Independent, modular browser scraping service
  - **Enrichment Pipeline**: LLM-powered job analysis and enhancement including Phase 5+ advanced services
  - **Immigration Support Service**: Comprehensive visa analysis and relocation planning *(Phase 5+)*
  - **Enterprise Multi-User Service**: Team collaboration and international expansion tracking *(Phase 5+)*
  - **Advanced Career Modeling Service**: Career pathway analysis and skill forecasting *(Phase 5+)*
  - **CLI Automation**: Complete workflow automation with configuration management
  - **Comprehensive Testing**: 440+ tests with strategic fast mode (6.46s) and comprehensive mode (~70s)

## Key Features
### **Core Job Intelligence Platform**
- **Multi-Source Job Aggregation**: API sources (RemoteOK, Greenhouse, Lever, Ashby, Workable, SmartRecruiters) + Browser scraping (Indeed, LinkedIn, ZipRecruiter, Greenhouse)
- **Intelligent Deduplication**: Advanced SQLite-based caching with fuzzy matching across all sources
- **AI-Powered Job Analysis**: LLM-powered job scoring, cultural fit assessment, and salary benchmarking
- **Geographic Intelligence**: Regional organization with cultural adaptation insights and visa requirements

### **Phase 5+ Advanced Features**
- **Immigration & Relocation Support**: Comprehensive visa analysis for 50+ countries, 200+ verified immigration lawyers, cost planning, timeline creation
- **Enterprise Multi-User Features**: Role-based permissions (Admin, Manager, Recruiter, Employee, Viewer), team collaboration, opportunity sharing, 6-stage international expansion tracking
- **Advanced Career Modeling**: International career pathway analysis, skill gap assessment, 5-year demand forecasting, personalized development plans with success probability scoring
- **Global Market Intelligence**: Regional talent analytics, competitive insights, hiring velocity benchmarking, cost-of-living adjustments

### **Production Infrastructure**
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
│   ├── cultural_fit_service.py   # Cultural fit assessment (Phase 5+)
│   ├── geographic_llm_integration.py # Geographic LLM integration (Phase 5+)
│   ├── salary_benchmarking_service.py # Salary benchmarking (Phase 5+)
│   ├── immigration_support_service.py # Immigration support (Phase 5+)
│   ├── enterprise_service.py     # Enterprise multi-user features (Phase 5+)
│   ├── career_modeling_service.py # Advanced career modeling (Phase 5+)
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
tests/                            # Test suite (440+ tests)
├── unit/                         # Unit tests with fast mode support
│   ├── enrichment/               # Enrichment tests (149 tests consolidated)
│   │   ├── test_cultural_fit_service.py     # Cultural fit assessment tests
│   │   ├── test_geographic_llm_integration.py # Geographic LLM tests
│   │   ├── test_phase5_integration.py       # Phase 5+ integration tests
│   │   ├── test_salary_benchmarking_service.py # Salary benchmarking tests
│   │   └── [other enrichment tests]        # Additional enrichment tests
│   ├── job_aggregator/           # JobAggregatorService tests
│   ├── cache/                    # Cache system tests
│   ├── models/                   # Data model tests
│   └── llm_provider/             # LLM provider tests
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
LLM-powered job analysis and enhancement system with Phase 5+ advanced features:

**Core Components:**
- **Job Description Parser**: Extract skills, requirements, compensation
- **ML Scorer**: Compatibility scoring based on user profile
- **Heuristic Scorer**: Rule-based job evaluation
- **Resume Parser**: Parse and analyze candidate profiles
- **LLM Integration**: Multi-provider LLM support for enhancement

**Phase 5+ Advanced Services:**
- **Cultural Fit Service**: International adaptation analysis with regional context
- **Geographic LLM Integration**: Location-specific insights and visa requirements
- **Salary Benchmarking Service**: Real-time market comparison with PPP adjustment
- **Immigration Support Service**: Comprehensive visa analysis and relocation planning
- **Enterprise Multi-User Service**: Team collaboration and expansion tracking
- **Advanced Career Modeling Service**: Career pathway analysis and skill forecasting

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

### Test Coverage (440+ Tests, Strategic Performance Optimization)
- **Fast Mode (334 tests, 6.46s)**: Optimized for development with core functionality validation
  - Core business logic and unit tests
  - Local computation and logic validation  
  - Rapid feedback loop for development
  - 100% pass rate for executed tests

- **Comprehensive Mode (440+ tests, ~70s)**: Full validation including external dependencies
  - Network-dependent API integration tests
  - Browser automation and scraping tests
  - Advanced feature tests (Phase 5+ services)
  - Complete end-to-end workflow validation

- **Strategic Test Organization**:
  - **Unit Tests (334+ in fast mode)**: Core functionality validation including 149 consolidated enrichment tests
  - **Integration Tests (15+ tests)**: Service-to-service communication
  - **End-to-End Tests (5+ tests)**: Complete workflow validation  
  - **Regression Tests (5+ tests)**: Stability and performance monitoring

### Test Features
- **Fast Mode Support**: `PYTEST_FAST_MODE=1` for 6.46s execution during development
- **Comprehensive Coverage**: Full test suite for CI/CD and production validation
- **Automatic API Key Handling**: LLM provider tests skip gracefully if API keys not configured
- **Secure Testing**: All file operations use SecureStorage
- **Consolidated Organization**: All enrichment tests properly organized in tests/unit/enrichment/
- **Network Test Isolation**: External dependencies excluded in fast mode for performance

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
5. **Run Fast Tests**: `PYTEST_FAST_MODE=1 python -m pytest tests/ -v` (should show 334+ tests passing in 6.46s)
6. **Try Example**: Run automated CLI with sample configuration

### Development Workflow
1. **Feature Development**: Create feature branch
2. **Write Tests**: Add comprehensive tests for new functionality
3. **Run Fast Tests**: `PYTEST_FAST_MODE=1 python -m pytest tests/ -v` during development
4. **Run Full Tests**: `python -m pytest tests/ -v` before commits (ensure all 440+ tests pass)
5. **Update Documentation**: Update relevant documentation files
6. **Code Review**: Submit pull request for review

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

The TPM Job Finder POC is production-ready with Phase 5+ enterprise capabilities:
- ✅ **Complete Test Coverage**: 440+ tests with strategic fast mode (6.46s) and comprehensive mode (~70s)
- ✅ **Production Architecture**: Modular, scalable service design with enterprise features
- ✅ **Comprehensive Monitoring**: Health checks and audit logging
- ✅ **Security Compliance**: Secure storage, API key management, input validation
- ✅ **Global Coverage**: 50+ countries immigration support, cultural intelligence, international expansion
- ✅ **Enterprise Features**: Multi-user collaboration, role-based access, team management
- ✅ **Advanced Analytics**: Career modeling, market forecasting, competitive intelligence
- ✅ **Documentation**: Complete documentation coverage including business process architecture
- ✅ **Configuration Management**: Flexible configuration system
- ✅ **Error Handling**: Robust error handling and recovery
- ✅ **Performance**: Async processing and optimization with fast test feedback
- ✅ **Phase 5+ Services**: Immigration, enterprise, and career modeling fully implemented and tested

---
_Last updated: September 2025 - Phase 5+ global job intelligence platform with comprehensive immigration support, enterprise multi-user features, and advanced career modeling validated through comprehensive test suite (440+ tests) with strategic performance optimization_
