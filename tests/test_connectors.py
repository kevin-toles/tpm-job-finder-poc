"""
Connector smoke tests
─────────────────────
Ensure each connector can parse its fixture and returns at least one
TPM job with the unified schema.
"""
import json
from pathlib import Path
from datetime import datetime, timezone

import pytest

from poc.connectors import (
    fetch_remoteok,
    fetch_greenhouse,
    fetch_lever,
)

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.mark.parametrize(
    "loader,fixture",
    [
        (fetch_remoteok, "remoteok_sample.json"),
        (lambda: fetch_greenhouse("sampleco"), "greenhouse_sample.json"),
        (lambda: fetch_lever("sampleco"), "lever_sample.json"),
    ],
)
def test_connector_smoke(monkeypatch, loader, fixture):
    sample = json.loads((FIXTURES / fixture).read_text())

    # Monkey-patch the low-level _load / _get_page helpers so the
    # connector reads the fixture instead of calling the network.
    if loader is fetch_remoteok:
        monkeypatch.setattr("poc.connectors.remoteok._get_page", lambda **_: sample)
    elif "greenhouse" in fixture:
        monkeypatch.setattr("poc.connectors.greenhouse._load", lambda slug: sample)
    else:
        monkeypatch.setattr("poc.connectors.lever._load", lambda org: sample)

    jobs = loader()  # run connector

    assert jobs, "No jobs returned"
    j = jobs[0]
    assert {"source", "id", "title", "company", "url", "date_posted"}.issubset(j)
    assert isinstance(j["date_posted"], datetime) and j["date_posted"].tzinfo
    assert j["date_posted"] <= datetime.now(timezone.utc)
