# Test Suite Documentation

## Overview

The TPM Job Finder POC includes a comprehensive test suite with **70+ tests** covering all major components and workflows. The test suite is designed to ensure production readiness and maintain code quality throughout development.

## Test Structure

```
tests/
├── unit/                         # Unit tests (45+ tests)
│   ├── test_job_aggregator/      # JobAggregatorService tests
│   ├── test_scrapers/            # Scraper tests
│   ├── test_enrichment/          # Enrichment pipeline tests
│   ├── test_cli/                 # CLI tests
│   ├── test_cache/               # Cache system tests
│   ├── test_models/              # Data model tests
│   ├── test_llm_provider/        # LLM provider tests
│   └── test_config/              # Configuration tests
├── integration/                  # Integration tests (15+ tests)
│   ├── test_connectors_integration.py
│   ├── test_service_integration.py
│   ├── test_enrichment_integration.py
│   └── test_scraping_integration.py
├── e2e/                          # End-to-end tests (5+ tests)
│   ├── test_connectors_e2e.py
│   ├── test_workflow_e2e.py
│   └── test_automation_e2e.py
└── regression/                   # Regression tests (5+ tests)
    ├── test_regression_workflows.py
    ├── test_performance_regression.py
    └── test_api_compatibility.py
```

## Test Categories

### 1. Unit Tests (45+ tests)

#### Job Aggregator Tests (`test_job_aggregator/`)
**Scope**: Core JobAggregatorService functionality
- Service initialization and configuration
- Multi-source job collection
- Health monitoring and status checks
- Error handling and recovery
- Rate limiting and throttling

**Key Test Files**:
- `test_job_aggregator_service.py`: Main service tests
- `test_api_aggregators.py`: API source integration tests
- `test_deduplication.py`: Cache and deduplication logic tests
- `test_health_monitoring.py`: Health check functionality tests

#### Scraper Tests (`test_scrapers/`)
**Scope**: Browser scraping functionality
- Individual scraper implementations
- Anti-detection mechanisms
- Service registry functionality
- Orchestrator coordination

**Key Test Files**:
- `test_indeed_scraper.py`: Indeed scraping tests
- `test_linkedin_scraper.py`: LinkedIn scraping tests
- `test_ziprecruiter_scraper.py`: ZipRecruiter scraping tests
- `test_greenhouse_scraper.py`: Greenhouse scraping tests
- `test_service_registry.py`: Service registry tests
- `test_scraping_orchestrator.py`: Orchestrator tests

#### Enrichment Tests (`test_enrichment/`)
**Scope**: Job enrichment and analysis
- Job description parsing
- Resume analysis and parsing
- ML scoring algorithms
- Heuristic scoring logic
- LLM integration

**Key Test Files**:
- `test_jd_parser.py`: Job description parsing tests
- `test_resume_parser.py`: Resume parsing tests
- `test_ml_scorer.py`: ML scoring tests
- `test_heuristic_scorer.py`: Heuristic scoring tests
- `test_enrichment_orchestrator.py`: Orchestrator tests

#### LLM Provider Tests (`test_llm_provider/`)
**Scope**: LLM integration and providers
- OpenAI provider functionality
- Anthropic provider functionality
- Google Gemini provider functionality
- DeepSeek provider functionality
- Ollama provider functionality
- Provider selection and fallback

**Key Test Files**:
- `test_openai_provider.py`: OpenAI integration tests
- `test_anthropic_provider.py`: Anthropic integration tests
- `test_gemini_provider.py`: Google Gemini tests
- `test_deepseek_provider.py`: DeepSeek tests
- `test_ollama_provider.py`: Ollama tests
- `test_provider_selector.py`: Provider selection tests

#### CLI Tests (`test_cli/`)
**Scope**: Command-line interface functionality
- Automated CLI workflow tests
- Manual CLI pipeline tests
- Configuration parsing tests
- Output format tests

#### Cache Tests (`test_cache/`)
**Scope**: Caching and deduplication
- Deduplication cache functionality
- Applied job tracking
- Cache manager coordination
- Performance tests

