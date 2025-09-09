import pytest
from job_aggregator.aggregators.ashby import AshbyConnector

@pytest.fixture
def mock_ashby(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                return {"jobs": [{
                    "title": "Product Manager",
                    "location": "Houston, TX",
                    "department": "Product",
                    "isRemote": True,
                    "descriptionHtml": "<p>Join our team</p>",
                    "descriptionPlain": "Join our team",
                    "publishedAt": "2021-04-30T16:21:55.393Z",
                    "employmentType": "FullTime",
                    "jobUrl": "https://jobs.ashbyhq.com/example_job",
                    "applyUrl": "https://jobs.ashbyhq.com/example/apply"
                }]}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    return AshbyConnector(board_name="demo")

def test_ashby_fetch_jobs(mock_ashby):
    jobs = mock_ashby.fetch_jobs()
    assert jobs
    job = jobs[0]
    assert job.title == "Product Manager"
    assert job.description == "Join our team"
    assert str(job.url) == "https://jobs.ashbyhq.com/example_job"
