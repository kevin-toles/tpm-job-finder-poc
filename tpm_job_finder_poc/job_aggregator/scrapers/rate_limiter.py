"""Rate limiting utilities for job scrapers."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional

class RateLimiter:
    """Rate limiter for managing request rates to job boards."""
    
    def __init__(self, requests_per_minute: int = 10):
        """Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests allowed per minute
        """
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute in seconds
        self.requests: Dict[str, list] = {}  # domain -> list of timestamps
        
    async def acquire(self, domain: str):
        """Wait until a request can be made for the given domain.
        
        Args:
            domain: The domain being accessed
        """
        now = datetime.now()
        if domain not in self.requests:
            self.requests[domain] = []
            
        # Remove timestamps older than our window
        window_start = now - timedelta(seconds=self.window_size)
        self.requests[domain] = [
            ts for ts in self.requests[domain]
            if ts > window_start
        ]
        
        # If we're at the limit, wait until the oldest request expires
        while len(self.requests[domain]) >= self.requests_per_minute:
            oldest = self.requests[domain][0]
            expires = oldest + timedelta(seconds=self.window_size)
            wait_time = (expires - now).total_seconds()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            now = datetime.now()
            
        # Add current request
        self.requests[domain].append(now)
