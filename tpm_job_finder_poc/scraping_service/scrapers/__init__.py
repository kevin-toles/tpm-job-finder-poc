"""
Scrapers package for scraping_service_v2.

Contains browser-based job scrapers for various job boards and platforms.
"""

from .base_scraper import BaseScraper, BrowserProfile
from .indeed import IndeedScraper
from .linkedin import LinkedInScraper
from .ziprecruiter import ZipRecruiterScraper
from .greenhouse import GreenhouseScraper

__all__ = [
    'BaseScraper',
    'BrowserProfile', 
    'IndeedScraper',
    'LinkedInScraper',
    'ZipRecruiterScraper', 
    'GreenhouseScraper'
]
