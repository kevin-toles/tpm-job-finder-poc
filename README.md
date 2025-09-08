

[![codecov](https://codecov.io/gh/kevin-toles/tpm-job-finder-poc/branch/dev/graph/badge.svg)](https://codecov.io/gh/kevin-toles/tpm-job-finder-poc)
# TPM Job Finder POC

## Test Coverage
Automated coverage reporting is enabled via Codecov. Every PR and commit updates the badge above and provides detailed coverage reports. Coverage is enforced in CI; PRs that reduce coverage below threshold will fail.

To view detailed coverage reports, click the badge or visit your Codecov dashboard.

## Overview
This repository is organized for modular, microservice-friendly development. All file, metadata, and log operations are now centralized through the `SecureStorage` class (`src/storage/secure_storage.py`), ensuring consistent, secure, and maintainable data handling across the application. Each major component, utility, and script lives in its own top-level folder, with dedicated test folders for unit, integration, and end-to-end tests.

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
Unit tests are kept within their respective component or script folders.
Integration and cross-component tests are in `integration_tests/`.
End-to-end tests are in `e2e_tests/`.
All file operations in tests and production code use `SecureStorage` for reading, writing, and metadata management, improving reliability and security.
LLM provider tests (unit, integration, e2e, regression, smoke) will be **skipped** if the required API key or local server is not configured. This is expected and ensures the suite does not fail due to missing external credentials.
Run all tests with:
	```
	PYTHONPATH=. pytest
	```

## LLM Provider API Keys & Security
- Add your API keys to `llm_keys.txt` in the project root, e.g.:
	```
	ChatGPT: sk-xxxxxx
	Anthropic: sk-ant-xxxxxx
	Gemini: <your-key>
	DeepSeek: <your-key>
	Ollama:  # leave blank for local
	```
- You can also set API keys as environment variables (recommended for CI/CD and security):
	- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY`
- **Never hard-code API keys in code or commit them to version control.**
- Use environment variables or `llm_keys.txt` (which should be excluded from public repos).


## Contributing
- Add new tests to the appropriate folder.
- Update README files in test folders to document test types and organization.

## More Info
See individual component and test folder README files for details.

---

## SecureStorage Integration

- All file, metadata, and log operations are routed through `SecureStorage` (`src/storage/secure_storage.py`).
- This ensures consistent, secure, and maintainable data handling across all modules, including ResumeStore, ResumeUploader, output utilities, analytics, and enrichment.
- All legacy file ops have been refactored to use SecureStorage methods for save, retrieve, and metadata management.

---

_Last updated: September 8, 2025_
---

## Test Suite Hygiene & Organization

- All test files are deduplicated, consistently structured, and free of obsolete stubs or commented code.
- Audit logger, Heuristic Scorer, and cross-component integration/e2e tests use standardized setup/teardown and log validation.
- Utility script `scripts/clean_py_artifacts.sh` is provided to remove Python build artifacts (`__pycache__`, `.pyc` files).
- See individual test folder READMEs for details on test types and conventions.
