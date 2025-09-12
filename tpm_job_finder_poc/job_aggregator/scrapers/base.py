"""Base scraper for job aggregation."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseJobScraper(ABC):
    """Base class for job scrapers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize base scraper with optional configuration."""
        self.config = config or {}
    
    @abstractmethod
    async def scrape_jobs(self, 
                         query: str, 
                         location: Optional[str] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape jobs based on query and location.
        
        Args:
            query: Job search query
            location: Location filter (optional)
            limit: Maximum number of jobs to return
            
        Returns:
            List of job dictionaries
        """
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """Get detailed information for a specific job.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            Detailed job information
        """
        pass
    
    def normalize_job_data(self, raw_job: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize job data to standard format.
        
        Args:
            raw_job: Raw job data from scraper
            
        Returns:
            Normalized job data
        """
        return {
            'id': raw_job.get('id'),
            'title': raw_job.get('title', ''),
            'company': raw_job.get('company', ''),
            'location': raw_job.get('location', ''),
            'description': raw_job.get('description', ''),
            'url': raw_job.get('url', ''),
            'date_posted': raw_job.get('date_posted'),
            'salary': raw_job.get('salary'),
            'source': self.__class__.__name__.lower().replace('scraper', ''),
            'scraped_at': datetime.now()
        }
