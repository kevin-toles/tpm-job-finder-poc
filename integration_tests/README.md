# Integration Tests

This folder contains tests that validate interactions between multiple components or services in the system.

## Organization
- Subfolders or files are grouped by workflow, feature, or integration point
- Common test utilities and fixtures are shared across integration tests
- Each component maintains its own integration test directory for component-specific integrations

## Component Integration Tests
- Job Aggregator (`job_aggregator/tests/integration/`):
  - Multi-source aggregation
  - Job normalizer pipeline
  - Cache service integration
  - Applied tracker integration

- Job Normalizer (`job_normalizer/tests/integration/`):
  - Data normalization pipeline
  - Deduplication service
  - Validation workflows

- Enrichment (`enrichment/tests/integration/`):
  - LLM provider integration
  - Scoring pipeline
  - Resume feedback generation

## Test Types
- Integration tests: Validate that two or more components work together as expected
- Cross-component tests: Cover scenarios where data flows between services
- Pipeline tests: Verify end-to-end data processing workflows

## How to Run
```bash
# Run all integration tests
PYTHONPATH=. pytest integration_tests

# Run component-specific integration tests
pytest job_aggregator/tests/integration
pytest job_normalizer/tests/integration
pytest enrichment/tests/integration
```

## Test Structure
- Each integration test follows the pattern:
  1. Setup test data and configuration
  2. Initialize required components
  3. Execute the integration workflow
  4. Verify the results and side effects
  5. Clean up test data

## Common Patterns
- Use pytest fixtures for component setup
- Mock external services where appropriate
- Validate data transformation between components
- Check error handling across component boundaries

## Adding New Tests
1. Identify the integration points to test
2. Create appropriate test files and fixtures
3. Document test requirements and setup
4. Follow existing patterns for similar integrations

_Last updated: September 9, 2025_
