"""Job model for representing job postings"""
from typing import Optional, List, Dict, Any
from datetime import datetime

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
                 remote: bool = False,
                 job_type: str = "full-time",
                 posted_date: Optional[datetime] = None,
                 source: str = "",
                 **kwargs):
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.url = url
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.remote = remote
        self.job_type = job_type
        self.posted_date = posted_date or datetime.now()
        self.source = source
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'url': self.url,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'remote': self.remote,
            'job_type': self.job_type,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None,
            'source': self.source,
            **self.metadata
        }
    
    def __str__(self):
        return f"Job(title='{self.title}', company='{self.company}', location='{self.location}')"
    
    def __repr__(self):
        return self.__str__()
