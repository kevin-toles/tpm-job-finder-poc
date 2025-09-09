from job_normalizer.jobs.normalizer import normalize_title, normalize_salary, normalize_location, normalize_job, dedupe_jobs
from job_normalizer.jobs.schema import JobPosting
from datetime import datetime, timezone


def test_normalize_title():
    assert normalize_title('  senior engineer ') == 'Senior Engineer'
    assert normalize_title('DATA scientist') == 'Data Scientist'

def test_normalize_salary():
    assert normalize_salary('$120,000') == '120000'
    assert normalize_salary('  $85,000 ') == '85000'
    assert normalize_salary(None) is None

def test_normalize_location():
    assert normalize_location(' new york ') == 'New York'
    assert normalize_location(None) is None

def test_normalize_job():
    job = JobPosting(
        id='1', source='test', company='Acme', title='  devops engineer ', location=' san francisco ', salary='$150,000', url='http://example.com', date_posted=datetime.now(timezone.utc), raw={}
    )
    norm = normalize_job(job)
    assert norm.title == 'Devops Engineer'
    assert norm.salary == '150000'
    assert norm.location == 'San Francisco'

def test_dedupe_jobs():
    job1 = JobPosting(id='1', source='test', company='Acme', title='Engineer', location='NY', salary=None, url='http://a.com', date_posted=datetime.now(timezone.utc), raw={})
    job2 = JobPosting(id='2', source='test', company='Acme', title='Engineer', location='NY', salary=None, url='http://a.com', date_posted=datetime.now(timezone.utc), raw={})
    job3 = JobPosting(id='3', source='test', company='Acme', title='Manager', location='NY', salary=None, url='http://b.com', date_posted=datetime.now(timezone.utc), raw={})
    deduped = dedupe_jobs([job1, job2, job3])
    assert len(deduped) == 2
    urls = {str(j.url) for j in deduped}
    assert 'http://a.com/' in urls
    assert 'http://b.com/' in urls
