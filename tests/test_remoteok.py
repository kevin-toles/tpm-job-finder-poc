"""
RemoteOK aggregator · unit tests
────────────────────────────────
Purpose
    Validate that `poc.aggregators.remoteok.fetch()` returns only TPM jobs
    posted within the requested window and that `date_posted` is tz-aware.

Test strategy
    • Mock the HTTP request so no network call occurs.
    • Use a fixture JSON identical to a real RemoteOK response.
    • Assert:
        – Every title contains "program manager".
        – All datetimes are timezone-aware and within the cutoff.
"""

from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest import mock
import json

import poc.aggregators.remoteok as remoteok

FIXTURE = Path(__file__).parent / "fixtures" / "remoteok_sample.json"


def load_fixture():
    return json.loads(FIXTURE.read_text())


def test_recent_tpm_jobs_only():
    """fetch(days=7) should keep only recent TPM jobs."""
    with mock.patch("requests.get") as m:
        m.return_value.json.return_value = load_fixture()
        m.return_value.raise_for_status.return_value = None

        jobs = remoteok.fetch(days=7)

    assert jobs, "Expected at least one job from fixture"
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    for job in jobs:
        # title filter
        assert "program manager" in job["title"].lower()
        # tz-aware + within window
        assert job["date_posted"].tzinfo is not None
        assert job["date_posted"] >= cutoff
