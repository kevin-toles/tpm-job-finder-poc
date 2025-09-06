"""
Pytest fixtures for aggregator unit-tests
─────────────────────────────────────────
Loads static JSON samples so tests are deterministic/offline.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterator

import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


def _load(name: str, root: Path) -> Any:
    with (root / name).open("r", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture
def remoteok_sample(fixtures_dir: Path) -> Any:
    return _load("remoteok_sample.json", fixtures_dir)


@pytest.fixture
def greenhouse_sample(fixtures_dir: Path) -> Any:
    return _load("greenhouse_sample.json", fixtures_dir)


@pytest.fixture
def lever_sample(fixtures_dir: Path) -> Any:
    return _load("lever_sample.json", fixtures_dir)
