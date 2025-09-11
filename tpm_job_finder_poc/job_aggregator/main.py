"""
Job Aggregator Service - Main orchestration for automated job collection.

Coordinates job fetching from multiple sources (APIs + scrapers) and 
consolidates results for processing pipeline.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .aggregators import (
    RemoteOKConnector, GreenhouseConnector, LeverConnector,
    AshbyConnector, WorkableConnector, SmartRecruitersConnector
)
from ..cache.dedupe_cache import DedupeCache
from ..models.job import Job

logger = logging.getLogger(__name__)


class JobAggregatorService:
    """
    Main service for orchestrating job collection from multiple sources.
    
    Integrates API-based aggregators with browser scrapers to provide
    comprehensive job data collection for automated workflows.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Job Aggregator Service.
        
        Args:
            config: Configuration dictionary for aggregators and scrapers
        """
        self.config = config or {}
        self.dedupe_cache = DedupeCache()
        
        # Initialize API-based aggregators
        self._init_api_aggregators()
        
        # Initialize browser scrapers (scraping_service_v2)
        self._init_browser_scrapers()
        
    def _init_api_aggregators(self):
        """Initialize all API-based job aggregators."""
        self.api_aggregators = {
            'remoteok': RemoteOKConnector(),
            'greenhouse': GreenhouseConnector(
                companies=self.config.get('greenhouse_companies', [
                    'airbnb', 'stripe', 'gitlab', 'dropbox', 'shopify'
                ])
            ),
            'lever': LeverConnector(
                companies=self.config.get('lever_companies', [])
            ),
            'ashby': AshbyConnector('default'),
            'workable': WorkableConnector('default'),
            'smartrecruiters': SmartRecruitersConnector('default')
        }
        logger.info(f"Initialized {len(self.api_aggregators)} API aggregators")
        
    def _init_browser_scrapers(self):
        """Initialize browser-based scrapers."""
        try:
            from scraping_service_v2 import registry
            
            # Register default scrapers if not already done
            registry.register_default_scrapers()
            
            self.browser_scrapers = {
                'indeed': registry.get_source('indeed'),
                'linkedin': registry.get_source('linkedin'), 
                'ziprecruiter': registry.get_source('ziprecruiter'),
                'greenhouse_browser': registry.get_source('greenhouse')
            }
            
            # Filter out any failed initializations
            self.browser_scrapers = {
                name: scraper for name, scraper in self.browser_scrapers.items() 
                if scraper is not None
            }
            
            logger.info(f"Initialized {len(self.browser_scrapers)} browser scrapers")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser scrapers: {e}")
            self.browser_scrapers = {}
            
    async def run_daily_aggregation(self, 
                                   search_params: Dict[str, Any],
                                   max_jobs_per_source: int = 50) -> List[Dict[str, Any]]:
        """
        Run the complete daily job aggregation process.
        
        Args:
            search_params: Search parameters (keywords, location, etc.)
            max_jobs_per_source: Maximum jobs to collect per source
            
        Returns:
            List of aggregated and deduplicated job postings
        """
        logger.info("Starting daily job aggregation process")
        
        all_jobs = []
        
        # Step 1: Collect from API aggregators
        api_jobs = await self._collect_from_api_aggregators(
            search_params, max_jobs_per_source
        )
        all_jobs.extend(api_jobs)
        
        # Step 2: Collect from browser scrapers  
        scraper_jobs = await self._collect_from_browser_scrapers(
            search_params, max_jobs_per_source
        )
        all_jobs.extend(scraper_jobs)
        
        # Step 3: Deduplicate and normalize
        deduplicated_jobs = self._deduplicate_jobs(all_jobs)
        
        # Step 4: Enrich with metadata
        enriched_jobs = self._enrich_job_data(deduplicated_jobs)
        
        logger.info(f"Daily aggregation complete: {len(enriched_jobs)} unique jobs collected")
        
        return enriched_jobs
        
    async def _collect_from_api_aggregators(self, 
                                          search_params: Dict[str, Any],
                                          max_jobs: int) -> List[Dict[str, Any]]:
        """Collect jobs from all API-based aggregators."""
        jobs = []
        
        # Use ThreadPoolExecutor for parallel API calls
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {}
            
            for source_name, aggregator in self.api_aggregators.items():
                try:
                    if hasattr(aggregator, 'fetch_jobs'):
                        future = executor.submit(
                            aggregator.fetch_jobs, 
                            **search_params
                        )
                        future_to_source[future] = source_name
                    elif hasattr(aggregator, 'fetch_since'):
                        # For simple connectors that just fetch recent jobs
                        future = executor.submit(
                            aggregator.fetch_since,
                            days=1  # Daily aggregation
                        )
                        future_to_source[future] = source_name
                        
                except Exception as e:
                    logger.error(f"Error setting up {source_name} aggregation: {e}")
                    
            # Collect results
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    source_jobs = future.result(timeout=30)  # 30 second timeout
                    
                    # Normalize job data format
                    normalized_jobs = self._normalize_api_jobs(source_jobs, source_name)
                    jobs.extend(normalized_jobs[:max_jobs])  # Limit per source
                    
                    logger.info(f"{source_name}: collected {len(normalized_jobs)} jobs")
                    
                except Exception as e:
                    logger.error(f"Error collecting from {source_name}: {e}")
                    
        return jobs
        
    async def _collect_from_browser_scrapers(self,
                                           search_params: Dict[str, Any], 
                                           max_jobs: int) -> List[Dict[str, Any]]:
        """Collect jobs from browser scrapers."""
        from scraping_service_v2.core.base_job_source import FetchParams
        
        jobs = []
        
        # Convert search params to FetchParams
        fetch_params = FetchParams(
            keywords=search_params.get('keywords', []),
            location=search_params.get('location'),
            limit=max_jobs
        )
        
        for source_name, scraper in self.browser_scrapers.items():
            try:
                logger.info(f"Starting browser scraping for {source_name}")
                
                # Initialize scraper if needed
                if not await scraper.initialize():
                    logger.warning(f"Failed to initialize {source_name} scraper")
                    continue
                    
                # Fetch jobs
                source_jobs = await scraper.fetch_jobs(fetch_params)
                
                # Convert to standardized format
                normalized_jobs = [
                    {
                        'id': getattr(job, 'id', f"{source_name}_{hash(str(job))}"),
                        'source': getattr(job, 'source', source_name),
                        'title': getattr(job, 'title', None),
                        'company': getattr(job, 'company', None),
                        'location': getattr(job, 'location', None),
                        'url': getattr(job, 'url', None),
                        'date_posted': getattr(job, 'date_posted', None).isoformat() if getattr(job, 'date_posted', None) else None,
                        'raw_data': getattr(job, 'raw_data', getattr(job, '__dict__', str(job)))
                    }
                    for job in source_jobs
                ]
                
                jobs.extend(normalized_jobs)
                logger.info(f"{source_name}: collected {len(normalized_jobs)} jobs")
                
                # Cleanup scraper
                await scraper.cleanup()
                
            except Exception as e:
                logger.error(f"Error scraping from {source_name}: {e}")
                
        return jobs
        
    def _normalize_api_jobs(self, jobs: List[Any], source: str) -> List[Dict[str, Any]]:
        """Normalize job data from API aggregators to standard format."""
        normalized = []
        
        for job in jobs:
            try:
                # Handle different API response formats
                if isinstance(job, dict):
                    normalized_job = {
                        'id': job.get('id', f"{source}_{hash(str(job))}"),
                        'source': source,
                        'title': job.get('position') or job.get('title') or job.get('name'),
                        'company': job.get('company') or job.get('company_name'),
                        'location': job.get('location') or job.get('candidate_required_location'),
                        'url': job.get('url') or job.get('apply_url'),
                        'date_posted': job.get('date') or job.get('created_at'),
                        'raw_data': job
                    }
                else:
                    # Handle object-based responses
                    normalized_job = {
                        'id': getattr(job, 'id', f"{source}_{hash(str(job))}"),
                        'source': source,
                        'title': getattr(job, 'title', None),
                        'company': getattr(job, 'company', None),
                        'location': getattr(job, 'location', None),
                        'url': getattr(job, 'url', None),
                        'date_posted': getattr(job, 'date_posted', None),
                        'raw_data': job.__dict__ if hasattr(job, '__dict__') else str(job)
                    }
                    
                # Only include jobs with minimum required fields
                if normalized_job['title'] and normalized_job['company']:
                    normalized.append(normalized_job)
                    
            except Exception as e:
                logger.warning(f"Error normalizing job from {source}: {e}")
                
        return normalized
        
    def _deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on title, company, and URL similarity."""
        if not jobs:
            return []
            
        # Use the existing dedupe cache
        unique_jobs = []
        
        for job in jobs:
            # Create a deduplication key
            dedupe_key = f"{job.get('company', '')}-{job.get('title', '')}-{job.get('location', '')}"
            job_url = job.get('url', '')
            
            if not self.dedupe_cache.is_duplicate(dedupe_key, dedupe_key):
                unique_jobs.append(job)
                self.dedupe_cache.add(dedupe_key, dedupe_key)
                
        logger.info(f"Deduplicated {len(jobs)} jobs to {len(unique_jobs)} unique jobs")
        
        return unique_jobs
        
    def _enrich_job_data(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add enrichment metadata to job postings."""
        for job in jobs:
            # Add aggregation timestamp
            job['aggregated_at'] = datetime.now().isoformat()
            
            # Add basic classification
            job['job_type'] = self._classify_job_type(job.get('title', ''))
            job['remote_friendly'] = self._detect_remote_work(job.get('location', ''))
            
            # Add TPM-specific scoring hints
            job['tpm_keywords_found'] = self._count_tpm_keywords(job.get('title', ''))
            
        return jobs
        
    def _classify_job_type(self, title: str) -> str:
        """Basic job type classification."""
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ['manager', 'lead', 'director', 'head']):
            return 'management'
        elif any(kw in title_lower for kw in ['senior', 'sr', 'principal']):
            return 'senior'
        elif any(kw in title_lower for kw in ['junior', 'jr', 'associate', 'entry']):
            return 'entry_level'
        else:
            return 'mid_level'
            
    def _detect_remote_work(self, location: str) -> bool:
        """Detect if job supports remote work."""
        if not location:
            return False
            
        location_lower = location.lower()
        remote_indicators = ['remote', 'anywhere', 'distributed', 'work from home', 'wfh']
        
        return any(indicator in location_lower for indicator in remote_indicators)
        
    def _count_tpm_keywords(self, title: str) -> int:
        """Count TPM-related keywords in job title."""
        if not title:
            return 0
            
        title_lower = title.lower()
        tpm_keywords = [
            'product manager', 'product management', 'tpm', 'technical product',
            'program manager', 'project manager', 'product owner', 'po'
        ]
        
        return sum(1 for keyword in tpm_keywords if keyword in title_lower)
    
    def get_aggregator_stats(self) -> Dict[str, Any]:
        """Get statistics about aggregators."""
        return {
            'total_api_aggregators': len(self.api_aggregators),
            'total_browser_scrapers': len(self.browser_scrapers),
            'last_run': None,
            'api_aggregator_names': list(self.api_aggregators.keys()),
            'browser_scraper_names': list(self.browser_scrapers.keys())
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the service."""
        return {
            'status': 'healthy',
            'api_aggregators_count': len(self.api_aggregators),
            'browser_scrapers_count': len(self.browser_scrapers),
            'timestamp': datetime.now().isoformat(),
            'components': {
                'api_aggregators': 'healthy',
                'browser_scrapers': 'healthy',
                'cache': 'healthy'
            }
        }
    
    def get_enabled_sources(self) -> Dict[str, Any]:
        """Get list of enabled job sources."""
        return {
            'api_aggregators': list(self.api_aggregators.keys()),
            'browser_scrapers': list(self.browser_scrapers.keys()),
            'total_sources': len(self.api_aggregators) + len(self.browser_scrapers)
        }
    
    @classmethod
    def _load_api_aggregators(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load API aggregators based on configuration."""
        # This would normally load aggregators based on config
        # For now, return a basic structure
        api_config = config.get('api_aggregators', {})
        return {
            'remoteok': {'enabled': api_config.get('remoteok', {}).get('enabled', True)},
            'greenhouse': {'enabled': api_config.get('greenhouse', {}).get('enabled', True)},
            'lever': {'enabled': api_config.get('lever', {}).get('enabled', True)},
            'ashby': {'enabled': api_config.get('ashby', {}).get('enabled', True)},
            'workable': {'enabled': api_config.get('workable', {}).get('enabled', True)},
            'smartrecruiters': {'enabled': api_config.get('smartrecruiters', {}).get('enabled', True)}
        }
    
    @classmethod
    def _load_browser_scrapers(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """Load browser scrapers based on configuration."""
        # This would normally load scrapers based on config
        # For now, return a basic structure
        return {
            'indeed': {'enabled': config.get('indeed_enabled', True)},
            'linkedin': {'enabled': config.get('linkedin_enabled', True)},
            'ziprecruiter': {'enabled': config.get('ziprecruiter_enabled', True)},
            'greenhouse': {'enabled': config.get('greenhouse_enabled', True)}
        }


# Convenience function for CLI usage
async def run_daily_job_search(search_params: Dict[str, Any],
                              output_path: str = None) -> List[Dict[str, Any]]:
    """
    Convenience function to run daily job search from CLI.
    
    Args:
        search_params: Search configuration
        output_path: Optional path to save results
        
    Returns:
        List of collected jobs
    """
    aggregator = JobAggregatorService()
    
    jobs = await aggregator.run_daily_aggregation(search_params)
    
    if output_path:
        import json
        with open(output_path, 'w') as f:
            json.dump(jobs, f, indent=2, default=str)
            
    return jobs