"""Job Normalizer Service Package.

This package provides a comprehensive microservice for job normalization,
validation, and deduplication functionality.

Components:
- service: Core service implementation
- config: Configuration management
- api: REST API endpoints

Usage:
    from tpm_job_finder_poc.job_normalizer_service import JobNormalizerService
    from tpm_job_finder_poc.job_normalizer_service.config import JobNormalizerServiceConfig
    
    config = JobNormalizerServiceConfig()
    service = JobNormalizerService(config)
    await service.start()
"""

from .service import JobNormalizerService
from .config import JobNormalizerServiceConfig
from .api import app

__all__ = ['JobNormalizerService', 'JobNormalizerServiceConfig', 'app']