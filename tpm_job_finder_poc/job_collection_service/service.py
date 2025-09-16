"""
Job Collection Service - Core service implementation.

Handles job collection from multiple sources including API-based aggregators
and browser scrapers, with deduplication, enrichment, and health monitoring.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from tpm_job_finder_poc.shared.contracts.job_collection_service import (
    IJobCollectionService,
    JobQuery,
    JobPosting,
    CollectionResult,
    SourceStatus,
    JobSourceType,
    JobType,
    JobCollectionError,
    SourceNotFoundError,
    ValidationError,
    JobCollectionTimeoutError
)
from .storage import JobStorage
from .enricher import JobEnricher
from .config import JobCollectionConfig

logger = logging.getLogger(__name__)


class JobCollectionService(IJobCollectionService):
    """
    Core job collection service implementation.
    
    Orchestrates job collection from multiple API and browser sources,
    handles deduplication, enrichment, and provides comprehensive
    job search capabilities.
    """
    
    def __init__(self, config: JobCollectionConfig, storage: JobStorage, enricher: JobEnricher):
        """
        Initialize job collection service.
        
        Args:
            config: Service configuration
            storage: Job storage backend
            enricher: Job enrichment service
        """
        self.config = config
        self.storage = storage
        self.enricher = enricher
        
        # Track enabled sources
        self._enabled_sources = set()
        
        # Initialize aggregators and scrapers
        self._api_aggregators = {}
        self._browser_scrapers = {}
        
        # Deduplication cache
        self._dedupe_cache = None
        
        # Initialize components
        self._init_components()
    
    def _init_components(self):
        """Initialize API aggregators, browser scrapers, and cache."""
        self._init_api_aggregators()
        self._init_browser_scrapers()
        self._init_dedupe_cache()
    
    def _init_api_aggregators(self):
        """Initialize API-based job aggregators."""
        try:
            from tpm_job_finder_poc.job_aggregator.aggregators import (
                RemoteOKConnector, GreenhouseConnector, LeverConnector,
                AshbyConnector, WorkableConnector, SmartRecruitersConnector
            )
            
            api_config = self.config.api_aggregators
            
            # RemoteOK
            if api_config.get('remoteok', {}).get('enabled', False):
                self._api_aggregators['remoteok'] = RemoteOKConnector()
                self._enabled_sources.add('remoteok')
            
            # Greenhouse
            if api_config.get('greenhouse', {}).get('enabled', False):
                companies = api_config.get('greenhouse', {}).get('companies', [])
                self._api_aggregators['greenhouse'] = GreenhouseConnector(companies=companies)
                self._enabled_sources.add('greenhouse')
            
            # Lever
            if api_config.get('lever', {}).get('enabled', False):
                companies = api_config.get('lever', {}).get('companies', [])
                self._api_aggregators['lever'] = LeverConnector(companies=companies)
                self._enabled_sources.add('lever')
            
            # Ashby
            if api_config.get('ashby', {}).get('enabled', False):
                self._api_aggregators['ashby'] = AshbyConnector('default')
                self._enabled_sources.add('ashby')
            
            # Workable
            if api_config.get('workable', {}).get('enabled', False):
                self._api_aggregators['workable'] = WorkableConnector('default')
                self._enabled_sources.add('workable')
            
            # SmartRecruiters
            if api_config.get('smartrecruiters', {}).get('enabled', False):
                self._api_aggregators['smartrecruiters'] = SmartRecruitersConnector('default')
                self._enabled_sources.add('smartrecruiters')
            
            logger.info(f"Initialized {len(self._api_aggregators)} API aggregators")
            
        except ImportError as e:
            logger.warning(f"Could not import API aggregators: {e}")
            self._api_aggregators = {}
    
    def _init_browser_scrapers(self):
        """Initialize browser-based scrapers."""
        try:
            from tpm_job_finder_poc.scraping_service import registry
            
            # Register default scrapers if not already done
            registry.register_default_scrapers()
            
            browser_config = self.config.browser_scrapers
            
            # Indeed
            if browser_config.get('indeed', {}).get('enabled', False):
                scraper = registry.get_source('indeed')
                if scraper:
                    self._browser_scrapers['indeed'] = scraper
                    self._enabled_sources.add('indeed')
            
            # LinkedIn
            if browser_config.get('linkedin', {}).get('enabled', False):
                scraper = registry.get_source('linkedin')
                if scraper:
                    self._browser_scrapers['linkedin'] = scraper
                    self._enabled_sources.add('linkedin')
            
            # ZipRecruiter
            if browser_config.get('ziprecruiter', {}).get('enabled', False):
                scraper = registry.get_source('ziprecruiter')
                if scraper:
                    self._browser_scrapers['ziprecruiter'] = scraper
                    self._enabled_sources.add('ziprecruiter')
            
            # Greenhouse Browser
            if browser_config.get('greenhouse_browser', {}).get('enabled', False):
                scraper = registry.get_source('greenhouse')
                if scraper:
                    self._browser_scrapers['greenhouse_browser'] = scraper
                    self._enabled_sources.add('greenhouse_browser')
            
            logger.info(f"Initialized {len(self._browser_scrapers)} browser scrapers")
            
        except ImportError as e:
            logger.warning(f"Could not import browser scrapers: {e}")
            self._browser_scrapers = {}
    
    def _init_dedupe_cache(self):
        """Initialize deduplication cache."""
        try:
            from tpm_job_finder_poc.cache.dedupe_cache import DedupeCache
            self._dedupe_cache = DedupeCache()
            logger.info("Initialized deduplication cache")
        except ImportError as e:
            logger.warning(f"Could not import dedupe cache: {e}")
            self._dedupe_cache = None
    
    async def collect_jobs(self, query: JobQuery) -> CollectionResult:
        """
        Collect jobs from configured sources based on query parameters.
        
        Args:
            query: Job collection query parameters
            
        Returns:
            CollectionResult with jobs and metadata
            
        Raises:
            JobCollectionError: When job collection fails
            ValidationError: When query parameters are invalid
        """
        start_time = datetime.now()
        
        try:
            # Validate query
            self._validate_query(query)
            
            # Determine sources to query
            sources_to_query = self._get_sources_to_query(query.sources)
            
            # Collect from all sources
            all_jobs = []
            api_jobs = await self._collect_from_api_aggregators(query, sources_to_query)
            all_jobs.extend(api_jobs)

            scraper_jobs = await self._collect_from_browser_scrapers(query, sources_to_query)
            all_jobs.extend(scraper_jobs)
            
            logger.info(f"DEBUG: Collected {len(all_jobs)} total raw jobs")
            if all_jobs:
                logger.info(f"DEBUG: First job keys: {list(all_jobs[0].keys())}")
                logger.info(f"DEBUG: First job sample: {all_jobs[0]}")
            
            # Deduplicate
            deduplicated_jobs = self._deduplicate_jobs(all_jobs)
            logger.info(f"DEBUG: {len(deduplicated_jobs)} jobs after deduplication")
            
            # Enrich
            enriched_jobs = await self._enrich_jobs(deduplicated_jobs)
            logger.info(f"DEBUG: {len(enriched_jobs)} jobs after enrichment")            # Convert to JobPosting objects
            job_postings = [self._convert_to_job_posting(job) for job in enriched_jobs]
            
            # Store jobs in database
            if job_postings:
                stored_count = await self.storage.store_jobs(job_postings)
                logger.info(f"Stored {stored_count} jobs to database")
            
            # Create result
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            successful_sources = [source for source in sources_to_query 
                                if source in self._enabled_sources]
            failed_sources = [source for source in sources_to_query 
                            if source not in self._enabled_sources]
            
            result = CollectionResult(
                jobs=job_postings,
                total_jobs=len(job_postings),
                raw_jobs=len(all_jobs),
                duplicates_removed=len(all_jobs) - len(deduplicated_jobs),
                sources_queried=sources_to_query,
                successful_sources=successful_sources,
                failed_sources=failed_sources,
                collection_time=end_time,
                duration_seconds=duration,
                errors={}
            )
            
            logger.info(f"Collected {len(job_postings)} jobs in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Job collection failed: {e}")
            raise JobCollectionError(f"Collection failed: {str(e)}") from e
    
    async def run_daily_aggregation(self, query: JobQuery) -> CollectionResult:
        """
        Run complete daily job aggregation process.
        
        Args:
            query: Job collection query parameters
            
        Returns:
            CollectionResult with aggregated and processed jobs
            
        Raises:
            JobCollectionError: When aggregation fails
        """
        logger.info("Starting daily job aggregation")
        
        # Ensure we're collecting from all enabled sources
        if not query.sources:
            query.sources = list(self._enabled_sources)
        
        # Collect jobs
        result = await self.collect_jobs(query)
        
        # Store collected jobs
        if result.jobs and self.storage:
            stored_count = await self.storage.store_jobs(result.jobs)
            logger.info(f"Stored {stored_count} jobs to storage")
        
        logger.info(f"Daily aggregation complete: {result.total_jobs} jobs collected")
        return result
    
    async def get_source_statuses(self) -> List[SourceStatus]:
        """
        Get status information for all configured job sources.
        
        Returns:
            List of SourceStatus objects
        """
        statuses = []
        now = datetime.now()
        
        # API aggregators
        for name, aggregator in self._api_aggregators.items():
            try:
                # Perform health check (simplified)
                healthy = True
                error_message = None
                
                status = SourceStatus(
                    name=name,
                    type=JobSourceType.API_AGGREGATOR,
                    enabled=name in self._enabled_sources,
                    healthy=healthy,
                    last_check=now,
                    error_message=error_message,
                    jobs_collected_today=0  # Would track this in real implementation
                )
                statuses.append(status)
            except Exception as e:
                logger.error(f"Error checking status for {name}: {e}")
                status = SourceStatus(
                    name=name,
                    type=JobSourceType.API_AGGREGATOR,
                    enabled=name in self._enabled_sources,
                    healthy=False,
                    last_check=now,
                    error_message=str(e),
                    jobs_collected_today=0
                )
                statuses.append(status)
        
        # Browser scrapers
        for name, scraper in self._browser_scrapers.items():
            try:
                healthy = True
                error_message = None
                
                status = SourceStatus(
                    name=name,
                    type=JobSourceType.BROWSER_SCRAPER,
                    enabled=name in self._enabled_sources,
                    healthy=healthy,
                    last_check=now,
                    error_message=error_message,
                    jobs_collected_today=0
                )
                statuses.append(status)
            except Exception as e:
                logger.error(f"Error checking status for {name}: {e}")
                status = SourceStatus(
                    name=name,
                    type=JobSourceType.BROWSER_SCRAPER,
                    enabled=name in self._enabled_sources,
                    healthy=False,
                    last_check=now,
                    error_message=str(e),
                    jobs_collected_today=0
                )
                statuses.append(status)
        
        return statuses
    
    async def enable_source(self, source_name: str) -> bool:
        """
        Enable a specific job source.
        
        Args:
            source_name: Name of the source to enable
            
        Returns:
            True if source was enabled successfully
            
        Raises:
            SourceNotFoundError: When source doesn't exist
        """
        # Check if source exists
        if (source_name not in self._api_aggregators and 
            source_name not in self._browser_scrapers):
            raise SourceNotFoundError(f"Source '{source_name}' not found")
        
        self._enabled_sources.add(source_name)
        logger.info(f"Enabled source: {source_name}")
        return True
    
    async def disable_source(self, source_name: str) -> bool:
        """
        Disable a specific job source.
        
        Args:
            source_name: Name of the source to disable
            
        Returns:
            True if source was disabled successfully
            
        Raises:
            SourceNotFoundError: When source doesn't exist
        """
        # Check if source exists
        if (source_name not in self._api_aggregators and 
            source_name not in self._browser_scrapers):
            raise SourceNotFoundError(f"Source '{source_name}' not found")
        
        self._enabled_sources.discard(source_name)
        logger.info(f"Disabled source: {source_name}")
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the job collection service.
        
        Returns:
            Health check status and details
        """
        now = datetime.now()
        
        # Check component health
        components_healthy = {
            'api_aggregators': len(self._api_aggregators) > 0,
            'browser_scrapers': len(self._browser_scrapers) > 0,
            'storage': self.storage is not None,
            'enricher': self.enricher is not None,
            'cache': self._dedupe_cache is not None
        }
        
        healthy_components = sum(components_healthy.values())
        total_components = len(components_healthy)
        
        # Determine overall status
        if healthy_components == total_components:
            status = "healthy"
        elif healthy_components >= total_components * 0.7:
            status = "degraded"
        else:
            status = "unhealthy"
        
        return {
            "status": status,
            "timestamp": now.isoformat(),
            "components": components_healthy,
            "sources_enabled": len(self._enabled_sources),
            "api_aggregators_count": len(self._api_aggregators),
            "browser_scrapers_count": len(self._browser_scrapers),
            "total_sources": len(self._api_aggregators) + len(self._browser_scrapers)
        }
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get collection statistics and metrics.
        
        Returns:
            Dictionary with collection statistics
        """
        storage_stats = {}
        if self.storage:
            storage_stats = await self.storage.get_storage_stats()
        
        return {
            "total_jobs_collected": storage_stats.get("total_jobs", 0),
            "jobs_collected_today": storage_stats.get("jobs_today", 0),
            "active_sources": len(self._enabled_sources),
            "available_sources": len(self._api_aggregators) + len(self._browser_scrapers),
            "api_aggregators": len(self._api_aggregators),
            "browser_scrapers": len(self._browser_scrapers),
            "storage_size_mb": storage_stats.get("storage_size_mb", 0),
            "last_update": datetime.now().isoformat()
        }
    
    def _validate_query(self, query: JobQuery):
        """Validate job query parameters."""
        if query.max_jobs_per_source <= 0:
            raise ValidationError("max_jobs_per_source must be positive")
        
        if query.date_range_days <= 0:
            raise ValidationError("date_range_days must be positive")
        
        if query.sources:
            available_sources = set(self._api_aggregators.keys()) | set(self._browser_scrapers.keys())
            invalid_sources = set(query.sources) - available_sources
            if invalid_sources:
                raise ValidationError(f"Invalid sources: {list(invalid_sources)}")
    
    def _get_sources_to_query(self, requested_sources: Optional[List[str]]) -> List[str]:
        """Get list of sources to query based on request and enabled sources."""
        if requested_sources:
            # Use only requested sources that are enabled
            return [s for s in requested_sources if s in self._enabled_sources]
        else:
            # Use all enabled sources
            return list(self._enabled_sources)
    
    async def _collect_from_api_aggregators(self, query: JobQuery, sources: List[str]) -> List[Dict[str, Any]]:
        """Collect jobs from API aggregators."""
        jobs = []
        search_params = self._convert_query_to_search_params(query)
        
        # Use ThreadPoolExecutor for parallel API calls
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {}
            
            for source_name in sources:
                if source_name in self._api_aggregators:
                    aggregator = self._api_aggregators[source_name]
                    try:
                        if hasattr(aggregator, 'fetch_jobs'):
                            future = executor.submit(aggregator.fetch_jobs, **search_params)
                        elif hasattr(aggregator, 'fetch_since'):
                            days_ago = datetime.now() - timedelta(days=query.date_range_days)
                            future = executor.submit(aggregator.fetch_since, days_ago)
                        else:
                            continue
                        
                        future_to_source[future] = source_name
                    except Exception as e:
                        logger.error(f"Error setting up {source_name} aggregation: {e}")
            
            # Collect results
            for future in as_completed(future_to_source):
                source_name = future_to_source[future]
                try:
                    source_jobs = future.result(timeout=30)
                    normalized_jobs = self._normalize_api_jobs(source_jobs, source_name)
                    jobs.extend(normalized_jobs[:query.max_jobs_per_source])
                    logger.info(f"{source_name}: collected {len(normalized_jobs)} jobs")
                except Exception as e:
                    logger.error(f"Error collecting from {source_name}: {e}")
        
        return jobs
    
    async def _collect_from_browser_scrapers(self, query: JobQuery, sources: List[str]) -> List[Dict[str, Any]]:
        """Collect jobs from browser scrapers."""
        try:
            from tpm_job_finder_poc.scraping_service.core.base_job_source import FetchParams
        except ImportError:
            logger.warning("Could not import FetchParams, skipping browser scrapers")
            return []
        
        jobs = []
        
        # Convert search params to FetchParams
        fetch_params = FetchParams(
            keywords=query.keywords,
            location=query.location,
            limit=query.max_jobs_per_source
        )
        
        for source_name in sources:
            if source_name in self._browser_scrapers:
                scraper = self._browser_scrapers[source_name]
                try:
                    logger.info(f"Starting browser scraping for {source_name}")
                    
                    # Initialize scraper
                    if not await scraper.initialize():
                        logger.warning(f"Failed to initialize {source_name} scraper")
                        continue
                    
                    # Fetch jobs
                    source_jobs = await scraper.fetch_jobs(fetch_params)
                    
                    # Convert to standardized format
                    normalized_jobs = self._normalize_scraper_jobs(source_jobs, source_name)
                    jobs.extend(normalized_jobs)
                    logger.info(f"{source_name}: collected {len(normalized_jobs)} jobs")
                    
                    # Cleanup
                    await scraper.cleanup()
                    
                except Exception as e:
                    logger.error(f"Error scraping from {source_name}: {e}")
        
        return jobs
    
    def _convert_query_to_search_params(self, query: JobQuery) -> Dict[str, Any]:
        """Convert JobQuery to search parameters for API aggregators."""
        params = {}
        
        if query.keywords:
            params['keywords'] = query.keywords
        
        if query.location:
            params['location'] = query.location
        
        return params
    
    def _normalize_api_jobs(self, jobs: List[Any], source: str) -> List[Dict[str, Any]]:
        """Normalize job data from API aggregators to standard format."""
        normalized = []
        
        for job in jobs:
            try:
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
    
    def _normalize_scraper_jobs(self, jobs: List[Any], source: str) -> List[Dict[str, Any]]:
        """Normalize job data from browser scrapers to standard format."""
        normalized = []
        
        for job in jobs:
            try:
                normalized_job = {
                    'id': getattr(job, 'id', f"{source}_{hash(str(job))}"),
                    'source': getattr(job, 'source', source),
                    'title': getattr(job, 'title', None),
                    'company': getattr(job, 'company', None),
                    'location': getattr(job, 'location', None),
                    'url': getattr(job, 'url', None),
                    'date_posted': getattr(job, 'date_posted', None),
                    'raw_data': getattr(job, 'raw_data', getattr(job, '__dict__', str(job)))
                }
                
                if normalized_job['title'] and normalized_job['company']:
                    normalized.append(normalized_job)
                    
            except Exception as e:
                logger.warning(f"Error normalizing scraper job from {source}: {e}")
        
        return normalized
    
    def _deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs."""
        if not jobs:
            return []
        
        if False and self._dedupe_cache:  # Temporarily disable cache
            # Use dedupe cache if available
            unique_jobs = []
            for job in jobs:
                dedupe_key = f"{job.get('company', '')}-{job.get('title', '')}-{job.get('location', '')}"
                logger.info(f"DEBUG: Checking dedupe for key: {dedupe_key}")
                if not self._dedupe_cache.is_duplicate(dedupe_key, dedupe_key):
                    unique_jobs.append(job)
                    self._dedupe_cache.add(dedupe_key, dedupe_key)
                    logger.info(f"DEBUG: Added unique job: {job.get('title', 'NO_TITLE')}")
                else:
                    logger.info(f"DEBUG: Filtered duplicate job: {job.get('title', 'NO_TITLE')}")
            return unique_jobs
        else:
            # Simple deduplication by URL and title+company
            seen_urls = set()
            seen_combinations = set()
            unique_jobs = []
            
            for job in jobs:
                # Check URL-based deduplication
                job_url = job.get('url', '')
                if job_url and job_url in seen_urls:
                    continue
                
                # Check title+company combination
                combo_key = f"{job.get('title', '')}|{job.get('company', '')}".lower()
                if combo_key in seen_combinations:
                    continue
                
                # Add to seen sets
                if job_url:
                    seen_urls.add(job_url)
                seen_combinations.add(combo_key)
                
                unique_jobs.append(job)
            
            return unique_jobs
    
    async def _enrich_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich jobs with additional metadata."""
        enriched_jobs = []
        
        for job in jobs:
            try:
                # Add aggregation timestamp
                job['aggregated_at'] = datetime.now()
                
                # Convert to JobPosting for enrichment
                job_posting = self._convert_to_job_posting(job)
                
                # Enrich the job using the enricher service
                enriched_job = await self.enricher.enrich_job(job_posting)
                
                # Update the job data with enriched values
                job['job_type'] = enriched_job.job_type.value if enriched_job.job_type else None
                job['remote_friendly'] = enriched_job.remote_friendly
                job['tpm_keywords_found'] = enriched_job.tpm_keywords_found
                
                enriched_jobs.append(job)
                
            except Exception as e:
                logger.warning(f"Error enriching job: {e}")
                # Add basic fields to avoid errors
                job['aggregated_at'] = datetime.now()
                job['job_type'] = JobType.MID_LEVEL.value
                job['remote_friendly'] = False
                job['tpm_keywords_found'] = 0
                enriched_jobs.append(job)
        
        return enriched_jobs
    
    def _classify_job_type_basic(self, title: str) -> JobType:
        """Basic job type classification."""
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ['manager', 'lead', 'director', 'head']):
            return JobType.MANAGEMENT
        elif any(kw in title_lower for kw in ['senior', 'sr', 'principal']):
            return JobType.SENIOR
        elif any(kw in title_lower for kw in ['junior', 'jr', 'associate', 'entry']):
            return JobType.ENTRY_LEVEL
        else:
            return JobType.MID_LEVEL
    
    def _detect_remote_work_basic(self, location: str) -> bool:
        """Basic remote work detection."""
        if not location:
            return False
        
        location_lower = location.lower()
        remote_indicators = ['remote', 'anywhere', 'distributed', 'work from home', 'wfh']
        
        return any(indicator in location_lower for indicator in remote_indicators)
    
    def _count_tpm_keywords_basic(self, title: str) -> int:
        """Basic TPM keyword counting."""
        if not title:
            return 0
        
        title_lower = title.lower()
        tpm_keywords = [
            'product manager', 'product management', 'tpm', 'technical product',
            'program manager', 'project manager', 'product owner', 'po'
        ]
        
        return sum(1 for keyword in tpm_keywords if keyword in title_lower)
    
    def _convert_to_job_posting(self, job_dict: Dict[str, Any]) -> JobPosting:
        """Convert job dictionary to JobPosting object."""
        # Parse date_posted if it's a string
        date_posted = job_dict.get('date_posted')
        if isinstance(date_posted, str):
            try:
                date_posted = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                date_posted = None
        
        # Parse aggregated_at if it's a string
        aggregated_at = job_dict.get('aggregated_at')
        if isinstance(aggregated_at, str):
            try:
                aggregated_at = datetime.fromisoformat(aggregated_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                aggregated_at = None
        
        # Parse job_type if it's a string
        job_type = job_dict.get('job_type')
        if isinstance(job_type, str):
            try:
                job_type = JobType(job_type)
            except ValueError:
                job_type = JobType.MID_LEVEL
        
        return JobPosting(
            id=job_dict.get('id', ''),
            source=job_dict.get('source', ''),
            title=job_dict.get('title', ''),
            company=job_dict.get('company', ''),
            location=job_dict.get('location'),
            url=job_dict.get('url'),
            date_posted=date_posted,
            job_type=job_type,
            remote_friendly=job_dict.get('remote_friendly', False),
            tpm_keywords_found=job_dict.get('tpm_keywords_found', 0),
            raw_data=job_dict.get('raw_data'),
            aggregated_at=aggregated_at
        )

    async def search_jobs(self, query: JobQuery) -> List[JobPosting]:
        """
        Search stored job postings.
        
        Args:
            query: Search query parameters
            
        Returns:
            List of matching job postings
        """
        return await self.storage.search_jobs(query)