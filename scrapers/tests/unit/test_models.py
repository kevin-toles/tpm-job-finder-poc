"""Unit tests for scraper models."""

import pytest
from src.models.job import Job, JobRequest, JobResponse

def test_job_model_validation():
    """Test Job model validation."""
    # Valid job data
    valid_job = Job(
        title="Technical Program Manager",
        company="Example Corp",
        location="San Francisco, CA",
        description="Example description",
        url="https://example.com/job",
        source="linkedin"
    )
    assert valid_job.title == "Technical Program Manager"
    
    # Invalid job data
    with pytest.raises(ValueError):
        Job(
            title="",  # Empty title should fail
            company="Example Corp",
            location="San Francisco, CA",
            description="Example description",
            url="https://example.com/job",
            source="linkedin"
        )

def test_job_request_validation():
    """Test JobRequest model validation."""
    # Valid request
    valid_request = JobRequest(
        source="linkedin",
        search_terms=["TPM", "Technical Program Manager"],
        location="San Francisco"
    )
    assert valid_request.source == "linkedin"
    assert len(valid_request.search_terms) == 2
    
    # Invalid source
    with pytest.raises(ValueError):
        JobRequest(
            source="invalid_source",
            search_terms=["TPM"]
        )
    
    # Empty search terms
    with pytest.raises(ValueError):
        JobRequest(
            source="linkedin",
            search_terms=[]
        )

def test_job_response_validation():
    """Test JobResponse model validation."""
    jobs = [
        Job(
            title="TPM Role 1",
            company="Company A",
            location="Location A",
            description="Description A",
            url="https://example.com/job1",
            source="linkedin"
        ),
        Job(
            title="TPM Role 2",
            company="Company B",
            location="Location B",
            description="Description B",
            url="https://example.com/job2",
            source="linkedin"
        )
    ]
    
    response = JobResponse(jobs=jobs)
    assert len(response.jobs) == 2
    assert all(isinstance(job, Job) for job in response.jobs)
