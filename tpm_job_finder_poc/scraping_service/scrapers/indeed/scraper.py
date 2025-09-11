"""
Indeed job scraper implementation.

Scrapes job postings from Indeed.com using browser automation.
"""

import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..base_scraper import BaseScraper, BrowserProfile
from ...core.base_job_source import JobPosting, FetchParams, RateLimitConfig

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    """
    Scraper for Indeed.com job postings.
    
    Handles job search, pagination, and detailed job extraction from Indeed's
    web interface using browser automation.
    """
    
    def __init__(self):
        """Initialize the Indeed scraper."""
        super().__init__(
            name="indeed",
            base_url="https://www.indeed.com",
            rate_limits=RateLimitConfig(
                requests_per_minute=8,  # Conservative to avoid blocking
                requests_per_hour=200,
                burst_limit=3
            )
        )
        
    def get_search_url(self, **kwargs) -> str:
        """
        Construct Indeed search URL.
        
        Args:
            **kwargs: Search parameters (q=keywords, l=location, etc.)
            
        Returns:
            Indeed search URL
        """
        base_search_url = f"{self.base_url}/jobs"
        
        # Build query parameters
        params = {}
        if 'q' in kwargs and kwargs['q']:
            params['q'] = kwargs['q']
        if 'l' in kwargs and kwargs['l']:
            params['l'] = kwargs['l']
            
        # Default parameters
        params['sort'] = 'date'  # Sort by most recent
        params['fromage'] = '7'  # Jobs from last 7 days
        
        if params:
            return f"{base_search_url}?{urlencode(params)}"
        return base_search_url
        
    def get_selectors(self) -> Dict[str, str]:
        """
        Get CSS selectors for Indeed job elements.
        
        Returns:
            Dictionary of selectors for different job elements
        """
        return {
            'job_cards': '[data-testid="job-result"]',
            'job_title': '[data-testid="job-title"] a',
            'job_title_fallback': 'h2.jobTitle a',
            'company_name': '[data-testid="company-name"]',
            'company_name_fallback': '.companyName',
            'location': '[data-testid="job-location"]',
            'location_fallback': '.companyLocation',
            'salary': '[data-testid="salary-snippet"]',
            'salary_fallback': '.salary-snippet',
            'summary': '[data-testid="job-snippet"]',
            'summary_fallback': '.summary',
            'date_posted': '[data-testid="job-posted-date"]',
            'date_posted_fallback': '.date',
            'next_button': '[aria-label="Next Page"]',
            'next_button_fallback': 'a[aria-label="Next"]',
            'popup_close': '[data-testid="popup-close"]',
            'cookie_accept': '#onetrust-accept-btn-handler'
        }
        
    async def parse_job_elements(self, driver) -> List[JobPosting]:
        """
        Parse job postings from Indeed search results page.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List of JobPosting objects
        """
        jobs = []
        selectors = self.get_selectors()
        
        try:
            # Wait for job cards to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors['job_cards']))
            )
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_cards'])
            logger.info(f"Found {len(job_cards)} job cards on page")
            
            for card in job_cards:
                try:
                    job = await self._parse_single_job(card, selectors)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning(f"Error parsing job card: {e}")
                    continue
                    
        except TimeoutException:
            logger.warning("No job cards found on page - may be blocked or empty results")
            
        except Exception as e:
            logger.error(f"Error parsing Indeed job elements: {e}")
            
        return jobs
        
    async def _parse_single_job(self, card_element, selectors: Dict[str, str]) -> Optional[JobPosting]:
        """
        Parse a single job card element.
        
        Args:
            card_element: Selenium WebElement for job card
            selectors: Dictionary of CSS selectors
            
        Returns:
            JobPosting object or None if parsing fails
        """
        try:
            # Extract job title and URL
            title_element = self._find_element_with_fallback(
                card_element, 
                [selectors['job_title'], selectors['job_title_fallback']]
            )
            
            if not title_element:
                logger.warning("Could not find job title element")
                return None
                
            title = title_element.text.strip()
            job_url = title_element.get_attribute('href')
            
            # Extract job ID from URL
            job_id = self._extract_job_id_from_url(job_url)
            
            # Extract company name
            company_element = self._find_element_with_fallback(
                card_element,
                [selectors['company_name'], selectors['company_name_fallback']]
            )
            company = company_element.text.strip() if company_element else "Unknown"
            
            # Extract location
            location_element = self._find_element_with_fallback(
                card_element,
                [selectors['location'], selectors['location_fallback']]
            )
            location = location_element.text.strip() if location_element else None
            
            # Extract salary (optional)
            salary_element = self._find_element_with_fallback(
                card_element,
                [selectors['salary'], selectors['salary_fallback']]
            )
            salary = salary_element.text.strip() if salary_element else None
            
            # Extract job summary/description
            summary_element = self._find_element_with_fallback(
                card_element,
                [selectors['summary'], selectors['summary_fallback']]
            )
            description = summary_element.text.strip() if summary_element else None
            
            # Extract posted date
            date_posted = self._parse_posted_date(card_element, selectors)
            
            return JobPosting(
                id=job_id,
                source="indeed",
                company=company,
                title=title,
                location=location,
                salary=salary,
                url=job_url,
                date_posted=date_posted,
                description=description,
                raw_data={
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'page_url': self._driver.current_url
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing single job: {e}")
            return None
            
    def _find_element_with_fallback(self, parent_element, selectors: List[str]):
        """Find element using multiple selector fallbacks."""
        for selector in selectors:
            try:
                return parent_element.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                continue
        return None
        
    def _extract_job_id_from_url(self, url: str) -> str:
        """Extract job ID from Indeed job URL."""
        if not url:
            return f"indeed_{datetime.now(timezone.utc).timestamp()}"
            
        # Indeed job URLs typically contain /viewjob?jk=JOBID
        match = re.search(r'jk=([a-f0-9]+)', url)
        if match:
            return f"indeed_{match.group(1)}"
            
        # Fallback to timestamp-based ID
        return f"indeed_{datetime.now(timezone.utc).timestamp()}"
        
    def _parse_posted_date(self, card_element, selectors: Dict[str, str]) -> Optional[datetime]:
        """Parse the job posted date from card element."""
        date_element = self._find_element_with_fallback(
            card_element,
            [selectors['date_posted'], selectors['date_posted_fallback']]
        )
        
        if not date_element:
            return datetime.now(timezone.utc)
            
        date_text = date_element.text.strip().lower()
        
        try:
            # Parse relative dates like "2 days ago", "1 day ago", "today"
            if 'today' in date_text or 'just posted' in date_text:
                return datetime.now(timezone.utc)
            elif 'yesterday' in date_text:
                return datetime.now(timezone.utc) - timedelta(days=1)
            elif 'day' in date_text:
                # Extract number of days
                match = re.search(r'(\d+)\s*day', date_text)
                if match:
                    days = int(match.group(1))
                    return datetime.now(timezone.utc) - timedelta(days=days)
            elif 'hour' in date_text:
                # Extract number of hours
                match = re.search(r'(\d+)\s*hour', date_text)
                if match:
                    hours = int(match.group(1))
                    return datetime.now(timezone.utc) - timedelta(hours=hours)
                    
        except (ValueError, AttributeError) as e:
            logger.warning(f"Could not parse date '{date_text}': {e}")
            
        return datetime.now(timezone.utc)
        
    async def _handle_pagination(self, params: FetchParams, current_count: int) -> List[JobPosting]:
        """
        Handle pagination to get more jobs.
        
        Args:
            params: Fetch parameters
            current_count: Current number of jobs fetched
            
        Returns:
            Additional jobs from next pages
        """
        additional_jobs = []
        selectors = self.get_selectors()
        
        # Limit pagination to avoid excessive requests
        max_pages = 3
        pages_scraped = 0
        
        while (pages_scraped < max_pages and 
               (params.limit is None or current_count + len(additional_jobs) < params.limit)):
            
            try:
                # Look for next button
                next_button = self._driver.find_element(
                    By.CSS_SELECTOR, 
                    selectors['next_button']
                )
                
                if not next_button or not next_button.is_enabled():
                    break
                    
                # Click next button
                next_button.click()
                
                # Wait for new page to load
                await self._wait_for_page_load()
                
                # Parse jobs from new page
                page_jobs = await self.parse_job_elements(self._driver)
                additional_jobs.extend(page_jobs)
                pages_scraped += 1
                
                logger.info(f"Scraped page {pages_scraped + 1}, got {len(page_jobs)} more jobs")
                
            except NoSuchElementException:
                logger.info("No more pages available")
                break
            except Exception as e:
                logger.error(f"Error during pagination: {e}")
                break
                
        return additional_jobs
        
    def get_supported_params(self) -> Dict[str, Any]:
        """
        Get parameters supported by Indeed scraper.
        
        Returns:
            Dictionary describing supported parameters
        """
        return {
            "keywords": {
                "type": "list",
                "description": "Job search keywords (combined with spaces)",
                "required": False
            },
            "location": {
                "type": "string",
                "description": "Job location (city, state, zip)",
                "required": False
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of jobs to return",
                "default": None
            },
            "date_range": {
                "type": "integer",
                "description": "Not directly used - Indeed defaults to recent jobs",
                "default": 7
            }
        }
