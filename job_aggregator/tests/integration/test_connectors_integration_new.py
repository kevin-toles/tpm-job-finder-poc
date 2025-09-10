import pytest
from job_aggregator.aggregators.ashby import AshbyConnector
from job_aggregator.aggregators.smartrecruiters import SmartRecruitersConnector
from job_aggregator.aggregators.workable import WorkableConnector
from job_aggregator.aggregators.recruitee import RecruiteeConnector

@pytest.mark.parametrize("connector", [
    AshbyConnector(board_name="demo"),
    SmartRecruitersConnector(company="demo"),
    WorkableConnector(subdomain="demo"),
    RecruiteeConnector(subdomain="demo"),
])
def test_connector_integration(monkeypatch, connector):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                if "ashbyhq" in url:
                    return {"jobs": [{"title": "PM", "location": "NYC", "department": "Product", "descriptionPlain": "desc", "jobUrl": "url", "publishedAt": "2021-01-01T00:00:00Z"}]}
                if "smartrecruiters" in url and "postings?" in url:
                    return {"content": [{"id": "1", "name": "SEO", "location": {"city": "SF"}, "applyUrl": "url", "createdOn": "2021-01-01T00:00:00Z"}]}
                if "smartrecruiters" in url:
                    return {"jobAd": {"sections": {"jobDescription": {"text": "desc"}}}}
                if "workable" in url:
                    return {"jobs": [{"title": "TPM", "shortcode": "A1", "url": "url", "description": "desc", "location": {"city": "Boston"}}]}
                if "recruitee" in url:
                    return {"offers": [{"id": 1, "title": "TPM", "url": "url", "description": "desc", "location": {"city": "Amsterdam"}}]}
                return {}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    jobs = connector.fetch_jobs()
    assert jobs
    job = jobs[0]
    assert job.title
    assert job.description
    assert job.url
