[![codecov](https://codecov.io/gh/kevin-toles/tpm-job-finder-poc/branch/dev/graph/badge.svg)](https://codecov.io/gh/kevin-toles/tpm-job-finder-poc)

# TPM Job Finder POC

A comprehensive, production-ready automated job search and aggregation system designed for Technical Product Managers and other professionals. This system provides intelligent job discovery, deduplication, enrichment, and workflow automation across multiple job platforms.

## 🚀 Key Features

- **Multi-Source Job Aggregation**: Collect jobs from API sources (RemoteOK, Greenhouse, Lever, Ashby, Workable, SmartRecruiters) and browser scraping (Indeed, LinkedIn, ZipRecruiter, Greenhouse)
- **Intelligent Deduplication**: Advanced cache-based deduplication across all sources
- **Job Enrichment**: LLM-powered job analysis, scoring, and metadata enhancement
- **Automated Workflows**: Complete CLI automation with configuration management
- **Browser Scraping Service**: Modern, modular scraping service with anti-detection
- **Health Monitoring**: Comprehensive service health checks and monitoring
- **Production-Ready**: Full test coverage (70+ tests), error handling, and audit logging

## 📁 Project Structure

This project follows a **clean, professional Python package structure**. For detailed guidance on file organization and development workflows:

- **📖 [Complete Structure Guide](docs/PROJECT_STRUCTURE.md)** - Comprehensive guide to project organization
- **⚡ [Quick Reference](docs/QUICK_REFERENCE.md)** - Fast lookup for file placement
- **🔄 [Import Migration Plan](docs/IMPORT_MIGRATION_PLAN.md)** - Import system migration guide

**Quick Structure Overview:**
```
tpm-job-finder-poc/
├── 📦 tpm_job_finder_poc/    # Main application package
├── 📚 docs/                  # Centralized documentation
├── 🧪 tests/                 # Test suite (70+ tests)
├── 🔧 scripts/               # Development automation
├── 📊 logs/                  # Application logs
└── 📈 output/                # Generated results
```

## 🏗️ Architecture Overview

The system follows a modular, microservice-inspired architecture:

```
tpm_job_finder_poc/           # Main package
├── job_aggregator/           # Core orchestration service
│   ├── main.py              # JobAggregatorService - main orchestrator
│   ├── aggregators/         # API-based job sources
│   └── services/            # Additional aggregation services
├── cli/                     # Command-line interfaces
│   ├── automated_cli.py     # Automated workflow CLI
│   └── runner.py            # Manual execution runner
├── cache/                   # Deduplication and caching
├── enrichment/              # Job enhancement and scoring
├── models/                  # Data models (Job, User, Application, Resume)
├── llm_provider/            # LLM integration for enrichment
├── scraping_service/        # Browser scraping engine (moved from scraping_service_v2)
│   ├── core/                # Core scraping infrastructure
│   │   ├── service_registry.py  # Service registration and discovery
│   │   ├── orchestrator.py      # Multi-source orchestration
│   │   └── base_job_source.py   # Base classes and types
│   └── scrapers/            # Browser-based scrapers
│       ├── base_scraper.py  # Base scraper implementation
│       ├── indeed/          # Indeed.com scraper
│       ├── linkedin/        # LinkedIn scraper
│       ├── ziprecruiter/    # ZipRecruiter scraper
│       └── greenhouse/      # Greenhouse.io scraper
├── error_handler/           # Error handling system (moved)
├── secure_storage/          # Secure file storage (moved)
├── config/                  # Configuration management
└── storage/                 # Data storage layer

scripts/                     # Development automation tools (moved)
├── demo_automation.py       # Demo workflow automation
├── run_tests.py            # Test automation
└── validate_automation.py  # Validation workflows

docs/                        # Centralized documentation (organized)
├── components/              # Component-specific documentation
├── PROJECT_STRUCTURE.md     # Complete structure guide
└── [strategic plans]       # All documentation centralized

tests/                       # Comprehensive test suite
├── unit/                    # Unit tests (45+ tests)
├── integration/             # Integration tests (15+ tests)
├── e2e/                     # End-to-end tests (5+ tests)
├── regression/              # Regression tests (5+ tests)
└── cross_component_tests/   # Cross-component tests (moved)
```

## 📊 Test Coverage & Quality

- **70+ Tests**: Complete test coverage across all components
- **Unit Tests**: Core functionality validation
- **Integration Tests**: Service-to-service communication
- **End-to-End Tests**: Complete workflow validation
- **Regression Tests**: Stability and performance monitoring
- **100% Pass Rate**: All tests passing with comprehensive validation

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/kevin-toles/tpm-job-finder-poc.git
cd tpm-job-finder-poc

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in editable mode
pip install -e .
```

### 2. Configuration
```bash
# Copy configuration template
cp config/automation_config.json.template config/automation_config.json

# Edit configuration for your needs
# Add your search parameters, API keys, output preferences
```

### 3. Basic Usage

#### Automated Workflow (Recommended)
```python
# Import current package structure
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams

# Initialize the service
service = JobAggregatorService()

# Run automated job collection
results = await service.collect_jobs(
    search_terms=["Product Manager", "TPM"],
    location="Remote",
    max_jobs=100
)
```

### 4. Run Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v                    # Unit tests only
python -m pytest tests/integration/ -v             # Integration tests only
python -m pytest tests/e2e/ -v                     # End-to-end tests only

# Run with coverage
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html
```

## 🏗️ Core Services

### JobAggregatorService
Central orchestration service that coordinates all job collection:
- **Multi-Source Collection**: API aggregators + browser scrapers
- **Intelligent Deduplication**: SQLite-based caching with fuzzy matching
- **Health Monitoring**: Service status tracking and error handling
- **Async Processing**: Concurrent job collection for performance

### Scraping Service v2
Independent, production-ready browser scraping service:
- **Modular Architecture**: Plugin-based scraper system
- **Anti-Detection**: Rotating user agents, delays, fingerprint masking
- **Service Registry**: Dynamic scraper registration and discovery
- **Orchestration**: Multi-source coordination with error handling

### Enrichment Pipeline
LLM-powered job analysis and enhancement:
- **Job Parsing**: Extract skills, requirements, compensation
- **ML Scoring**: Compatibility scoring based on user profile
- **Metadata Enhancement**: Job categorization and tagging
- **Resume Analysis**: Parse and match candidate profiles

## 📁 Project Structure

```
tpm-job-finder-poc/
├── README.md                     # This file
├── PROJECT_OVERVIEW.md           # Detailed architecture documentation
├── requirements.txt              # Python dependencies
├── pytest.ini                   # Test configuration
└── CHANGELOG.md                  # Version history

# Core Package
tpm_job_finder_poc/               # Main application package
├── __init__.py
├── job_aggregator/               # Job collection orchestration
│   ├── main.py                   # JobAggregatorService
│   ├── aggregators/              # API-based job sources
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
│   └── llm_provider.py           # LLM integration
├── models/                       # Data models
│   ├── job.py                    # Job model
│   ├── user.py                   # User model
│   ├── application.py            # Application model
│   └── resume.py                 # Resume model
├── llm_provider/                 # LLM service providers
│   ├── openai_provider.py        # OpenAI integration
│   ├── anthropic_provider.py     # Anthropic Claude integration
│   ├── gemini_provider.py        # Google Gemini integration
│   └── deepseek_provider.py      # DeepSeek integration
└── storage/                      # Data persistence

## 🔧 Configuration

### Automation Configuration
Create `tpm_job_finder_poc/config/automation_config.json`:
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

### Environment Variables
```bash
# LLM Provider API Keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-gemini-key"

# Optional: Job Board API Keys
export REMOTEOK_API_KEY="your-remoteok-key"
export GREENHOUSE_API_KEY="your-greenhouse-key"

# Database Configuration
export DATABASE_URL="sqlite:///./jobs.db"

# Logging
export LOG_LEVEL="INFO"
```

## 🔍 Advanced Usage

### Custom Job Sources
Add new job sources by extending the base classes:

```python
# Updated imports using current package structure
from tpm_job_finder_poc.scraping_service.scrapers.base_scraper import BaseScraper
from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams, JobResult

class CustomJobScraper(BaseScraper):
    source_name = "custom_site"
    
    async def fetch_jobs(self, params: FetchParams) -> List[JobResult]:
        # Implement your scraping logic
        pass
```

### Custom Enrichment
Extend the enrichment pipeline:

```python
from tpm_job_finder_poc.enrichment.orchestrator import EnrichmentOrchestrator

class CustomEnricher:
    def enrich_job(self, job_data: dict) -> dict:
        # Add custom enrichment logic
        return enhanced_job_data

# Register with orchestrator
orchestrator = EnrichmentOrchestrator()
orchestrator.register_enricher("custom", CustomEnricher())
```

## 📊 Monitoring & Health

### Health Checks
```bash
# Check service health
python -c "
from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
service = JobAggregatorService()
health = await service.health_check()
print(f'Service Health: {health.status}')
"

# Check scraping service health
python -c "
from tpm_job_finder_poc.scraping_service.core.orchestrator import ScrapingOrchestrator
orchestrator = ScrapingOrchestrator()
health = await orchestrator.health_check()
print(f'Scrapers: {health}')
"
```

### Audit Logging
All operations are logged with audit trails:
- Job collection events
- Enrichment operations
- User interactions
- System errors and warnings

Logs are available in:
- `app.log` - Application logs
- `audit_logger/` - Detailed audit trails
- `webhook.log` - Webhook events

## 🔐 LLM Provider API Keys & Security

### API Key Management

**How to Provide API Keys (Local & Hosted):**

1. **Local Development:**
   - Place your API keys in a file named `llm_keys.txt` in the project root:
     ```txt
     OPENAI_API_KEY=sk-xxxxxx
     ANTHROPIC_API_KEY=sk-ant-xxxxxx
     GEMINI_API_KEY=your-key
     DEEPSEEK_API_KEY=your-key
     OLLAMA_API_KEY=  # leave blank for local
     ```
   - This file is in `.gitignore` and will never be committed.

2. **Hosted/CI/CD Environments:**
   - Set API keys as environment variables for security:
     - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY`
   - Most cloud platforms and CI/CD systems allow you to set these securely.

**Important Security Notes:**
- Never hard-code API keys in code or commit them to version control.
- Do not store secrets in the repo. Only use local files or environment variables.
- For production, always use environment variables.

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/unit/ -v                    # Unit tests only
python -m pytest tests/integration/ -v             # Integration tests only
python -m pytest tests/e2e/ -v                     # End-to-end tests only
python -m pytest tests/regression/ -v              # Regression tests only

# Run with coverage
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html
```

### Test Organization
- **Unit Tests (45+ tests)**: Core functionality validation
- **Integration Tests (15+ tests)**: Service-to-service communication
- **End-to-End Tests (5+ tests)**: Complete workflow validation
- **Regression Tests (5+ tests)**: Stability and performance monitoring

### Test Features
- **100% Pass Rate**: All tests passing with comprehensive validation
- **LLM Provider Tests**: Automatically skipped if API keys not configured
- **Secure Testing**: All file operations use SecureStorage for safety
- **Comprehensive Coverage**: Tests cover all major components and workflows

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Run the test suite** (`python -m pytest tests/ -v`)
5. **Ensure 100% test pass rate**
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests in development
python -m pytest tests/ -v --cov=tpm_job_finder_poc

# Run specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Check code quality
python -m flake8 tpm_job_finder_poc/
python -m black tpm_job_finder_poc/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Browser Automation**: Selenium WebDriver for reliable web scraping
- **Data Processing**: Pandas for efficient data manipulation
- **LLM Integration**: OpenAI, Anthropic, Google for job enrichment
- **Testing**: Pytest for comprehensive test coverage
- **Documentation**: Sphinx for API documentation

## 📞 Support

For questions, issues, or contributions:
- **Issues**: [GitHub Issues](https://github.com/kevin-toles/tpm-job-finder-poc/issues)
- **Discussions**: [GitHub Discussions](https://github.com/kevin-toles/tpm-job-finder-poc/discussions)
- **Documentation**: [Project Docs](./docs/)

---

**Built with ❤️ for Technical Product Managers and job seekers everywhere.**
