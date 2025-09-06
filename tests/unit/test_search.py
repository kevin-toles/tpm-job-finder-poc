"""
Unit tests for core search functionality.

Tests for the job search engine and related functions.
"""

import pytest
from unittest.mock import Mock, patch
from src.core.search import JobSearchEngine, analyze_job_market, calculate_job_score


class TestJobSearchEngine:
    """Test cases for JobSearchEngine class."""
    
    def test_init(self):
        """Test JobSearchEngine initialization."""
        engine = JobSearchEngine()
        assert engine is not None
    
    def test_search_jobs_empty_criteria(self):
        """Test search with empty criteria."""
        engine = JobSearchEngine()
        result = engine.search_jobs({})
        assert isinstance(result, list)
        assert len(result) == 0  # Placeholder returns empty list
    
    def test_search_jobs_with_criteria(self):
        """Test search with specific criteria."""
        engine = JobSearchEngine()
        criteria = {
            "keywords": ["technical program manager"],
            "location": "Remote"
        }
        result = engine.search_jobs(criteria)
        assert isinstance(result, list)
    
    def test_filter_jobs(self):
        """Test job filtering functionality."""
        engine = JobSearchEngine()
        jobs = [{"title": "TPM", "company": "Test Corp"}]
        filters = {"companies": ["Test Corp"]}
        
        result = engine.filter_jobs(jobs, filters)
        assert isinstance(result, list)
        assert result == jobs  # Placeholder returns input


class TestUtilityFunctions:
    """Test cases for utility functions."""
    
    def test_analyze_job_market(self):
        """Test job market analysis function."""
        result = analyze_job_market("San Francisco")
        assert isinstance(result, dict)
        assert "location" in result
        assert result["location"] == "San Francisco"
    
    def test_calculate_job_score(self):
        """Test job scoring function."""
        job = {"title": "Technical Program Manager", "company": "Test Corp"}
        preferences = {"keywords": ["TPM"]}
        
        score = calculate_job_score(job, preferences)
        assert isinstance(score, float)
        assert score == 0.0  # Placeholder returns 0.0