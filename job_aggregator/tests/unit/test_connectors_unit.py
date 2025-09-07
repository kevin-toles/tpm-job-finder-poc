import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pytest
from job_aggregator.aggregators.greenhouse import GreenhouseConnector
from job_aggregator.aggregators.lever import LeverConnector

GREENHOUSE_FIXTURE = Path(__file__).parents[1] / "fixtures" / "greenhouse_sample.json"
LEVER_FIXTURE = Path(__file__).parents[1] / "fixtures" / "lever_sample.json"

def _mock_http(monkeypatch, payload):
    import requests
    resp = requests.Response()
    resp.status_code = 200
    resp._content = json.dumps(payload).encode()
    monkeypatch.setattr("requests.get", lambda *args, **kwargs: resp)

def test_greenhouse_fetch_since(monkeypatch):
    sample = json.loads(GREENHOUSE_FIXTURE.read_text(encoding="utf-8"))
    # Set job date to recent
    for job in sample["jobs"]:
        job["updated_at"] = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    _mock_http(monkeypatch, sample)
    jobs = GreenhouseConnector(companies=["greenhouse"]).fetch_since(days=7)
    assert jobs, "Should return at least one posting from Greenhouse"
    for job in jobs:
        assert job.source == "greenhouse"
        assert job.date_posted >= datetime.now(timezone.utc) - timedelta(days=7)

def test_lever_fetch_since(monkeypatch):
    sample = json.loads(LEVER_FIXTURE.read_text(encoding="utf-8"))
    # Set job date to recent
    for job in sample:
        job["createdAt"] = int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp() * 1000)
    _mock_http(monkeypatch, sample)
    jobs = LeverConnector(companies=["lever"]).fetch_since(days=7)
    assert jobs, "Should return at least one posting from Lever"
    for job in jobs:
        assert job.source == "lever"
        assert job.date_posted >= datetime.now(timezone.utc) - timedelta(days=7)
