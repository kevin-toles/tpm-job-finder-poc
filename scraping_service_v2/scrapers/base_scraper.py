"""
Base scraper class for browser-based job sources.

Provides common functionality for sources that scrape jobs using browser automation
with Selenium or Playwright.
"""

from abc import abstractmethod
from typing import Dict, Any, Optional, List, Union
import asyncio
import logging
from datetime import datetime, timezone
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

from ..core.base_job_source import (
    BaseJobSource,
    SourceType,
    JobPosting,
    FetchParams,
    HealthCheckResult,
    HealthStatus,
    RateLimitConfig,
    SourceUnavailableError,
    RateLimitError
)

logger = logging.getLogger(__name__)


class BrowserProfile:
    """Browser fingerprint profile for anti-detection."""
    
    def __init__(self, user_agent: str, viewport: tuple = (1920, 1080)):
        self.user_agent = user_agent
        self.viewport_width, self.viewport_height = viewport
        
    @classmethod
    def random_profile(cls) -> 'BrowserProfile':
        """Generate a random realistic browser profile."""
        profiles = [
            cls("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", (1440, 900)),
            cls("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", (1920, 1080)),
            cls("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", (1920, 1080)),
        ]
        import random
        return random.choice(profiles)


class BaseScraper(BaseJobSource):
    """
    Base class for browser-based job scrapers.
    
    Provides common functionality for web scraping including browser management,
    anti-detection measures, and element interaction utilities.
    """
    
    def __init__(self, name: str, base_url: str, rate_limits: Optional[RateLimitConfig] = None):
        """
        Initialize the scraper.
        
        Args:
            name: Name of the scraper
            base_url: Base URL of the job site
            rate_limits: Rate limiting configuration
        """
        super().__init__(name, SourceType.BROWSER_SCRAPER)
        self.base_url = base_url.rstrip('/')
        self._rate_limits = rate_limits or RateLimitConfig(
            requests_per_minute=10,  # Conservative for browser scraping
            requests_per_hour=300
        )
        self._driver: Optional[webdriver.Chrome] = None
        self._profile = BrowserProfile.random_profile()
        self._last_request_time: Optional[datetime] = None
        
    @abstractmethod
    def get_search_url(self, **kwargs) -> str:
        """
        Construct the search URL for job queries.
        
        Args:
            **kwargs: Search parameters (keywords, location, etc.)
            
        Returns:
            URL for job search
        """
        pass
        
    @abstractmethod
    def get_selectors(self) -> Dict[str, str]:
        """
        Get CSS selectors for job elements.
        
        Returns:
            Dictionary mapping element names to CSS selectors
        """
        pass
        
    @abstractmethod
    async def parse_job_elements(self, driver: webdriver.Chrome) -> List[JobPosting]:
        """
        Parse job postings from the current page.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            List of parsed job postings
        """
        pass
        
    async def setup_browser(self) -> webdriver.Chrome:
        """
        Set up and configure the browser instance.
        
        Returns:
            Configured WebDriver instance
        """
        options = Options()
        
        # Anti-detection measures
        options.add_argument(f"--user-agent={self._profile.user_agent}")
        options.add_argument(f"--window-size={self._profile.viewport_width},{self._profile.viewport_height}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Performance optimizations
        options.add_argument("--disable-images")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-extensions")
        
        # Headless mode (can be disabled for debugging)
        options.add_argument("--headless")
        
        # Use webdriver-manager for automatic driver management
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Execute script to remove webdriver property
        # Execute JavaScript for anti-detection (safely)
        try:
            driver.execute_script("""
                // Remove webdriver traces (check if property exists first)
                if (navigator.webdriver !== undefined) {
                    try {
                        delete navigator.webdriver;
                    } catch(e) {
                        // Property might be non-configurable, skip
                        console.log('Could not delete webdriver property:', e);
                    }
                }
            """)
        except Exception as e:
            logger.warning(f"Could not execute anti-detection script: {e}")
        
        return driver
        
    async def initialize(self) -> bool:
        """
        Initialize the scraper including browser setup.
        
        Returns:
            True if initialization was successful
        """
        try:
            self._driver = await self.setup_browser()
            logger.info(f"Successfully initialized scraper: {self.name}")
            return True
        except Exception as e:
            logger.error(f"Error initializing scraper {self.name}: {e}")
            return False
            
    async def cleanup(self) -> None:
        """Clean up resources including browser instance."""
        if self._driver:
            try:
                self._driver.quit()
            except Exception as e:
                logger.warning(f"Error closing browser for {self.name}: {e}")
            self._driver = None
            
    async def health_check(self) -> HealthCheckResult:
        """
        Perform a health check by visiting the base URL.
        
        Returns:
            HealthCheckResult with current site status
        """
        start_time = datetime.now(timezone.utc)
        
        if not self._driver:
            await self.initialize()
            
        try:
            # Navigate to base URL and check if it loads
            self._driver.get(self.base_url)
            
            # Wait for page to load
            WebDriverWait(self._driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            # Check if we got blocked or redirected to CAPTCHA
            current_url = self._driver.current_url
            page_source = self._driver.page_source.lower()
            
            if "captcha" in page_source or "robot" in page_source:
                return HealthCheckResult(
                    status=HealthStatus.DEGRADED,
                    message="CAPTCHA or bot detection detected",
                    timestamp=end_time,
                    response_time_ms=response_time
                )
            elif "blocked" in page_source or "access denied" in page_source:
                return HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message="Access blocked by site",
                    timestamp=end_time,
                    response_time_ms=response_time
                )
            else:
                return HealthCheckResult(
                    status=HealthStatus.HEALTHY,
                    message="Site is accessible and loading normally",
                    timestamp=end_time,
                    response_time_ms=response_time
                )
                
        except TimeoutException:
            end_time = datetime.now(timezone.utc)
            return HealthCheckResult(
                status=HealthStatus.DEGRADED,
                message="Page load timeout",
                timestamp=end_time,
                response_time_ms=-1
            )
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            return HealthCheckResult(
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=end_time,
                response_time_ms=-1
            )
            
    def get_rate_limits(self) -> RateLimitConfig:
        """Get the rate limiting configuration."""
        return self._rate_limits
        
    async def fetch_jobs(self, params: FetchParams) -> List[JobPosting]:
        """
        Fetch jobs using browser automation.
        
        Args:
            params: Parameters for job fetching
            
        Returns:
            List of JobPosting objects
        """
        jobs = []
        
        if not self._driver:
            await self.initialize()
            
        try:
            # Apply rate limiting
            await self._apply_rate_limiting()
            
            # Construct search URL
            search_url = self._build_search_url(params)
            
            # Navigate to search page
            logger.info(f"Navigating to: {search_url}")
            self._driver.get(search_url)
            
            # Wait for page to load
            await self._wait_for_page_load()
            
            # Handle any popups or cookie banners
            await self._handle_popups()
            
            # Parse jobs from current page
            page_jobs = await self.parse_job_elements(self._driver)
            jobs.extend(page_jobs)
            
            # Handle pagination if needed and limit not reached
            if params.limit is None or len(jobs) < params.limit:
                jobs.extend(await self._handle_pagination(params, len(jobs)))
                
            # Apply limit if specified
            if params.limit and len(jobs) > params.limit:
                jobs = jobs[:params.limit]
                
            self._last_request_time = datetime.now(timezone.utc)
            logger.info(f"Successfully scraped {len(jobs)} jobs from {self.name}")
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error scraping jobs from {self.name}: {e}")
            raise SourceUnavailableError(f"Scraping failed: {str(e)}")
            
    def _build_search_url(self, params: FetchParams) -> str:
        """Build search URL from parameters."""
        search_params = {}
        
        if params.keywords:
            search_params['q'] = ' '.join(params.keywords)
        if params.location:
            search_params['l'] = params.location
            
        return self.get_search_url(**search_params)
        
    async def _wait_for_page_load(self, timeout: int = 15) -> None:
        """Wait for page to fully load."""
        try:
            WebDriverWait(self._driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            # Additional wait for dynamic content
            await asyncio.sleep(2)
        except TimeoutException:
            logger.warning(f"Page load timeout for {self.name}")
            
    async def _handle_popups(self) -> None:
        """Handle common popups and cookie banners."""
        # Common selectors for cookie acceptance buttons
        cookie_selectors = [
            "[data-testid='cookie-accept']",
            "#onetrust-accept-btn-handler",
            ".cookie-accept",
            "[aria-label*='Accept']",
            "button[id*='accept']"
        ]
        
        for selector in cookie_selectors:
            try:
                element = self._driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    element.click()
                    await asyncio.sleep(1)
                    break
            except NoSuchElementException:
                continue
                
    async def _handle_pagination(self, params: FetchParams, current_count: int) -> List[JobPosting]:
        """Handle pagination to get more jobs."""
        # Default implementation - override in specific scrapers
        return []
        
    async def _apply_rate_limiting(self) -> None:
        """Apply rate limiting between requests."""
        if self._last_request_time:
            min_interval = 60.0 / self._rate_limits.requests_per_minute
            elapsed = (datetime.now(timezone.utc) - self._last_request_time).total_seconds()
            
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)
                
    def _find_element_with_fallback(self, parent_element, selectors: List[str]):
        """Find element using multiple selector fallbacks."""
        for selector in selectors:
            try:
                return parent_element.find_element(By.CSS_SELECTOR, selector)
            except NoSuchElementException:
                continue
        return None
                
    def get_supported_params(self) -> Dict[str, Any]:
        """
        Get the parameters supported by browser scrapers.
        
        Returns:
            Dictionary describing supported parameters
        """
        return {
            "keywords": {"type": "list", "description": "Job search keywords"},
            "location": {"type": "string", "description": "Job location"},
            "date_range": {"type": "integer", "description": "Days to look back for jobs"},
            "limit": {"type": "integer", "description": "Maximum number of jobs to return"}
        }