#### Model Tests (`test_models/`)
**Scope**: Data model validation
- Job model tests
- User model tests
- Application model tests
- Resume model tests

### 2. Integration Tests (15+ tests)

#### Service Integration (`test_service_integration.py`)
**Scope**: Cross-service communication and integration
- JobAggregatorService + Scraping Service integration
- JobAggregatorService + Enrichment pipeline integration
- Cache system integration across services
- Configuration sharing between services

#### API Integration (`test_connectors_integration.py`)
**Scope**: External API integration
- RemoteOK API integration
- Greenhouse API integration
- Lever API integration
- API error handling and resilience

#### Enrichment Integration (`test_enrichment_integration.py`)
**Scope**: Enrichment pipeline integration
- Job data flow through enrichment pipeline
- LLM provider integration
- Scoring system integration
- Feedback generation integration

#### Scraping Integration (`test_scraping_integration.py`)
**Scope**: Browser scraping integration
- Scraping service integration with main application
- Multi-source scraping coordination
- Health monitoring integration
- Error handling across scraping workflows

### 3. End-to-End Tests (5+ tests)

#### Complete Workflow Tests (`test_workflow_e2e.py`)
**Scope**: Full system workflow validation
- Complete job search workflow from collection to enrichment
- Multi-source data collection and deduplication
- Enrichment pipeline end-to-end processing
- Output generation and formatting

#### Automation Tests (`test_automation_e2e.py`)
**Scope**: Automated CLI workflow testing
- Configuration-driven automated workflows
- Multi-format output generation
- Error recovery in automated workflows
- Performance and timing validation

#### External Integration Tests (`test_connectors_e2e.py`)
**Scope**: External system integration
- Real API integration tests (when credentials available)
- Browser scraping against live sites (rate-limited)
- Complete data flow validation
- System resilience under real conditions

### 4. Regression Tests (5+ tests)

#### Performance Regression (`test_performance_regression.py`)
**Scope**: Performance monitoring and regression detection
- Job collection performance benchmarks
- Enrichment processing speed tests
- Memory usage and resource consumption
- Scalability tests

#### API Compatibility (`test_api_compatibility.py`)
**Scope**: API compatibility and stability
- External API compatibility validation
- Data format consistency checks
- Backward compatibility tests
- Version compatibility tests

#### Workflow Regression (`test_regression_workflows.py`)
**Scope**: Workflow stability and consistency
- Core workflow regression testing
- Output format consistency
- Configuration compatibility
- Feature regression detection

## Test Features

### 1. Automatic API Key Handling
**LLM Provider Tests**: Automatically skip tests if API keys not configured
```python
@pytest.mark.skipif(not has_openai_key(), reason="OpenAI API key not configured")
def test_openai_job_analysis():
    # Test implementation
    pass
```

### 2. Secure Testing
**SecureStorage Integration**: All file operations use SecureStorage for safety
```python
def test_secure_file_operations():
    with SecureStorage() as storage:
        # Test secure file operations
        pass
```

### 3. Mock and Live Testing
**Flexible Testing Modes**: Support both mock and live testing
```python
@pytest.mark.parametrize("use_mock", [True, False])
def test_api_integration(use_mock):
    if use_mock:
        # Use mock responses
        pass
    else:
        # Use live API (when available)
        pass
```

### 4. Comprehensive Coverage
**Coverage Tracking**: Monitor test coverage across all components
```bash
# Run tests with coverage
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html
```

## Running Tests

### Full Test Suite
```bash
# Run all 70+ tests
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html --cov-report=term
```

### Test Categories
```bash
# Unit tests only (45+ tests)
python -m pytest tests/unit/ -v

# Integration tests only (15+ tests)
python -m pytest tests/integration/ -v

# End-to-end tests only (5+ tests)
python -m pytest tests/e2e/ -v

# Regression tests only (5+ tests)
python -m pytest tests/regression/ -v
```

### Specific Component Tests
```bash
# Job aggregator tests
python -m pytest tests/unit/test_job_aggregator/ -v

# Scraper tests
python -m pytest tests/unit/test_scrapers/ -v

# Enrichment tests
python -m pytest tests/unit/test_enrichment/ -v

# LLM provider tests
python -m pytest tests/unit/test_llm_provider/ -v
```

