"""
Job Aggregator Service - Core business logic implementation.

Handles job aggregation from multiple sources with deduplication,
enrichment, and normalization.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..shared.contracts.job_aggregator_service import (
    IJobAggregatorService,
    SearchParams,
    AggregatedJob,
    AggregationResult,
    SourceStatus,
    SourceType,
    HealthStatus,
    JobAggregatorError,
    SourceUnavailableError,
    RateLimitError,
    ValidationError
)

logger = logging.getLogger(__name__)


class JobAggregatorService(IJobAggregatorService):
    """
    Core service for orchestrating job collection from multiple sources.
    
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
        
        # Initialize components
        self._init_dedupe_cache()
        self._init_api_aggregators()
        self._init_browser_scrapers()
        
    def _init_dedupe_cache(self):
        """Initialize deduplication cache."""
        try:
            from ..cache.dedupe_cache import DedupeCache
            self.dedupe_cache = DedupeCache()
        except ImportError:
            logger.warning("DedupeCache not available, using simple deduplication")
            self.dedupe_cache = None
        
    def _init_api_aggregators(self):
        """Initialize all API-based job aggregators."""
        try:
            from .aggregators import (
                RemoteOKConnector, GreenhouseConnector, LeverConnector,
                AshbyConnector, WorkableConnector, SmartRecruitersConnector
            )
            
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
            
        except ImportError as e:
            logger.error(f"Failed to import aggregators: {e}")
            self.api_aggregators = {}
        
    def _init_browser_scrapers(self):
        """Initialize browser-based scrapers."""
        try:
            from .scrapers.factory import ScraperFactory
            
            # Try to get available scrapers from factory
            available_scrapers = ['indeed', 'linkedin', 'ziprecruiter']
            self.browser_scrapers = {}
            
            for scraper_name in available_scrapers:
                try:
                    scraper = ScraperFactory.get_scraper(scraper_name, [], None)
                    if scraper is not None:
                        self.browser_scrapers[scraper_name] = scraper
                except Exception as e:
                    logger.warning(f"Failed to initialize {scraper_name} scraper: {e}")
            
            # Filter out any failed initializations
            self.browser_scrapers = {
                name: scraper for name, scraper in self.browser_scrapers.items() 
                if scraper is not None
            }
            
            logger.info(f"Initialized {len(self.browser_scrapers)} browser scrapers")
            
        except Exception as e:
            logger.error(f"Failed to initialize browser scrapers: {e}")
            self.browser_scrapers = {}
            
    async def aggregate_jobs(self, 
                           search_params: SearchParams,
                           max_jobs_per_source: int = 50) -> AggregationResult:
        """
        Aggregate jobs from all configured sources.
        
        Args:
            search_params: Search criteria for job collection
            max_jobs_per_source: Maximum jobs to collect per source
            
        Returns:
            AggregationResult with collected and processed jobs
        """
        start_time = datetime.now()
        logger.info("Starting job aggregation process")
        
        # Validate input
        if not search_params.keywords and not search_params.location:
            raise ValidationError("Either keywords or location must be specified")
        
        all_jobs = []
        sources_used = []
        errors = []
        
        try:
            # Step 1: Collect from API sources
            api_jobs = await self._collect_from_api_sources(
                search_params, max_jobs_per_source
            )
            all_jobs.extend(api_jobs)
            sources_used.extend([job.source for job in api_jobs])
            
            # Step 2: Collect from browser scrapers  
            scraper_jobs = await self._collect_from_browser_scrapers(
                search_params, max_jobs_per_source
            )
            all_jobs.extend(scraper_jobs)
            sources_used.extend([job.source for job in scraper_jobs])
            
            # Step 3: Deduplicate jobs
            deduplicated_jobs = self._deduplicate_jobs(all_jobs)
            
            # Step 4: Enrich job data
            enriched_jobs = self._enrich_job_data(deduplicated_jobs)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            result = AggregationResult(
                jobs=enriched_jobs,
                total_collected=len(all_jobs),
                total_deduplicated=len(enriched_jobs),
                sources_used=list(set(sources_used)),
                duration_seconds=duration,
                errors=errors
            )
            
            logger.info(f"Aggregation complete: {len(enriched_jobs)} unique jobs from {len(set(sources_used))} sources")
            return result
            
        except Exception as e:
            logger.error(f"Job aggregation failed: {e}")
            # Return partial results even on error
            duration = (datetime.now() - start_time).total_seconds()
            return AggregationResult(
                jobs=[],
                total_collected=0,
                total_deduplicated=0,
                sources_used=[],
                duration_seconds=duration,
                errors=[str(e)]
            )
    
    async def _collect_from_api_sources(self, 
                                       search_params: SearchParams, 
                                       max_jobs_per_source: int) -> List[AggregatedJob]:
        """Collect jobs from API sources - wrapper for test mocking."""
        # Convert dict results to AggregatedJob objects
        dict_jobs = await self._collect_from_api_aggregators(search_params, max_jobs_per_source)
        return self._convert_to_aggregated_jobs(dict_jobs)
    
    async def _collect_from_browser_scrapers(self, 
                                           search_params: SearchParams, 
                                           max_jobs_per_source: int) -> List[AggregatedJob]:
        """Collect jobs from browser scrapers - updated signature for test compatibility."""
        # Convert dict results to AggregatedJob objects  
        dict_jobs = await self._collect_from_browser_scrapers_internal(search_params, max_jobs_per_source)
        return self._convert_to_aggregated_jobs(dict_jobs)
        
    async def _collect_from_api_aggregators(self, 
                                          search_params: SearchParams,
                                          max_jobs: int) -> List[Dict[str, Any]]:
        """Collect jobs from all API-based aggregators."""
        jobs = []
        
        if not self.api_aggregators:
            logger.warning("No API aggregators available")
            return jobs
        
        # Use ThreadPoolExecutor for parallel API calls
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all aggregator tasks
            futures = []
            for name, aggregator in self.api_aggregators.items():
                if hasattr(aggregator, 'fetch_jobs'):
                    future = executor.submit(
                        self._safe_fetch_from_aggregator,
                        name, aggregator, search_params, max_jobs
                    )
                    futures.append(future)
            
            # Collect results as they complete
            for future in as_completed(futures):
                try:
                    aggregator_jobs = future.result(timeout=30)
                    if aggregator_jobs:
                        jobs.extend(aggregator_jobs)
                except Exception as e:
                    logger.error(f"API aggregator failed: {e}")
                    
        logger.info(f"Collected {len(jobs)} jobs from API aggregators")
        return jobs
        
    def _safe_fetch_from_aggregator(self, name: str, aggregator: Any, 
                                   search_params: SearchParams, max_jobs: int) -> List[Dict[str, Any]]:
        """Safely fetch jobs from an aggregator with error handling."""
        try:
            # Convert SearchParams to aggregator-specific format
            params = {
                'query': search_params.keywords or '',
                'location': search_params.location or '',
                'limit': max_jobs
            }
            
            raw_jobs = aggregator.fetch_jobs(**params)
            normalized_jobs = self._normalize_api_jobs(raw_jobs, name)
            
            logger.info(f"Fetched {len(normalized_jobs)} jobs from {name}")
            return normalized_jobs
            
        except Exception as e:
            logger.error(f"Failed to fetch from {name}: {e}")
            return []
            
    async def _collect_from_browser_scrapers_internal(self,
                                           search_params: SearchParams,
                                           max_jobs: int) -> List[Dict[str, Any]]:
        """Collect jobs from browser scrapers."""
        jobs = []
        
        if not self.browser_scrapers:
            logger.warning("No browser scrapers available")
            return jobs
            
        for name, scraper in self.browser_scrapers.items():
            try:
                if hasattr(scraper, 'fetch_jobs'):
                    # Convert SearchParams to scraper format
                    fetch_params = {
                        'query': search_params.keywords or '',
                        'location': search_params.location or '',
                        'limit': max_jobs
                    }
                    
                    scraper_jobs = await scraper.fetch_jobs(fetch_params)
                    normalized_jobs = self._normalize_scraper_jobs(scraper_jobs, name)
                    
                    jobs.extend(normalized_jobs)
                    logger.info(f"Collected {len(normalized_jobs)} jobs from {name}")
                    
            except Exception as e:
                logger.error(f"Browser scraper {name} failed: {e}")
                
        return jobs
    
    async def _collect_from_single_api_source(self, source_name: str, search_params: SearchParams) -> List[AggregatedJob]:
        """Collect jobs from a single API aggregator source."""
        try:
            if source_name not in self.api_aggregators:
                return []
                
            aggregator = self.api_aggregators[source_name]
            raw_jobs = await aggregator.fetch_jobs({
                'keywords': search_params.keywords,
                'location': search_params.location,
                'limit': search_params.max_results
            })
            
            return self._normalize_api_jobs(raw_jobs, source_name)
            
        except Exception as e:
            logger.error(f"API aggregator {source_name} failed: {e}")
            return []
        
    def _normalize_api_jobs(self, jobs: List[Any], source: str) -> List[Dict[str, Any]]:
        """Normalize jobs from API aggregators to standard format."""
        normalized = []
        
        for job in jobs:
            try:
                # Handle different job object types
                if hasattr(job, '__dict__'):
                    job_dict = job.__dict__
                elif isinstance(job, dict):
                    job_dict = job
                else:
                    logger.warning(f"Unknown job type from {source}: {type(job)}")
                    continue
                
                normalized_job = {
                    'id': job_dict.get('id', f"{source}_{len(normalized)}"),
                    'source': source,
                    'source_type': SourceType.API_AGGREGATOR.value,
                    'title': job_dict.get('title', ''),
                    'company': job_dict.get('company', ''),
                    'location': job_dict.get('location'),
                    'url': job_dict.get('url'),
                    'description': job_dict.get('description'),
                    'salary': job_dict.get('salary'),
                    'date_posted': job_dict.get('date_posted'),
                    'raw_data': job_dict
                }
                
                # Add enrichment
                normalized_job.update(self._enrich_job_data(normalized_job))
                normalized.append(normalized_job)
                
            except Exception as e:
                logger.error(f"Failed to normalize job from {source}: {e}")
                
        return normalized
        
    def _normalize_scraper_jobs(self, jobs: List[Any], source: str) -> List[Dict[str, Any]]:
        """Normalize jobs from browser scrapers to standard format."""
        normalized = []
        
        for job in jobs:
            try:
                if hasattr(job, 'to_dict'):
                    job_dict = job.to_dict()
                elif isinstance(job, dict):
                    job_dict = job
                else:
                    logger.warning(f"Unknown job type from scraper {source}: {type(job)}")
                    continue
                
                normalized_job = {
                    'id': job_dict.get('id', f"{source}_{len(normalized)}"),
                    'source': source,
                    'source_type': SourceType.BROWSER_SCRAPER.value,
                    'title': job_dict.get('title', ''),
                    'company': job_dict.get('company', ''),
                    'location': job_dict.get('location'),
                    'url': job_dict.get('url'),
                    'description': job_dict.get('description'),
                    'salary': job_dict.get('salary'),
                    'date_posted': job_dict.get('date_posted'),
                    'raw_data': job_dict
                }
                
                # Add enrichment
                normalized_job.update(self._enrich_job_data(normalized_job))
                normalized.append(normalized_job)
                
            except Exception as e:
                logger.error(f"Failed to normalize scraper job from {source}: {e}")
                
        return normalized
        
    def _deduplicate_jobs(self, jobs: List[AggregatedJob]) -> List[AggregatedJob]:
        """Remove duplicate jobs based on title and company."""
        if self.dedupe_cache:
            # Use advanced deduplication cache with simple key-based approach for job aggregation
            seen = set()
            unique_jobs = []
            
            for job in jobs:
                key = f"{job.title}-{job.company}".lower()
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
                    
            return unique_jobs
        else:
            # Simple deduplication
            seen = set()
            unique_jobs = []
            
            for job in jobs:
                key = f"{job.title}-{job.company}".lower()
                if key not in seen:
                    seen.add(key)
                    unique_jobs.append(job)
                    
            return unique_jobs
        
        def _convert_to_aggregated_jobs(self, job_dicts: List[Dict[str, Any]]) -> List[AggregatedJob]:
            """Convert dictionary job data to AggregatedJob objects."""
            aggregated_jobs = []
            
            for job_dict in job_dicts:
                aggregated_job = AggregatedJob(
                    id=job_dict.get('id', ''),
                    title=job_dict.get('title', ''),
                    company=job_dict.get('company', ''),
                    description=job_dict.get('description', ''),
                    location=job_dict.get('location', ''),
                    salary_range=job_dict.get('salary_range', ''),
                    posted_date=job_dict.get('posted_date'),
                    source=job_dict.get('source', ''),
                    url=job_dict.get('url', ''),
                    remote_work_detected=job_dict.get('remote_work_detected', False),
                    tpm_keyword_count=job_dict.get('tpm_keyword_count', 0),
                    relevance_score=job_dict.get('relevance_score', 0.0)
                )
                aggregated_jobs.append(aggregated_job)
                
            return aggregated_jobs
        
    def _enrich_job_data(self, jobs: List[AggregatedJob]) -> List[AggregatedJob]:
        """Enrich job data with additional metadata."""
        enriched_jobs = []
        
        for job in jobs:
            # Create a copy and enrich it
            enriched_job = AggregatedJob(
                id=job.id,
                source=job.source,
                source_type=job.source_type,
                title=job.title,
                company=job.company,
                location=job.location,
                url=job.url,
                description=job.description,
                salary=job.salary,
                job_type=job.job_type or self._classify_job_type(job.title),
                remote_friendly=self._detect_remote_work(job),
                tpm_keywords_found=self._count_tpm_keywords(job),
                date_posted=job.date_posted,
                raw_data=job.raw_data,
                aggregated_at=job.aggregated_at or datetime.now(timezone.utc)
            )
            enriched_jobs.append(enriched_job)
            
        return enriched_jobs
        
    def _classify_job_type(self, title: str) -> str:
        """Classify job type based on title."""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['senior', 'sr', 'lead', 'principal', 'staff']):
            return 'senior'
        elif any(keyword in title_lower for keyword in ['junior', 'entry', 'associate', 'intern']):
            return 'entry'
        elif any(keyword in title_lower for keyword in ['manager', 'director', 'vp', 'head of', 'ceo', 'cto', 'executive']):
            return 'executive'
        else:
            return 'mid_level'
        
    def _detect_remote_work(self, job: AggregatedJob) -> bool:
        """Detect if a job offers remote work opportunities."""
        # Check various fields for remote work indicators
        remote_indicators = ['remote', 'work from home', 'wfh', 'telecommute', 'distributed']
        
        # Check title
        if job.title:
            title_lower = job.title.lower()
            if any(indicator in title_lower for indicator in remote_indicators):
                return True
        
        # Check location
        if job.location:
            location_lower = job.location.lower()
            if any(indicator in location_lower for indicator in remote_indicators):
                return True
                
        # Check description
        if job.description:
            description_lower = job.description.lower()
            if any(indicator in description_lower for indicator in remote_indicators):
                return True
                
        return False
    
    def _count_tpm_keywords(self, job: AggregatedJob) -> int:
        """Count TPM-related keywords in job title and description."""
        tpm_keywords = [
            'technical product manager', 'tpm', 'product manager',
            'technical pm', 'sr. product manager', 'senior product manager',
            'product lead', 'product owner', 'technical product',
            'cross-functional', 'technical leadership', 'product strategy',
            'roadmap', 'stakeholder', 'technical product management'
        ]
        
        count = 0
        
        # Check title
        if job.title:
            title_lower = job.title.lower()
            count += sum(1 for keyword in tpm_keywords if keyword in title_lower)
        
        # Check description
        if job.description:
            description_lower = job.description.lower()
            count += sum(1 for keyword in tpm_keywords if keyword in description_lower)
            
        return count
        
        # Check for specific TPM keywords in order of specificity
        # More specific matches first to avoid double counting
        if 'technical program manager' in title_lower:
            return 1
        elif 'engineering program manager' in title_lower:
            return 1  
        elif 'technical project manager' in title_lower:
            return 1
        elif 'program manager' in title_lower:
            return 1
        elif 'tpm' in title_lower:
            return 1
        
        return 0
        
    def _convert_to_aggregated_jobs(self, jobs: List[Dict[str, Any]]) -> List[AggregatedJob]:
        """Convert job dictionaries to AggregatedJob objects."""
        aggregated_jobs = []
        
        for job in jobs:
            try:
                aggregated_job = AggregatedJob(
                    id=job.get('id', ''),
                    source=job.get('source', ''),
                    source_type=SourceType(job.get('source_type', SourceType.API_AGGREGATOR.value)),
                    title=job.get('title', ''),
                    company=job.get('company', ''),
                    location=job.get('location'),
                    url=job.get('url'),
                    description=job.get('description'),
                    salary=job.get('salary'),
                    job_type=job.get('job_type'),
                    remote_friendly=job.get('remote_friendly', False),
                    tpm_keywords_found=job.get('tpm_keywords_found', 0),
                    date_posted=job.get('date_posted'),
                    raw_data=job.get('raw_data'),
                    aggregated_at=job.get('aggregated_at')
                )
                aggregated_jobs.append(aggregated_job)
                
            except Exception as e:
                logger.error(f"Failed to convert job to AggregatedJob: {e}")
                
        return aggregated_jobs
        
    async def get_source_statuses(self) -> List[SourceStatus]:
        """Get health status of all configured sources."""
        statuses = []
        
        # Check API aggregators
        for name, aggregator in self.api_aggregators.items():
            try:
                # Simple health check - try to instantiate
                status = SourceStatus(
                    name=name,
                    type=SourceType.API_AGGREGATOR,
                    status=HealthStatus.HEALTHY,
                    last_success=datetime.now()
                )
            except Exception as e:
                status = SourceStatus(
                    name=name,
                    type=SourceType.API_AGGREGATOR,
                    status=HealthStatus.UNHEALTHY,
                    last_error=str(e)
                )
            statuses.append(status)
            
        # Check browser scrapers
        for name, scraper in self.browser_scrapers.items():
            try:
                status = SourceStatus(
                    name=name,
                    type=SourceType.BROWSER_SCRAPER,
                    status=HealthStatus.HEALTHY,
                    last_success=datetime.now()
                )
            except Exception as e:
                status = SourceStatus(
                    name=name,
                    type=SourceType.BROWSER_SCRAPER,
                    status=HealthStatus.UNHEALTHY,
                    last_error=str(e)
                )
            statuses.append(status)
            
        return statuses
        
    async def health_check(self) -> Dict[str, Any]:
        """Perform service health check."""
        total_sources = len(self.api_aggregators) + len(self.browser_scrapers)
        healthy_sources = total_sources  # For now, assume all initialized sources are healthy
        
        return {
            "status": "healthy" if healthy_sources > 0 else "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "sources": {
                "api_aggregators": list(self.api_aggregators.keys()),
                "browser_scrapers": list(self.browser_scrapers.keys())
            },
            "total_sources": total_sources,
            "healthy_sources": healthy_sources
        }
        
    def get_enabled_sources(self) -> Dict[str, List[str]]:
        """Get list of enabled sources by type."""
        return {
            "api_sources": list(self.api_aggregators.keys()),
            "scraping_sources": list(self.browser_scrapers.keys())
        }
    
    async def get_source_statuses(self) -> List[SourceStatus]:
        """Get detailed status information for all sources."""
        statuses = []
        
        # Add API aggregator statuses
        for name in self.api_aggregators.keys():
            status = SourceStatus(
                name=name,
                type=SourceType.API_AGGREGATOR,
                status=HealthStatus.HEALTHY,  # For now, assume initialized sources are healthy
                jobs_collected=0,  # Could be tracked with usage metrics
                last_success=datetime.now(timezone.utc),
                last_error=None
            )
            statuses.append(status)
        
        # Add browser scraper statuses  
        for name in self.browser_scrapers.keys():
            status = SourceStatus(
                name=name,
                type=SourceType.BROWSER_SCRAPER,
                status=HealthStatus.HEALTHY,  # For now, assume initialized sources are healthy
                jobs_collected=0,  # Could be tracked with usage metrics
                last_success=datetime.now(timezone.utc),
                last_error=None
            )
            statuses.append(status)
            
        return statuses