"""
Compatibility module for scraping_service_v2.

This module provides backward compatibility for imports after the scraping service
was moved to tpm_job_finder_poc.scraping_service.

All imports from scraping_service_v2 will be redirected to the new location.
"""

# Import all components from the new location and re-export them
try:
    from tpm_job_finder_poc.scraping_service import *
    from tpm_job_finder_poc.scraping_service.core.service_registry import ServiceRegistry
    from tpm_job_finder_poc.scraping_service.core.orchestrator import ScrapingOrchestrator
    from tpm_job_finder_poc.scraping_service.core.base_job_source import (
        BaseJobSource, 
        FetchParams,
        ScrapingResult,
        JobData
    )
    from tpm_job_finder_poc.scraping_service.scrapers import *
    
    # Create registry instance for backward compatibility
    registry = ServiceRegistry()
    
    # Import scrapers for backward compatibility
    from tpm_job_finder_poc.scraping_service.scrapers.indeed.scraper import IndeedScraper
    from tpm_job_finder_poc.scraping_service.scrapers.linkedin.scraper import LinkedInScraper
    from tpm_job_finder_poc.scraping_service.scrapers.ziprecruiter.scraper import ZipRecruiterScraper
    from tpm_job_finder_poc.scraping_service.scrapers.greenhouse.scraper import GreenhouseScraper
    
except ImportError as e:
    import warnings
    warnings.warn(
        f"Failed to import from new scraping service location: {e}. "
        "The scraping service may not be properly installed.",
        ImportWarning
    )
    
    # Provide dummy implementations to prevent complete failure
    class DummyServiceRegistry:
        def __init__(self):
            pass
        def get_scrapers(self):
            return []
    
    class DummyOrchestrator:
        def __init__(self):
            pass
    
    registry = DummyServiceRegistry()
    ServiceRegistry = DummyServiceRegistry
    ScrapingOrchestrator = DummyOrchestrator
