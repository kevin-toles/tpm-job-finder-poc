"""
RemoteOK aggregator · unit tests
────────────────────────────────
Purpose
    • Validate that `poc.aggregators.remoteok.fetch()` returns only
      Technical Program Manager postings published within the requested window.

Why test this early?
    • If the RemoteOK JSON schema changes, these tests fail first.
    • Guarantees that downstream steps (normalizer, scorer, exporter) receive
      predictable fields.

What makes a result “valid”?
    1. Title contains “program manager” (case-insensitive)
    2. Job’s epoch timestamp ≥ <cut-off>
    3. Required keys: id, title, company, url, date_posted

Test strategy
    • Mock the API call (no network).
    • Use a fixture payload identical to the real RemoteOK endpoint.
    • Edge-case fixture covers:
        – Job older than N days   → filtered out
        – Non-TPM title           → filtered out
        – Well-formed TPM posting → kept
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest import mock
import json

import pytest

import poc.aggregators.remoteok as remoteok


FIXTURE = Path(__file__).parent / "fixtures" / "remoteok_sample.json"


def _load_fixture():
    """Return the JSON list that RemoteOK would normally return."""
    return json.loads(FIXTURE.read_text())


def test_keeps_only_recent_tpm_jobs():
    """fetch(days=X) should return *only* TPM jobs posted within X days."""
    with mock.patch("requests.get") as m:
        m.return_value.json.return_value = _load_fixture()
        m.return_value.raise_for_status.return_value = None

        jobs = remoteok.fetch(days=7)

    assert jobs, "No jobs returned (fixture should include at least one hit)"

    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    for job in jobs:
        assert "program manager" in job["title"].lower()
        assert job["date_posted"] >= cutoff, "Job is older than cutoff"
