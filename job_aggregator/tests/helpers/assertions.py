"""Helper functions for test assertions."""

def assert_valid_job_data(job_data):
    """Assert that job data has all required fields."""
    required_fields = ["title", "company", "location", "description"]
    for field in required_fields:
        assert field in job_data, f"Missing required field: {field}"
        assert job_data[field], f"Field {field} cannot be empty"

def assert_valid_response_format(response):
    """Assert that API response has correct format."""
    assert isinstance(response, dict), "Response must be a dictionary"
    assert "jobs" in response, "Response missing 'jobs' key"
    assert isinstance(response["jobs"], list), "'jobs' must be a list"
