"""Base class for job board scrapers."""

import abc
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple
import logging
import aiohttp
from bs4 import BeautifulSoup
import random
import os
from urllib.parse import urlparse
from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.rate_limiter import RateLimiter
from job_aggregator.scrapers.retry import with_retry
from job_aggregator.scrapers.browser_simulator import BrowserSimulator
from job_aggregator.scrapers.captcha_handler import CaptchaHandler
from job_aggregator.scrapers.response_cache import ResponseCache
from job_aggregator.scrapers.selector_maintainer import SelectorMaintainer
from job_aggregator.scrapers.selector_health import SelectorHealthChecker
from job_aggregator.scrapers.config import JobScraperConfig, ScraperConfig

logger = logging.getLogger(__name__)

class BaseJobScraper(abc.ABC):
    """Base class for all job board scrapers with enhanced features."""
    
    def __init__(
        self, 
        search_terms: List[str], 
        location: Optional[str] = None,
        proxy_list: Optional[List[str]] = None,
        user_agent_list: Optional[List[str]] = None,
        config_file: Optional[str] = None,
        selectors_file: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """Initialize the scraper with enhanced parameters.
        
        Args:
            search_terms: List of job titles/keywords to search for
            location: Optional location filter
            proxy_list: Optional list of proxy servers to use
            requests_per_minute: Maximum requests per minute to any domain
            user_agent_list: Optional list of user agents to rotate through
            cache_dir: Optional directory for response caching
            cache_max_age: Maximum age of cached responses in seconds
            captcha_service_url: Optional CAPTCHA solving service URL
            captcha_api_key: Optional CAPTCHA solving service API key
        """
        # Load configuration
        if not config_file:
            config_file = os.path.join(os.path.dirname(__file__), 'scraper_config.json')
        self.config_manager = JobScraperConfig(config_file)
        
        # Get config for this scraper
        scraper_name = self.__class__.__name__.lower().replace('scraper', '')
        self.config = self.config_manager.get_config(scraper_name)
        
        if not self.config or not self.config.enabled:
            raise ValueError(f"Scraper {scraper_name} is disabled in configuration")
            
        self.search_terms = search_terms
        self.location = location
        self.proxy_list = proxy_list or []
        
        # Initialize browser simulator if enabled
        self.browser = BrowserSimulator() if self.config.browser_simulation_enabled else None
        
        # Initialize response cache if enabled
        if self.config.cache_enabled and cache_dir:
            self.cache = ResponseCache(cache_dir, self.config.cache_max_age)
        else:
            self.cache = None
            
        # Initialize CAPTCHA handler if enabled
        if self.config.captcha_service_enabled:
            self.captcha_handler = CaptchaHandler(
                self.config.captcha_service_url,
                self.config.captcha_api_key
            )
        else:
            self.captcha_handler = None
            
        # Initialize selector maintainer
        if not selectors_file:
            selectors_file = os.path.join(os.path.dirname(__file__), 'selectors.json')
        self.selector_maintainer = SelectorMaintainer(selectors_file)
        self.health_checker = SelectorHealthChecker(self.selector_maintainer)
        self.last_health_check = None
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self._scrape_stats = {
            'requests_made': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'jobs_found': 0,
            'captchas_encountered': 0,
            'captchas_solved': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'start_time': None,
            'end_time': None
        }
    
    async def __aenter__(self):
        """Set up async resources - creates aiohttp session."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        """Clean up async resources."""
        if self.session:
            await self.session.close()
            self.session = None
    
    @abc.abstractmethod
    async def search(self, search_term: str) -> List[JobPosting]:
        """Search for jobs matching the given term.
        
        Args:
            search_term: The job title or keyword to search for
            
        Returns:
            List of normalized JobPosting objects
        """
        pass
    
    @abc.abstractmethod 
    async def get_job_details(self, url: str) -> Optional[str]:
        """Get full job description from job detail page.
        
        Args:
            url: URL of the job posting
            
        Returns:
            Job description text if found, None otherwise
        """
        pass
    
    async def fetch_all_jobs(self) -> List[JobPosting]:
        """Enhanced job fetching with statistics and parallel processing.
        
        Returns:
            Combined list of all jobs found
        """
        # Run health check if needed (every 6 hours)
        await self._check_selector_health()
        
        self._scrape_stats['start_time'] = datetime.now()
        all_jobs = []
        
        # Create tasks for parallel processing of search terms
        tasks = []
        for term in self.search_terms:
            tasks.append(self.search(term))
            
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for term, result in zip(self.search_terms, results):
            if isinstance(result, Exception):
                logger.error(f"Error searching for term '{term}': {str(result)}")
                continue
            all_jobs.extend(result)
            
        # Update stats
        self._scrape_stats['jobs_found'] = len(all_jobs)
        
        # Deduplicate by job URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)
                
        self._scrape_stats['end_time'] = datetime.now()
        duration = (self._scrape_stats['end_time'] - self._scrape_stats['start_time']).total_seconds()
        
        # Log scraping summary
        logger.info(f"Scraping completed in {duration:.2f} seconds:")
        logger.info(f"- Requests made: {self._scrape_stats['requests_made']}")
        logger.info(f"- Successful requests: {self._scrape_stats['successful_requests']}")
        logger.info(f"- Failed requests: {self._scrape_stats['failed_requests']}")
        logger.info(f"- Total jobs found: {self._scrape_stats['jobs_found']}")
        logger.info(f"- Unique jobs: {len(unique_jobs)}")
        
        return unique_jobs
    
    @with_retry(max_retries=3, initial_delay=1.0, max_delay=30.0, logger=logger)
    async def _get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Enhanced helper to fetch and parse a page with advanced features.
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object for the page if successful, None otherwise
            
        Raises:
            aiohttp.ClientError: If request fails after all retries
        """
        if not self.session:
            raise RuntimeError("Scraper must be used as async context manager")
            
        # Check cache first
        if self.cache:
            cached = await self.cache.get(url)
            if cached:
                self._scrape_stats['cache_hits'] += 1
                return BeautifulSoup(cached.content, 'html.parser')
            self._scrape_stats['cache_misses'] += 1
            
        # Get or create rate limiter for this domain
        domain = urlparse(url).netloc
        if domain not in self.rate_limiters:
            self.rate_limiters[domain] = RateLimiter()
            
        # Wait for rate limit
        await self.rate_limiters[domain].acquire(domain)
        
        # Get browser profile and headers
        headers = self.browser.generate_headers()
        proxy = random.choice(self.proxy_list) if self.proxy_list else None
        
        self._scrape_stats['requests_made'] += 1
        
        try:
            async with self.session.get(
                url,
                headers=headers,
                proxy=proxy,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    
                    # Check for CAPTCHA
                    if self.captcha_handler:
                        captcha_solution = await self.captcha_handler.handle_captcha(html, self.session)
                        if captcha_solution:
                            self._scrape_stats['captchas_encountered'] += 1
                            # If we have a solution, submit it and get the real page
                            if 'solution' in captcha_solution:
                                self._scrape_stats['captchas_solved'] += 1
                                # Implementation would depend on the specific CAPTCHA type
                                # and how the site expects the solution
                                pass
                    
                    # Cache successful response
                    if self.cache:
                        await self.cache.set(
                            url,
                            html,
                            dict(resp.headers),
                            resp.status
                        )
                    
                    # Simulate human-like behavior
                    soup = BeautifulSoup(html, 'html.parser')
                    page_height = self._estimate_page_height(soup)
                    scroll_points = await self.browser.simulate_scroll(page_height)
                    
                    # Simulate scrolling
                    for pos, delay in scroll_points:
                        await asyncio.sleep(delay)
                    
                    self._scrape_stats['successful_requests'] += 1
                    return soup
                else:
                    self._scrape_stats['failed_requests'] += 1
                    logger.error(f"Error fetching {url}: Status {resp.status}")
                    return None
        except Exception as e:
            self._scrape_stats['failed_requests'] += 1
            logger.error(f"Error fetching {url}: {str(e)}")
            raise
            
    def _estimate_page_height(self, soup: BeautifulSoup) -> int:
        """Estimate page height based on content.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            Estimated page height in pixels
        """
        # Count all block-level elements
        block_elements = soup.find_all(['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        # Rough estimate: 50 pixels per block element
        return len(block_elements) * 50
    
            
    def _clean_text(self, text: str) -> str:
        """Clean up scraped text.
        
        Args:
            text: Raw text from page
            
        Returns:
            Cleaned text with normalized whitespace
        """
        return " ".join(text.split())
        
    async def _check_selector_health(self):
        """Run periodic health check on selectors."""
        now = datetime.now(timezone.utc)
        
        # Run health check every 6 hours
        if (not self.last_health_check or 
            (now - self.last_health_check) > timedelta(hours=6)):
            
            logger.info("Running selector health check...")
            results = await self.health_checker.check_selectors(self)
            self.last_health_check = now
            
            # Log results
            report = self.health_checker.get_health_report()
            site = self.__class__.__name__.lower().replace('scraper', '')
            
            if site in report:
                for purpose, metrics in report[site].items():
                    success_rate = metrics['success_rate']
                    if success_rate < 80:  # Alert if success rate drops below 80%
                        logger.warning(
                            f"Low selector success rate for {site}/{purpose}: "
                            f"{success_rate:.1f}% ({metrics['total_checks']} checks)"
                        )
                            async def _extract_field(
        self,
        soup: BeautifulSoup,
        site: str,
        purpose: str,
        sample_content: Optional[str] = None
    ) -> Tuple[Optional[str], bool]:
        """Extract a field from the page using maintained selectors.
        
        Args:
            soup: BeautifulSoup object of the page
            site: Website identifier
            purpose: Purpose of the selector (e.g., 'job_title')
            sample_content: Optional sample content to help repair selectors
            
        Returns:
            Tuple of (extracted text or None, whether extraction succeeded)
        """
        selector = self.selector_maintainer.get_selector(site, purpose)
        if not selector:
            return None, False
            
        element = soup.select_one(selector)
        if element:
            text = self._clean_text(element.get_text())
            if text:
                self.selector_maintainer.report_success(site, purpose)
                return text, True
                
        # If extraction failed, try to repair the selector
        self.selector_maintainer.report_failure(site, purpose)
        html = str(soup)
        new_selector = await self.selector_maintainer.repair_selector(
            site,
            purpose,
            html,
            sample_content
        )
        
        if new_selector:
            # Try the new selector
            element = soup.select_one(new_selector)
            if element:
                text = self._clean_text(element.get_text())
                if text:
                    return text, True
                    
        return None, False
            