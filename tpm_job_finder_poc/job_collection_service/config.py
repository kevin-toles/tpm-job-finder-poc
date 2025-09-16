"""
Job Collection Service - Configuration management.

Handles loading and validation of service configuration from various sources.
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class JobCollectionConfig:
    """
    Configuration for job collection service.
    
    Includes settings for API aggregators, browser scrapers, storage,
    and operational parameters.
    """
    
    # General settings
    max_jobs_per_source: int = 50
    collection_timeout_seconds: int = 30
    enable_deduplication: bool = True
    enable_enrichment: bool = True
    
    # API aggregator configurations
    api_aggregators: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "remoteok": {"enabled": True},
        "greenhouse": {
            "enabled": False,
            "companies": ["airbnb", "stripe", "gitlab", "dropbox", "shopify"]
        },
        "lever": {
            "enabled": False,
            "companies": []
        },
        "ashby": {"enabled": False},
        "workable": {"enabled": False},
        "smartrecruiters": {"enabled": False}
    })
    
    # Browser scraper configurations
    browser_scrapers: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "indeed": {"enabled": False},
        "linkedin": {"enabled": False},
        "ziprecruiter": {"enabled": False},
        "greenhouse_browser": {"enabled": False}
    })
    
    # Storage configuration
    storage: Dict[str, Any] = field(default_factory=lambda: {
        "backend": "file",
        "path": "./job_storage"
    })
    
    # Enrichment configuration
    enrichment: Dict[str, Any] = field(default_factory=lambda: {
        "enable_job_classification": True,
        "enable_remote_detection": True,
        "enable_tpm_scoring": True,
        "enable_skill_extraction": False
    })
    
    # Rate limiting configuration
    rate_limits: Dict[str, Any] = field(default_factory=lambda: {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "backoff_factor": 2.0,
        "max_retries": 3
    })
    
    # Health check configuration
    health_check: Dict[str, Any] = field(default_factory=lambda: {
        "enabled": True,
        "check_interval_seconds": 300,
        "failure_threshold": 3
    })
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'JobCollectionConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            JobCollectionConfig instance
        """
        # Create instance with defaults
        config = cls()
        
        # Update with provided values
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
            else:
                logger.warning(f"Unknown configuration key: {key}")
        
        return config
    
    @classmethod
    def from_environment(cls) -> 'JobCollectionConfig':
        """
        Create configuration from environment variables.
        
        Returns:
            JobCollectionConfig instance
        """
        config = cls()
        
        # General settings
        if os.getenv('JOB_COLLECTION_MAX_JOBS_PER_SOURCE'):
            config.max_jobs_per_source = int(os.getenv('JOB_COLLECTION_MAX_JOBS_PER_SOURCE'))
        
        if os.getenv('JOB_COLLECTION_TIMEOUT_SECONDS'):
            config.collection_timeout_seconds = int(os.getenv('JOB_COLLECTION_TIMEOUT_SECONDS'))
        
        if os.getenv('JOB_COLLECTION_ENABLE_DEDUPLICATION'):
            config.enable_deduplication = os.getenv('JOB_COLLECTION_ENABLE_DEDUPLICATION').lower() == 'true'
        
        if os.getenv('JOB_COLLECTION_ENABLE_ENRICHMENT'):
            config.enable_enrichment = os.getenv('JOB_COLLECTION_ENABLE_ENRICHMENT').lower() == 'true'
        
        # Storage configuration
        if os.getenv('JOB_COLLECTION_STORAGE_BACKEND'):
            config.storage['backend'] = os.getenv('JOB_COLLECTION_STORAGE_BACKEND')
        
        if os.getenv('JOB_COLLECTION_STORAGE_PATH'):
            config.storage['path'] = os.getenv('JOB_COLLECTION_STORAGE_PATH')
        
        # API aggregator enables
        if os.getenv('JOB_COLLECTION_ENABLE_REMOTEOK'):
            config.api_aggregators['remoteok']['enabled'] = os.getenv('JOB_COLLECTION_ENABLE_REMOTEOK').lower() == 'true'
        
        if os.getenv('JOB_COLLECTION_ENABLE_GREENHOUSE'):
            config.api_aggregators['greenhouse']['enabled'] = os.getenv('JOB_COLLECTION_ENABLE_GREENHOUSE').lower() == 'true'
        
        if os.getenv('JOB_COLLECTION_ENABLE_LEVER'):
            config.api_aggregators['lever']['enabled'] = os.getenv('JOB_COLLECTION_ENABLE_LEVER').lower() == 'true'
        
        # Browser scraper enables
        if os.getenv('JOB_COLLECTION_ENABLE_INDEED'):
            config.browser_scrapers['indeed']['enabled'] = os.getenv('JOB_COLLECTION_ENABLE_INDEED').lower() == 'true'
        
        if os.getenv('JOB_COLLECTION_ENABLE_LINKEDIN'):
            config.browser_scrapers['linkedin']['enabled'] = os.getenv('JOB_COLLECTION_ENABLE_LINKEDIN').lower() == 'true'
        
        logger.info("Loaded configuration from environment variables")
        return config
    
    @classmethod
    def from_file(cls, file_path: str) -> 'JobCollectionConfig':
        """
        Create configuration from file.
        
        Args:
            file_path: Path to configuration file (JSON or YAML)
            
        Returns:
            JobCollectionConfig instance
        """
        import json
        
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    config_dict = json.load(f)
                elif file_path.endswith(('.yml', '.yaml')):
                    try:
                        import yaml
                        config_dict = yaml.safe_load(f)
                    except ImportError:
                        raise ImportError("PyYAML required for YAML configuration files")
                else:
                    raise ValueError(f"Unsupported configuration file format: {file_path}")
            
            logger.info(f"Loaded configuration from file: {file_path}")
            return cls.from_dict(config_dict)
            
        except Exception as e:
            logger.error(f"Error loading configuration from file {file_path}: {e}")
            raise
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        # Validate general settings
        if self.max_jobs_per_source <= 0:
            raise ValueError("max_jobs_per_source must be positive")
        
        if self.collection_timeout_seconds <= 0:
            raise ValueError("collection_timeout_seconds must be positive")
        
        # Validate API aggregator configuration
        if not isinstance(self.api_aggregators, dict):
            raise ValueError("api_aggregators must be a dictionary")
        
        for source_name, source_config in self.api_aggregators.items():
            if not isinstance(source_config, dict):
                raise ValueError(f"Configuration for {source_name} must be a dictionary")
            
            if 'enabled' not in source_config:
                raise ValueError(f"Configuration for {source_name} must include 'enabled' field")
        
        # Validate browser scraper configuration
        if not isinstance(self.browser_scrapers, dict):
            raise ValueError("browser_scrapers must be a dictionary")
        
        for source_name, source_config in self.browser_scrapers.items():
            if not isinstance(source_config, dict):
                raise ValueError(f"Browser scraper configuration for {source_name} must be a dictionary")
            
            if 'enabled' not in source_config:
                raise ValueError(f"Browser scraper configuration for {source_name} must include 'enabled' field")
        
        # Validate storage configuration
        if not isinstance(self.storage, dict):
            raise ValueError("storage must be a dictionary")
        
        if 'backend' not in self.storage:
            raise ValueError("storage configuration must include 'backend' field")
        
        supported_backends = ['file', 'database', 'memory']
        if self.storage['backend'] not in supported_backends:
            raise ValueError(f"storage backend must be one of: {supported_backends}")
        
        # Validate rate limits
        if not isinstance(self.rate_limits, dict):
            raise ValueError("rate_limits must be a dictionary")
        
        required_rate_limit_fields = ['requests_per_minute', 'requests_per_hour', 'backoff_factor', 'max_retries']
        for field in required_rate_limit_fields:
            if field not in self.rate_limits:
                raise ValueError(f"rate_limits must include '{field}' field")
            
            if not isinstance(self.rate_limits[field], (int, float)):
                raise ValueError(f"rate_limits.{field} must be numeric")
            
            if self.rate_limits[field] <= 0:
                raise ValueError(f"rate_limits.{field} must be positive")
        
        logger.info("Configuration validation passed")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Configuration as dictionary
        """
        return {
            'max_jobs_per_source': self.max_jobs_per_source,
            'collection_timeout_seconds': self.collection_timeout_seconds,
            'enable_deduplication': self.enable_deduplication,
            'enable_enrichment': self.enable_enrichment,
            'api_aggregators': self.api_aggregators,
            'browser_scrapers': self.browser_scrapers,
            'storage': self.storage,
            'enrichment': self.enrichment,
            'rate_limits': self.rate_limits,
            'health_check': self.health_check
        }
    
    def get_enabled_api_aggregators(self) -> List[str]:
        """
        Get list of enabled API aggregators.
        
        Returns:
            List of enabled API aggregator names
        """
        return [
            name for name, config in self.api_aggregators.items()
            if config.get('enabled', False)
        ]
    
    def get_enabled_browser_scrapers(self) -> List[str]:
        """
        Get list of enabled browser scrapers.
        
        Returns:
            List of enabled browser scraper names
        """
        return [
            name for name, config in self.browser_scrapers.items()
            if config.get('enabled', False)
        ]
    
    def get_all_enabled_sources(self) -> List[str]:
        """
        Get list of all enabled job sources.
        
        Returns:
            List of all enabled source names
        """
        return self.get_enabled_api_aggregators() + self.get_enabled_browser_scrapers()
    
    def enable_source(self, source_name: str) -> bool:
        """
        Enable a specific job source.
        
        Args:
            source_name: Name of the source to enable
            
        Returns:
            True if source was enabled
        """
        if source_name in self.api_aggregators:
            self.api_aggregators[source_name]['enabled'] = True
            logger.info(f"Enabled API aggregator: {source_name}")
            return True
        elif source_name in self.browser_scrapers:
            self.browser_scrapers[source_name]['enabled'] = True
            logger.info(f"Enabled browser scraper: {source_name}")
            return True
        else:
            logger.warning(f"Unknown source: {source_name}")
            return False
    
    def disable_source(self, source_name: str) -> bool:
        """
        Disable a specific job source.
        
        Args:
            source_name: Name of the source to disable
            
        Returns:
            True if source was disabled
        """
        if source_name in self.api_aggregators:
            self.api_aggregators[source_name]['enabled'] = False
            logger.info(f"Disabled API aggregator: {source_name}")
            return True
        elif source_name in self.browser_scrapers:
            self.browser_scrapers[source_name]['enabled'] = False
            logger.info(f"Disabled browser scraper: {source_name}")
            return True
        else:
            logger.warning(f"Unknown source: {source_name}")
            return False