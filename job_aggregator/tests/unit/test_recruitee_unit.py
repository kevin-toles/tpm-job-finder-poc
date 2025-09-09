import pytest
from job_aggregator.aggregators.recruitee import RecruiteeConnector

@pytest.fixture
def mock_recruitee(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                return {"offers": [{
                    "id": 123456,
                    "title": "Technical Program Manager",
                    "slug": "technical-program-manager",
                    "url": "https://demo.recruitee.com/o/technical-program-manager",
                    "location": {"city": "Amsterdam", "country": "Netherlands"},
                    "description": "Recruitee job description"
                }]}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    return RecruiteeConnector(subdomain="demo")

def test_recruitee_fetch_jobs(mock_recruitee):
    jobs = mock_recruitee.fetch_jobs()
    assert jobs
    job = jobs[0]
    assert job.title == "Technical Program Manager"
    assert job.description == "Recruitee job description"
    assert str(job.url) == "https://demo.recruitee.com/o/technical-program-manager"
