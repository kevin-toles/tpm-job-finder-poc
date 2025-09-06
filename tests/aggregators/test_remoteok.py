"""
RemoteOK connector unit-tests
────────────────────────────
Verifies that the aggregator:
  • returns a list of JobPosting objects
  • normalises datetime to *UTC & tz-aware*
  • populates required fields (company, title, url, …)

Fixture data lives in tests/aggregators/fixtures/remoteok_sample.json
"""

from datetime import timezone
from pathlib import Path
from typing import Any

import json

from poc.aggregators.remoteok import fetch  # ← your connector
from poc.jobs.schema import JobPosting     # unified model


FIXTURE = Path(__file__).with_suffix("").parent / "fixtures" / "remoteok_sample.json"


def _load_fixture() -> list[dict[str, Any]]:
    with FIXTURE.open("r", encoding="utf-8") as fp:
        return json.load(fp)


def test_fetch_returns_jobposting_objects(monkeypatch) -> None:
    """fetch() should return fully-typed JobPosting instances."""

    monkeypatch.setattr("poc.aggregators.remoteok._get_raw", _load_fixture)

    jobs = fetch(days=7)

    assert jobs, "No jobs returned"
    assert all(isinstance(j, JobPosting) for j in jobs)


def test_jobposting_fields_are_normalised(monkeypatch) -> None:
    """Dates must be UTC & tz-aware; URLs and titles populated."""

    monkeypatch.setattr("poc.aggregators.remoteok._get_raw", _load_fixture)

    job = fetch(days=7)[0]          # first sample

    # --- datetime normalisation -------------------------------------------
    assert job.date_posted.tzinfo is timezone.utc

    # --- required fields ---------------------------------------------------
    as_dict = job.model_dump()      # <- v2 serialisation
    for field in ("id", "source", "company", "title", "url"):
        assert as_dict[field], f"{field} missing / empty"
