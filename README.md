## Quick Start

1. **Installation**
```bash
# Clone the repository
git clone https://github.com/kevin-toles/tpm-job-finder-poc.git
cd tpm-job-finder-poc

# Install in editable mode
pip install -e .
```

2. **Running the CLI Runner**
```bash
python -m tpm_job_finder_poc.cli_runner.main \
  --input jobs.json \
  --resume resume.pdf \
  --applied applied.xlsx \
  --output results.csv \
  --log output.log \
  --export-format csv \
  --dedupe \
  --enrich \
  --verbose
```

3. **Running the CLI Pipeline**
```bash
python -m tpm_job_finder_poc.cli \
  --input jobs.json \
  --resume resume.pdf \
  --applied applied.xlsx \
  --output results.xlsx \
  --log output.log \
  --export-format excel \
  --dedupe \
  --enrich \
  --verbose
```


[![codecov](https://codecov.io/gh/kevin-toles/tpm-job-finder-poc/branch/dev/graph/badge.svg)](https://codecov.io/gh/kevin-toles/tpm-job-finder-poc)
# TPM Job Finder POC

## Test Coverage
Automated coverage reporting is enabled via Codecov. Every PR and commit updates the badge above and provides detailed coverage reports. Coverage is enforced in CI; PRs that reduce coverage below threshold will fail.

To view detailed coverage reports, click the badge or visit your Codecov dashboard.

## Overview
This repository is organized as a modern Python package with a src layout. All components are now part of the `tpm_job_finder_poc` package, ensuring proper isolation and dependency management.

## Project Structure
```
src/tpm_job_finder_poc/     # Main package directory
├── __init__.py
├── cli/                    # Command-line interface
├── cli_runner/            # CLI runner for batch processing
├── logging_service/       # Centralized logging
├── error_service/        # Error handling
├── resume/               # Resume management
│   ├── store/           # Resume storage
│   └── uploader/        # Resume upload handling
├── cache/               # Caching and deduplication
└── enrichment/          # Job enrichment and scoring

cross_component_tests/      # Shared, cross-component and utility tests
├── unit/                   # Unit tests
├── integration_tests/      # Integration tests
├── e2e_tests/              # End-to-end tests
└── regression_tests/       # Regression tests


## Testing
Unit tests are kept within their respective component or script folders.
Integration and cross-component tests are in `integration_tests/`.
End-to-end tests are in `e2e_tests/`.
All file operations in tests and production code use `SecureStorage` for reading, writing, and metadata management, improving reliability and security.
LLM provider tests (unit, integration, e2e, regression, smoke) will be **skipped** if the required API key or local server is not configured. This is expected and ensures the suite does not fail due to missing external credentials.
Run all tests with:
	```
	PYTHONPATH=. pytest cross_component_tests
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
