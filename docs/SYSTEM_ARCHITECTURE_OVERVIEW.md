# TPM Job Finder POC - System Architecture Overview

**Version**: 3.0 (TDD-Complete Architecture)  
**Branch**: `dev`  
**Last Updated**: September 16, 2025

## 📖 **Overview**

This document provides a comprehensive guide to the TPM Job Finder POC system architecture, explaining the modern, TDD-complete service implementations alongside legacy components. This serves as the central navigation point for understanding how core services work together to deliver global job intelligence.

## 🏗️ **System Architecture Philosophy**

The TPM Job Finder POC has evolved into a **production-ready, TDD-driven architecture** that:

- ✅ **TDD Excellence**: Core services implemented with complete Test-Driven Development (RED-GREEN-REFACTOR cycles)
- ✅ **Modern Service Architecture**: New JobCollectionService represents production-ready patterns
- ✅ **Legacy Compatibility**: Maintains JobAggregatorService during transition period
- ✅ **Separates concerns** clearly between code, documentation, tests, and development tools
- ✅ **Follows Python best practices** with proper package layout and modern Pydantic V2
- ✅ **Zero Technical Debt**: Recent refactoring eliminated all warnings and deprecated patterns
- ✅ **Enables scalability** for team collaboration and production deployment

## 🚀 **Modern Architecture Highlights**

### **Production-Ready Services (TDD-Complete)**
- ✅ **JobCollectionService**: Complete TDD implementation (30/30 tests, zero warnings)
- ✅ **JobNormalizerService**: Complete TDD microservice (63/63 tests, REST API, advanced features)
- ✅ **Multi-Resume Intelligence**: ~142,000+ lines of comprehensive test coverage
- ✅ **Service Contracts**: IJobCollectionService & IJobNormalizerService interfaces with lifecycle management
- ✅ **Error Handling**: Specific exception types (ValidationError, JobCollectionTimeoutError, JobNormalizationError)
- ✅ **Data Pipeline**: Raw Data → Deduplication → Enrichment → JobPosting objects
- ✅ **Health Monitoring**: Real source status tracking and system health checks

### **Legacy Services (Transitioning)**
- 🔄 **JobAggregatorService**: Legacy orchestration service (functional but being replaced)
- � **Traditional Testing**: Existing test suites for backward compatibility

## 📁 **Modern System Structure**

