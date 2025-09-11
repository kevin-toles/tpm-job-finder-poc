"""
Greenhouse job scraper implementation.

Scrapes job postings from Greenhouse.io-powered company job boards.
Handles dynamic company discovery and various Greenhouse board layouts.
"""

import re
import time
import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode, quote, urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from ..base_scraper import BaseScraper, BrowserProfile
from ...core.base_job_source import JobPosting, FetchParams, RateLimitConfig

logger = logging.getLogger(__name__)


class GreenhouseScraper(BaseScraper):
    """
    Scraper for Greenhouse.io-powered company job boards.
    
    Handles job boards hosted on [company].greenhouse.io or custom domains
    using Greenhouse's job board system.
    """
    
    def __init__(self):
        """Initialize the Greenhouse scraper."""
        super().__init__(
            name="greenhouse",
            base_url="https://greenhouse.io",
            rate_limits=RateLimitConfig(
                requests_per_minute=15,  # Conservative for company boards
                requests_per_hour=400,
                burst_limit=5
            )
        )
        self.known_companies = self._get_default_greenhouse_companies()
        
    def _get_default_greenhouse_companies(self) -> Set[str]:
        """
        Get a default list of known companies using Greenhouse.
        
        Returns:
            Set of company identifiers/subdomains
        """
        return {
            # Tech companies known to use Greenhouse
            'airbnb', 'stripe', 'gitlab', 'dropbox', 'shopify', 'twilio', 
            'coinbase', 'palantir', 'snowflake', 'databricks', 'figma',
            'canva', 'notion', 'airtable', 'gusto', 'plaid', 'square',
            'doordash', 'instacart', 'lyft', 'pinterest', 'reddit',
            'discord', 'zoom', 'atlassian', 'okta', 'datadog', 'elastic'
        }
        
    def get_search_url(self, **kwargs) -> str:
        """
        Construct Greenhouse job board URL.
        
        Args:
            **kwargs: Search parameters (company=company_slug, department=dept, etc.)
            
        Returns:
            Greenhouse job board URL
        """
        company = kwargs.get('company')
        if not company:
            # If no specific company, we'll use a discovery approach
            return f"{self.base_url}/companies"
            
        # Build company job board URL
        if company.endswith('.greenhouse.io'):
            base_url = f"https://{company}/jobs"
        elif '.' in company:
            # Custom domain (e.g., jobs.company.com)
            base_url = f"https://{company}/jobs"
        else:
            # Greenhouse subdomain
            base_url = f"https://{company}.greenhouse.io/jobs"
            
        # Add query parameters
        params = {}
        if 'department' in kwargs and kwargs['department']:
            params['department_id[]'] = kwargs['department']
        if 'location' in kwargs and kwargs['location']:
            params['location[]'] = kwargs['location']
        if 'q' in kwargs and kwargs['q']:
            params['search'] = kwargs['q']
            
        if params:
            return f"{base_url}?{urlencode(params, doseq=True)}"
        return base_url
        
    def get_selectors(self) -> Dict[str, str]:
        """
        Get CSS selectors for Greenhouse job elements.
        
        Returns:
            Dictionary of selectors for different job elements
        """
        return {
            # Job search selectors (Greenhouse boards have consistent structure)
            'job_cards': '.opening',
            'job_cards_fallback': '[data-mapped="true"]',
            'job_title': '.opening a',
            'job_title_fallback': '.job-title',
            'department': '.department',
            'department_fallback': '.opening-department',
            'location': '.location',
            'location_fallback': '.opening-location',
            'job_link': '.opening a',
            'job_link_fallback': 'a[href*="/jobs/"]',
            
            # Company discovery selectors
            'company_links': 'a[href*="greenhouse.io"]',
            'company_names': '.company-name',
            
            # Pagination and loading
            'load_more_button': '.load-more',
            'pagination_next': '.next',
            
            # Content areas
            'job_description': '.job-post-content',
            'job_requirements': '.requirements',
            
            # Filters
            'department_filter': 'select[name="department"]',
            'location_filter': 'select[name="location"]'
        }
        
    async def setup_browser(self):
        """
        Set up Greenhouse-specific browser configuration.
        
        Returns:
            Configured WebDriver instance with Greenhouse optimizations
        """
        # Use standard profile for Greenhouse boards
        self._profile = BrowserProfile(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport=(1280, 800)
        )
        
        driver = await super().setup_browser()
        
        # Greenhouse-specific optimizations (safe)
        try:
            driver.execute_script("""
                // Safe anti-detection setup
                console.log('Greenhouse setup complete');
            """)
        except Exception as e:
            logger.warning(f"Greenhouse setup failed: {e}")
        
        return driver
        
    async def fetch_jobs(self, params: FetchParams) -> List[JobPosting]:
        """
        Fetch jobs from Greenhouse boards.
        
        If no specific company is provided, will attempt discovery across
        multiple known companies using Greenhouse.
        
        Args:
            params: Fetch parameters
            
        Returns:
            List of JobPosting objects
        """
        if not await self.initialize():
            return []
            
        company = params.extra_params.get('company') if params.extra_params else None
        
        if company:
            # Scrape specific company
            return await self._scrape_company_board(company, params)
        else:
            # Discovery mode - scrape multiple companies
            return await self._scrape_multiple_companies(params)
            
    async def _scrape_company_board(self, company: str, params: FetchParams) -> List[JobPosting]:
        """Scrape a specific company's Greenhouse board."""
        try:
            # Build search URL for company
            search_params = {
                'company': company,
                'q': ' '.join(params.keywords) if params.keywords else None,
                'location': params.location
            }
            search_url = self.get_search_url(**search_params)
            
            logger.info(f"Scraping Greenhouse board for {company}: {search_url}")
            
            self._driver.get(search_url)
            await self._wait_for_page_load()
            
            # Parse jobs from this company
            jobs = await self.parse_job_elements(self._driver)
            
            # Handle pagination if needed
            if params.limit is None or len(jobs) < params.limit:
                additional_jobs = await self._handle_pagination(params, len(jobs))
                jobs.extend(additional_jobs)
                
            # Set company name in job data
            for job in jobs:
                if not job.company or job.company == "Unknown":
                    job.company = company.replace('-', ' ').title()
                    
            return jobs[:params.limit] if params.limit else jobs
            
        except Exception as e:
            logger.error(f"Error scraping Greenhouse board for {company}: {e}")
            return []
            
    async def _scrape_multiple_companies(self, params: FetchParams) -> List[JobPosting]:
        """Scrape multiple companies' Greenhouse boards."""
        all_jobs = []
        companies_per_batch = 5
        companies = list(self.known_companies)
        
        # Limit companies if we have a job limit
        if params.limit:
            max_companies = min(10, (params.limit // 5) + 1)
            companies = companies[:max_companies]
        else:
            companies = companies[:companies_per_batch]
            
        logger.info(f"Discovery mode: scraping {len(companies)} Greenhouse companies")
        
        for company in companies:
            try:
                company_jobs = await self._scrape_company_board(company, 
                    FetchParams(
                        keywords=params.keywords,
                        location=params.location,
                        limit=5 if params.limit else None  # Limit per company in discovery mode
                    ))
                    
                all_jobs.extend(company_jobs)
                
                # Check if we've hit overall limit
                if params.limit and len(all_jobs) >= params.limit:
                    break
                    
                # Rate limiting between companies
                time.sleep(2)
                
            except Exception as e:
                logger.warning(f"Error scraping {company}: {e}")
                continue
                
        return all_jobs[:params.limit] if params.limit else all_jobs
        
    async def parse_job_elements(self, driver) -> List[JobPosting]:
        """
        Parse job postings from Greenhouse job board.
        
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
            
            if not job_cards:
                # Try fallback selector
                job_cards = driver.find_elements(By.CSS_SELECTOR, selectors['job_cards_fallback'])
                
            logger.info(f"Found {len(job_cards)} Greenhouse job cards on page")
            
            for i, card in enumerate(job_cards):
                try:
                    # Scroll card into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(0.2)
                    
                    job = await self._parse_single_greenhouse_job(card, selectors)
                    if job:
                        jobs.append(job)
                        
                except Exception as e:
                    logger.warning(f"Error parsing Greenhouse job card {i}: {e}")
                    continue
                    
        except TimeoutException:
            logger.warning("No Greenhouse job cards found - board may be empty or inaccessible")
            
        except Exception as e:
            logger.error(f"Error parsing Greenhouse job elements: {e}")
            
        return jobs
        
    async def _parse_single_greenhouse_job(self, card_element, selectors: Dict[str, str]) -> Optional[JobPosting]:
        """
        Parse a single Greenhouse job card element.
        
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
                [selectors['job_link'], selectors['job_link_fallback']]
            )
            job_url = job_link.get_attribute('href') if job_link else None
            
            # Make URL absolute if relative
            if job_url and job_url.startswith('/'):
                base_url = f"{urlparse(self._driver.current_url).scheme}://{urlparse(self._driver.current_url).netloc}"
                job_url = f"{base_url}{job_url}"
            
            # Extract job ID from URL
            job_id = self._extract_greenhouse_job_id(job_url)
            
            # Extract company name from URL or page
            company = self._extract_company_name()
            
            # Extract department
            department_element = self._find_element_with_fallback(
                card_element,
                [selectors['department'], selectors['department_fallback']]
            )
            department = department_element.text.strip() if department_element else None
            
            # Extract location
            location_element = self._find_element_with_fallback(
                card_element,
                [selectors['location'], selectors['location_fallback']]
            )
            location = location_element.text.strip() if location_element else None
            
            return JobPosting(
                id=job_id,
                source="greenhouse",
                company=company,
                title=title,
                location=location,
                url=job_url,
                date_posted=datetime.now(timezone.utc),  # Greenhouse doesn't always show dates
                raw_data={
                    'scraped_at': datetime.now(timezone.utc).isoformat(),
                    'page_url': self._driver.current_url,
                    'department': department,
                    'greenhouse_board': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing single Greenhouse job: {e}")
            return None
            
    def _extract_greenhouse_job_id(self, job_url: Optional[str]) -> str:
        """Extract Greenhouse job ID from URL."""
        if job_url:
            # Greenhouse URLs typically have /jobs/{id} pattern
            match = re.search(r'/jobs/(\d+)', job_url)
            if match:
                return f"greenhouse_{match.group(1)}"
                
        # Fallback to timestamp
        return f"greenhouse_{int(datetime.now(timezone.utc).timestamp())}"
        
    def _extract_company_name(self) -> str:
        """Extract company name from current page/URL."""
        current_url = self._driver.current_url
        
        # Try to get from subdomain
        match = re.search(r'https://([^.]+)\.greenhouse\.io', current_url)
        if match:
            return match.group(1).replace('-', ' ').title()
            
        # Try to get from page title or content
        try:
            title = self._driver.title
            if 'Jobs at' in title:
                return title.replace('Jobs at ', '').split(' |')[0].strip()
        except:
            pass
            
        return "Unknown"
        
    async def _handle_pagination(self, params: FetchParams, current_count: int) -> List[JobPosting]:
        """
        Handle Greenhouse pagination (load more functionality).
        
        Args:
            params: Fetch parameters
            current_count: Current job count
            
        Returns:
            Additional jobs from pagination
        """
        additional_jobs = []
        selectors = self.get_selectors()
        max_loads = 2  # Conservative for company boards
        loads_completed = 0
        
        while (loads_completed < max_loads and 
               (params.limit is None or current_count + len(additional_jobs) < params.limit)):
            
            try:
                # Look for load more button
                load_more = self._driver.find_element(By.CSS_SELECTOR, selectors['load_more_button'])
                
                if not load_more or not load_more.is_displayed() or not load_more.is_enabled():
                    break
                    
                # Click load more
                self._driver.execute_script("arguments[0].click();", load_more)
                
                # Wait for new content
                time.sleep(3)
                
                # Parse newly loaded jobs
                page_jobs = await self.parse_job_elements(self._driver)
                
                # Filter out duplicates (compare by URL or ID)
                existing_ids = {job.id for job in additional_jobs}
                new_jobs = [job for job in page_jobs if job.id not in existing_ids]
                
                if not new_jobs:
                    break  # No new jobs loaded
                    
                additional_jobs.extend(new_jobs)
                loads_completed += 1
                
                logger.info(f"Greenhouse load more {loads_completed}: {len(new_jobs)} new jobs")
                
            except NoSuchElementException:
                logger.info("No more Greenhouse content to load")
                break
            except Exception as e:
                logger.error(f"Greenhouse pagination error: {e}")
                break
                
        return additional_jobs
        
    def get_supported_params(self) -> Dict[str, Any]:
        """
        Get parameters supported by Greenhouse scraper.
        
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
                "description": "Job location",
                "required": False
            },
            "company": {
                "type": "string",
                "description": "Specific company slug (e.g., 'airbnb', 'stripe')",
                "required": False
            },
            "department": {
                "type": "string",
                "description": "Department filter",
                "required": False
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of jobs to return",
                "default": None
            }
        }
