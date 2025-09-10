# Scraper Service Tests

## Overview
This directory contains the complete test suite for the Job Scraper Microservice, covering unit, integration, regression, and end-to-end testing scenarios.

## Test Organization
```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Tests for component interactions
├── regression/     # Tests for specific bug fixes
├── e2e/           # Full workflow tests
├── fixtures/       # Shared test data and mocks
└── conftest.py    # Common test configuration
```

## Running Tests

### All Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src
```

### Specific Test Types
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# Regression tests
pytest tests/regression/

# E2E tests
pytest tests/e2e/
```

## Test Categories

### Unit Tests
- Model validation (Job, JobRequest, JobResponse)
- Metrics collection
- Scraper implementations (LinkedIn, Indeed, ZipRecruiter)
- Configuration management
- Rate limiting and caching

### Integration Tests
- API endpoints
- Multi-source job aggregation
- Metrics and monitoring
- Configuration updates
- Cache integration
- Error handling

### Regression Tests
- Rate limiting issues (#156)
- Retry logic (#178)
- URL sanitization (#189)
- Memory leaks (#201)
- Response caching
- Error recovery

### End-to-End Tests
- Complete job search workflows
- Multi-source aggregation
- Error handling scenarios
- Configuration management
- Performance monitoring

## Test Environment

### Requirements
- Python 3.13+
- pytest
- pytest-asyncio
- pytest-cov
- httpx
- aioresponses

### Configuration
Tests use a separate configuration with:
- Reduced rate limits
- Disabled caching (optional)
- Mock responses
- In-memory storage

## Metrics and Monitoring
- All tests report metrics via Prometheus
- Health checks are validated
- Performance metrics are collected
- Error tracking is verified

## Best Practices
1. Follow AAA pattern (Arrange, Act, Assert)
2. Use fixtures for common setup
3. Mock external services
4. Clear test names and documentation
5. Appropriate use of markers
6. Proper async/await usage

## Adding New Tests
1. Choose appropriate test category
2. Use existing fixtures when possible
3. Follow naming conventions
4. Include relevant metrics
5. Document special requirements

## Integration with CI/CD
- Tests run on every PR
- Coverage requirements: 85%
- Performance benchmarks
- Security scanning

## Troubleshooting
- Check mock data in fixtures/
- Verify rate limiting settings
- Ensure clean test state
- Review metrics output

---
_Last updated: September 9, 2025_
