"""
Job Collection Service - Dependency injection and service builders.

Provides factory functions and builders for creating service components.
"""

import logging
import os
from typing import Optional, Dict, Any

from .service import JobCollectionService
from .storage import JobStorage
from .enricher import JobEnricher
from .config import JobCollectionConfig
from .api import create_job_collection_api

logger = logging.getLogger(__name__)


class JobCollectionServiceBuilder:
    """Builder for job collection service components."""
    
    def __init__(self):
        """Initialize builder."""
        self._config: Optional[JobCollectionConfig] = None
        self._storage: Optional[JobStorage] = None
        self._enricher: Optional[JobEnricher] = None
    
    def with_config(self, config: JobCollectionConfig) -> 'JobCollectionServiceBuilder':
        """
        Set configuration.
        
        Args:
            config: Service configuration
            
        Returns:
            Builder instance
        """
        self._config = config
        return self
    
    def with_config_from_file(self, file_path: str) -> 'JobCollectionServiceBuilder':
        """
        Set configuration from file.
        
        Args:
            file_path: Path to configuration file
            
        Returns:
            Builder instance
        """
        self._config = JobCollectionConfig.from_file(file_path)
        return self
    
    def with_config_from_environment(self) -> 'JobCollectionServiceBuilder':
        """
        Set configuration from environment variables.
        
        Returns:
            Builder instance
        """
        self._config = JobCollectionConfig.from_environment()
        return self
    
    def with_default_config(self) -> 'JobCollectionServiceBuilder':
        """
        Set default configuration.
        
        Returns:
            Builder instance
        """
        self._config = JobCollectionConfig()
        return self
    
    def with_storage(self, storage: JobStorage) -> 'JobCollectionServiceBuilder':
        """
        Set storage component.
        
        Args:
            storage: Storage instance
            
        Returns:
            Builder instance
        """
        self._storage = storage
        return self
    
    def with_enricher(self, enricher: JobEnricher) -> 'JobCollectionServiceBuilder':
        """
        Set enricher component.
        
        Args:
            enricher: Enricher instance
            
        Returns:
            Builder instance
        """
        self._enricher = enricher
        return self
    
    def build_storage(self) -> JobStorage:
        """
        Build storage component.
        
        Returns:
            Storage instance
        """
        if not self._config:
            raise ValueError("Configuration required to build storage")
        
        storage_config = self._config.storage
        storage_type = storage_config.get('backend', 'file')
        
        if storage_type == 'file':
            storage_path = storage_config.get('path', './job_storage')
            return JobStorage(storage_path)
        elif storage_type == 'memory':
            return JobStorage(':memory:')
        else:
            raise ValueError(f"Unsupported storage backend: {storage_type}")
    
    def build_enricher(self) -> JobEnricher:
        """
        Build enricher component.
        
        Returns:
            Enricher instance
        """
        if not self._config:
            raise ValueError("Configuration required to build enricher")
        
        enrichment_config = self._config.enrichment
        return JobEnricher(enrichment_config)
    
    def build_service(self) -> JobCollectionService:
        """
        Build job collection service.
        
        Returns:
            Service instance
        """
        if not self._config:
            raise ValueError("Configuration required to build service")
        
        # Validate configuration
        self._config.validate()
        
        # Build components if not provided
        if not self._storage:
            self._storage = self.build_storage()
        
        if not self._enricher:
            self._enricher = self.build_enricher()
        
        return JobCollectionService(
            config=self._config,
            storage=self._storage,
            enricher=self._enricher
        )
    
    def build_api(self) -> Any:
        """
        Build FastAPI application.
        
        Returns:
            FastAPI application
        """
        service = self.build_service()
        return create_job_collection_api(service, self._config)
    
    def build_all(self) -> Dict[str, Any]:
        """
        Build all components.
        
        Returns:
            Dictionary with all components
        """
        service = self.build_service()
        api = create_job_collection_api(service, self._config)
        
        return {
            'config': self._config,
            'storage': self._storage,
            'enricher': self._enricher,
            'service': service,
            'api': api
        }


def create_job_collection_service(
    config_source: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    storage_path: Optional[str] = None
) -> JobCollectionService:
    """
    Create job collection service with automatic dependency injection.
    
    Args:
        config_source: Configuration source ('env', 'file:<path>', or None for defaults)
        config_dict: Configuration dictionary (overrides config_source)
        storage_path: Override storage path
        
    Returns:
        Configured service instance
    """
    builder = JobCollectionServiceBuilder()
    
    # Configure based on source
    if config_dict:
        config = JobCollectionConfig.from_dict(config_dict)
        builder.with_config(config)
    elif config_source == 'env':
        builder.with_config_from_environment()
    elif config_source and config_source.startswith('file:'):
        file_path = config_source[5:]  # Remove 'file:' prefix
        builder.with_config_from_file(file_path)
    else:
        builder.with_default_config()
    
    # Override storage path if provided
    if storage_path:
        if not builder._config:
            builder.with_default_config()
        builder._config.storage['path'] = storage_path
    
    return builder.build_service()


