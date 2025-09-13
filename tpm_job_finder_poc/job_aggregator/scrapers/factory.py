"""Factory for job board scrapers."""

from typing import List, Optional, Type

from tpm_job_finder_poc.job_aggregator.scrapers.base import BaseJobScraper
# from tpm_job_finder_poc.job_aggregator.scrapers.indeed import IndeedScraper
# from tpm_job_finder_poc.job_aggregator.scrapers.ziprecruiter import ZipRecruiterScraper

class ScraperFactory:
    """Factory for creating job board scrapers."""
    
    _scrapers: dict[str, Type[BaseJobScraper]] = {
        # "indeed": IndeedScraper,
        # "ziprecruiter": ZipRecruiterScraper
    }
    
    @classmethod
    def get_scraper(cls, source: str, search_terms: List[str], location: Optional[str] = None) -> Optional[BaseJobScraper]:
        """Get a scraper instance for the given source.
        
        Args:
            source: Name of job board ("indeed", "ziprecruiter", etc.)
            search_terms: List of job titles/keywords to search for
            location: Optional location filter
            
        Returns:
            Scraper instance if source is supported, None otherwise
        """
        scraper_class = cls._scrapers.get(source.lower())
        if scraper_class:
            return scraper_class(search_terms, location)
        return None
        
    @classmethod
    def get_all_scrapers(cls, search_terms: List[str], location: Optional[str] = None) -> List[BaseJobScraper]:
        """Get scraper instances for all supported job boards.
        
        Args:
            search_terms: List of job titles/keywords to search for
            location: Optional location filter
            
        Returns:
            List of scraper instances
        """
        return [
            scraper_class(search_terms, location)
            for scraper_class in cls._scrapers.values()
        ]
