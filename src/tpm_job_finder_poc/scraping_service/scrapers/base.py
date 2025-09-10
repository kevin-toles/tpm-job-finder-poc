"""
Base scraper interface that all job board scrapers must implement.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class ScrapedJob:
    """Standardized job data structure for scraped jobs."""
    id: str
    title: str
    company: str
    location: str
    description: str
    url: str
    source: str
    scraped_at: datetime
    salary_range: Optional[str] = None
    raw_data: Optional[Dict] = None

class BaseScraper(ABC):
    """Abstract base class for all job board scrapers."""
    
    def __init__(self, config: Dict):
        """
        Initialize the scraper with configuration.
        
        Args:
            config: Dictionary containing scraper configuration:
                - use_proxy: bool
                - rate_limit: int (requests per minute)
                - timeout: int (seconds)
                - ...other scraper-specific settings
        """
        self.config = config
        self.name = self.__class__.__name__.lower().replace('scraper', '')
    
    @abstractmethod
    async def search_jobs(self, query: str, location: Optional[str] = None, **kwargs) -> List[ScrapedJob]:
        """
        Search for jobs using the provided criteria.
        
        Args:
            query: Search term (e.g., "Technical Program Manager")
            location: Optional location filter
            **kwargs: Additional search parameters
            
        Returns:
            List of ScrapedJob objects
            
        Raises:
            ScraperError: If there's an error during scraping
        """
        pass
    
    @abstractmethod
    async def get_job_details(self, job_url: str) -> ScrapedJob:
        """
        Fetch detailed information for a specific job.
        
        Args:
            job_url: URL of the job posting
            
        Returns:
            ScrapedJob object with full details
            
        Raises:
            ScraperError: If there's an error fetching the job
        """
        pass
    
    @abstractmethod
    async def verify_access(self) -> bool:
        """
        Verify that the scraper can access the job board.
        
        Returns:
            bool indicating if access is working
            
        Raises:
            ScraperError: If there's an error checking access
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict:
        """
        Check the health/status of the scraper.
        
        Returns:
            Dict containing:
                - status: str ('ok', 'error', etc.)
                - details: Dict of additional info
                - last_successful_scrape: datetime
                
        Raises:
            ScraperError: If health check fails
        """
        pass

class ScraperError(Exception):
    """Base exception for scraper errors."""
    pass

class RateLimitError(ScraperError):
    """Raised when rate limits are exceeded."""
    pass

class AccessDeniedError(ScraperError):
    """Raised when access is denied (e.g., bot detection)."""
    pass

class ParseError(ScraperError):
    """Raised when there's an error parsing job data."""
    pass
