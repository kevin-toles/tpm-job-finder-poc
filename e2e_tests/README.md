# End-to-End (E2E) Tests

This folder contains tests that validate full workflows and user scenarios across the entire system.

## Organization
- Test files are grouped by major workflow or user journey (e.g., job pipeline, resume upload and export).
- Use fixtures and shared setup as needed.

## Test Types
- End-to-end tests: Cover the complete flow from input to output, often spanning multiple services and components.

## How to Run
```
PYTHONPATH=. pytest e2e_tests
```

## Conventions
- Use clear, scenario-based test names.
- Document any special setup, environment variables, or dependencies in this README.
