"""
Unit tests for JobDescriptionExtractor
"""
import pytest
from job_aggregator.services.job_description_extractor import JobDescriptionExtractor

class DummyResponse:
    def __init__(self, text):
        self.text = text

@pytest.fixture
def extractor(monkeypatch):
    extractor = JobDescriptionExtractor()
    # Patch requests.get to return dummy HTML for each domain
    def dummy_get(url, timeout=10):
        if 'greenhouse.io' in url:
            return DummyResponse('<div class="description">Greenhouse job description</div>')
        if 'lever.co' in url:
            return DummyResponse('<div class="content">Lever job description</div>')
        if 'remoteok.com' in url:
            return DummyResponse('<div class="job-description">RemoteOK job description</div>')
        return DummyResponse('<div class="description">Generic job description</div>')
    monkeypatch.setattr('requests.get', dummy_get)
    return extractor

def test_greenhouse_extraction(extractor):
    url = 'https://boards.greenhouse.io/example'
    desc = extractor.extract(url)
    assert desc == 'Greenhouse job description'

def test_lever_extraction(extractor):
    url = 'https://jobs.lever.co/example'
    desc = extractor.extract(url)
    assert desc == 'Lever job description'

def test_remoteok_extraction(extractor):
    url = 'https://remoteok.com/example'
    desc = extractor.extract(url)
    assert desc == 'RemoteOK job description'

def test_generic_extraction(extractor):
    url = 'https://example.com/job'
    desc = extractor.extract(url)
    assert desc == 'Generic job description'
