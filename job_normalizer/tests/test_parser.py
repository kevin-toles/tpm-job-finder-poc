from job_normalizer.jobs.parser import parse_job
from job_normalizer.jobs.schema import JobPosting
from datetime import datetime, timezone

def test_parse_job_basic():
    raw = {
        'id': 'abc123',
        'company': 'Acme',
        'title': 'Engineer',
        'location': 'Remote',
        'salary': '$100,000',
        'url': 'http://example.com',
        'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
    }
    job = parse_job(raw, source='test_source')
    assert isinstance(job, JobPosting)
    assert job.id == 'abc123'
    assert job.company == 'Acme'
    assert job.title == 'Engineer'
    assert job.location == 'Remote'
    assert job.salary == '$100,000'
    assert str(job.url) == 'http://example.com/'
    assert job.source == 'test_source'
    assert job.date_posted == datetime(2025, 9, 6, tzinfo=timezone.utc)
    assert job.raw == raw

def test_parse_job_missing_fields():
    raw = {
        'id': 'xyz789',
        'company': 'Beta',
        'title': 'Manager',
        'url': 'http://beta.com',
    }
    job = parse_job(raw, source='test_source')
    assert job.location is None
    assert job.salary is None
