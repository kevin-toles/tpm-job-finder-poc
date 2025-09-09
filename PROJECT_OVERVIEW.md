# TPM Job Finder POC: Project Overview

## Purpose
This document provides a high-level overview of the TPM Job Finder Proof of Concept (POC) application. It is intended for new developers, teams with dependencies, and stakeholders who need a broad understanding of the system before diving into detailed documentation.

## Architecture Summary
- **Language & Frameworks:** Python 3.13, pytest, Flask
- **Project Structure:** Standard Python package (`tpm_job_finder_poc`) with src layout
- **Core Features:**
  - Centralized logging (`CentralLogger`)
  - Centralized error handling (`handle_error`)
  - Modular job source connectors (Greenhouse, Lever, RemoteOK)
  - LLM provider adapters (OpenAI, Anthropic, Gemini, DeepSeek, Ollama)
  - Secure storage, webhook automation, audit logging
- **Testing:** Comprehensive unit, integration, regression, and end-to-end tests for all critical components
- **Security:** Automated scanning (Bandit, DeepSource), request timeouts, subprocess input validation

## Project Structure
The project follows a modern Python package structure with `src/tpm_job_finder_poc/` as the main package:

```
src/tpm_job_finder_poc/
├── __init__.py
├── cli/                # Command-line interface
├── cli_runner/        # CLI runner for batch processing
├── logging_service/   # Centralized logging
├── error_service/     # Error handling
├── resume/           # Resume management
│   ├── store/       # Resume storage
│   └── uploader/    # Resume upload handling
├── cache/           # Caching and deduplication
├── enrichment/      # Job enrichment and scoring
└── models/          # Data models
```

## Key Components
- **CLI & CLI Runner:** Main entry points for batch processing (`cli/` and `cli_runner/`)
- **Logging Service:** Centralized logging with cloud hook support (`logging_service/`)
- **Error Service:** Global error handling and reporting (`error_service/`)
- **Resume Management:**
  - Store: Resume file storage and retrieval (`resume/store/`)
  - Uploader: Resume upload processing (`resume/uploader/`)
- **Cache:** Job deduplication and application tracking (`cache/`)
- **Enrichment:** LLM-based job enrichment and scoring (`enrichment/`)

## Usage

### Running the CLI Runner
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

### Running the CLI Pipeline
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

## Security & Compliance
- All external requests use timeouts
- Subprocess calls are validated for input safety
- Bandit and DeepSource scans are run regularly
- API keys are managed securely through environment variables or secure local storage
- All file operations use secure paths and proper permissions

## Feature Flags for Job Source Connectors
You can enable or disable job source connectors using feature flags in your environment or `.env` file:

```bash
ENABLE_GREENHOUSE=true   # default: enabled
ENABLE_LEVER=true       # default: enabled
ENABLE_REMOTEOK=true    # default: enabled
```

## Developer Onboarding
1. Clone the repository
2. Install in editable mode: `pip install -e .`
3. Configure API keys (see README.md)
4. Run tests: `pytest`
5. Review module-specific documentation
6. Start with small changes to understand the workflow

## Testing Overview
- Unit tests: In each component's tests/ directory
- Integration tests: In integration_tests/
- End-to-end tests: In e2e_tests/
- Regression tests: In regression_tests/
- All tests use pytest and follow consistent patterns

## Change Management
This file is updated whenever major changes are made to:
- Project structure or architecture
- Security measures
- Core features or interfaces
- Testing strategy

For detailed change logs, see CHANGELOG.md.

---
_Last updated: September 9, 2025_
