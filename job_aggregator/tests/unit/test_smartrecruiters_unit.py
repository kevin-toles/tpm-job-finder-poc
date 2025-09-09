import pytest
from job_aggregator.aggregators.smartrecruiters import SmartRecruitersConnector

@pytest.fixture
def mock_smartrecruiters(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                if "postings?" in url:
                    return {"content": [{"id": "884352026", "name": "SEO Manager", "location": {"city": "San Francisco"}, "applyUrl": "https://www.smartrecruiters.com/.../seo-manager", "createdOn": "2021-04-30T16:21:55.393Z"}]}
                else:
                    return {"jobAd": {"sections": {"jobDescription": {"text": "SEO job description"}}}}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    return SmartRecruitersConnector(company="demo")

def test_smartrecruiters_fetch_jobs(mock_smartrecruiters):
    jobs = mock_smartrecruiters.fetch_jobs()
    assert jobs
    job = jobs[0]
    assert job.title == "SEO Manager"
    assert job.description == "SEO job description"
    assert str(job.url).startswith("https://www.smartrecruiters.com/")
