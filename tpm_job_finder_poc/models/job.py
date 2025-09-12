"""Job model for representing job postings"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class Job:
    """Represents a job posting"""
    
    def __init__(self, 
                 title: str,
                 company: str, 
                 location: str = "",
                 description: str = "",
                 url: str = "",
                 salary_min: Optional[float] = None,
                 salary_max: Optional[float] = None,
                 salary: Optional[str] = None,  # Add salary field for E2E compatibility
                 remote: bool = False,
                 job_type: str = "full-time",
                 posted_date: Optional[datetime] = None,
                 date_posted: Optional[datetime] = None,  # Add date_posted alias
                 source: str = "",
                 id: Optional[str] = None,  # Add id field for E2E compatibility
                 **kwargs):
        self.id = id or str(uuid.uuid4())  # Generate unique ID if not provided
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.url = url
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.salary = salary  # String representation of salary
        self.remote = remote
        self.job_type = job_type
        self.posted_date = posted_date or date_posted or datetime.now()
        self.date_posted = self.posted_date  # Alias for compatibility
        self.source = source
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary': self.salary,
            'remote': self.remote,
            'job_type': self.job_type,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'date_posted': self.date_posted.isoformat() if self.date_posted else None,
            'source': self.source,
            **self.metadata
        }
    
    def __str__(self):
        return f"Job(id='{self.id}', title='{self.title}', company='{self.company}', location='{self.location}')"
    
    def __repr__(self):
        return self.__str__()
