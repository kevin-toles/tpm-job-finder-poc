"""
LinkedIn job scraper implementation.

Scrapes job postings from LinkedIn.com using browser automation.
Handles authentication requirements and LinkedIn's anti-bot measures.
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


class LinkedInScraper(BaseScraper):
    """
    Scraper for LinkedIn.com job postings.
    
    Handles LinkedIn's authentication requirements, complex DOM structure,
    and aggressive anti-bot measures.
    """
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the LinkedIn scraper.
        
        Args:
            email: LinkedIn login email (optional for guest browsing)
            password: LinkedIn login password (optional for guest browsing)
        """
        super().__init__(
            name="linkedin",
            base_url="https://www.linkedin.com",
            rate_limits=RateLimitConfig(
                requests_per_minute=5,  # Very conservative due to LinkedIn's strict limits
                requests_per_hour=100,
                burst_limit=2
            )
        )
        self.email = email
        self.password = password
        self.authenticated = False
        
    def get_search_url(self, **kwargs) -> str:
        """
        Construct LinkedIn job search URL.
        
        Args:
            **kwargs: Search parameters (q=keywords, location=location, etc.)
            
        Returns:
            LinkedIn job search URL
        """
        base_search_url = f"{self.base_url}/jobs/search"
        
        # Build query parameters
        params = {}
        if 'q' in kwargs and kwargs['q']:
            params['keywords'] = kwargs['q']
        if 'location' in kwargs and kwargs['location']:
            params['location'] = kwargs['location']
            
        # Default parameters for job search
        params['f_TPR'] = 'r86400'  # Past 24 hours (LinkedIn time filter)
        params['f_JT'] = 'F'  # Full-time jobs
        params['sortBy'] = 'DD'  # Sort by date posted (most recent)
        
        if params:
            return f"{base_search_url}?{urlencode(params)}"
        return base_search_url
        
    def get_selectors(self) -> Dict[str, str]:
        """
        Get CSS selectors for LinkedIn job elements.
        
        Returns:
            Dictionary of selectors for different job elements
        """
        return {
            # Authentication selectors
            'email_field': '#username',
            'password_field': '#password',
            'login_button': '[data-litms-control-urn="login-submit"]',
            
            # Job search selectors
            'job_cards': '[data-entity-urn*="urn:li:fsd_jobPosting"]',
            'job_cards_fallback': '.job-card-container',
            'job_title': '.job-card-list__title',
            'job_title_fallback': '[data-control-name="job_card_click"]',
            'company_name': '.job-card-container__company-name',
            'company_name_fallback': '[data-control-name="company_link"]',
            'location': '.job-card-container__metadata-item',
            'location_fallback': '.job-result-card__location',
            'date_posted': '.job-card-container__listed-status',
            'date_posted_fallback': 'time',
            'job_link': '[data-control-name="job_card_click"]',
            
            # Pagination
            'next_button': '[aria-label="View next page"]',
            'page_numbers': '.artdeco-pagination__indicator',
            
            # Popups and overlays
            'guest_overlay': '.guest-sign-up-modal',
            'auth_wall': '[data-test-modal="sign-up-modal"]',
            'cookie_banner': '.artdeco-global-alert-banner',
            'close_button': '[data-test-icon="close-medium"]'
        }
        
    async def setup_browser(self):
        """
        Set up LinkedIn-specific browser configuration.
        
        Returns:
            Configured WebDriver instance with LinkedIn optimizations
        """
        # Use specialized profile for LinkedIn
        self._profile = BrowserProfile(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport=(1440, 900)
        )
        
        driver = await super().setup_browser()
        
        # LinkedIn-specific settings (safe anti-detection)
        try:
            driver.execute_script("""
                // Safe anti-detection - don't redefine existing properties
                console.log('LinkedIn anti-detection setup');
            """)
        except Exception as e:
            logger.warning(f"LinkedIn anti-detection setup failed: {e}")
        
        return driver
        
    async def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn if credentials are provided.
        
        Returns:
            True if authentication successful or not required
        """
        if not self.email or not self.password:
            logger.info("No LinkedIn credentials provided, using guest mode")
            return True
            
        if self.authenticated:
            return True
            
        try:
            # Navigate to login page
            self._driver.get(f"{self.base_url}/login")
            await self._wait_for_page_load()
            
            selectors = self.get_selectors()
            
            # Wait for login form
            WebDriverWait(self._driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors['email_field']))
            )
            
            # Enter credentials
            email_field = self._driver.find_element(By.CSS_SELECTOR, selectors['email_field'])
            email_field.clear()
            email_field.send_keys(self.email)
            
            password_field = self._driver.find_element(By.CSS_SELECTOR, selectors['password_field'])
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Submit login
            login_button = self._driver.find_element(By.CSS_SELECTOR, selectors['login_button'])
            login_button.click()
            
            # Wait for redirect after login
            await self._wait_for_page_load(timeout=15)
            
            # Check if we're logged in (look for profile elements)
            if 'feed' in self._driver.current_url or 'mynetwork' in self._driver.current_url:
                self.authenticated = True
                logger.info("LinkedIn authentication successful")
                return True
            else:
                logger.warning("LinkedIn authentication may have failed")
                return False
                
        except Exception as e:
            logger.error(f"LinkedIn authentication error: {e}")
            return False
            
    async def initialize(self) -> bool:
        """
        Initialize LinkedIn scraper with authentication.
        
        Returns:
            True if initialization successful
        """
        success = await super().initialize()
        if not success:
            return False
            
        # Attempt authentication
        return await self.authenticate()
        
    async def parse_job_elements(self, driver) -> List[JobPosting]:
        """
        Parse job postings from LinkedIn search results page.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List of JobPosting objects
        """
        jobs = []
        selectors = self.get_selectors()
        
        # Handle guest mode overlays
        await self._handle_linkedin_overlays()
        
        try:
            # Wait for job cards to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors['job_cards']))
            )
            
            job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_cards'])
            
            if not job_cards:
                # Try fallback selector
                job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_cards_fallback'])
                
            logger.info(f"Found {len(job_cards)} LinkedIn job cards on page")
            
            for i, card in enumerate(job_cards):
                try:
                    # Scroll card into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.5)  # Brief pause for stability
                    
                    job = await self._parse_single_linkedin_job(card, selectors)
                    if job:
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing LinkedIn job card {i}: {e}")
                    continue
                    
        except TimeoutException:
            logger.warning("No LinkedIn job cards found - may be blocked or authentication required")
            
        except Exception as e:
            logger.error(f"Error parsing LinkedIn job elements: {e}")
            
        return jobs
        
    async def _parse_single_linkedin_job(self, card_element, selectors: Dict[str, str]) -> Optional[JobPosting]:
        """
        Parse a single LinkedIn job card element.
        
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
            job_id = self._extract_linkedin_job_id(card_element, job_url)
            
            # Extract company name
            company_element = self._find_element_with_fallback(
                card_element,
                [selectors['company_name'], selectors['company_name_fallback']]
            )
            company = company_element.text.strip() if company_element else "Unknown"
            
            # Extract location
            location_elements = card_element.find_elements(By.CSS_SELECTOR, selectors['location'])
            location = None
            for elem in location_elements:
                text = elem.text.strip()
                # LinkedIn location usually contains city/state
                if any(indicator in text.lower() for indicator in [',', 'remote', 'hybrid', 'on-site']):
                    location = text
                    break
                    
            # Extract posted date
            date_posted = self._parse_linkedin_date(card_element, selectors)
            
            return JobPosting(
                id=job_id,
                source="linkedin",
                company=company,
                title=title,
                location=location,
                url=job_url,
                date_posted=date_posted,
                raw_data={
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'page_url': self._driver.current_url,
                    'authenticated': self.authenticated
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing single LinkedIn job: {e}")
            return None
            
    def _extract_linkedin_job_id(self, card_element, job_url: Optional[str]) -> str:
        """Extract LinkedIn job ID from card or URL."""
        # Try to get from data attribute
        try:
            urn = card_element.get_attribute('data-entity-urn')
            if urn and 'jobPosting:' in urn:
                return f"linkedin_{urn.split('jobPosting:')[1]}"
        except:
            pass
            
        # Try to extract from URL
        if job_url:
            match = re.search(r'/jobs/view/(\d+)', job_url)
            if match:
                return f"linkedin_{match.group(1)}"
                
        # Fallback to timestamp
        return f"linkedin_{int(datetime.now(timezone.utc).timestamp())}"
        
    def _parse_linkedin_date(self, card_element, selectors: Dict[str, str]) -> Optional[datetime]:
        """Parse LinkedIn job posted date."""
        date_element = self._find_element_with_fallback(
            card_element,
            [selectors['date_posted'], selectors['date_posted_fallback']]
        )
        
        if not date_element:
            return datetime.now(timezone.utc)
            
        date_text = date_element.text.strip().lower()
        
        try:
            # LinkedIn uses relative dates
            if 'just now' in date_text or 'promoted' in date_text:
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
            logger.warning(f"Could not parse LinkedIn date '{date_text}': {e}")
            
        return datetime.now(timezone.utc)
        
    async def _handle_linkedin_overlays(self):
        """Handle LinkedIn's guest mode overlays and popups."""
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
            
        # Handle guest signup modal
        try:
            guest_modal = self._driver.find_element(By.CSS_SELECTOR, selectors['guest_overlay'])
            if guest_modal.is_displayed():
                close_button = guest_modal.find_element(By.CSS_SELECTOR, selectors['close_button'])
                close_button.click()
                time.sleep(1)
        except (NoSuchElementException, ElementClickInterceptedException):
            pass
            
        # Handle auth wall
        try:
            auth_wall = self._driver.find_element(By.CSS_SELECTOR, selectors['auth_wall'])
            if auth_wall.is_displayed():
                # Try to dismiss or navigate around it
                self._driver.execute_script("arguments[0].style.display = 'none';", auth_wall)
        except NoSuchElementException:
            pass
            
    async def _handle_pagination(self, params: FetchParams, current_count: int) -> List[JobPosting]:
        """
        Handle LinkedIn pagination.
        
        Args:
            params: Fetch parameters
            current_count: Current job count
            
        Returns:
            Additional jobs from next pages
        """
        additional_jobs = []
        selectors = self.get_selectors()
        max_pages = 2  # Conservative for LinkedIn
        pages_scraped = 0
        
        while (pages_scraped < max_pages and 
               (params.limit is None or current_count + len(additional_jobs) < params.limit)):
            
            try:
                # Scroll to bottom to load more content
                self._driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Look for next button
                next_button = self._driver.find_element(By.CSS_SELECTOR, selectors['next_button'])
                
                if not next_button or not next_button.is_enabled():
                    break
                    
                # Click next with JavaScript to avoid interception
                self._driver.execute_script("arguments[0].click();", next_button)
                
                # Wait for new page
                await self._wait_for_page_load(timeout=10)
                time.sleep(3)  # Additional wait for LinkedIn
                
                # Handle overlays again
                await self._handle_linkedin_overlays()
                
                # Parse new page
                page_jobs = await self.parse_job_elements(self._driver)
                additional_jobs.extend(page_jobs)
                pages_scraped += 1
                
                logger.info(f"LinkedIn page {pages_scraped + 1}: {len(page_jobs)} more jobs")
                
            except NoSuchElementException:
                logger.info("No more LinkedIn pages available")
                break
            except Exception as e:
                logger.error(f"LinkedIn pagination error: {e}")
                break
                
        return additional_jobs
        
    def get_supported_params(self) -> Dict[str, Any]:
        """
        Get parameters supported by LinkedIn scraper.
        
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
            "authentication": {
                "type": "object",
                "description": "LinkedIn credentials for authenticated access",
                "properties": {
                    "email": {"type": "string"},
                    "password": {"type": "string"}
                },
                "required": False
            }
        }
