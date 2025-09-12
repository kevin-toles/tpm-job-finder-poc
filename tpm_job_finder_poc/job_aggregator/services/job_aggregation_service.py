"""Service for aggregating jobs from both API-based sources and web scraping."""

import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting
from tpm_job_finder_poc.job_aggregator.services.job_scraping_service import JobScrapingService

# Import API-based connectors
from tpm_job_finder_poc.job_aggregator.aggregators.adzuna import AdzunaConnector
from tpm_job_finder_poc.job_aggregator.aggregators.ashby import AshbyConnector
from tpm_job_finder_poc.job_aggregator.aggregators.careerjet import CareerjetConnector
from tpm_job_finder_poc.job_aggregator.aggregators.jooble import JoobleConnector
from tpm_job_finder_poc.job_aggregator.aggregators.recruitee import RecruiteeConnector
from tpm_job_finder_poc.job_aggregator.aggregators.smartrecruiters import SmartRecruitersConnector
from tpm_job_finder_poc.job_aggregator.aggregators.usajobs import USAJobsConnector
from tpm_job_finder_poc.job_aggregator.aggregators.workable import WorkableConnector

class JobAggregationService:
    """Service for aggregating jobs from all available sources."""
    
    def __init__(
        self,
        search_terms: List[str],
        location: Optional[str] = None,
        api_config: Optional[dict] = None,
        scraping_sources: Optional[List[str]] = None
    ):
        """Initialize the job aggregation service.
        
        Args:
            search_terms: List of job titles/keywords to search for
            location: Optional location filter
            api_config: Configuration for API-based connectors including:
                - adzuna: {"app_id": str, "app_key": str}
                - careerjet: {"affiliate_id": str, "locales": List[str]}
                - jooble: {"api_key": str}
                - usajobs: {"user_agent": str, "api_key": str}
                - smartrecruiters: {"companies": List[str]}
                - ashby: {"board_names": List[str]}
                - workable: {"subdomains": List[str]}
                - recruitee: {"subdomains": List[str]}
            scraping_sources: Optional list of job boards to scrape
        """
        self.search_terms = search_terms
        self.location = location
        self.api_config = api_config or {}
        
        # Initialize API-based connectors
        self.api_connectors = []
        
        if "adzuna" in self.api_config:
            cfg = self.api_config["adzuna"]
            self.api_connectors.append(
                AdzunaConnector(cfg["app_id"], cfg["app_key"])
            )
            
        if "careerjet" in self.api_config:
            cfg = self.api_config["careerjet"]
            self.api_connectors.append(
                CareerjetConnector(
                    affiliate_id=cfg["affiliate_id"],
                    locales=cfg.get("locales", ["en_US", "en_GB", "en_CA", "en_AU", "en_SG"])
                )
            )
            
        if "jooble" in self.api_config:
            self.api_connectors.append(
                JoobleConnector(self.api_config["jooble"]["api_key"])
            )
            
        if "usajobs" in self.api_config:
            cfg = self.api_config["usajobs"]
            self.api_connectors.append(
                USAJobsConnector(cfg["user_agent"], cfg["api_key"])
            )
            
        if "smartrecruiters" in self.api_config:
            for company in self.api_config["smartrecruiters"]["companies"]:
                self.api_connectors.append(SmartRecruitersConnector(company))
                
        if "ashby" in self.api_config:
            for board in self.api_config["ashby"]["board_names"]:
                self.api_connectors.append(AshbyConnector(board))
                
        if "workable" in self.api_config:
            for subdomain in self.api_config["workable"]["subdomains"]:
                self.api_connectors.append(WorkableConnector(subdomain))
                
        if "recruitee" in self.api_config:
            for subdomain in self.api_config["recruitee"]["subdomains"]:
                self.api_connectors.append(RecruiteeConnector(subdomain))
                
        # Initialize scraping service
        self.scraping_service = JobScrapingService(
            search_terms=search_terms,
            location=location,
            sources=scraping_sources
        )
        
    async def fetch_all_jobs(self) -> List[Dict[str, Any]]:
        """Fetch jobs from all sources - both API-based and scraped.
        
        Returns:
            Combined list of jobs from all sources
        """
        all_jobs = []
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        # Fetch from API-based sources
        for connector in self.api_connectors:
            try:
                if hasattr(connector, 'fetch_since'):
                    jobs = connector.fetch_since(week_ago)
                else:
                    jobs = connector.fetch_jobs()
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error from {connector.__class__.__name__}: {str(e)}")
                continue
                
        # Fetch from scraping sources
        try:
            scraped_jobs = await self.scraping_service.fetch_all_jobs()
            all_jobs.extend(scraped_jobs)
        except Exception as e:
            print(f"Error from scraping service: {str(e)}")
            
        return all_jobs
        
    def deduplicate_jobs(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on URL.
        
        Args:
            jobs: List of jobs to deduplicate
            
        Returns:
            Deduplicated list of jobs
        """
        seen_urls = set()
        unique_jobs = []
        
        for job in jobs:
            job_url = job.get('url', '')
            if job_url and job_url not in seen_urls:
                seen_urls.add(job_url)
                unique_jobs.append(job)
                
        return unique_jobs
