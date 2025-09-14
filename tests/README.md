# Test Suite Documentation

## Overview

The TPM Job Finder POC includes a comprehensive test suite with **440+ tests** covering all major components and workflows. The test suite features a strategic **fast mode** (6.46s execution) for development and a **comprehensive mode** (~70s execution) for complete validation, ensuring both rapid development feedback and production readiness.

## Test Performance Strategy

### Fast Mode (Recommended for Development)
- **Execution Time**: 6.46 seconds
- **Tests Executed**: 334 tests passing 
- **Coverage**: Core business logic, local computations, unit tests
- **Usage**: `PYTEST_FAST_MODE=1 python -m pytest tests/ -v`
- **Benefits**: Instant feedback loop, 100% pass rate for executed tests

### Comprehensive Mode (CI/CD and Production Validation)  
- **Execution Time**: ~70 seconds
- **Tests Executed**: 440+ tests
- **Coverage**: Full suite including network/browser dependencies
- **Usage**: `python -m pytest tests/ -v`
- **Benefits**: Complete validation, external service testing

## Test Structure

```
tests/
├── unit/                         # Unit tests (334+ in fast mode, 400+ total)
│   ├── enrichment/               # Enrichment tests (149 tests consolidated)
│   │   ├── test_cultural_fit_service.py     # Cultural fit assessment tests
│   │   ├── test_geographic_llm_integration.py # Geographic LLM integration tests  
│   │   ├── test_phase5_integration.py       # Phase 5+ advanced feature tests
│   │   ├── test_salary_benchmarking_service.py # Salary benchmarking tests
│   │   └── [other enrichment tests]        # Additional enrichment functionality
│   ├── job_aggregator/           # JobAggregatorService tests
│   ├── cache/                    # Cache system tests
│   ├── models/                   # Data model tests
│   ├── llm_provider/             # LLM provider tests
│   └── config/                   # Configuration tests
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

### 1. Unit Tests (334+ tests in fast mode, 400+ total)

#### Enrichment Tests (`enrichment/` - 149 tests consolidated)
**Scope**: Advanced job enhancement and analysis services
- **Cultural Fit Assessment**: Regional work culture compatibility analysis
- **Geographic LLM Integration**: Location-aware LLM responses and cultural adaptation
- **Phase 5+ Integration**: Advanced career modeling, immigration support, enterprise features
- **Salary Benchmarking**: Market-based compensation analysis
- **Core Enrichment**: Job parsing, resume analysis, ML scoring

**Key Test Files**:
- `test_cultural_fit_service.py`: Cultural compatibility assessment (17,396 bytes)
- `test_geographic_llm_integration.py`: Geographic LLM integration (23,311+ bytes)
- `test_phase5_integration.py`: Advanced feature integration (32,895 bytes)
- `test_salary_benchmarking_service.py`: Salary benchmarking functionality (19,738 bytes)

#### Job Aggregator Tests (`job_aggregator/`)
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

#### Scraper Tests (`scrapers/`) - Fast Mode Excluded
**Scope**: Browser scraping functionality (excluded in fast mode for performance)
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
**Scope**: Core job enrichment and analysis (included in fast mode)
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

### 1. Fast Mode Support
**Strategic Performance Optimization**: Fast mode excludes network/browser tests for rapid development feedback
```python
FAST_MODE = os.getenv('PYTEST_FAST_MODE', '0') == '1'

@pytest.mark.skipif(FAST_MODE, reason="Browser scraping tests excluded in fast mode")
def test_browser_scraping():
    # Test implementation
    pass
```

### 2. Automatic API Key Handling
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
# Run tests with coverage (fast mode)
PYTEST_FAST_MODE=1 python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html

# Run full coverage
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html
```

### 5. Consolidated Test Organization
**Enrichment Test Consolidation**: All 149 enrichment tests properly organized in central location
- All tests moved from scattered locations to `tests/unit/enrichment/`
- Newer, more comprehensive test versions retained
- Proper test categorization and organization
- No duplicate or obsolete test files

