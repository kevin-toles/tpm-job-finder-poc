### Running the CLI Runner

To run the CLI runner, use:

```bash
python -m src.cli_runner.main --input ... --resume ... --applied ... --output ... --log ... --export-format csv --dedupe --enrich --verbose
```

### Running the CLI Pipeline

To run the CLI pipeline, use:

```bash
python -m src.cli --input ... --resume ... --applied ... --output ... --log ... --export-format excel --dedupe --enrich --verbose
```
# TPM Job Finder POC: Project Overview

## Purpose
This document provides a high-level overview of the TPM Job Finder Proof of Concept (POC) application. It is intended for new developers, teams with dependencies, and stakeholders who need a broad understanding of the system before diving into detailed documentation.

## Architecture Summary
- **Language & Frameworks:** Python 3.13, pytest, Flask
- **Core Features:**
  - Centralized logging (`CentralLogger`)
  - Centralized error handling (`handle_error`)
  - Modular job source connectors (Greenhouse, Lever, RemoteOK)
  - LLM provider adapters (OpenAI, Anthropic, Gemini, DeepSeek, Ollama)
  - Secure storage, webhook automation, audit logging
- **Testing:** Comprehensive unit, integration, regression, and end-to-end tests for all critical components
- **Security:** Automated scanning (Bandit, DeepSource), request timeouts, subprocess input validation

## Key Modules
- **src/poc/aggregators/**: Integrates job sources
- **src/poc/enrichment/**: LLM-based job enrichment and scoring
- **src/poc/controllers/**: API and business logic
- **src/poc/cache/**: Deduplication and application tracking
- **src/poc/export/**: Data export (Excel, etc.)
- **src/poc/models/**: Data models for jobs and users
- **src/poc/webhook/**: Automation and deployment hooks
- **src/poc/logger.py**: Centralized logging service
- **src/poc/health.py**: Health checks and monitoring

## Security & Compliance
- All external requests use timeouts
- Subprocess calls are validated for input safety
- Bandit and DeepSource scans are run regularly; all medium/high severity issues are addressed

### API Key Handling


### Feature Flags for Job Source Connectors

You can enable or disable job source connectors (Greenhouse, Lever, RemoteOK) using feature flags in your environment or `.env` file. This helps control which APIs are called without changing code.

**How to use:**
- Add the following to your `.env` file or set as environment variables:
  - `ENABLE_GREENHOUSE=true` (default: enabled)
  - `ENABLE_LEVER=true` (default: enabled)
  - `ENABLE_REMOTEOK=true` (default: enabled)
- The application will only call the APIs for connectors that are enabled.

See `config/config.py` for details.

## Developer Onboarding
- Start with this overview for system context
- Dive into module-specific documentation for details
- Review test suites for examples of expected behavior
- See `README.md` for setup and usage instructions

## Change Management
This file is updated whenever major changes are made to the architecture, security, or core features. For detailed change logs, see the repository history and module-level documentation.

---
_Last updated: September 8, 2025_
