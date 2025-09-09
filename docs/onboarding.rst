Onboarding Guide
================

Welcome to the TPM Job Finder POC! This guide will help you get started with development, testing, and deployment.

Quick Start
----------

1. Install Requirements
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/kevin-toles/tpm-job-finder-poc.git
   cd tpm-job-finder-poc

   # Create and activate a virtual environment (optional but recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate

   # Install the package in editable mode with all dependencies
   pip install -e .

2. Configure API Keys
~~~~~~~~~~~~~~~~~~~

For local development:

1. Create ``api_keys.txt`` in your project root with:

   .. code-block:: text

      OPENAI_API_KEY=sk-xxxxxx
      ANTHROPIC_API_KEY=sk-ant-xxxxxx
      GEMINI_API_KEY=your-key
      DEEPSEEK_API_KEY=your-key
      OLLAMA_API_KEY=  # leave blank for local

2. The loader utility will automatically find and load these keys.

For production/CI:

- Set these as secure environment variables

3. Run Tests
~~~~~~~~~~~

.. code-block:: bash

   # Run all tests
   pytest

   # Run specific test categories
   pytest tests/unit/
   pytest tests/integration_tests/
   pytest tests/e2e_tests/
   pytest tests/regression_tests/

Project Structure
----------------

The project is organized as a Python package with a src layout:

.. code-block:: text

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

   tests/                   # Test directories
   ├── unit/               # Unit tests
   ├── integration_tests/  # Integration tests
   ├── e2e_tests/         # End-to-end tests
   └── regression_tests/  # Regression tests

Adding New Features
-----------------

1. Package Structure
~~~~~~~~~~~~~~~~~~

- Place new modules in appropriate directories under ``src/tpm_job_finder_poc/``
- Follow existing patterns for module organization
- Create ``__init__.py`` files for new packages

2. Testing
~~~~~~~~~

- Add unit tests in ``tests/unit/``
- Add integration tests in ``tests/integration_tests/``
- Add end-to-end tests in ``tests/e2e_tests/``
- Add regression tests in ``tests/regression_tests/``

3. Documentation
~~~~~~~~~~~~~~

- Update relevant RST files in ``docs/``
- Add docstrings to new modules and functions
- Update ``PROJECT_OVERVIEW.md`` for architectural changes

Contributing Guidelines
---------------------

Code Style
~~~~~~~~~

- Follow PEP 8
- Use type hints
- Write clear docstrings
- Run ``ruff`` for linting

Git Workflow
~~~~~~~~~~~

1. Create a feature branch from ``dev``
2. Make changes and add tests
3. Run full test suite
4. Create a pull request
5. Address review comments

Documentation
~~~~~~~~~~~~

- Keep documentation in sync with code
- Update RST files for API changes
- Include examples in docstrings

Troubleshooting
--------------

Common Issues
~~~~~~~~~~~

1. Import Errors:
   - Ensure package is installed in editable mode
   - Check PYTHONPATH if running tests directly

2. API Key Issues:
   - Verify api_keys.txt is properly formatted
   - Check environment variables

3. Test Failures:
   - Run with -v for verbose output
   - Check test requirements are installed
   - Verify API keys for integration tests
