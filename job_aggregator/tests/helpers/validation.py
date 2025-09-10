"""Functions to validate test data and responses."""

def validate_job_fields(job):
    """Validate required and optional job fields."""
    errors = []
    
    # Required fields
    required = ["title", "company", "location"]
    for field in required:
        if field not in job:
            errors.append(f"Missing required field: {field}")
            
    # Optional fields with defaults
    optional = {
        "description": "",
        "salary_range": "Not specified",
        "employment_type": "Full-time"
    }
    for field, default in optional.items():
        if field not in job:
            job[field] = default
            
    return errors

def validate_response_structure(response):
    """Validate the structure of API response."""
    if not isinstance(response, dict):
        return ["Response must be a dictionary"]
        
    errors = []
    if "jobs" not in response:
        errors.append("Response missing 'jobs' key")
    elif not isinstance(response["jobs"], list):
        errors.append("'jobs' must be a list")
        
    return errors
