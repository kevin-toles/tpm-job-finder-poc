"""
Job Collection Service - Main module.

A microservice for collecting job postings from multiple sources including
API aggregators and browser scrapers.
"""

from .service import JobCollectionService
from .storage import JobStorage
from .enricher import JobEnricher
from .config import JobCollectionConfig
from .api import JobCollectionAPI, create_job_collection_api
from .builders import (
    JobCollectionServiceBuilder,
    create_job_collection_service,
    create_job_collection_api_app,
    create_development_service,
    create_production_service,
    create_test_service,
    build_with_defaults,
    build_from_env,
    build_from_file,
    build_api_with_defaults,
    build_api_from_env
)

__version__ = "1.0.0"
__all__ = [
    # Core service
    "JobCollectionService",
    "JobStorage", 
    "JobEnricher",
    "JobCollectionConfig",
    
    # API
    "JobCollectionAPI",
    "create_job_collection_api",
    
    # Builders and factories
    "JobCollectionServiceBuilder",
    "create_job_collection_service",
    "create_job_collection_api_app",
    "create_development_service",
    "create_production_service", 
    "create_test_service",
    "build_with_defaults",
    "build_from_env",
    "build_from_file",
    "build_api_with_defaults",
    "build_api_from_env"
]