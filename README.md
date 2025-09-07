
# TPM Job Finder POC

## Overview
This repository is organized for modular, microservice-friendly development. Each major component, utility, and script lives in its own top-level folder, with dedicated test folders for unit, integration, and end-to-end tests.

## Structure
- `job_aggregator/` — ATS connectors and related logic
	- `tests/unit/` — Unit tests for connectors and internal functions
	- `tests/integration/` — Integration tests for aggregator workflows
- `job_normalizer/` — Centralized job parsing and normalization
	- `tests/unit/` — Unit tests for normalization and parsing
	- `tests/integration/` — Integration tests for normalizer workflows
- `llm_provider/`, `heuristic_scorer/`, `enrichment/`, etc. — Each service/component in its own folder
- `integration_tests/` — Cross-component and integration tests
	- `fixtures/` — Shared test data
	- `conftest.py` — Shared setup/fixtures
- `e2e_tests/` — End-to-end workflow tests
- `scripts/` — Utility scripts
	- `tests/unit/` — Unit tests for scripts

## Testing
- Unit tests are kept within their respective component or script folders.
- Integration and cross-component tests are in `integration_tests/`.
- End-to-end tests are in `e2e_tests/`.
- Run all tests with:
	```
	PYTHONPATH=. pytest
	```

## Contributing
- Add new tests to the appropriate folder.
- Update README files in test folders to document test types and organization.

## More Info
See individual component and test folder README files for details.
---
