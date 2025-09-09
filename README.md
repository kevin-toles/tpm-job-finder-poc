

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

### API Key Management

**How to Provide API Keys (Local & Hosted):**

1. **Local Development:**
	 - Place your API keys in a file named `api_keys.txt` at:
		 - `~/Desktop/tpm-job-finder-poc/api_keys.txt`
	 - Example structure:
		 ```txt
		 OPENAI_API_KEY=sk-xxxxxx
		 ANTHROPIC_API_KEY=sk-ant-xxxxxx
		 GEMINI_API_KEY=your-key
		 DEEPSEEK_API_KEY=your-key
		 OLLAMA_API_KEY=  # leave blank for local
		 ```
	 - This file is **never** stored in the repo. The loader utility will automatically find it.

2. **Public Repo Security:**
	- The file `api_keys.json` is listed in `.gitignore` and will never be committed to the repository.
	- You can safely make your repo public without exposing your API keys.

2. **Hosted/CI/CD Environments:**
	 - Set API keys as environment variables for security:
		 - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `DEEPSEEK_API_KEY`, `OLLAMA_API_KEY`
	 - Most cloud platforms and CI/CD systems allow you to set these securely.

**Important Security Notes:**
- Never hard-code API keys in code or commit them to version control.
- Do not store secrets in the repo. Only use local files or environment variables.
- The loader utility will check the repo config file (if present), then fall back to your external file.
- For production, always use environment variables.

See below for more details and troubleshooting.


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