```
tpm-job-finder-poc/                 # ROOT - Project root directory
│
├── 🔧 PROJECT CONFIGURATION        # Core project setup files
│   ├── setup.py                    # Python package configuration
│   ├── requirements.txt            # Project dependencies
│   ├── pytest.ini                 # Test configuration
│   ├── .gitignore                  # Git ignore patterns
│   ├── README.md                   # Main project documentation
│   ├── PROJECT_OVERVIEW.md         # Comprehensive project overview
│   ├── TDD_COMPONENT_AUDIT_CATALOG.md # TDD refactoring progress tracker
│   ├── CHANGELOG.md                # Version history and changes
│   └── dedupe_cache.db            # Deduplication database
│
├── 📚 DOCUMENTATION HUB            # Centralized documentation
│   └── docs/
│       ├── components/             # Component-specific documentation
│       │   ├── job_aggregator.md   # Legacy job aggregation service docs
│       │   ├── scraping_service.md # Web scraping service docs
│       │   ├── enrichment.md       # Data enrichment docs
│       │   ├── llm_provider.md     # LLM integration docs
│       │   ├── job_normalizer.md   # Job normalization docs
│       │   ├── JobPosting.md       # Job posting model docs
│       │   └── COMPONENT_INTEGRATION_MAP.md # Service integration guide
│       ├── architecture/           # System architecture documentation
│       │   ├── SYSTEM_ARCHITECTURE_WORKFLOWS.md # Technical workflows
│       │   └── BUSINESS_PROCESS_ARCHITECTURE.md # Business processes
│       ├── api/                    # API documentation
│       ├── Careerjet_Integration_Plan.md # Strategic plans
│       ├── SYSTEM_ARCHITECTURE_OVERVIEW.md    # This file
│       ├── AUTOMATION_README.md    # Automation documentation
│       ├── CODECOV.md             # Code coverage info
│       └── QUICK_REFERENCE.md     # Essential commands and patterns
│
├── 🏗️ DEVELOPMENT TOOLS           # Development automation and scripts
│   └── scripts/
│       ├── demo_automation.py      # Demo workflow automation
│       ├── generate_html.py        # Documentation generation
│       ├── run_tests.py           # Test automation script
│       ├── deploy.sh              # Deployment automation
│       └── validate_automation.py  # Validation workflows
│
├── 🧪 TESTING INFRASTRUCTURE      # Comprehensive test suite (440+ tests)
│   └── tests/
│       ├── unit/                   # Unit tests with TDD excellence
│       │   ├── job_collection_service/ # Modern service TDD tests (30 tests, complete)
│       │   ├── enrichment/         # Multi-resume intelligence (149 tests)
│       │   ├── job_aggregator/     # Legacy job aggregator unit tests
│       │   ├── test_scraping_service/ # Scraper unit tests
│       │   ├── cli/                # CLI unit tests
│       │   ├── cache/              # Cache unit tests
│       │   ├── models/             # Model unit tests
│       │   └── llm_provider/       # LLM provider unit tests
│       ├── integration/            # Integration tests (15+ tests)
│       │   ├── test_connectors_integration.py
│       │   ├── test_service_integration.py
│       │   ├── test_enrichment_integration.py
│       │   └── test_scraping_integration.py
│       ├── e2e/                   # End-to-end tests (5+ tests)
│       │   ├── test_connectors_e2e.py
│       │   ├── test_workflow_e2e.py
│       │   └── test_automation_e2e.py
│       ├── regression/            # Regression tests (5+ tests)
│       │   ├── test_regression_workflows.py
│       │   ├── test_performance_regression.py
│       │   └── test_api_compatibility.py
│       └── cross_component_tests/ # Cross-component integration tests
│           ├── cli_runner/        # CLI runner tests
│           ├── error_service/     # Error service tests
│           ├── logging_service/   # Logging service tests
│           ├── scraping_service/  # Scraping service tests
│           ├── poc/               # POC utility tests
│           ├── webhook/           # Webhook tests
│           └── fixtures/          # Test fixtures and data
│
├── 🏭 CORE SERVICES               # Main application services
│   └── tpm_job_finder_poc/
│       ├── job_collection_service/ # 🚀 MODERN (TDD-Complete)
│       │   ├── service.py          # JobCollectionService - production implementation
│       │   ├── api.py              # REST API endpoints (Pydantic V2)
│       │   ├── config.py           # Service configuration
│       │   └── __init__.py
│       ├── job_aggregator/         # 🔄 LEGACY (Transitioning)
│       │   ├── main.py             # JobAggregatorService - legacy orchestrator
│       │   ├── aggregators/        # API-based job sources
│       │   ├── cache/              # Deduplication cache
│       │   ├── controllers/        # Request handlers
│       │   ├── scrapers/           # Browser scraper integration
│       │   └── services/           # Supporting services
│       ├── enrichment/             # ✅ TDD-COMPLETE Multi-resume intelligence
│       │   ├── hybrid_selection_engine.py     # Two-stage selection logic
│       │   ├── enhanced_content_analyzer.py   # Content analysis
│       │   ├── resume_discovery_service.py    # Resume discovery
│       │   ├── cultural_fit_service.py        # Cultural fit assessment
│       │   ├── geographic_llm_integration.py  # Geographic intelligence
│       │   ├── salary_benchmarking_service.py # Salary benchmarking
│       │   ├── immigration_support_service.py # Immigration support (Phase 5+)
│       │   ├── enterprise_service.py          # Enterprise features (Phase 5+)
│       │   ├── career_modeling_service.py     # Career modeling (Phase 5+)
│       │   └── interfaces.py                  # Service interfaces
│       ├── shared/                 # Shared contracts and interfaces
│       │   └── contracts/
│       │       └── job_collection_service.py  # IJobCollectionService interface

│       │   └── integration/       # Cross-component integration
│
├── 📊 OUTPUT & DATA               # Generated data and logs
│   ├── output/                    # Generated results
│   │   ├── results.csv            # CSV output
│   │   ├── results.json           # JSON output
│   │   └── results.xlsx           # Excel output
│   ├── logs/                      # Application logs
│   │   ├── automated_cli.log      # Automated CLI logs
│   │   └── cli_runner.log         # CLI runner logs
│   └── secure_storage/            # Secure data storage
│       ├── files/                 # Secure file storage
│       │   └── sample_resume.txt  # Sample resume data
│       ├── logs/                  # Secure audit logs
│       │   └── audit.jsonl        # Audit trail logs
│       └── metadata/              # File metadata storage
│           ├── sample_resume.txt.json     # Resume metadata
│           └── test_analytics.json       # Analytics metadata
│
└── 🔧 ENVIRONMENT & BUILD         # Environment and build artifacts
    ├── .venv/                     # Python virtual environment
    ├── .pytest_cache/             # Test cache
    ├── tpm_job_finder_poc.egg-info/ # Package metadata
    ├── .github/                   # GitHub workflows and actions
    │   └── workflows/             # CI/CD workflows
    └── .git/                      # Git repository data
```

