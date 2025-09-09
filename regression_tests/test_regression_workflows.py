"""
Regression tests for major cross-component workflows in the job finder system.
These tests ensure that changes do not break critical business logic or integration points.
"""
import pytest
from job_aggregator.aggregators.remoteok import RemoteOKConnector
from job_aggregator.aggregators.greenhouse import GreenhouseConnector
from job_aggregator.aggregators.lever import LeverConnector
from job_normalizer.jobs.parser import parse_job
from job_normalizer.jobs.normalizer import normalize_job, dedupe_jobs
from job_normalizer.jobs.schema import JobPosting
from datetime import datetime, timezone

# Example fixture data for regression tests
REMOTEOK_RAW = {
    'id': '123456',
    'position': 'Technical Program Manager',
    'company': 'Acme Corp',
    'epoch': 1736025600,
    'location': 'Remote',
    'url': 'https://remoteok.com/remote-jobs/123456',
    'tags': ['tpm', 'remote'],
    'salary': '$150k–$180k',
    'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
}

GREENHOUSE_RAW = {
    'id': 7890,
    'title': 'Senior Technical Program Manager',
    'company': 'SampleCo',
    'location': 'Remote',
    'salary': None,
    'url': 'https://boards.greenhouse.io/sampleco/jobs/7890',
    'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
}

LEVER_RAW = {
    'id': 'abc123',
    'text': 'Technical Program Manager',
    'company': 'SampleCo',
    'categories': {
        'location': 'San Francisco, CA',
        'team': 'Engineering'
    },
    'createdAt': '2025-09-05T11:22:33Z',
    'hostedUrl': 'https://jobs.lever.co/sampleco/abc123',
    'date_posted': datetime(2025, 9, 6, tzinfo=timezone.utc)
}


@pytest.mark.parametrize("connector, raw, mapping", [
    (RemoteOKConnector(), REMOTEOK_RAW, {
        'id': lambda r: str(r['id']),
        'title': lambda r: r.get('position', ''),
        'company': lambda r: r.get('company', ''),
        'location': lambda r: r.get('location', None),
        'salary': lambda r: r.get('salary', None),
        'url': lambda r: r.get('url', ''),
        'date_posted': lambda r: r.get('date_posted', datetime.now(timezone.utc)),
    }),
    (GreenhouseConnector(), GREENHOUSE_RAW, {
        'id': lambda r: str(r['id']),
        'title': lambda r: r.get('title', ''),
        'company': lambda r: r.get('company', ''),
        'location': lambda r: r.get('location', None),
        'salary': lambda r: r.get('salary', None),
        'url': lambda r: r.get('url', ''),
        'date_posted': lambda r: r.get('date_posted', datetime.now(timezone.utc)),
    }),
    (LeverConnector(), LEVER_RAW, {
        'id': lambda r: r.get('id', ''),
        'title': lambda r: r.get('text', ''),
        'company': lambda r: r.get('company', ''),
        'location': lambda r: r.get('categories', {}).get('location', None),
        'salary': lambda r: None,
        'url': lambda r: r.get('hostedUrl', ''),
        'date_posted': lambda r: r.get('date_posted', datetime.now(timezone.utc)),
    }),
])
def test_connector_to_normalizer_regression(connector, raw, mapping):
    # Map raw connector data to unified schema
    mapped = {k: fn(raw) for k, fn in mapping.items()}
    job = parse_job(mapped, source=connector.__class__.__name__.replace('Connector','').lower())
    norm = normalize_job(job)
    assert isinstance(norm, JobPosting)
    assert norm.id
    assert norm.title
    assert norm.company
    assert norm.url
    assert norm.date_posted.tzinfo is not None
    # Deduplication should not remove unique jobs
    jobs = [norm]
    deduped = dedupe_jobs(jobs)
    assert len(deduped) == 1

def test_deduplication_regression():
    job1 = JobPosting(id='1', source='remoteok', company='Acme', title='TPM', location='Remote', salary=None, url='http://a.com', date_posted=datetime.now(timezone.utc), raw={})
    job2 = JobPosting(id='2', source='remoteok', company='Acme', title='TPM', location='Remote', salary=None, url='http://a.com', date_posted=datetime.now(timezone.utc), raw={})
    job3 = JobPosting(id='3', source='greenhouse', company='Beta', title='Manager', location='NY', salary=None, url='http://b.com', date_posted=datetime.now(timezone.utc), raw={})
    jobs = [job1, job2, job3]
    deduped = dedupe_jobs(jobs)
    assert len(deduped) == 2
    urls = {str(j.url) for j in deduped}
    assert 'http://a.com/' in urls
    assert 'http://b.com/' in urls
