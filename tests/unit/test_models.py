"""
Unit tests for data models.

Tests for Pydantic models and data validation.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from src.models.job import JobPosting, SearchCriteria, JobFilter, UserProfile


class TestJobPosting:
    """Test cases for JobPosting model."""
    
    def test_valid_job_posting(self):
        """Test creating a valid job posting."""
        job_data = {
            "id": "job123",
            "title": "Technical Program Manager",
            "company": "Test Corp",
            "location": "Remote",
            "description": "Great TPM role",
            "posted_date": datetime.now(),
            "application_url": "https://example.com/apply",
            "source": "lever"
        }
        
        job = JobPosting(**job_data)
        assert job.id == "job123"
        assert job.title == "Technical Program Manager"
        assert job.company == "Test Corp"
    
    def test_missing_required_fields(self):
        """Test validation error for missing required fields."""
        with pytest.raises(ValidationError):
            JobPosting(title="TPM")  # Missing required fields
    
    def test_job_posting_with_requirements(self):
        """Test job posting with requirements list."""
        job_data = {
            "id": "job123",
            "title": "Technical Program Manager",
            "company": "Test Corp",
            "location": "Remote",
            "description": "Great TPM role",
            "requirements": ["5+ years experience", "Python knowledge"],
            "posted_date": datetime.now(),
            "application_url": "https://example.com/apply",
            "source": "lever"
        }
        
        job = JobPosting(**job_data)
        assert len(job.requirements) == 2
        assert "Python knowledge" in job.requirements


class TestSearchCriteria:
    """Test cases for SearchCriteria model."""
    
    def test_empty_search_criteria(self):
        """Test creating empty search criteria."""
        criteria = SearchCriteria()
        assert criteria.keywords == []
        assert criteria.location is None
        assert criteria.remote_allowed is False
    
    def test_search_criteria_with_data(self):
        """Test search criteria with all fields."""
        criteria = SearchCriteria(
            keywords=["TPM", "technical"],
            location="San Francisco",
            remote_allowed=True,
            experience_level="Senior",
            salary_min=120000,
            salary_max=180000
        )
        
        assert "TPM" in criteria.keywords
        assert criteria.location == "San Francisco"
        assert criteria.remote_allowed is True
        assert criteria.salary_min == 120000


class TestJobFilter:
    """Test cases for JobFilter model."""
    
    def test_empty_job_filter(self):
        """Test creating empty job filter."""
        filter_obj = JobFilter()
        assert filter_obj.companies == []
        assert filter_obj.excluded_companies == []
        assert filter_obj.required_skills == []
    
    def test_job_filter_with_data(self):
        """Test job filter with data."""
        filter_obj = JobFilter(
            companies=["Google", "Microsoft"],
            excluded_companies=["Bad Corp"],
            required_skills=["Python", "Leadership"],
            preferred_skills=["AWS"]
        )
        
        assert "Google" in filter_obj.companies
        assert "Bad Corp" in filter_obj.excluded_companies
        assert "Python" in filter_obj.required_skills


class TestUserProfile:
    """Test cases for UserProfile model."""
    
    def test_user_profile_creation(self):
        """Test creating a user profile."""
        profile = UserProfile(
            name="John Doe",
            email="john@example.com",
            skills=["Python", "Leadership"],
            experience_years=8
        )
        
        assert profile.name == "John Doe"
        assert profile.email == "john@example.com"
        assert profile.experience_years == 8
        assert "Python" in profile.skills
    
    def test_user_profile_with_preferences(self):
        """Test user profile with job preferences."""
        preferences = JobFilter(
            companies=["Tech Corp"],
            required_skills=["Leadership"]
        )
        
        profile = UserProfile(
            name="Jane Smith",
            email="jane@example.com",
            preferences=preferences
        )
        
        assert profile.preferences.companies == ["Tech Corp"]
        assert profile.preferences.required_skills == ["Leadership"]