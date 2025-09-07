# Integration Tests

This folder contains tests that validate interactions between multiple components or services in the system.

## Organization
- Subfolders or files are grouped by workflow, feature, or integration point (e.g., aggregator-to-normalizer, enrichment pipeline).
- Shared fixtures and setup files are kept here for reuse across integration tests.

## Test Types
- Integration tests: Validate that two or more components work together as expected.
- Cross-component tests: Cover scenarios where data flows between services.

## How to Run
```
PYTHONPATH=. pytest integration_tests
```

## Conventions
- Use descriptive test names and file structures for clarity.
- Document any special setup or dependencies in this README.
