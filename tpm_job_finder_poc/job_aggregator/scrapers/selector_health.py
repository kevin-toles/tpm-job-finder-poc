"""Health check system for web scraping selectors."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup
from .selector_maintainer import SelectorMaintainer
from .base import BaseJobScraper

logger = logging.getLogger(__name__)

class SelectorHealthChecker:
    """Monitors and validates selectors across job boards."""
    
    def __init__(self, selector_maintainer: SelectorMaintainer):
        """Initialize the health checker.
        
        Args:
            selector_maintainer: The selector maintainer instance to check
        """
        self.selector_maintainer = selector_maintainer
        self.health_stats: Dict[str, Dict[str, Dict[str, int]]] = {}
        
    async def check_selectors(self, scraper: BaseJobScraper) -> Dict[str, Dict[str, bool]]:
        """Check all selectors for a specific scraper.
        
        Args:
            scraper: The scraper instance to check selectors for
            
        Returns:
            Dict of site -> purpose -> health status
        """
        # Get the scraper's site name from its class
        site = scraper.__class__.__name__.lower().replace('scraper', '')
        
        # Initialize stats for this site
        if site not in self.health_stats:
            self.health_stats[site] = {}
            
        # Get sample pages
        search_page = await self._get_sample_search_page(scraper)
        detail_page = await self._get_sample_detail_page(scraper)
        
        results = {
            'search_page': {},
            'detail_page': {}
        }
        
        if search_page:
            # Check search page selectors
            search_selectors = [
                'job_card_title',
                'job_card_company',
                'job_card_location',
                'job_card_salary',
                'job_card_date'
            ]
            
            for purpose in search_selectors:
                success = await self._check_selector(site, purpose, search_page)
                results['search_page'][purpose] = success
                
                # Update stats
                if purpose not in self.health_stats[site]:
                    self.health_stats[site][purpose] = {
                        'success': 0,
                        'failure': 0,
                        'last_check': None
                    }
                    
                if success:
                    self.health_stats[site][purpose]['success'] += 1
                else:
                    self.health_stats[site][purpose]['failure'] += 1
                    
                self.health_stats[site][purpose]['last_check'] = datetime.now()
                
        if detail_page:
            # Check detail page selectors
            detail_selectors = [
                'job_title',
                'job_description'
            ]
            
            for purpose in detail_selectors:
                success = await self._check_selector(site, purpose, detail_page)
                results['detail_page'][purpose] = success
                
                # Update stats
                if purpose not in self.health_stats[site]:
                    self.health_stats[site][purpose] = {
                        'success': 0,
                        'failure': 0,
                        'last_check': None
                    }
                    
                if success:
                    self.health_stats[site][purpose]['success'] += 1
                else:
                    self.health_stats[site][purpose]['failure'] += 1
                    
                self.health_stats[site][purpose]['last_check'] = datetime.now()
                
        return results
        
    async def _get_sample_search_page(self, scraper: BaseJobScraper) -> Optional[BeautifulSoup]:
        """Get a sample search page for testing selectors.
        
        Args:
            scraper: The scraper to test
            
        Returns:
            BeautifulSoup object of search page if successful
        """
        try:
            # Use a common job title that should always return results
            async with scraper:
                soup = await scraper._get_page(scraper.BASE_SEARCH_URL)
                return soup
        except Exception as e:
            logger.error(f"Error getting sample search page: {str(e)}")
            return None
            
    async def _get_sample_detail_page(self, scraper: BaseJobScraper) -> Optional[BeautifulSoup]:
        """Get a sample job detail page for testing selectors.
        
        Args:
            scraper: The scraper to test
            
        Returns:
            BeautifulSoup object of detail page if successful
        """
        try:
            # First get a job URL from the search page
            async with scraper:
                search_soup = await scraper._get_page(scraper.BASE_SEARCH_URL)
                if not search_soup:
                    return None
                    
                # Try to find any job link
                if isinstance(scraper, BaseJobScraper):
                    link = None
                    for selector in [
                        "a.job_link",  # ZipRecruiter
                        "a.jcs-JobTitle",  # Indeed
                        "a.base-card__full-link"  # LinkedIn
                    ]:
                        link = search_soup.select_one(selector)
                        if link and link.get('href'):
                            break
                            
                    if link and link.get('href'):
                        detail_soup = await scraper._get_page(link['href'])
                        return detail_soup
                        
        except Exception as e:
            logger.error(f"Error getting sample detail page: {str(e)}")
            
        return None
        
    async def _check_selector(
        self,
        site: str,
        purpose: str,
        soup: BeautifulSoup
    ) -> bool:
        """Check if a selector successfully extracts content.
        
        Args:
            site: Website identifier
            purpose: Purpose of the selector
            soup: BeautifulSoup object to test against
            
        Returns:
            True if selector successfully extracts content
        """
        selector = self.selector_maintainer.get_selector(site, purpose)
        if not selector:
            return False
            
        element = soup.select_one(selector)
        if not element:
            return False
            
        text = element.get_text(strip=True)
        return bool(text)
        
    def get_health_report(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Generate a health report for all monitored selectors.
        
        Returns:
            Dict containing health metrics for each site and selector
        """
        report = {}
        
        for site, purposes in self.health_stats.items():
            report[site] = {}
            
            for purpose, stats in purposes.items():
                total = stats['success'] + stats['failure']
                if total == 0:
                    success_rate = 0
                else:
                    success_rate = (stats['success'] / total) * 100
                    
                report[site][purpose] = {
                    'success_rate': success_rate,
                    'total_checks': total,
                    'last_check': stats['last_check'].isoformat() if stats['last_check'] else None
                }
                
        return report
