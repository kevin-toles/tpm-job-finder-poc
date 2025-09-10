"""Base scraper implementation."""

import aiohttp
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.job import Job
from .config import ScraperConfig
from .rate_limiter import RateLimiter
from .browser_simulator import BrowserSimulator
from .proxy_rotator import ProxyRotator
from .response_cache import ResponseCache

class BaseScraper(ABC):
    """Base class for all job scrapers."""

    def __init__(self, config: ScraperConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter(config.requests_per_minute)
        self.browser_simulator = BrowserSimulator() if config.browser_simulation_enabled else None
        self.proxy_rotator = ProxyRotator() if config.proxy_enabled else None
        self.cache = ResponseCache(config.cache_max_age) if config.cache_enabled else None
        self.retry_count = 0

    async def __aenter__(self):
        """Set up async context."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up async context."""
        if self.session:
            await self.session.close()

    @abstractmethod
    async def fetch_jobs(
        self,
        search_terms: List[str],
        location: Optional[str] = None,
        max_results: int = 10
    ) -> List[Job]:
        """Fetch jobs from the job board."""
        pass

    async def make_request(self, url: str, **kwargs) -> dict:
        """Make HTTP request with rate limiting and retries."""
        await self.rate_limiter.wait()

        headers = self._get_headers()
        if self.browser_simulator:
            headers.update(self.browser_simulator.get_headers())

        if self.proxy_rotator:
            kwargs['proxy'] = self.proxy_rotator.get_proxy()

        if self.cache:
            cached = self.cache.get(url)
            if cached:
                return cached

        for attempt in range(self.config.max_retries + 1):
            try:
                async with self.session.get(url, headers=headers, **kwargs) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if self.cache:
                        self.cache.set(url, data)
                    return data
            except aiohttp.ClientError as e:
                self.retry_count += 1
                if attempt == self.config.max_retries:
                    raise e
                await asyncio.sleep(2 ** attempt)

    def _get_headers(self) -> dict:
        """Get base headers for requests."""
        return {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
        }