## Running Tests

### Fast Mode (Recommended for Development)
```bash
# Fast mode - 6.46s execution, 334 tests passing
PYTEST_FAST_MODE=1 python -m pytest tests/ -v

# Fast mode with coverage  
PYTEST_FAST_MODE=1 python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html --cov-report=term
```

### Comprehensive Mode (Full Validation)
```bash
# Run all 440+ tests (~70s execution)
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=tpm_job_finder_poc --cov-report=html --cov-report=term
```

### Test Categories
```bash
# Unit tests only (334+ in fast mode, 400+ total)
python -m pytest tests/unit/ -v
PYTEST_FAST_MODE=1 python -m pytest tests/unit/ -v  # Fast mode

# Integration tests only (15+ tests)
python -m pytest tests/integration/ -v

# End-to-end tests only (5+ tests)  
python -m pytest tests/e2e/ -v

# Regression tests only (5+ tests)
python -m pytest tests/regression/ -v
```

### Specific Component Tests
```bash
# Enrichment tests (149 consolidated tests)
python -m pytest tests/unit/enrichment/ -v

# Job aggregator tests
python -m pytest tests/unit/job_aggregator/ -v

# Scraper tests (excluded in fast mode)
python -m pytest tests/unit/test_scrapers/ -v

# LLM provider tests
python -m pytest tests/unit/llm_provider/ -v

# Cultural fit and geographic analysis
python -m pytest tests/unit/enrichment/test_cultural_fit_service.py -v
python -m pytest tests/unit/enrichment/test_geographic_llm_integration.py -v

# Phase 5+ advanced features
python -m pytest tests/unit/enrichment/test_phase5_integration.py -v
```

### Parallel Testing
```bash
# Run tests in parallel for faster execution (fast mode)
PYTEST_FAST_MODE=1 python -m pytest tests/ -v -n auto

# Run full tests in parallel
python -m pytest tests/ -v -n auto
```

### Live Testing (Use Responsibly)
```bash
# Run tests against live APIs and sites (rate-limited)
python -m pytest tests/e2e/ -v --live --slow

# Run without fast mode to include network tests
python -m pytest tests/integration/ -v --live
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
export PYTEST_FAST_MODE="1"              # Enable fast mode (6.46s execution)
export TEST_MODE="unit"                   # Test mode selection
export TEST_LLM_PROVIDER="mock"          # Use mock LLM responses
export TEST_API_MOCK="true"              # Use mock API responses
export TEST_SCRAPING_MOCK="true"         # Use mock scraping responses
export TEST_TIMEOUT=300                  # Test timeout in seconds
export TEST_RATE_LIMIT="conservative"    # Rate limiting for live tests
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
- **100% Pass Rate**: All executed tests must pass
- **Fast Mode Performance**: Must execute in <10 seconds
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
python -m pytest tests/unit/enrichment/test_cultural_fit_service.py::test_assess_cultural_fit -v -s

# Run enrichment tests with fast mode
PYTEST_FAST_MODE=1 python -m pytest tests/unit/enrichment/ -v -s

# Debug failed tests
python -m pytest tests/ --pdb --tb=long

# Run tests with logging
PYTEST_FAST_MODE=1 python -m pytest tests/ -v --log-level=DEBUG
```

### Common Issues
- **API Key Issues**: Ensure LLM API keys are configured for LLM tests
- **Fast Mode**: Use `PYTEST_FAST_MODE=1` for development, full mode for CI/CD
- **Rate Limiting**: Use mock mode for frequent test runs
- **Browser Issues**: Ensure Chrome/Chromium installed for scraper tests (excluded in fast mode)
- **Network Issues**: Check internet connectivity for live tests (excluded in fast mode)
- **Test Organization**: All enrichment tests are now in `tests/unit/enrichment/`

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

_Last updated: September 2025 - Comprehensive test suite with 440+ tests, strategic fast mode (6.46s), and consolidated enrichment test organization_