## 🎯 **Architecture Principles**
│
└── 🔧 ENVIRONMENT & BUILD         # Environment and build artifacts
    ├── .venv/                     # Python virtual environment
    ├── .pytest_cache/             # Test cache
    ├── tpm_job_finder_poc.egg-info/ # Package metadata
    ├── .github/                   # GitHub workflows and actions
    │   └── workflows/             # CI/CD workflows
    └── .git/                      # Git repository data
```

## 🎯 **Architecture Principles**

### 1. **Modern vs Legacy Service Design**

The architecture clearly distinguishes between modern TDD-complete services and legacy components:

**🚀 Modern Services (TDD-Complete)**
- `job_collection_service/` - Production-ready with 30/30 tests passing
- `enrichment/` - Multi-resume intelligence with 149+ tests
- Follow strict interface contracts (`shared/contracts/`)
- Implement complete lifecycle management
- Zero-warning Pydantic V2 compliance

**🔄 Legacy Services (Transitioning)** 
- `job_aggregator/` - Original orchestrator service (planned for modernization)
- Maintain backward compatibility during migration
- Gradual replacement with modern equivalents

### 2. **Clear Separation of Concerns**

Each top-level directory has a specific purpose:

- **`docs/`**: ALL documentation (no scattered READMEs)
- **`scripts/`**: ALL development tools and automation
- **`tests/`**: ALL testing code with proper hierarchy (440+ tests)
- **`tpm_job_finder_poc/`**: ONLY production application code
- **`logs/`**: ALL log files (no logs in root)

### 3. **Test-Driven Development Excellence**

**TDD Methodology Applied:**
- Complete RED-GREEN-REFACTOR cycles for new services
- Interface-driven development with strict contracts
- Comprehensive test coverage (440+ tests across categories)
- Zero-warning implementations with modern patterns
- Production-ready code from day one

**Test Categories:**
- **Unit Tests**: 440+ focused tests including TDD-complete services
- **Integration Tests**: Cross-service testing and API validation  
- **End-to-End Tests**: Complete workflow validation
- **Regression Tests**: Preventing functionality degradation

### 4. **Modern Development Patterns**

**Code Quality Standards:**
- Pydantic V2 compliance with ConfigDict patterns
- Type hints throughout codebase
- Comprehensive error handling and logging
- Health monitoring and observability
- Security-first design principles

**Service Architecture:**
- Interface segregation with shared contracts
- Dependency injection patterns
- Lifecycle management (start/stop/health)
- Configurable service composition
- Graceful error handling and recovery

## 🔧 **Core Service Contracts**

### JobCollectionService Interface

The modern `IJobCollectionService` contract defines the standard for job collection services:

```python
# Located: tpm_job_finder_poc/shared/contracts/job_collection_service.py
class IJobCollectionService:
    async def start(self) -> None
    async def stop(self) -> None  
    async def collect_jobs(self, config: JobCollectionConfig) -> List[JobPosting]
    async def get_health_status(self) -> Dict[str, Any]
    async def get_statistics(self) -> Dict[str, Any]
