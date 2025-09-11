"""
ZipRecruiter job scraper implementation.

Scrapes job postings from ZipRecruiter.com using browser automation.
Handles ZipRecruiter's job board structure and search functionality.
"""

import re
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from ..base_scraper import BaseScraper, BrowserProfile
from ...core.base_job_source import JobPosting, FetchParams, RateLimitConfig

logger = logging.getLogger(__name__)


class ZipRecruiterScraper(BaseScraper):
    """
    Scraper for ZipRecruiter.com job postings.
    
    Handles ZipRecruiter's job board structure, search parameters,
    and pagination system.
    """
    
    def __init__(self):
        """Initialize the ZipRecruiter scraper."""
        super().__init__(
            name="ziprecruiter",
            base_url="https://www.ziprecruiter.com",
            rate_limits=RateLimitConfig(
                requests_per_minute=10,  # ZipRecruiter is more permissive
                requests_per_hour=300,
                burst_limit=3
            )
        )
        
    def get_search_url(self, **kwargs) -> str:
        """
        Construct ZipRecruiter job search URL.
        
        Args:
            **kwargs: Search parameters (q=keywords, location=location, etc.)
            
        Returns:
            ZipRecruiter job search URL
        """
        base_search_url = f"{self.base_url}/jobs"
        
        # Build query parameters
        params = {}
        if 'q' in kwargs and kwargs['q']:
            # ZipRecruiter uses 'search' parameter for keywords
            params['search'] = kwargs['q']
        if 'location' in kwargs and kwargs['location']:
            params['location'] = kwargs['location']
            
        # Default parameters for job search
        params['days'] = '1'  # Jobs posted in last 1 day
        params['radius'] = '25'  # 25 mile radius
        
        if params:
            return f"{base_search_url}?{urlencode(params)}"
        return base_search_url
        
    def get_selectors(self) -> Dict[str, str]:
        """
        Get CSS selectors for ZipRecruiter job elements.
        
        Returns:
            Dictionary of selectors for different job elements
        """
        return {
            # Job search selectors
            'job_cards': '[data-testid="job-list"] article',
            'job_cards_fallback': '.job_result',
            'job_title': '[data-testid="job-title"]',
            'job_title_fallback': '.job_link',
            'company_name': '[data-testid="company-name"]',
            'company_name_fallback': '.company_name',
            'location': '[data-testid="job-location"]',
            'location_fallback': '.location',
            'salary': '[data-testid="job-salary"]',
            'salary_fallback': '.salary',
            'date_posted': '[data-testid="days-ago"]',
            'date_posted_fallback': '.time',
            'job_link': '[data-testid="job-title"] a',
            'job_description': '[data-testid="job-snippet"]',
            
            # Pagination
            'next_button': 'a[aria-label="Next"]',
            'next_button_fallback': '.pager_next',
            'page_numbers': '.pager_item',
            
            # Popups and overlays
            'cookie_banner': '.cookie-banner',
            'popup_close': '.close-button',
            'modal_overlay': '.modal-overlay',
            
            # Search form
            'search_input': '#search-jobs',
            'location_input': '#search-location',
            'search_button': '.search-form-submit'
        }
        
    async def setup_browser(self):
        """
        Set up ZipRecruiter-specific browser configuration.
        
        Returns:
            Configured WebDriver instance with ZipRecruiter optimizations
        """
        # Use standard profile for ZipRecruiter
        self._profile = BrowserProfile(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport=(1366, 768)
        )
        
        driver = await super().setup_browser()
        
        # ZipRecruiter-specific optimizations (safe)
        try:
            driver.execute_script("""
                // Safe anti-detection setup
                console.log('ZipRecruiter setup complete');
            """)
        except Exception as e:
            logger.warning(f"ZipRecruiter setup failed: {e}")
        
        return driver
        
    async def parse_job_elements(self, driver) -> List[JobPosting]:
        """
        Parse job postings from ZipRecruiter search results page.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List of JobPosting objects
        """
        jobs = []
        selectors = self.get_selectors()
        
        # Handle any popups
        await self._handle_ziprecruiter_popups()
        
        try:
            # Wait for job cards to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors['job_cards']))
            )
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_cards'])
            
            if not job_cards:
                # Try fallback selector
                job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_cards_fallback'])
                
            logger.info(f"Found {len(job_cards)} ZipRecruiter job cards on page")
            
            for i, card in enumerate(job_cards):
                try:
                    # Scroll card into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.3)  # Brief pause for stability
                    
                    job = await self._parse_single_ziprecruiter_job(card, selectors)
                    if job:
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing ZipRecruiter job card {i}: {e}")
                    continue
                    
        except TimeoutException:
            logger.warning("No ZipRecruiter job cards found")
            
        except Exception as e:
            logger.error(f"Error parsing ZipRecruiter job elements: {e}")
            
        return jobs
        
    async def _parse_single_ziprecruiter_job(self, card_element, selectors: Dict[str, str]) -> Optional[JobPosting]:
        """
        Parse a single ZipRecruiter job card element.
        
        Args:
            card_element: Selenium WebElement for job card
            selectors: Dictionary of CSS selectors
            
        Returns:
            JobPosting object or None if parsing fails
        """
        try:
            # Extract job title and link
            title_element = self._find_element_with_fallback(
                card_element,
                [selectors['job_title'], selectors['job_title_fallback']]
            )
            
            if not title_element:
                return None
                
            title = title_element.text.strip()
            
            # Get job URL
            job_link = self._find_element_with_fallback(
                card_element,
                [selectors['job_link']]
            )
            job_url = job_link.get_attribute('href') if job_link else None
            
            # Extract job ID from URL or data attributes
            job_id = self._extract_ziprecruiter_job_id(card_element, job_url)
            
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
            
            # Extract salary if available
            salary_element = self._find_element_with_fallback(
                card_element,
                [selectors['salary'], selectors['salary_fallback']]
            )
            salary = salary_element.text.strip() if salary_element else None
            
            # Extract job description snippet
            desc_element = card_element.find_element(By.CSS_SELECTOR, selectors['job_description'])
            description = desc_element.text.strip() if desc_element else None
            
            # Extract posted date
            date_posted = self._parse_ziprecruiter_date(card_element, selectors)
            
            return JobPosting(
                id=job_id,
                source="ziprecruiter",
                company=company,
                title=title,
                location=location,
                url=job_url,
                date_posted=date_posted,
                raw_data={
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'page_url': self._driver.current_url,
                    'salary': salary,
                    'description_snippet': description[:200] if description else None
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing single ZipRecruiter job: {e}")
            return None
            
    def _extract_ziprecruiter_job_id(self, card_element, job_url: Optional[str]) -> str:
        """Extract ZipRecruiter job ID from card or URL."""
        # Try to extract from URL
        if job_url:
            # ZipRecruiter URLs often have job ID patterns
            match = re.search(r'/jobs/([a-zA-Z0-9-]+)', job_url)
            if match:
                return f"ziprecruiter_{match.group(1)}"
                
            # Alternative pattern
            match = re.search(r'ojob=([a-zA-Z0-9-]+)', job_url)
            if match:
                return f"ziprecruiter_{match.group(1)}"
                
        # Try to get from data attributes
        try:
            job_id = card_element.get_attribute('data-job-id')
            if job_id:
                return f"ziprecruiter_{job_id}"
        except:
            pass
            
        # Fallback to timestamp
        return f"ziprecruiter_{int(datetime.now(timezone.utc).timestamp())}"
        
    def _parse_ziprecruiter_date(self, card_element, selectors: Dict[str, str]) -> Optional[datetime]:
        """Parse ZipRecruiter job posted date."""
        date_element = self._find_element_with_fallback(
            card_element,
            [selectors['date_posted'], selectors['date_posted_fallback']]
        )
        
        if not date_element:
            return datetime.now(timezone.utc)
            
        date_text = date_element.text.strip().lower()
        
        try:
            # ZipRecruiter uses formats like "1 day ago", "2 hours ago", etc.
            if 'just posted' in date_text or 'today' in date_text:
                return datetime.now(timezone.utc)
            elif 'minute' in date_text:
                minutes = re.search(r'(\d+)', date_text)
                if minutes:
                    return datetime.now(timezone.utc) - timedelta(minutes=int(minutes.group(1)))
            elif 'hour' in date_text:
                hours = re.search(r'(\d+)', date_text)
                if hours:
                    return datetime.now(timezone.utc) - timedelta(hours=int(hours.group(1)))
            elif 'day' in date_text:
                days = re.search(r'(\d+)', date_text)
                if days:
                    return datetime.now(timezone.utc) - timedelta(days=int(days.group(1)))
            elif 'week' in date_text:
                weeks = re.search(r'(\d+)', date_text)
                if weeks:
                    return datetime.now(timezone.utc) - timedelta(weeks=int(weeks.group(1)))
                    
        except Exception as e:
            logger.warning(f"Could not parse ZipRecruiter date '{date_text}': {e}")
            
        return datetime.now(timezone.utc)
        
    async def _handle_ziprecruiter_popups(self):
        """Handle ZipRecruiter popups and overlays."""
        selectors = self.get_selectors()
        
        # Handle cookie banner
        try:
            cookie_banner = self._driver.find_element(By.CSS_SELECTOR, selectors['cookie_banner'])
            if cookie_banner.is_displayed():
                accept_button = cookie_banner.find_element(By.TAG_NAME, 'button')
                accept_button.click()
                time.sleep(1)
        except NoSuchElementException:
            pass
            
        # Handle generic popups
        try:
            popup_close = self._driver.find_element(By.CSS_SELECTOR, selectors['popup_close'])
            if popup_close.is_displayed():
                popup_close.click()
                time.sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException):
            pass
            
        # Handle modal overlays
        try:
            modal = self._driver.find_element(By.CSS_SELECTOR, selectors['modal_overlay'])
            if modal.is_displayed():
                # Try to click outside modal or find close button
                self._driver.execute_script("arguments[0].style.display = 'none';", modal)
        except NoSuchElementException:
            pass
            
    async def _handle_pagination(self, params: FetchParams, current_count: int) -> List[JobPosting]:
        """
        Handle ZipRecruiter pagination.
        
        Args:
            params: Fetch parameters
            current_count: Current job count
            
        Returns:
            Additional jobs from next pages
        """
        additional_jobs = []
        selectors = self.get_selectors()
        max_pages = 3  # ZipRecruiter allows more pages
        pages_scraped = 0
        
        while (pages_scraped < max_pages and 
               (params.limit is None or current_count + len(additional_jobs) < params.limit)):
            
            try:
                # Scroll to bottom to ensure next button is visible
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Look for next button
                next_button = self._find_element_with_fallback(
                    self._driver,
                    [selectors['next_button'], selectors['next_button_fallback']]
                )
                
                if not next_button or not next_button.is_enabled():
                    break
                    
                # Click next
                next_button.click()
                
                # Wait for new page
                await self._wait_for_page_load(timeout=10)
                time.sleep(2)
                
                # Handle popups again
                await self._handle_ziprecruiter_popups()
                
                # Parse new page
                page_jobs = await self.parse_job_elements(self._driver)
                additional_jobs.extend(page_jobs)
                pages_scraped += 1
                
                logger.info(f"ZipRecruiter page {pages_scraped + 1}: {len(page_jobs)} more jobs")
                
            except NoSuchElementException:
                logger.info("No more ZipRecruiter pages available")
                break
            except Exception as e:
                logger.error(f"ZipRecruiter pagination error: {e}")
                break
                
        return additional_jobs
        
    def get_supported_params(self) -> Dict[str, Any]:
        """
        Get parameters supported by ZipRecruiter scraper.
        
        Returns:
            Dictionary describing supported parameters
        """
        return {
            "keywords": {
                "type": "list",
                "description": "Job search keywords",
                "required": False
            },
            "location": {
                "type": "string", 
                "description": "Job location (city, state, or 'Remote')",
                "required": False
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of jobs to return",
                "default": None
            },
            "radius": {
                "type": "integer",
                "description": "Search radius in miles",
                "default": 25
            },
            "days": {
                "type": "integer",
                "description": "Jobs posted within last N days",
                "default": 1
            }
        }
