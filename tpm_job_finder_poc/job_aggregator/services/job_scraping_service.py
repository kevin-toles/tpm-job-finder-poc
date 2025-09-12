"""Service for scraping jobs from various job boards."""

import asyncio
from datetime import datetime
from typing import List, Optional

from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting
from tpm_job_finder_poc.job_aggregator.scrapers.factory import ScraperFactory

class JobScrapingService:
    """Service for scraping jobs from multiple job boards."""
    
    def __init__(self, search_terms: List[str], location: Optional[str] = None, sources: Optional[List[str]] = None):
        """Initialize the scraping service.
        
        Args:
            search_terms: List of job titles/keywords to search for
            location: Optional location filter
            sources: Optional list of job board sources to use. If None, all available scrapers will be used.
        """
        self.search_terms = search_terms
        self.location = location
        if sources:
            self.scrapers = [
                ScraperFactory.get_scraper(source, search_terms, location)
                for source in sources
                if ScraperFactory.get_scraper(source, search_terms, location) is not None
            ]
        else:
            self.scrapers = ScraperFactory.get_all_scrapers(search_terms, location)
            
    async def fetch_all_jobs(self) -> List[JobPosting]:
        """Fetch jobs from all configured job boards.
        
        Returns:
            Combined list of jobs from all sources
        """
        all_jobs = []
        
        # Create tasks for each scraper
        async with asyncio.TaskGroup() as group:
            tasks = []
            for scraper in self.scrapers:
                # Use scraper as async context manager
                async with scraper:
                    task = group.create_task(scraper.fetch_all_jobs())
                    tasks.append(task)
            
            # Wait for all tasks to complete
            for task in tasks:
                try:
                    jobs = await task
                    all_jobs.extend(jobs)
                except Exception as e:
                    # Log error but continue with other scrapers
                    print(f"Error from scraper: {str(e)}")
                    continue
                    
        return all_jobs
