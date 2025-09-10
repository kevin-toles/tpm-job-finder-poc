"""Caching system for job scraper responses."""

import asyncio
from typing import Optional, Any, Dict
import json
import hashlib
import os
import aiofiles
import time
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
import pickle

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with content and metadata."""
    content: str
    url: str
    timestamp: float
    headers: Dict[str, str]
    status_code: int
    
    def is_expired(self, max_age: int) -> bool:
        """Check if cache entry is expired.
        
        Args:
            max_age: Maximum age in seconds
            
        Returns:
            True if expired, False otherwise
        """
        return time.time() - self.timestamp > max_age

class ResponseCache:
    """Caches HTTP responses for job scrapers."""
    
    def __init__(
        self,
        cache_dir: str = ".cache",
        max_age: int = 3600,  # 1 hour default
        max_size: int = 1000  # Maximum number of entries
    ):
        """Initialize cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_age: Maximum age of cache entries in seconds
            max_size: Maximum number of cache entries
        """
        self.cache_dir = cache_dir
        self.max_age = max_age
        self.max_size = max_size
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_cache_path(self, url: str) -> str:
        """Get filesystem path for cached response.
        
        Args:
            url: URL of the response
            
        Returns:
            Path to cache file
        """
        # Create unique filename from URL
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{url_hash}.cache")
        
    async def get(self, url: str) -> Optional[CacheEntry]:
        """Get cached response if available and not expired.
        
        Args:
            url: URL to retrieve from cache
            
        Returns:
            CacheEntry if found and valid, None otherwise
        """
        cache_path = self._get_cache_path(url)
        try:
            if not os.path.exists(cache_path):
                return None
                
            async with aiofiles.open(cache_path, 'rb') as f:
                entry = pickle.loads(await f.read())
                
            if entry.is_expired(self.max_age):
                await self._remove(cache_path)
                return None
                
            return entry
        except Exception as e:
            logger.error(f"Error reading cache for {url}: {str(e)}")
            return None
            
    async def set(
        self,
        url: str,
        content: str,
        headers: Dict[str, str],
        status_code: int
    ) -> None:
        """Cache a response.
        
        Args:
            url: URL of the response
            content: Response content
            headers: Response headers
            status_code: Response status code
        """
        entry = CacheEntry(
            content=content,
            url=url,
            timestamp=time.time(),
            headers=headers,
            status_code=status_code
        )
        
        cache_path = self._get_cache_path(url)
        
        try:
            async with aiofiles.open(cache_path, 'wb') as f:
                await f.write(pickle.dumps(entry))
                
            # Cleanup old entries if needed
            await self._cleanup()
        except Exception as e:
            logger.error(f"Error caching response for {url}: {str(e)}")
            
    async def _remove(self, cache_path: str):
        """Remove a cache file.
        
        Args:
            cache_path: Path to cache file to remove
        """
        try:
            os.remove(cache_path)
        except Exception as e:
            logger.error(f"Error removing cache file {cache_path}: {str(e)}")
            
    async def _cleanup(self):
        """Remove old cache entries if cache is too large."""
        try:
            cache_files = []
            for filename in os.listdir(self.cache_dir):
                path = os.path.join(self.cache_dir, filename)
                cache_files.append((os.path.getmtime(path), path))
                
            # Sort by modification time
            cache_files.sort()
            
            # Remove oldest files if we have too many
            while len(cache_files) > self.max_size:
                _, path = cache_files.pop(0)
                await self._remove(path)
                
        except Exception as e:
            logger.error(f"Error during cache cleanup: {str(e)}")
            
    async def clear(self):
        """Clear all cached responses."""
        try:
            for filename in os.listdir(self.cache_dir):
                path = os.path.join(self.cache_dir, filename)
                await self._remove(path)
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dict with cache statistics
        """
        try:
            files = os.listdir(self.cache_dir)
            total_size = sum(
                os.path.getsize(os.path.join(self.cache_dir, f))
                for f in files
            )
            
            return {
                'entries': len(files),
                'size_bytes': total_size,
                'max_age': self.max_age,
                'max_size': self.max_size
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {str(e)}")
            return {}
