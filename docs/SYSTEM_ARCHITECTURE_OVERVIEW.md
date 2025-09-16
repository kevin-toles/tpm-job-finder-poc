# TPM Job Finder POC - Project Structure Guide

**Version**: 2.0 (Clean Structure)  
**Branch**: `clean-structure-v2`  
**Last Updated**: September 11, 2025

## 📖 **Overview**

This document provides a comprehensive guide to the TPM Job Finder POC project structure, explaining how to navigate, maintain, and contribute to the codebase while adhering to professional Python development standards.

## 🏗️ **Project Structure Philosophy**

The TPM Job Finder POC follows a **clean, production-ready Python package structure** that:

- ✅ **Separates concerns** clearly between code, documentation, tests, and development tools
- ✅ **Follows Python best practices** with proper package layout
- ✅ **Centralizes documentation** for easy maintenance and discovery
- ✅ **Organizes development tools** for streamlined workflows
- ✅ **Maintains backward compatibility** during transitions
- ✅ **Enables scalability** for team collaboration and production deployment

## 📁 **Complete Directory Structure**

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
│   ├── CHANGELOG.md                # Version history and changes
│   └── dedupe_cache.db            # Deduplication database
│
├── 📚 DOCUMENTATION HUB            # Centralized documentation
│   └── docs/
│       ├── components/             # Component-specific documentation
│       │   ├── job_aggregator.md   # Job aggregation service docs
│       │   ├── scraping_service.md # Web scraping service docs
│       │   ├── enrichment.md       # Data enrichment docs
│       │   ├── llm_provider.md     # LLM integration docs
│       │   ├── job_normalizer.md   # Job normalization docs
│       │   ├── JobPosting.md       # Job posting model docs
│       │   └── scraping_service_phase2.md # Scraping evolution docs
│       ├── api/                    # API documentation
│       ├── Careerjet_Integration_Plan.md # Strategic plans
│       ├── Careerjet_Integration_Plan.html # HTML version
│       ├── IMPORT_MIGRATION_PLAN.md # Import migration guide
│       ├── SYSTEM_ARCHITECTURE_OVERVIEW.md    # This file
│       ├── AUTOMATION_README.md    # Automation documentation
│       ├── CODECOV.md             # Code coverage info
│       ├── RELEASE.md             # Release procedures
│       ├── STUBS_README.md        # Stub documentation
│       ├── STUB_CATALOG.md        # Stub catalog
│       ├── conf.py                # Sphinx configuration
│       ├── config.rst             # Configuration docs
│       ├── index.rst              # Sphinx index
│       └── onboarding.rst         # Onboarding guide
│
├── 🏗️ DEVELOPMENT TOOLS           # Development automation and scripts
│   └── scripts/
│       ├── demo_automation.py      # Demo workflow automation
│       ├── generate_html.py        # Documentation generation
│       ├── run_tests.py           # Test automation script
│       ├── deploy.sh              # Deployment automation
│       └── validate_automation.py  # Validation workflows
│
├── 🧪 TESTING INFRASTRUCTURE      # Comprehensive test suite
│   └── tests/
│       ├── unit/                   # Unit tests (45+ tests)
│       │   ├── test_job_aggregator/ # Job aggregator unit tests
│       │   ├── test_scrapers/      # Scraper unit tests
│       │   ├── test_enrichment/    # Enrichment unit tests
│       │   ├── test_cli/           # CLI unit tests
│       │   ├── test_cache/         # Cache unit tests
│       │   ├── test_models/        # Model unit tests
│       │   ├── test_llm_provider/  # LLM provider unit tests
│       │   └── test_config/        # Configuration unit tests
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
│       ├── cross_component_tests/ # Cross-component tests
│       │   ├── cli_runner/        # CLI runner tests
│       │   ├── error_service/     # Error service tests
│       │   ├── logging_service/   # Logging service tests
│       │   ├── scraping_service/  # Scraping service tests
│       │   ├── poc/               # POC utility tests
│       │   ├── webhook/           # Webhook tests
│       │   ├── fixtures/          # Test fixtures and data
│       │   └── integration/       # Cross-component integration
│       ├── requirements.txt       # Test-specific dependencies
│       └── README.md              # Test suite documentation
│
├── 📦 MAIN APPLICATION PACKAGE    # Core application code
│   └── tpm_job_finder_poc/         # Main Python package
│       ├── __init__.py            # Package initialization
│       ├── job_aggregator/        # Job collection and aggregation
│       │   ├── __init__.py
│       │   ├── main.py            # Main aggregator service
│       │   ├── health.py          # Health monitoring
│       │   ├── Dockerfile         # Container configuration
│       │   ├── requirements.txt   # Service dependencies
│       │   ├── aggregators/       # API aggregators
│       │   ├── cache/             # Caching utilities
│       │   ├── controllers/       # Service controllers
│       │   ├── data/              # Data utilities
│       │   ├── scrapers/          # Browser scrapers
│       │   ├── services/          # Core services
│       │   └── tests/             # Service-specific tests
│       ├── scraping_service/      # Web scraping engine
│       │   ├── __init__.py
│       │   ├── core/              # Core scraping functionality
│       │   │   ├── base_job_source.py
│       │   │   ├── orchestrator.py
│       │   │   └── service_registry.py
│       │   ├── scrapers/          # Site-specific scrapers
│       │   │   ├── base_scraper.py
│       │   │   ├── indeed/        # Indeed scraper
│       │   │   ├── linkedin/      # LinkedIn scraper
│       │   │   ├── ziprecruiter/  # ZipRecruiter scraper
│       │   │   └── greenhouse/    # Greenhouse scraper
│       │   ├── demo_phase2.py     # Phase 2 demo
│       │   ├── validate_phase2.py # Phase 2 validation
│       │   └── requirements.txt   # Service dependencies
│       ├── enrichment/            # Data enrichment and analysis
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
│       ├── job_normalizer/        # Job data normalization
│       │   ├── __init__.py
│       │   ├── Dockerfile         # Container configuration
│       │   ├── requirements.txt   # Service dependencies
│       │   ├── jobs/              # Job processing
│       │   └── tests/             # Normalization tests
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
├── 🛠️ TEMPORARY & DEVELOPMENT     # Temporary and legacy files
│   └── temp_dev_files/            # Temporary development files
│       ├── debug_tools/           # Debugging utilities
│       ├── legacy_src/            # Legacy code preservation
│       ├── logs_and_dumps/        # Log files and dumps
│       ├── migration_scripts/     # Migration utilities
│       ├── refactoring_helpers/   # Refactoring tools
│       └── test_analytics         # Test analytics data
│
└── 🔧 ENVIRONMENT & BUILD         # Environment and build artifacts
    ├── .venv/                     # Python virtual environment
    ├── .pytest_cache/             # Test cache
    ├── tpm_job_finder_poc.egg-info/ # Package metadata
    ├── .github/                   # GitHub workflows and actions
    │   └── workflows/             # CI/CD workflows
    └── .git/                      # Git repository data
```

## 🎯 **Structure Principles**

### 1. **Clear Separation of Concerns**

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