```

**Implementation Examples:**
- ✅ `JobCollectionService` - TDD-complete production implementation
- 🔄 `JobAggregatorService` - Legacy service being modernized

### Service Dependencies

**Modern Service Stack:**
- `JobStorage` - Data persistence and retrieval
- `JobEnricher` - Data enhancement and normalization  
- `JobCollectionConfig` - Service configuration management
- Health monitoring and statistics tracking

## 📊 **Testing Strategy**

### TDD Implementation Progress

**Completed (TDD-Complete):**
1. ✅ **JobCollectionService** - 30/30 tests, zero warnings, production-ready
2. ✅ **Enrichment Services** - 149+ tests, multi-resume intelligence complete

**In Progress (Legacy → Modern Migration):**
- 🔄 **JobAggregatorService** - Planned for TDD refactoring
- 🔄 **ScrapingService** - Browser automation modernization planned

### Test Coverage Metrics

- **Total Tests**: 440+ comprehensive tests
- **Unit Test Coverage**: Extensive coverage for core services
- **Integration Coverage**: Cross-service validation
- **TDD Services**: 179+ tests (job_collection_service + enrichment)
- **Warning-Free**: Modern services achieve zero warnings

## 🚀 **Getting Started**

### Quick Development Setup

```bash
# Clone and setup
git clone <repository>
cd tpm-job-finder-poc

# Install dependencies
pip install -r requirements.txt

# Run TDD-complete service tests
pytest tests/unit/job_collection_service/ -v

# Run enrichment service tests  
pytest tests/unit/enrichment/ -v

# Run all tests
pytest --tb=short
```

### Modern Service Usage

```python
# Using the TDD-complete JobCollectionService
from tpm_job_finder_poc.job_collection_service import JobCollectionService
from tpm_job_finder_poc.job_collection_service.config import JobCollectionConfig

# Initialize service
service = JobCollectionService()
await service.start()

# Configure and collect jobs
config = JobCollectionConfig(
    sources=["api", "scraping"],
    max_results=100,
    enable_enrichment=True
)

jobs = await service.collect_jobs(config)
stats = await service.get_statistics()
health = await service.get_health_status()

