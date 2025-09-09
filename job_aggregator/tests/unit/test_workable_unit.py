import pytest
from job_aggregator.aggregators.workable import WorkableConnector

@pytest.fixture
def mock_workable(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                return {"jobs": [{
                    "title": "Senior TPM",
                    "shortcode": "ABCDEF",
                    "department": "Engineering",
                    "url": "https://demo.workable.com/jobs/ABCDEF",
                    "application_url": "https://apply.workable.com/demo/j/ABCDEF/",
                    "description": "Full job description...",
                    "location": {"city": "Boston", "country": "United States"}
                }]}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    return WorkableConnector(subdomain="demo")

def test_workable_fetch_jobs(mock_workable):
    jobs = mock_workable.fetch_jobs()
    assert jobs
    job = jobs[0]
    assert job.title == "Senior TPM"
    assert job.description == "Full job description..."
    assert str(job.url) == "https://demo.workable.com/jobs/ABCDEF"