### Parallel Testing
```bash
# Run tests in parallel for faster execution
python -m pytest tests/ -v -n auto
```

### Live Testing (Use Responsibly)
```bash
# Run tests against live APIs and sites (rate-limited)
python -m pytest tests/e2e/ -v --live --slow
```

## Test Configuration

### pytest.ini Configuration
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    regression: Regression tests
    slow: Slow tests that may take longer
    live: Tests that require live API/scraping access
    llm: Tests that require LLM API keys
```

### Environment Configuration
```bash
# Test environment variables
export TEST_MODE="unit"                    # Test mode selection
export TEST_LLM_PROVIDER="mock"           # Use mock LLM responses
export TEST_API_MOCK="true"               # Use mock API responses
export TEST_SCRAPING_MOCK="true"          # Use mock scraping responses
export TEST_TIMEOUT=300                   # Test timeout in seconds
export TEST_RATE_LIMIT="conservative"     # Rate limiting for live tests
```

## Test Data

### Mock Data
**Standardized Test Data**: Consistent mock data across all tests
- Mock job data with various formats and sources
- Mock resume data in multiple formats
- Mock API responses for all external services
- Mock LLM responses for enrichment testing

### Test Fixtures
**Reusable Test Components**: Shared fixtures for common test scenarios
```python
@pytest.fixture
def sample_job_data():
    return {
        "title": "Senior Product Manager",
        "company": "TechCorp",
        "location": "Remote",
        "description": "...",
        "source": "indeed"
    }

@pytest.fixture
def mock_llm_provider():
    return MockLLMProvider()
```

## Continuous Integration

### CI/CD Pipeline
**Automated Testing**: All tests run automatically on push/PR
```yaml
# GitHub Actions workflow
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.13
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python -m pytest tests/ -v --cov=tpm_job_finder_poc
```

### Quality Gates
**Test Quality Requirements**:
- **100% Pass Rate**: All tests must pass
- **Minimum Coverage**: 85% code coverage required
- **Performance**: No performance regressions
- **Security**: All security tests must pass

## Test Maintenance

### Regular Maintenance Tasks
1. **Update Mock Data**: Keep mock data current with real API responses
2. **Review Selectors**: Update scraper selectors for site changes
3. **API Compatibility**: Verify external API compatibility
4. **Performance Baselines**: Update performance benchmarks
5. **Documentation**: Keep test documentation current

### Adding New Tests
1. **Follow Naming Conventions**: Use descriptive test names
2. **Use Appropriate Category**: Place tests in correct category
3. **Add Documentation**: Document complex test scenarios
4. **Mock External Dependencies**: Use mocks for external services
5. **Test Edge Cases**: Include error conditions and edge cases

## Debugging Tests

### Test Debugging
```bash
# Run specific test with detailed output
python -m pytest tests/unit/test_job_aggregator/test_service.py::test_collect_jobs -v -s

# Debug failed tests
python -m pytest tests/ --pdb --tb=long

# Run tests with logging
python -m pytest tests/ -v --log-level=DEBUG
```

### Common Issues
- **API Key Issues**: Ensure LLM API keys are configured for LLM tests
- **Rate Limiting**: Use mock mode for frequent test runs
- **Browser Issues**: Ensure Chrome/Chromium installed for scraper tests
- **Network Issues**: Check internet connectivity for live tests

## Performance Testing

### Performance Benchmarks
```bash
# Run performance tests
python -m pytest tests/regression/test_performance_regression.py -v

# Memory usage testing
python -m pytest tests/ --profile --profile-svg
```

### Load Testing
```bash
# Stress test the system
python -m pytest tests/regression/test_load_testing.py -v --concurrent=10
```

## Future Enhancements

- **Visual Testing**: Screenshot comparison for scraper validation
- **Contract Testing**: API contract validation
- **Chaos Testing**: System resilience under failure conditions
- **Security Testing**: Automated security vulnerability testing
- **Performance Profiling**: Detailed performance analysis

---

_Last updated: January 2025 - Comprehensive test suite with 70+ tests ensuring production readiness_