# Clean shutdown
await service.stop()
```

## 📋 **Documentation Navigation**

### Architecture Documents
- [`SYSTEM_ARCHITECTURE_OVERVIEW.md`](SYSTEM_ARCHITECTURE_OVERVIEW.md) - This document
- [`SYSTEM_ARCHITECTURE_WORKFLOWS.md`](architecture/SYSTEM_ARCHITECTURE_WORKFLOWS.md) - Technical workflows
- [`BUSINESS_PROCESS_ARCHITECTURE.md`](../BUSINESS_PROCESS_ARCHITECTURE.md) - Business processes

### Component Documentation  
- [`job_collection_service/`](components/) - Modern service documentation
- [`enrichment.md`](components/enrichment.md) - Multi-resume intelligence
- [`scraping_service.md`](components/scraping_service.md) - Browser automation
- [`llm_provider.md`](components/llm_provider.md) - LLM integration

### Development Guides
- [`TDD_COMPONENT_AUDIT_CATALOG.md`](../TDD_COMPONENT_AUDIT_CATALOG.md) - TDD progress tracking
- [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md) - Essential commands and patterns
- [`AUTOMATION_README.md`](AUTOMATION_README.md) - Automation workflows

---

*This document reflects the current system architecture as of the latest TDD implementation completion. For the most current implementation status, refer to the TDD Component Audit Catalog.*
│       │   ├── __init__.py
│       │   ├── embeddings.py      # Vector embeddings
│       │   ├── entity_canonicalizer.py # Entity canonicalization
│       │   ├── heuristic_scorer.py # Heuristic scoring
│       │   ├── heuristic_scorer_health.py # Health monitoring
│       │   ├── jd_parser.py       # Job description parsing
│       │   ├── llm_provider.py    # LLM integration
│       │   ├── ml_scorer.py       # Machine learning scoring
│       │   ├── orchestrator.py    # Enrichment orchestration
│       │   ├── orchestrator_health.py # Health monitoring
│       │   ├── resume_feedback_generator.py # Resume feedback
│       │   ├── resume_parser.py   # Resume parsing
│       │   ├── taxonomy_mapper.py # Taxonomy mapping
│       │   ├── timeline_analyzer.py # Timeline analysis
│       │   └── tests/             # Enrichment tests
│       ├── llm_provider/          # LLM integration layer
│       │   ├── __init__.py
│       │   ├── adapter.py         # LLM adapter interface
│       │   ├── anthropic_provider.py # Anthropic integration
│       │   ├── base.py            # Base LLM provider
│       │   ├── deepseek_provider.py # DeepSeek integration
│       │   ├── gemini_provider.py # Google Gemini integration
│       │   ├── ollama_provider.py # Ollama integration
│       │   ├── openai_provider.py # OpenAI integration
│       │   ├── health.py          # Health monitoring
│       │   ├── Dockerfile         # Container configuration
│       │   ├── requirements.txt   # Service dependencies
│       │   └── tests/             # LLM provider tests
│       ├── models/                # Data models and schemas
│       │   ├── __init__.py
│       │   ├── application.py     # Application model
│       │   ├── job.py             # Job model
│       │   ├── resume.py          # Resume model
│       │   ├── user.py            # User model
│       │   └── tests/             # Model tests
│       ├── cache/                 # Caching system
│       │   ├── __init__.py
│       │   ├── applied_tracker.py # Applied job tracking
│       │   ├── cache_manager.py   # Cache management
│       │   ├── dedupe_cache.py    # Deduplication cache
│       │   └── tests/             # Cache tests
│       ├── config/                # Configuration management
│       │   ├── __init__.py
│       │   ├── config.py          # Configuration loader
│       │   ├── automation_config.json # Automation settings
│       │   ├── llm_keys.txt       # LLM API keys
│       │   └── tests/             # Configuration tests
│       ├── cli/                   # Command-line interface
│       │   ├── __init__.py
│       │   ├── __main__.py        # CLI entry point
│       │   ├── cli.py             # CLI implementation
│       │   ├── runner.py          # CLI runner
│       │   ├── requirements.txt   # CLI dependencies
│       │   └── tests/             # CLI tests
│       ├── job_normalizer/        # Job data normalization (Legacy)
│       │   ├── __init__.py
│       │   ├── Dockerfile         # Container configuration
│       │   ├── requirements.txt   # Service dependencies
│       │   ├── jobs/              # Job processing functions
│       │   └── tests/             # Normalization tests
│       ├── job_normalizer_service/ # 🚀 TDD Job Normalization Microservice
│       │   ├── __init__.py
│       │   ├── service.py         # Core service implementation
│       │   ├── api.py             # FastAPI REST endpoints
│       │   ├── config.py          # Service configuration
│       │   └── README.md          # Service documentation
│       ├── resume_store/          # Resume storage and management
│       │   ├── __init__.py
│       │   ├── metadata.py        # Resume metadata
│       │   ├── search.py          # Resume search
│       │   ├── store.py           # Resume storage
│       │   ├── requirements.txt   # Service dependencies
│       │   ├── resume/            # Resume data
│       │   └── tests/             # Resume store tests
│       ├── resume_uploader/       # Resume upload functionality
│       │   ├── __init__.py
│       │   ├── parser.py          # Resume parsing
│       │   ├── storage.py         # Upload storage
│       │   ├── uploader.py        # Upload handler
│       │   ├── requirements.txt   # Service dependencies
│       │   └── tests/             # Upload tests
│       ├── audit_logger/          # Audit logging system
│       │   ├── __init__.py
│       │   ├── audit_trail.py     # Audit trail management
│       │   ├── logger.py          # Audit logger
│       │   ├── requirements.txt   # Logger dependencies
│       │   └── tests/             # Audit tests
│       ├── health_monitor/        # System health monitoring
│       │   ├── __init__.py
│       │   └── tests/             # Health monitor tests
│       ├── storage/               # Data storage layer
│       │   └── [storage modules]  # Storage implementations
│       ├── webhook/               # Webhook functionality
│       │   └── [webhook modules]  # Webhook implementations
│       ├── error_handler/         # Error handling system
│       │   ├── __init__.py
│       │   └── handler.py         # Error handler
│       ├── secure_storage/        # Secure file storage
│       │   ├── files/             # Secure file storage
│       │   ├── logs/              # Secure logs
│       │   └── metadata/          # File metadata
│       └── cli_runner/            # CLI runner system
│           └── [CLI runner modules]
│
├── 🔄 COMPATIBILITY & MIGRATION   # Backward compatibility
│   └── scraping_service_v2.py      # Compatibility module for imports
│
├── 📊 OUTPUT & DATA               # Generated data and logs
│   ├── output/                    # Generated results
│   │   ├── results.csv            # CSV output
│   │   ├── results.json           # JSON output
│   │   └── results.xlsx           # Excel output
│   └── logs/                      # Application logs
│       └── cli_runner.log         # CLI runner logs
│
│
└── 🔧 ENVIRONMENT & BUILD         # Environment and build artifacts
    ├── .venv/                     # Python virtual environment
    ├── .pytest_cache/             # Test cache
    ├── tpm_job_finder_poc.egg-info/ # Package metadata
    ├── .github/                   # GitHub workflows and actions
    │   └── workflows/             # CI/CD workflows
    └── .git/                      # Git repository data
```

