import pytest
import json
from src.poc.aggregators.remoteok import RemoteOKConnector
from src.poc.aggregators.greenhouse import GreenhouseConnector
from src.poc.aggregators.lever import LeverConnector
from src.poc.jobs.schema import JobPosting

def load_fixture(path):
    with open(path) as f:
        return json.load(f)

@pytest.mark.parametrize("connector, fixture_path", [
    (RemoteOKConnector(), "tests/fixtures/remoteok_sample.json"),
    (GreenhouseConnector(), "tests/fixtures/greenhouse_sample.json"),
    (LeverConnector(), "tests/fixtures/lever_sample.json"),
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
