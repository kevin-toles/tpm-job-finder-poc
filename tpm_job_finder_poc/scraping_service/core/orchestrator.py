"""
Orchestrator for coordinating job fetching across multiple sources.

Manages the workflow of fetching jobs from multiple sources, handling
failures, deduplication, and aggregation of results.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set
from concurrent.futures import as_completed
from collections import defaultdict

from .base_job_source import (
    BaseJobSource, 
    FetchParams, 
    JobPosting, 
    HealthStatus,
    SourceUnavailableError,
    AuthenticationError,
    RateLimitError
)
from .service_registry import ServiceRegistry

logger = logging.getLogger(__name__)


class ScrapingOrchestrator:
    """
    Orchestrates job fetching across multiple sources.
    
    Handles parallel fetching, error handling, result aggregation,
    and basic deduplication of job postings.
    """
    
    def __init__(self, registry: ServiceRegistry, max_concurrent: int = 10):
        """
        Initialize the orchestrator.
        
        Args:
            registry: Service registry containing job sources
            max_concurrent: Maximum number of concurrent fetch operations
        """
        self.registry = registry
        self.max_concurrent = max_concurrent
        self._semaphore = asyncio.Semaphore(max_concurrent)
        
    async def fetch_all_sources(
        self, 
        params: FetchParams, 
        source_names: Optional[List[str]] = None,
        include_unhealthy: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch jobs from all or specified sources.
        
        Args:
            params: Parameters for the job fetch operation
            source_names: Optional list of specific sources to use
            include_unhealthy: Whether to include sources with unhealthy status
            
        Returns:
            Dictionary containing aggregated results and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        # Determine which sources to use
        if source_names:
            sources = [self.registry.get_source(name) for name in source_names]
            sources = [s for s in sources if s is not None]
        else:
            # Get all enabled sources
            enabled_source_names = self.registry.list_sources(enabled_only=True)
            sources = [self.registry.get_source(name) for name in enabled_source_names]
            
        # Filter by health status if requested
        if not include_unhealthy:
            healthy_sources = []
            for source in sources:
                health_status = self.registry.get_health_status(source.name)
                if health_status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED, HealthStatus.UNKNOWN]:
                    healthy_sources.append(source)
                else:
                    logger.warning(f"Skipping unhealthy source: {source.name}")
            sources = healthy_sources
            
        logger.info(f"Fetching jobs from {len(sources)} sources with params: {params}")
        
        # Execute fetches concurrently
        tasks = []
        for source in sources:
            task = asyncio.create_task(self._fetch_from_source(source, params))
            tasks.append(task)
            
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        all_jobs = []
        source_results = {}
        errors = {}
        
        for i, result in enumerate(results):
            source = sources[i]
            
            if isinstance(result, Exception):
                error_msg = str(result)
                logger.error(f"Error fetching from {source.name}: {error_msg}")
                errors[source.name] = error_msg
                source_results[source.name] = {
                    "jobs": [],
                    "count": 0,
                    "error": error_msg
                }
            else:
                jobs = result if result else []
                all_jobs.extend(jobs)
                source_results[source.name] = {
                    "jobs": [job.to_dict() for job in jobs],
                    "count": len(jobs),
                    "error": None
                }
                
        # Basic deduplication
        deduplicated_jobs = self._deduplicate_jobs(all_jobs)
        
        end_time = datetime.now(timezone.utc)
        fetch_duration = (end_time - start_time).total_seconds()
        
        return {
            "jobs": [job.to_dict() for job in deduplicated_jobs],
            "metadata": {
                "total_jobs": len(deduplicated_jobs),
                "raw_jobs": len(all_jobs),
                "duplicates_removed": len(all_jobs) - len(deduplicated_jobs),
                "sources_queried": len(sources),
                "successful_sources": len(sources) - len(errors),
                "failed_sources": len(errors),
                "fetch_start_time": start_time.isoformat(),
                "fetch_end_time": end_time.isoformat(),
                "fetch_duration_seconds": fetch_duration,
                "timestamp": end_time.isoformat(),
                "params": {
                    "keywords": params.keywords,
                    "location": params.location,
                    "company_ids": params.company_ids,
                    "date_range": params.date_range,
                    "limit": params.limit,
                    "offset": params.offset
                }
            },
            "source_results": source_results,
            "errors": errors
        }
        
    async def fetch_from_sources(
        self,
        source_names: List[str],
        params: FetchParams
    ) -> Dict[str, Any]:
        """
        Fetch jobs from specific sources by name.
        
        Args:
            source_names: List of source names to fetch from
            params: Parameters for the job fetch operation
            
        Returns:
            Dictionary containing results and metadata
        """
        return await self.fetch_all_sources(
            params=params,
            source_names=source_names
        )
        
    async def _fetch_from_source(
        self,
        source: BaseJobSource,
        params: FetchParams
    ) -> List[JobPosting]:
        """
        Fetch jobs from a single source with error handling.
        
        Args:
            source: The job source to fetch from
            params: Parameters for the fetch operation
            
        Returns:
            List of job postings from the source
        """
        async with self._semaphore:
            try:
                logger.debug(f"Starting fetch from {source.name}")
                
                jobs = await source.fetch_jobs(params)
                
                logger.info(f"Successfully fetched {len(jobs)} jobs from {source.name}")
                return jobs
                
            except RateLimitError as e:
                logger.warning(f"Rate limit exceeded for {source.name}: {e}")
                if hasattr(e, 'retry_after') and e.retry_after:
                    logger.info(f"Suggested retry after: {e.retry_after} seconds")
                raise
                
            except AuthenticationError as e:
                logger.error(f"Authentication failed for {source.name}: {e}")
                raise
                
            except SourceUnavailableError as e:
                logger.warning(f"Source {source.name} is unavailable: {e}")
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error fetching from {source.name}: {e}")
                raise
                
    def _deduplicate_jobs(self, jobs: List[JobPosting]) -> List[JobPosting]:
        """
        Remove duplicate jobs from the list.
        
        Args:
            jobs: List of job postings to deduplicate
            
        Returns:
            Deduplicated list of job postings
        """
        if not jobs:
            return []
            
        # Simple deduplication based on URL and title+company
        seen_urls: Set[str] = set()
        seen_combinations: Set[str] = set()
        deduplicated = []
        
        for job in jobs:
            # Check URL-based deduplication first (most reliable)
            if job.url and job.url in seen_urls:
                continue
                
            # Check title+company combination
            combo_key = f"{job.title}|{job.company}".lower()
            if combo_key in seen_combinations:
                continue
                
            # Add to seen sets
            if job.url:
                seen_urls.add(job.url)
            seen_combinations.add(combo_key)
            
            deduplicated.append(job)
            
        logger.info(f"Deduplication: {len(jobs)} -> {len(deduplicated)} jobs")
        return deduplicated
        
    async def health_check_sources(
        self,
        source_names: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Run health checks on sources.
        
        Args:
            source_names: Optional list of specific sources to check
            
        Returns:
            Dictionary mapping source names to health check results
        """
        if source_names:
            sources = [self.registry.get_source(name) for name in source_names]
            sources = [s for s in sources if s is not None]
        else:
            source_names = self.registry.list_sources()
            sources = [self.registry.get_source(name) for name in source_names]
            
        results = {}
        
        for source in sources:
            try:
                start_time = datetime.now(timezone.utc)
                health_result = await source.health_check()
                end_time = datetime.now(timezone.utc)
                
                results[source.name] = {
                    "status": health_result.status.value,
                    "message": health_result.message,
                    "response_time_ms": health_result.response_time_ms,
                    "timestamp": health_result.timestamp.isoformat(),
                    "details": health_result.details,
                    "check_duration_ms": (end_time - start_time).total_seconds() * 1000
                }
                
            except Exception as e:
                logger.error(f"Health check failed for {source.name}: {e}")
                results[source.name] = {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"Health check failed: {str(e)}",
                    "response_time_ms": -1,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "details": None,
                    "check_duration_ms": -1
                }
                
        return results
        
    async def get_source_capabilities(self) -> Dict[str, Any]:
        """
        Get capabilities and supported parameters for all sources.
        
        Returns:
            Dictionary mapping source names to their capabilities
        """
        source_names = self.registry.list_sources()
        capabilities = {}
        
        for name in source_names:
            source = self.registry.get_source(name)
            if source:
                try:
                    capabilities[name] = {
                        "type": source.source_type.value,
                        "enabled": source.is_enabled(),
                        "supported_params": source.get_supported_params(),
                        "rate_limits": source.get_rate_limits().__dict__,
                        "health_status": self.registry.get_health_status(name).value if self.registry.get_health_status(name) else "unknown"
                    }
                except Exception as e:
                    logger.error(f"Error getting capabilities for {name}: {e}")
                    capabilities[name] = {
                        "type": source.source_type.value,
                        "enabled": source.is_enabled(), 
                        "error": str(e)
                    }
                    
        return capabilities
        
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the orchestrator.
        
        Returns:
            Dictionary with orchestrator statistics
        """
        registry_stats = self.registry.get_registry_stats()
        
        return {
            "max_concurrent": self.max_concurrent,
            "registry_stats": registry_stats,
            "semaphore_available": self._semaphore._value,
            "semaphore_locked": self.max_concurrent - self._semaphore._value
        }
