# Job Aggregator Integration Tests

## Overview
Contains integration tests for job aggregator workflows and interactions with other components.

## Integration Points Tested
- Job Aggregator → Job Normalizer pipeline
- Job Aggregator → Cache Service
- Job Aggregator → Applied Tracker
- Multi-source aggregation

## Test Structure
```
integration/
├── test_aggregation.py      # Tests multi-source job aggregation
├── test_normalizer.py       # Tests integration with job normalizer
├── test_cache.py           # Tests caching integration
└── test_applied.py         # Tests applied job tracking
```

## Running Tests
```bash
# Run all integration tests
pytest job_aggregator/tests/integration

# Run specific integration test
pytest job_aggregator/tests/integration/test_aggregation.py
```

## Test Data
- Mock responses in `fixtures/response_mocks.py`
- Common assertions in `helpers/assertions.py`
- Validation utilities in `helpers/validation.py`

## Configuration
Integration tests use a reduced rate limit and shorter cache TTL:
```python
TEST_CONFIG = {
    "requests_per_minute": 2,
    "cache_max_age": 60
}
```

## Common Patterns
- Use async/await for all scraper operations
- Validate job data structure and content
- Check integration with downstream services
- Verify error handling across components

## Adding New Tests
1. Create test file in appropriate directory
2. Import needed fixtures and helpers
3. Use pytest.mark.integration decorator
4. Follow existing patterns for async tests

_Last updated: September 9, 2025_
