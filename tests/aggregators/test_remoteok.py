"""
RemoteOKConnector unit-test
───────────────────────────
Ensures:
  • Returns JobPosting items
  • Titles match 'program manager' / 'tpm'
  • date_posted is UTC & ≤ cut-off
"""
from datetime import datetime, timedelta, timezone
import json

import requests
from pathlib import Path
from pytest_mock import MockerFixture

from job_aggregator.aggregators.remoteok import RemoteOKConnector
from job_normalizer.jobs.schema import JobPosting

FIXTURE = Path(__file__).parents[1] / "fixtures" / "remoteok_sample.json"


def _mock_http(mocker: MockerFixture, payload: list[dict]) -> None:
    """Monkey-patch requests.get to return fixture JSON."""
    resp = requests.Response()
    resp.status_code = 200
    resp._content = json.dumps(payload).encode()           # type: ignore[attr-defined]
    mocker.setattr("requests.get", lambda *args, **kwargs: resp)


def test_recent_tpm_jobs(monkeypatch: MockerFixture) -> None:
    sample = json.loads(FIXTURE.read_text(encoding="utf-8"))
    # make sure at least one record is < 7 days old
    sample[0]["epoch"] = int(
        (datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()
    )

    _mock_http(monkeypatch, sample)

    jobs = RemoteOKConnector().fetch_since(days=7)
    assert jobs, "Should return at least one posting"

    job: JobPosting = jobs[0]
    assert job.source == "remoteok"
    assert "program manager" in job.title.lower() or "tpm" in job.title.lower()
    assert job.date_posted.tzinfo is timezone.utc
    assert job.date_posted >= datetime.now(timezone.utc) - timedelta(days=7)
