"""
Data models for the job finder application.

This module contains Pydantic models for data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class JobPosting(BaseModel):
    """Model for a job posting."""
    
    id: str = Field(..., description="Unique identifier for the job posting")
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    description: str = Field(..., description="Job description")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    salary_range: Optional[str] = Field(None, description="Salary range")
    posted_date: datetime = Field(..., description="Date when job was posted")
    application_url: str = Field(..., description="URL to apply for the job")
    source: str = Field(..., description="Source of the job posting")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SearchCriteria(BaseModel):
    """Model for job search criteria."""
    
    keywords: List[str] = Field(default_factory=list, description="Search keywords")
    location: Optional[str] = Field(None, description="Preferred location")
    remote_allowed: bool = Field(False, description="Include remote positions")
    experience_level: Optional[str] = Field(None, description="Experience level requirement")
    salary_min: Optional[int] = Field(None, description="Minimum salary")
    salary_max: Optional[int] = Field(None, description="Maximum salary")


class JobFilter(BaseModel):
    """Model for job filtering criteria."""
    
    companies: List[str] = Field(default_factory=list, description="Preferred companies")
    excluded_companies: List[str] = Field(default_factory=list, description="Companies to exclude")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills")


class UserProfile(BaseModel):
    """Model for user profile and preferences."""
    
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")
    skills: List[str] = Field(default_factory=list, description="User skills")
    experience_years: int = Field(0, description="Years of experience")
    preferences: JobFilter = Field(default_factory=JobFilter, description="Job preferences")
    saved_searches: List[SearchCriteria] = Field(default_factory=list, description="Saved search criteria")