## 🎯 **Architecture Principles**

### 1. **Modern vs Legacy Service Design**

The architecture clearly distinguishes between modern TDD-complete services and legacy components:

**🚀 Modern Services (TDD-Complete)**
- `job_collection_service/` - Production-ready with 30/30 tests passing
- `enrichment/` - Multi-resume intelligence with 149+ tests
- Follow strict interface contracts (`shared/contracts/`)
- Implement complete lifecycle management
- Zero-warning Pydantic V2 compliance

**🔄 Legacy Services (Transitioning)** 
- `job_aggregator/` - Original orchestrator service (planned for modernization)
- Maintain backward compatibility during migration
- Gradual replacement with modern equivalents

### 2. **Clear Separation of Concerns**

Each top-level directory has a specific purpose:

- **`docs/`**: ALL documentation (no scattered READMEs)
- **`scripts/`**: ALL development tools and automation
- **`tests/`**: ALL testing code with proper hierarchy
- **`tpm_job_finder_poc/`**: ONLY production application code
- **`logs/`**: ALL log files (no logs in root)
- **`output/`**: ALL generated results

### 2. **Python Package Best Practices**

- ✅ **Package structure**: `tpm_job_finder_poc/` as main package
- ✅ **Module organization**: Clear component separation
- ✅ **Import compatibility**: Maintained through compatibility layer
- ✅ **Configuration centralization**: All configs in `config/`
- ✅ **Test organization**: Hierarchical test structure

### 3. **Documentation Centralization**

- ✅ **Component docs**: All in `docs/components/`
- ✅ **Strategic plans**: Centralized in `docs/`
- ✅ **API docs**: Organized in `docs/api/`
- ✅ **No scattered READMEs**: Everything in docs hierarchy

### 4. **Development Tool Organization**

- ✅ **Scripts centralization**: All automation in `scripts/`
- ✅ **Build tools**: Accessible and organized
- ✅ **Deployment automation**: Centralized workflows
- ✅ **Validation tools**: Easy to find and use

