"""Models for job scraping requests and responses."""

from typing import List, Optional
from pydantic import BaseModel, Field

class JobRequest(BaseModel):
    """Job search request model."""
    source: str = Field(..., description="Job board source (linkedin, indeed, ziprecruiter)")
    search_terms: List[str] = Field(..., description="Search terms for job search")
    location: Optional[str] = Field(None, description="Location for job search")
    max_results: Optional[int] = Field(10, description="Maximum number of results to return")

class Job(BaseModel):
    """Job posting model."""
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    posted_date: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None

class JobResponse(BaseModel):
    """Job search response model."""
    jobs: List[Job]
