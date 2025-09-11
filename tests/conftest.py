"""Centralized test fixtures for the entire test suite."""

from pathlib import Path
import os
import pytest

# Ensure deterministic CWD in tests that use relative file paths
@pytest.fixture(scope="session", autouse=True)
def _set_cwd_to_repo_root():
    os.chdir(Path(__file__).resolve().parent.parent)  # repo/tests -> repo

# Common paths for samples/fixtures (adjust if yours differ)
@pytest.fixture(scope="session")
def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent

@pytest.fixture(scope="session")
def fixtures_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures"

# Example convenience paths used by CLI/regression tests
@pytest.fixture
def sample_jobs(fixtures_dir: Path) -> Path:
    return fixtures_dir / "remoteok_sample.json"

@pytest.fixture
def sample_resume(fixtures_dir: Path) -> Path:
    return fixtures_dir / "sample_resume.txt"

@pytest.fixture
def sample_applied(fixtures_dir: Path) -> Path:
    return fixtures_dir / "sample_applied.xlsx"

# Remove conflicting tmp_path_factory - pytest provides this built-in

# Audit logger specific fixtures
@pytest.fixture
def audit_log_path(tmp_path):
    """Provide temporary audit log path."""
    return tmp_path / "test_audit.jsonl"

# CLI runner fixtures  
@pytest.fixture
def sample_config():
    """Provide sample configuration for CLI tests."""
    return {
        "input_file": "sample_jobs.json",
        "resume_file": "sample_resume.txt",
        "output_format": "json"
    }