def create_job_collection_api_app(
    config_source: Optional[str] = None,
    config_dict: Optional[Dict[str, Any]] = None,
    storage_path: Optional[str] = None
) -> Any:
    """
    Create job collection API application with automatic dependency injection.
    
    Args:
        config_source: Configuration source ('env', 'file:<path>', or None for defaults)
        config_dict: Configuration dictionary (overrides config_source)
        storage_path: Override storage path
        
    Returns:
        FastAPI application
    """
    builder = JobCollectionServiceBuilder()
    
    # Configure based on source
    if config_dict:
        config = JobCollectionConfig.from_dict(config_dict)
        builder.with_config(config)
    elif config_source == 'env':
        builder.with_config_from_environment()
    elif config_source and config_source.startswith('file:'):
        file_path = config_source[5:]  # Remove 'file:' prefix
        builder.with_config_from_file(file_path)
    else:
        builder.with_default_config()
    
    # Override storage path if provided
    if storage_path:
        if not builder._config:
            builder.with_default_config()
        builder._config.storage['path'] = storage_path
    
    return builder.build_api()


def create_development_service(
    enable_sources: Optional[list] = None,
    storage_path: Optional[str] = None
) -> JobCollectionService:
    """
    Create job collection service with development configuration.
    
    Args:
        enable_sources: List of sources to enable (default: ['remoteok'])
        storage_path: Storage path (default: './dev_job_storage')
        
    Returns:
        Development-configured service
    """
    if enable_sources is None:
        enable_sources = ['remoteok']
    
    if storage_path is None:
        storage_path = './dev_job_storage'
    
    # Create development configuration
    config_dict = {
        'max_jobs_per_source': 20,
        'collection_timeout_seconds': 30,
        'enable_deduplication': True,
        'enable_enrichment': True,
        'storage': {
            'backend': 'file',
            'path': storage_path
        },
        'api_aggregators': {
            'remoteok': {'enabled': 'remoteok' in enable_sources},
            'greenhouse': {'enabled': 'greenhouse' in enable_sources},
            'lever': {'enabled': 'lever' in enable_sources}
        },
        'browser_scrapers': {
            'indeed': {'enabled': 'indeed' in enable_sources},
            'linkedin': {'enabled': 'linkedin' in enable_sources}
        }
    }
    
    return create_job_collection_service(config_dict=config_dict)


def create_production_service(
    config_file_path: Optional[str] = None
) -> JobCollectionService:
    """
    Create job collection service with production configuration.
    
    Args:
        config_file_path: Path to production configuration file
        
    Returns:
        Production-configured service
    """
    if config_file_path and os.path.exists(config_file_path):
        return create_job_collection_service(config_source=f'file:{config_file_path}')
    else:
        # Use environment variables for production
        return create_job_collection_service(config_source='env')


def create_test_service(
    storage_path: Optional[str] = None
) -> JobCollectionService:
    """
    Create job collection service for testing.
    
    Args:
        storage_path: Test storage path (default: memory)
        
    Returns:
        Test-configured service
    """
    if storage_path is None:
        storage_path = ':memory:'
    
    config_dict = {
        'max_jobs_per_source': 5,
        'collection_timeout_seconds': 5,
        'enable_deduplication': True,
        'enable_enrichment': False,  # Disable for faster tests
        'storage': {
            'backend': 'memory' if storage_path == ':memory:' else 'file',
            'path': storage_path
        },
        'api_aggregators': {
            'remoteok': {'enabled': True}
        },
        'browser_scrapers': {
            'indeed': {'enabled': False},
            'linkedin': {'enabled': False}
        }
    }
    
    return create_job_collection_service(config_dict=config_dict)


# Convenience factory functions
def build_with_defaults() -> JobCollectionService:
    """Build service with default configuration."""
    return JobCollectionServiceBuilder().with_default_config().build_service()


def build_from_env() -> JobCollectionService:
    """Build service from environment variables."""
    return JobCollectionServiceBuilder().with_config_from_environment().build_service()


def build_from_file(file_path: str) -> JobCollectionService:
    """Build service from configuration file."""
    return JobCollectionServiceBuilder().with_config_from_file(file_path).build_service()


def build_api_with_defaults() -> Any:
    """Build API with default configuration."""
    return JobCollectionServiceBuilder().with_default_config().build_api()


def build_api_from_env() -> Any:
    """Build API from environment variables."""
    return JobCollectionServiceBuilder().with_config_from_environment().build_api()