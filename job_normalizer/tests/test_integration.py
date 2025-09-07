from job_normalizer.jobs.parser import parse_job
from job_normalizer.jobs.normalizer import normalize_job, dedupe_jobs
from job_normalizer.jobs.schema import JobPosting
from datetime import datetime, timezone

def test_parse_and_normalize_integration():
    raw_jobs = [
        {
            'id': '1', 'company': 'Acme', 'title': '  devops engineer ', 'location': ' san francisco ', 'salary': '$150,000', 'url': 'http://example.com', 'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
        },
        {
            'id': '2', 'company': 'Acme', 'title': 'Devops Engineer', 'location': 'San Francisco', 'salary': '$150,000', 'url': 'http://example.com', 'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
        },
        {
            'id': '3', 'company': 'Beta', 'title': 'Manager', 'location': 'Remote', 'salary': '$120,000', 'url': 'http://beta.com', 'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
        }
    ]
    jobs = [parse_job(raw, source='test_source') for raw in raw_jobs]
    normalized = [normalize_job(job) for job in jobs]
    deduped = dedupe_jobs(normalized)
    assert len(deduped) == 2
    titles = {job.title for job in deduped}
    assert 'Devops Engineer' in titles
    assert 'Manager' in titles
    companies = {job.company for job in deduped}
    assert 'Acme' in companies
    assert 'Beta' in companies
    urls = {str(job.url) for job in deduped}
    assert 'http://example.com/' in urls
    assert 'http://beta.com/' in urls
