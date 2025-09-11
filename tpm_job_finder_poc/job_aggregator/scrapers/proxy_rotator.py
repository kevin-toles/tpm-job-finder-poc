"""IP rotation and proxy validation utilities."""

import asyncio
from typing import List, Dict, Optional, Set
import aiohttp
import logging
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

@dataclass
class ProxyStats:
    """Statistics for a proxy server."""
    address: str
    success_count: int = 0
    failure_count: int = 0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    banned_until: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate of the proxy."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def is_banned(self) -> bool:
        """Check if proxy is currently banned."""
        if not self.banned_until:
            return False
        return datetime.now() < self.banned_until
    
    def update_response_time(self, new_time: float):
        """Update average response time with new measurement."""
        if self.avg_response_time == 0.0:
            self.avg_response_time = new_time
        else:
            # Exponential moving average
            alpha = 0.1  # Smoothing factor
            self.avg_response_time = (1 - alpha) * self.avg_response_time + alpha * new_time

class ProxyRotator:
    """Manages and rotates through proxy servers."""
    
    def __init__(
        self,
        proxies: List[str],
        min_success_rate: float = 0.7,
        max_failures: int = 3,
        ban_duration: int = 300  # 5 minutes
    ):
        """Initialize the proxy rotator.
        
        Args:
            proxies: List of proxy URLs
            min_success_rate: Minimum success rate to keep using a proxy
            max_failures: Maximum consecutive failures before temporary ban
            ban_duration: How long to ban failing proxies (seconds)
        """
        self.proxies = {proxy: ProxyStats(proxy) for proxy in proxies}
        self.min_success_rate = min_success_rate
        self.max_failures = max_failures
        self.ban_duration = ban_duration
        self.current_failures: Dict[str, int] = {proxy: 0 for proxy in proxies}
        
    async def validate_proxies(self, test_url: str = "https://api.ipify.org?format=json"):
        """Test all proxies and remove invalid ones.
        
        Args:
            test_url: URL to use for testing proxies
        """
        async def test_proxy(proxy: str) -> bool:
            try:
                start_time = time.time()
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        test_url,
                        proxy=proxy,
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        if resp.status == 200:
                            response_time = time.time() - start_time
                            self.proxies[proxy].update_response_time(response_time)
                            self.proxies[proxy].success_count += 1
                            self.proxies[proxy].last_success = datetime.now()
                            return True
            except Exception as e:
                logger.warning(f"Proxy validation failed for {proxy}: {str(e)}")
                self.proxies[proxy].failure_count += 1
                return False
                
        # Test all proxies concurrently
        tasks = [test_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Remove failed proxies
        for proxy, result in zip(list(self.proxies.keys()), results):
            if not result:
                logger.warning(f"Removing invalid proxy: {proxy}")
                del self.proxies[proxy]
                
    def get_proxy(self) -> Optional[str]:
        """Get the next available proxy.
        
        Returns:
            Proxy URL if available, None otherwise
        """
        now = datetime.now()
        available_proxies = [
            proxy for proxy, stats in self.proxies.items()
            if not stats.is_banned
            and stats.success_rate >= self.min_success_rate
        ]
        
        if not available_proxies:
            logger.warning("No proxies available!")
            return None
            
        # Weight proxies by success rate and response time
        weights = []
        for proxy in available_proxies:
            stats = self.proxies[proxy]
            # Normalize response time (lower is better)
            response_score = 1.0 / (stats.avg_response_time + 1.0)
            # Combine success rate and response score
            weight = stats.success_rate * response_score
            weights.append(weight)
            
        # Normalize weights
        total = sum(weights)
        if total > 0:
            weights = [w/total for w in weights]
            return random.choices(available_proxies, weights=weights, k=1)[0]
        
        return random.choice(available_proxies)
        
    def report_success(self, proxy: str):
        """Report successful use of a proxy."""
        if proxy in self.proxies:
            self.proxies[proxy].success_count += 1
            self.proxies[proxy].last_success = datetime.now()
            self.current_failures[proxy] = 0
            
    def report_failure(self, proxy: str):
        """Report failed use of a proxy."""
        if proxy in self.proxies:
            self.proxies[proxy].failure_count += 1
            self.current_failures[proxy] += 1
            
            # Ban proxy if too many consecutive failures
            if self.current_failures[proxy] >= self.max_failures:
                self.proxies[proxy].banned_until = datetime.now() + timedelta(seconds=self.ban_duration)
                self.current_failures[proxy] = 0
                logger.warning(f"Proxy {proxy} banned until {self.proxies[proxy].banned_until}")
                
    def get_stats(self) -> Dict[str, Dict]:
        """Get statistics for all proxies."""
        return {
            proxy: {
                "success_rate": stats.success_rate,
                "success_count": stats.success_count,
                "failure_count": stats.failure_count,
                "avg_response_time": stats.avg_response_time,
                "banned_until": stats.banned_until.isoformat() if stats.banned_until else None,
                "last_success": stats.last_success.isoformat() if stats.last_success else None
            }
            for proxy, stats in self.proxies.items()
        }
