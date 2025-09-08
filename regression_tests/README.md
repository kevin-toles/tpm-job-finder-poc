# Regression Tests

This folder contains regression tests for major cross-component workflows in the TPM Job Finder system. These tests ensure that changes do not break critical business logic, integration points, or data handling.

## Purpose
- Protect against regressions in job aggregation, parsing, normalization, deduplication, and schema validation.
- Validate edge cases, malformed data, and duplicate job handling.
- Ensure consistent behavior across connectors, parsers, and normalizers.

## SecureStorage Integration
- All file, metadata, and log operations in regression tests use the SecureStorage class (`src/storage/secure_storage.py`).
- This centralizes data handling, improves reliability, and enforces security best practices.

## How to Run
```bash
PYTHONPATH=. pytest regression_tests/
```

## How to Extend
- Add new tests for any workflow or integration point you want protected against regressions.
- Use realistic fixture data and simulate real-world scenarios.
- Follow the SecureStorage pattern for all file and metadata operations.

## Conventions
- Use clear, scenario-based test names.
- Document any special setup, environment variables, or dependencies in this README.
- Keep test files deduplicated and free of obsolete code.

---
_Last updated: September 8, 2025_
