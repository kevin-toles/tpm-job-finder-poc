# Regression Tests

This folder contains regression tests for major cross-component workflows in the job finder system. These tests ensure that changes do not break critical business logic or integration points.

## What is covered?
- Connector → Parser → Normalizer → Deduplication workflow
- Schema and field validation
- Deduplication logic
- Edge cases for malformed and duplicate jobs

## How to run
```
PYTHONPATH=. pytest regression_tests/
```

## How to extend
- Add new tests for any workflow or integration point you want protected against regressions.
- Use realistic fixture data and simulate real-world scenarios.