## 📋 **File Placement Guidelines**

### ✅ **DO: Proper File Placement**

| File Type | Correct Location | Example |
|-----------|------------------|---------|
| **Application Code** | `tpm_job_finder_poc/[component]/` | `tpm_job_finder_poc/job_aggregator/main.py` |
| **Component Documentation** | `docs/components/` | `docs/components/job_aggregator.md` |
| **Development Scripts** | `scripts/` | `scripts/run_tests.py` |
| **Unit Tests** | `tests/unit/test_[component]/` | `tests/unit/test_job_aggregator/` |
| **Integration Tests** | `tests/integration/` | `tests/integration/test_service_integration.py` |
| **Configuration Files** | `tpm_job_finder_poc/config/` | `tpm_job_finder_poc/config/automation_config.json` |
| **Log Files** | `logs/` | `logs/cli_runner.log` |
| **Generated Results** | `output/` | `output/results.xlsx` |
| **Strategic Documentation** | `docs/` | `docs/Careerjet_Integration_Plan.md` |

### ❌ **DON'T: Avoid These Patterns**

| Anti-Pattern | Why It's Wrong | Correct Approach |
|--------------|----------------|------------------|
| **Root clutter** | `root/my_script.py` | Move to `scripts/my_script.py` |
| **Scattered docs** | `component/README.md` | Move to `docs/components/component.md` |
| **Mixed concerns** | `tpm_job_finder_poc/build_script.py` | Move to `scripts/build_script.py` |
| **Logs in root** | `root/app.log` | Move to `logs/app.log` |
| **Config scatter** | `component/config.json` | Centralize in `tpm_job_finder_poc/config/` |

## 🔧 **Adding New Components**

### Step 1: Create Component Structure

```bash
# Create new component
mkdir -p tpm_job_finder_poc/new_component
touch tpm_job_finder_poc/new_component/__init__.py
touch tpm_job_finder_poc/new_component/main.py

# Create component tests
mkdir -p tests/unit/test_new_component
touch tests/unit/test_new_component/__init__.py
touch tests/unit/test_new_component/test_main.py
```

### Step 2: Add Documentation

```bash
# Create component documentation
touch docs/components/new_component.md
```

### Step 3: Add Configuration (if needed)

```bash
# Add configuration if needed
touch tpm_job_finder_poc/config/new_component_config.json
```

### Step 4: Update Dependencies

```bash
# Add to main requirements if needed
echo "new-dependency==1.0.0" >> requirements.txt

# Or create component-specific requirements
touch tpm_job_finder_poc/new_component/requirements.txt
```

## 🧪 **Testing Structure Guidelines**

### Test Hierarchy

```
tests/
├── unit/                    # Fast, isolated tests
│   └── test_[component]/    # One directory per component
├── integration/             # Cross-service tests
├── e2e/                    # Full workflow tests
├── regression/             # Performance and compatibility
└── cross_component_tests/  # Legacy cross-component tests
```

### Test File Naming

- **Unit tests**: `test_[module_name].py`
- **Integration tests**: `test_[feature]_integration.py`
- **E2E tests**: `test_[workflow]_e2e.py`
- **Regression tests**: `test_[area]_regression.py`

## 📚 **Documentation Guidelines**

### Documentation Structure

```
docs/
├── components/              # Component-specific docs
├── api/                    # API documentation
├── [Strategic Plans].md    # High-level plans
├── [Process Guides].md     # Process documentation
└── README.md              # Documentation index
```

### Documentation Standards

1. **Component docs**: Always use `docs/components/[component].md`
2. **Strategic plans**: Use descriptive names in `docs/`
3. **API docs**: Auto-generated in `docs/api/`
4. **Process guides**: Clear, actionable documentation

## 🔄 **Import System Guidelines**

### Current Import Patterns

