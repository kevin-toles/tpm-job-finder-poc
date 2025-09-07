
import pytest
import json
import os
from job_aggregator.aggregators.remoteok import RemoteOKConnector
from job_aggregator.aggregators.greenhouse import GreenhouseConnector
from job_aggregator.aggregators.lever import LeverConnector
from job_normalizer.jobs.schema import JobPosting

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../fixtures"))

def load_fixture(path):
    with open(path) as f:
        return json.load(f)

@pytest.mark.parametrize("connector, fixture_path", [
    (RemoteOKConnector(), os.path.join(FIXTURE_DIR, "remoteok_sample.json")),
    (GreenhouseConnector(), os.path.join(FIXTURE_DIR, "greenhouse_sample.json")),
    (LeverConnector(), os.path.join(FIXTURE_DIR, "lever_sample.json")),
])
def test_connector_end_to_end(connector, fixture_path):
    sample_data = load_fixture(fixture_path)
    jobs = connector.normalize_jobs_from_data(sample_data)
    assert jobs, f"No jobs returned for {connector.__class__.__name__}"
    for job in jobs:
        print(f"Job type: {type(job)}, JobPosting type: {type(JobPosting)}")
        assert type(job).__name__ == "JobPosting"
        assert job.id
        assert job.title
        assert job.company
        assert job.location is not None
        assert job.url
