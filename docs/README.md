# TPM Job Finder POC - Documentation

Welcome to the comprehensive documentation for the TPM Job Finder POC, a production-ready automated job search and aggregation system featuring modern TDD-complete services alongside legacy components.

**🚀 Latest Updates:**
- ✅ **JobCollectionService** - TDD-complete with 30/30 tests passing, zero warnings
- ✅ **Enrichment Services** - Multi-resume intelligence with 149+ tests  
- 📊 **Test Coverage** - 440+ comprehensive tests across all categories
- 🏗️ **Modern Architecture** - Interface-driven design with Pydantic V2 compliance

## 📚 **Quick Navigation** Job Finder POC - Documentation

Welcome to the comprehensive documentation for the TPM Job Finder POC, a production-ready automated job search and aggregation system.

## � **Quick Navigation**

- **[📖 HOLISTIC_DOCUMENTATION_GUIDE.md](HOLISTIC_DOCUMENTATION_GUIDE.md)** - Complete organized documentation with holistic system perspective
- **[📖 SYSTEM_ARCHITECTURE_OVERVIEW.md](SYSTEM_ARCHITECTURE_OVERVIEW.md)** - Comprehensive guide to system architecture, organization, and development workflows
- **[⚡ QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Fast lookup reference for file placement and common commands  
- **[🔄 IMPORT_MIGRATION_PLAN.md](IMPORT_MIGRATION_PLAN.md)** - Import system migration guide and compatibility layer documentation

## Documentation Structure (Organized)

```
docs/
├── README.md                    # This file - documentation home
├── HOLISTIC_DOCUMENTATION_GUIDE.md  # Complete organized documentation with holistic perspective
├── SYSTEM_ARCHITECTURE_OVERVIEW.md  # Complete system architecture guide
├── QUICK_REFERENCE.md           # Quick reference for file placement
├── IMPORT_MIGRATION_PLAN.md     # Import migration documentation
├── specifications/              # User-facing specs and requirements
│   ├── Advanced Resume Parsing_Scoring Functionality.md
│   ├── MULTI_RESUME_USAGE_GUIDE.md
│   └── USER_WORKFLOW_GUIDE.md
├── architecture/                # System design and architecture
│   ├── PROJECT_OVERVIEW.md
│   ├── BUSINESS_PROCESS_ARCHITECTURE.md
│   └── SYSTEM_ARCHITECTURE_WORKFLOWS.md
├── implementation/              # Implementation details and status
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── PHASE5_IMPLEMENTATION_SUMMARY.md
│   ├── ADVANCED_ANALYTICS_IMPLEMENTATION.md
│   └── DOCUMENT_SYNCHRONIZATION_STATUS.md
├── testing/                     # Testing strategies and analysis
│   ├── (TDD_COMPONENT_AUDIT_CATALOG.md moved to root)
│   └── FAST_MODE_TEST_ANALYSIS.md
├── components/                  # Component-specific documentation
│   ├── enrichment.md            # Multi-resume intelligence & LLM integration
│   ├── job_aggregator.md        # Job aggregation service docs
│   ├── scraping_service.md      # Web scraping service docs
│   ├── llm_provider.md          # LLM integration docs
│   └── [other components]       # Additional component docs
├── api/                        # Auto-generated API documentation
├── Careerjet_Integration_Plan.* # Strategic enhancement plans
├── index.rst                    # Sphinx documentation index
├── conf.py                      # Sphinx configuration
├── config.rst                   # Configuration documentation
├── onboarding.rst              # Developer onboarding guide
└── _build/                     # Generated documentation output
```

## Quick Navigation

### 📚 Core Documentation
- **[README.md](../README.md)**: Main project documentation and quick start
- **[PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md)**: Comprehensive architecture overview
- **[User Workflow Guide](../USER_WORKFLOW_GUIDE.md)**: End-user workflows and personas
- **[System Architecture Workflows](../SYSTEM_ARCHITECTURE_WORKFLOWS.md)**: Technical workflows and data flows
- **[CHANGELOG.md](../CHANGELOG.md)**: Version history and changes

### 🏗️ Architecture Documentation
- **[Job Aggregator Service](../tpm_job_finder_poc/job_aggregator/README.md)**: Central orchestration service
- **[Scraping Service v2](../scraping_service_v2/README.md)**: Browser scraping service
- **[Enrichment Pipeline](../tpm_job_finder_poc/enrichment/README.md)**: Job enhancement and analysis
- **[Test Suite](../tests/README.md)**: Comprehensive testing documentation

### 🚀 Getting Started
1. **[Installation Guide](../README.md#installation)**: Set up the development environment
2. **[Configuration Guide](../README.md#configuration)**: Configure API keys and settings
3. **[Usage Examples](../README.md#basic-usage)**: Common usage patterns
4. **[Developer Onboarding](../PROJECT_OVERVIEW.md#developer-onboarding)**: New developer guide

### 🔧 Development Resources
- **[API Reference](./api/)**: Auto-generated API documentation
- **[Configuration Reference](./config.rst)**: Detailed configuration options
- **[Testing Guide](../tests/README.md)**: Testing strategies and execution
- **[Contributing Guidelines](../README.md#contributing)**: How to contribute

## System Overview

The TPM Job Finder POC is a sophisticated job aggregation system featuring:

- **Multi-Source Collection**: API sources + browser scraping across 10+ platforms
- **Intelligent Processing**: LLM-powered enrichment and deduplication
- **Production-Ready**: 440+ tests with strategic fast mode (6.46s) and comprehensive validation (~70s)
- **Modular Architecture**: Microservice-inspired design with clear separation
- **Advanced Features**: Phase 5+ services including cultural fit assessment, geographic LLM integration, and career modeling

## Core Services

### 1. JobAggregatorService
Central orchestration service coordinating all job collection activities across multiple sources with intelligent deduplication and health monitoring.

**Key Features**: Multi-source coordination, SQLite caching, async processing, comprehensive error handling

### 2. Scraping Service v2
Independent browser scraping service with anti-detection capabilities for Indeed, LinkedIn, ZipRecruiter, and Greenhouse.

**Key Features**: Modular design, anti-detection, service registry, health monitoring

### 3. Enrichment Pipeline
LLM-powered job analysis and enhancement system supporting multiple providers (OpenAI, Anthropic, Google Gemini, DeepSeek, Ollama).

**Key Features**: Job parsing, ML scoring, resume analysis, feedback generation, cultural fit assessment, geographic analysis

**Advanced Services**: Cultural fit assessment, geographic LLM integration, salary benchmarking, immigration support, enterprise features

### 4. CLI Automation
Complete workflow automation with configuration management supporting multiple output formats and automated workflows.

**Key Features**: Configuration-driven workflows, multi-format output, error handling

## Technology Stack

- **Language**: Python 3.13+
- **Web Scraping**: Selenium WebDriver
- **Testing**: pytest (440+ tests with strategic fast mode)
- **Async Processing**: asyncio
- **Database**: SQLite (caching and deduplication)
- **LLM Integration**: Multiple providers (OpenAI, Anthropic, Google, DeepSeek, Ollama)
- **Security**: SecureStorage for all file operations

## API Documentation

### Auto-Generated Documentation
The `api/` directory contains auto-generated API documentation for all modules:

- **JobAggregatorService API**: Service methods and configuration
- **Scraping Service API**: Scraper interfaces and orchestration
- **Enrichment API**: Enrichment pipeline and LLM integration
- **CLI API**: Command-line interface documentation
- **Models API**: Data models and schemas

### Generating API Docs
```bash
# Generate Sphinx documentation
cd docs/
make html

# View generated docs
open _build/html/index.html
```

## Configuration Documentation

### Configuration Files
- **Main Configuration**: `config/automation_config.json`
- **Job Aggregator Config**: `config/job_aggregator_config.json`
- **Scraping Service Config**: Built into scraping_service_v2
- **LLM Provider Keys**: `llm_keys.txt` (gitignored)

### Environment Variables
```bash
# LLM Provider API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-gemini-key

# Optional API Keys
REMOTEOK_API_KEY=your-remoteok-key
GREENHOUSE_API_KEY=your-greenhouse-key

# Configuration
DATABASE_URL=sqlite:///./jobs.db
LOG_LEVEL=INFO
```

## Testing Documentation

### Test Categories
- **Unit Tests (334+ in fast mode, 400+ total)**: Core functionality validation including 149 consolidated enrichment tests
- **Integration Tests (15+ tests)**: Service-to-service communication
- **End-to-End Tests (5+ tests)**: Complete workflow validation
- **Regression Tests (5+ tests)**: Stability and performance monitoring

### Running Tests
```bash
# Fast mode (recommended for development) - 6.46s execution
PYTEST_FAST_MODE=1 python -m pytest tests/ -v

# Comprehensive mode (full validation) - ~70s execution
python -m pytest tests/ -v

# Enrichment tests (149 consolidated tests)
python -m pytest tests/unit/enrichment/ -v
```

## Security Documentation

### Security Features
- **API Key Management**: Secure handling with environment variables and gitignored files
- **Secure Storage**: All file operations through SecureStorage layer
- **Input Validation**: Comprehensive validation and sanitization
- **Rate Limiting**: Respectful rate limiting across all services

### Security Best Practices
- Never commit API keys to version control
- Use environment variables in production
- Regularly update dependencies
- Monitor for security vulnerabilities

## Deployment Documentation

### Production Readiness
The system is production-ready with:
- ✅ Complete test coverage (440+ tests with strategic performance optimization)
- ✅ Comprehensive monitoring and health checks
- ✅ Security compliance and best practices
- ✅ Modular, scalable architecture
- ✅ Comprehensive documentation
- ✅ Advanced enrichment services (Phase 5+ features)

### Deployment Options
- **Local Development**: Direct Python execution
- **Docker**: Containerized deployment (Dockerfiles included)
- **Cloud**: AWS, GCP, Azure compatible
- **CI/CD**: GitHub Actions integration

## Monitoring & Observability

### Health Monitoring
- Service health checks for all components
- Real-time error tracking and alerting
- Performance metrics and monitoring
- Comprehensive audit logging

### Logging
- **Application Logs**: `app.log`
- **Audit Trails**: `audit_logger/`
- **Webhook Events**: `webhook.log`
- **CLI Execution**: `cli_runner.log`

## Performance Documentation

### Performance Features
- **Async Processing**: Concurrent job collection
- **Intelligent Caching**: SQLite-based deduplication
- **Rate Limiting**: Optimized rate limits per service
- **Resource Management**: Efficient browser instance management
- **Strategic Testing**: Fast mode (6.46s) for development, comprehensive mode (~70s) for validation

### Benchmarks
- Job collection: 100+ jobs/minute across all sources
- Enrichment processing: 10+ jobs/second with LLM
- Deduplication: <100ms per job comparison
- Memory usage: <500MB during normal operation
- Test execution: 6.46s (fast mode) to 70s (comprehensive mode)

## Contributing to Documentation

### Documentation Standards
- Use clear, concise language
- Include code examples for all features
- Maintain up-to-date architecture diagrams
- Document all configuration options
- Include troubleshooting guides

### Updating Documentation
1. Update relevant README files for component changes
2. Update PROJECT_OVERVIEW.md for architectural changes
3. Update CHANGELOG.md for all changes
4. Regenerate API documentation for code changes
5. Update configuration documentation for new options

## Support & Community

### Getting Help
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and community support
- **Documentation**: Comprehensive guides and references
- **Code Review**: Contribute improvements and fixes

### Community Guidelines
- Be respectful and inclusive
- Provide clear, reproducible examples
- Help others learn and grow
- Contribute back to the community

---

## Version Information

- **Current Version**: v1.0.0 (Production Ready)
- **Documentation Last Updated**: September 2025
- **Test Suite Status**: 440+ tests with strategic fast mode (6.46s) and comprehensive validation
- **Architecture Status**: Production-ready with comprehensive validation and advanced features

---

_For the most current information, always refer to the main [README.md](../README.md) and [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) files._
