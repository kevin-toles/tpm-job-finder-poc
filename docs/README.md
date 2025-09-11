# TPM Job Finder POC - Documentation

Welcome to the comprehensive documentation for the TPM Job Finder POC, a production-ready automated job search and aggregation system.

## 📁 **Project Structure & Organization**

- **[📖 PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Comprehensive guide to project organization, file placement, and development workflows
- **[⚡ QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Fast lookup reference for file placement and common commands  
- **[🔄 IMPORT_MIGRATION_PLAN.md](IMPORT_MIGRATION_PLAN.md)** - Import system migration guide and compatibility layer documentation

## Documentation Structure

```
docs/
├── README.md                    # This file - documentation home
├── PROJECT_STRUCTURE.md         # Complete project structure guide
├── QUICK_REFERENCE.md           # Quick reference for file placement
├── IMPORT_MIGRATION_PLAN.md     # Import migration documentation
├── components/                  # Component-specific documentation
│   ├── job_aggregator.md        # Job aggregation service docs
│   ├── scraping_service.md      # Web scraping service docs
│   ├── enrichment.md            # Data enrichment docs
│   ├── llm_provider.md          # LLM integration docs
│   └── [other components]       # Additional component docs
├── Careerjet_Integration_Plan.* # Strategic enhancement plans
├── index.rst                    # Sphinx documentation index
├── conf.py                      # Sphinx configuration
├── config.rst                   # Configuration documentation
├── onboarding.rst              # Developer onboarding guide
├── api/                        # Auto-generated API documentation
└── _build/                     # Generated documentation output
```

## Quick Navigation

### 📚 Core Documentation
- **[README.md](../README.md)**: Main project documentation and quick start
- **[PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md)**: Comprehensive architecture overview
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
- **Production-Ready**: 70+ tests, comprehensive monitoring, and security
- **Modular Architecture**: Microservice-inspired design with clear separation

## Core Services

### 1. JobAggregatorService
Central orchestration service coordinating all job collection activities across multiple sources with intelligent deduplication and health monitoring.

**Key Features**: Multi-source coordination, SQLite caching, async processing, comprehensive error handling

### 2. Scraping Service v2
Independent browser scraping service with anti-detection capabilities for Indeed, LinkedIn, ZipRecruiter, and Greenhouse.

**Key Features**: Modular design, anti-detection, service registry, health monitoring

### 3. Enrichment Pipeline
LLM-powered job analysis and enhancement system supporting multiple providers (OpenAI, Anthropic, Google Gemini, DeepSeek, Ollama).

**Key Features**: Job parsing, ML scoring, resume analysis, feedback generation

### 4. CLI Automation
Complete workflow automation with configuration management supporting multiple output formats and automated workflows.

**Key Features**: Configuration-driven workflows, multi-format output, error handling

## Technology Stack

- **Language**: Python 3.13+
- **Web Scraping**: Selenium WebDriver
- **Testing**: pytest (70+ tests)
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
- **Unit Tests (45+ tests)**: Core functionality validation
- **Integration Tests (15+ tests)**: Service-to-service communication
- **End-to-End Tests (5+ tests)**: Complete workflow validation
- **Regression Tests (5+ tests)**: Stability and performance monitoring

### Running Tests
```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html
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
- ✅ Complete test coverage (70+ tests passing)
- ✅ Comprehensive monitoring and health checks
- ✅ Security compliance and best practices
- ✅ Modular, scalable architecture
- ✅ Comprehensive documentation

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

### Benchmarks
- Job collection: 100+ jobs/minute across all sources
- Enrichment processing: 10+ jobs/second with LLM
- Deduplication: <100ms per job comparison
- Memory usage: <500MB during normal operation

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
- **Documentation Last Updated**: January 2025
- **Test Suite Status**: 70+ tests passing (100% pass rate)
- **Architecture Status**: Production-ready with comprehensive validation

---

_For the most current information, always refer to the main [README.md](../README.md) and [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) files._
