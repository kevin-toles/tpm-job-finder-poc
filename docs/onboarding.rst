Onboarding Guide
================

Welcome to the TPM Job Finder POC! This guide will help you get started with development, testing, and deployment.

## Setup
- Clone the repository
- Install Python 3.11+
- Install dependencies: `pip install -r requirements.txt`
- Configure environment variables and secrets as described in the main README

## Running Tests
- Run all tests: `PYTHONPATH=. pytest`
- Coverage is reported automatically in CI

## Adding New Services
- Place new service code in its own folder under `src/`
- Add tests in the corresponding `tests/` folder
- Update documentation in `docs/`

## Contributing
- Follow code style and linting rules (ruff)
- Write tests for new features
- Update onboarding and config docs as needed