```python
# ✅ Correct: Use package imports
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
from tpm_job_finder_poc.scraping_service.core.orchestrator import ScrapingOrchestrator

# ✅ Acceptable: Use compatibility layer (temporary)
from scraping_service_v2.core.orchestrator import ScrapingOrchestrator

# ❌ Avoid: Direct relative imports from moved modules
from scraping_service_v2.core.orchestrator import ScrapingOrchestrator  # Will be deprecated
```

### Migration Status

- **Current**: Compatibility layer active (`scraping_service_v2.py`)
- **Phase 2**: Update all imports to use package structure
- **Phase 3**: Remove compatibility layer

## 🚀 **Development Workflow**

### 1. **Setting Up Development**

```bash
# Clone and setup
git clone https://github.com/kevin-toles/tpm-job-finder-poc.git
cd tpm-job-finder-poc
git checkout clean-structure-v2

# Setup environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. **Running Tests**

```bash
# Use the centralized test script
python scripts/run_tests.py

# Or run pytest directly
python -m pytest tests/ -v
```

### 3. **Adding Features**

1. **Create component** in `tpm_job_finder_poc/[component]/`
2. **Add tests** in `tests/unit/test_[component]/`
3. **Document component** in `docs/components/[component].md`
4. **Update main docs** if needed

### 4. **Running Automation**

```bash
# Use centralized scripts
python scripts/demo_automation.py      # Run demos
python scripts/validate_automation.py  # Validate system
python scripts/generate_html.py        # Generate docs
```

## 📊 **Maintenance Guidelines**

### Regular Maintenance Tasks

1. **Clean cache files**:
   ```bash
   find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
   find . -name "*.pyc" -delete
   ```

2. **Update documentation**:
   - Keep component docs current in `docs/components/`
   - Update strategic plans in `docs/`
   - Regenerate API docs as needed

3. **Organize logs**:
   - Move new log files to `logs/`
   - Archive old logs as needed

4. **Review structure**:
   - Ensure no files in wrong locations
   - Check for scattered documentation
   - Validate import patterns

### Quality Checks

```bash
# Check for files in wrong locations
find . -maxdepth 1 -name "*.py" | grep -v "setup.py\|scraping_service_v2.py"

# Check for scattered documentation
find tpm_job_finder_poc/ -name "*.md" | head -5

# Validate import compatibility
python -c "from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService; print('✅ Imports working')"
```

## 🎯 **Best Practices Summary**

### ✅ **DO**

- **Follow the structure**: Put files in their designated locations
- **Centralize documentation**: Use `docs/` hierarchy
- **Use package imports**: Import from `tpm_job_finder_poc.*`
- **Organize by component**: Keep related code together
- **Use provided scripts**: Leverage `scripts/` automation
- **Write tests**: Follow the test hierarchy
- **Document changes**: Update relevant documentation

### ❌ **DON'T**

- **Scatter files**: Don't put random files in root
- **Mix concerns**: Don't put scripts in application package
- **Skip documentation**: Don't leave components undocumented
- **Break imports**: Don't use deprecated import patterns
- **Ignore structure**: Don't create new organizational patterns
- **Bypass scripts**: Don't reinvent existing automation

## 🔗 **Related Documentation**

- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**: Complete project overview
- **[IMPORT_MIGRATION_PLAN.md](IMPORT_MIGRATION_PLAN.md)**: Import system migration
- **[Careerjet_Integration_Plan.md](Careerjet_Integration_Plan.md)**: Strategic enhancement plan
- **[tests/README.md](../tests/README.md)**: Comprehensive test documentation
- **[scripts/](../scripts/)**: Development automation tools

## 📞 **Getting Help**

1. **Structure questions**: Refer to this document
2. **Component docs**: Check `docs/components/`
3. **API reference**: See `docs/api/`
4. **Test guidance**: See `tests/README.md`
5. **Automation help**: Check scripts in `scripts/`

---

**Remember**: This structure is designed for **scalability**, **maintainability**, and **team collaboration**. Following these guidelines ensures the project remains **professional** and **production-ready** as it grows! 🚀

_Last updated: September 11, 2025 - Clean Structure v2.0_
