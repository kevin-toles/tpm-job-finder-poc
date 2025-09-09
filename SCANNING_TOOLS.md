# Codebase Scanning & Analysis Tools

This document lists all static analysis, security, and code quality tools configured for this repository. It includes tools that require configuration files in the codebase and are integrated with CI/CD or external services.

---

## Configured Scanning Tools

### 1. DeepSource
- **Config file:** `.deepsource.toml`
- **Analyzers enabled:**
  - Python (code quality, bug risks)
  - Bandit (security)
  - Coverage (test coverage)
  - Secrets (hardcoded secret detection)
  - Docker (Dockerfile analysis)

### 2. GitHub CodeQL
- **Config file:** `.github/workflows/codeql.yml`
- **Purpose:** Security analysis for Python code (OWASP, CVEs, etc.)
- **Runs on:** dev, qa, uat, stage, main branches

### 3. Pylint
- **Config:** Step in `.github/workflows/ci.yml`
- **Purpose:** Python static analysis and style enforcement
- **Runs on:** All major branches via CI

### 4. Ruff
- **Config:** Step in `.github/workflows/ci.yml`
- **Purpose:** Fast Python linter and style checker
- **Runs on:** All major branches via CI

### 5. Bandit
- **Config:** Enabled via DeepSource and CodeQL
- **Purpose:** Python security analysis

### 6. Codecov
- **Config:** Step in `.github/workflows/ci.yml`
- **Purpose:** Test coverage reporting

---

## How to Add More Tools
- Add the required config file (e.g., `.pylintrc`, `.mypy.ini`) to the repo root.
- Add a step to the CI workflow to run the tool.
- Document the tool and its config here.

---

_Last updated: September 8, 2025_
