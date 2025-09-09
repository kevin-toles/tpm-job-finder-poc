import pytest
from job_aggregator.aggregators.ashby import AshbyConnector
from job_aggregator.aggregators.smartrecruiters import SmartRecruitersConnector
from job_aggregator.aggregators.workable import WorkableConnector
from job_aggregator.aggregators.recruitee import RecruiteeConnector

def test_ashby_e2e(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                return {"jobs": [{"title": "PM", "location": "NYC", "department": "Product", "descriptionPlain": "desc", "jobUrl": "https://example.com/job/ashby123", "publishedAt": "2021-01-01T00:00:00Z"}]}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    jobs = AshbyConnector(board_name="demo").fetch_jobs()
    assert jobs[0].description == "desc"

def test_smartrecruiters_e2e(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                if "postings?" in url:
                    return {"content": [{"id": "1", "name": "SEO", "location": {"city": "SF"}, "applyUrl": "https://example.com/job/sr123", "createdOn": "2021-01-01T00:00:00Z"}]}
                else:
                    return {"jobAd": {"sections": {"jobDescription": {"text": "desc"}}}}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    jobs = SmartRecruitersConnector(company="demo").fetch_jobs()
    assert jobs[0].description == "desc"

def test_workable_e2e(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                return {"jobs": [{"title": "TPM", "shortcode": "A1", "url": "https://example.com/job/workable123", "description": "desc", "location": {"city": "Boston"}}]}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    jobs = WorkableConnector(subdomain="demo").fetch_jobs()
    assert jobs[0].description == "desc"

def test_recruitee_e2e(monkeypatch):
    def dummy_get(url):
        class DummyResp:
            def raise_for_status(self): pass
            def json(self):
                return {"offers": [{"id": 1, "title": "TPM", "url": "https://example.com/job/recruitee123", "description": "desc", "location": {"city": "Amsterdam"}}]}
        return DummyResp()
    monkeypatch.setattr("requests.get", dummy_get)
    jobs = RecruiteeConnector(subdomain="demo").fetch_jobs()
    assert jobs[0].description == "desc"
