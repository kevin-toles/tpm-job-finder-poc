"""
Service registry for managing job sources in the scraping service.

Provides dynamic registration and discovery of job sources, including
both API connectors and browser scrapers.
"""

from typing import Dict, List, Optional, Type, Any
import logging
from .base_job_source import BaseJobSource, SourceType, HealthStatus

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """
    Registry for managing job sources in the scraping service.
    
    Provides methods to register, discover, and manage different job sources
    including health monitoring and dynamic enable/disable functionality.
    """
    
    def __init__(self):
        self._sources: Dict[str, BaseJobSource] = {}
        self._source_configs: Dict[str, Dict[str, Any]] = {}
        self._health_status: Dict[str, HealthStatus] = {}
        
    def register_source(self, source: BaseJobSource, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new job source with the service.
        
        Args:
            source: The job source instance to register
            config: Optional configuration for the source
            
        Returns:
            True if registration was successful
        """
        if not isinstance(source, BaseJobSource):
            raise ValueError(f"Source must be an instance of BaseJobSource, got {type(source)}")
            
        if source.name in self._sources:
            logger.warning(f"Source '{source.name}' is already registered, replacing existing")
            
        self._sources[source.name] = source
        self._source_configs[source.name] = config or {}
        self._health_status[source.name] = HealthStatus.UNKNOWN
        
        logger.info(f"Registered job source: {source.name} ({source.source_type.value})")
        return True
        
    def unregister_source(self, source_name: str) -> bool:
        """
        Unregister a job source from the service.
        
        Args:
            source_name: Name of the source to unregister
            
        Returns:
            True if unregistration was successful
        """
        if source_name not in self._sources:
            logger.warning(f"Attempted to unregister unknown source: {source_name}")
            return False
            
        # Clean up the source
        source = self._sources[source_name]
        try:
            import asyncio
            if asyncio.iscoroutinefunction(source.cleanup):
                # Note: In real implementation, this should be handled in async context
                logger.warning(f"Source {source_name} cleanup is async, skipping")
            else:
                source.cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup of source {source_name}: {e}")
            
        # Remove from registries
        del self._sources[source_name]
        del self._source_configs[source_name]
        del self._health_status[source_name]
        
        logger.info(f"Unregistered job source: {source_name}")
        return True
        
    def get_source(self, source_name: str) -> Optional[BaseJobSource]:
        """
        Get a registered job source by name.
        
        Args:
            source_name: Name of the source to retrieve
            
        Returns:
            The job source instance or None if not found
        """
        return self._sources.get(source_name)
        
    def list_sources(self, source_type: Optional[SourceType] = None, enabled_only: bool = False) -> List[str]:
        """
        List all registered job sources.
        
        Args:
            source_type: Optional filter by source type
            enabled_only: If True, only return enabled sources
            
        Returns:
            List of source names
        """
        sources = []
        for name, source in self._sources.items():
            # Filter by type if specified
            if source_type and source.source_type != source_type:
                continue
                
            # Filter by enabled status if specified
            if enabled_only and not source.is_enabled():
                continue
                
            sources.append(name)
            
        return sorted(sources)
        
    def get_sources_by_type(self, source_type: SourceType) -> List[BaseJobSource]:
        """
        Get all sources of a specific type.
        
        Args:
            source_type: Type of sources to retrieve
            
        Returns:
            List of job source instances
        """
        return [
            source for source in self._sources.values()
            if source.source_type == source_type
        ]
        
    def enable_source(self, source_name: str) -> bool:
        """
        Enable a job source.
        
        Args:
            source_name: Name of the source to enable
            
        Returns:
            True if successful
        """
        source = self._sources.get(source_name)
        if not source:
            logger.warning(f"Cannot enable unknown source: {source_name}")
            return False
            
        source.enable()
        logger.info(f"Enabled job source: {source_name}")
        return True
        
    def disable_source(self, source_name: str) -> bool:
        """
        Disable a job source.
        
        Args:
            source_name: Name of the source to disable
            
        Returns:
            True if successful
        """
        source = self._sources.get(source_name)
        if not source:
            logger.warning(f"Cannot disable unknown source: {source_name}")
            return False
            
        source.disable()
        logger.info(f"Disabled job source: {source_name}")
        return True
        
    async def health_check_all(self) -> Dict[str, HealthStatus]:
        """
        Run health checks on all registered sources.
        
        Returns:
            Dictionary mapping source names to health status
        """
        results = {}
        
        for name, source in self._sources.items():
            try:
                health_result = await source.health_check()
                results[name] = health_result.status
                self._health_status[name] = health_result.status
                
                if health_result.status != HealthStatus.HEALTHY:
                    logger.warning(f"Source {name} health check: {health_result.message}")
                    
            except Exception as e:
                logger.error(f"Health check failed for source {name}: {e}")
                results[name] = HealthStatus.UNHEALTHY
                self._health_status[name] = HealthStatus.UNHEALTHY
                
        return results
        
    async def health_check_source(self, source_name: str) -> Optional[HealthStatus]:
        """
        Run health check on a specific source.
        
        Args:
            source_name: Name of the source to check
            
        Returns:
            Health status or None if source not found
        """
        source = self._sources.get(source_name)
        if not source:
            return None
            
        try:
            health_result = await source.health_check()
            self._health_status[source_name] = health_result.status
            return health_result.status
        except Exception as e:
            logger.error(f"Health check failed for source {source_name}: {e}")
            self._health_status[source_name] = HealthStatus.UNHEALTHY
            return HealthStatus.UNHEALTHY
            
    def get_health_status(self, source_name: str) -> Optional[HealthStatus]:
        """
        Get the last known health status for a source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Health status or None if source not found
        """
        return self._health_status.get(source_name)
        
    def get_source_config(self, source_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            Configuration dictionary or None if source not found
        """
        return self._source_configs.get(source_name)
        
    def update_source_config(self, source_name: str, config: Dict[str, Any]) -> bool:
        """
        Update the configuration for a specific source.
        
        Args:
            source_name: Name of the source
            config: New configuration dictionary
            
        Returns:
            True if successful
        """
        if source_name not in self._sources:
            logger.warning(f"Cannot update config for unknown source: {source_name}")
            return False
            
        self._source_configs[source_name] = config
        logger.info(f"Updated configuration for source: {source_name}")
        return True
        
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the registry.
        
        Returns:
            Dictionary with registry statistics
        """
        total_sources = len(self._sources)
        enabled_sources = sum(1 for source in self._sources.values() if source.is_enabled())
        
        type_counts = {}
        for source in self._sources.values():
            source_type = source.source_type.value
            type_counts[source_type] = type_counts.get(source_type, 0) + 1
            
        health_counts = {}
        for status in self._health_status.values():
            status_name = status.value
            health_counts[status_name] = health_counts.get(status_name, 0) + 1
            
        return {
            "total_sources": total_sources,
            "enabled_sources": enabled_sources,
            "disabled_sources": total_sources - enabled_sources,
            "sources_by_type": type_counts,
            "health_distribution": health_counts
        }
        
    async def initialize_all_sources(self) -> Dict[str, bool]:
        """
        Initialize all registered sources.
        
        Returns:
            Dictionary mapping source names to initialization success status
        """
        results = {}
        
        for name, source in self._sources.items():
            try:
                success = await source.initialize()
                results[name] = success
                if success:
                    logger.info(f"Successfully initialized source: {name}")
                else:
                    logger.warning(f"Failed to initialize source: {name}")
            except Exception as e:
                logger.error(f"Error initializing source {name}: {e}")
                results[name] = False
                
        return results
        
    async def cleanup_all_sources(self) -> None:
        """Clean up all registered sources."""
        for name, source in self._sources.items():
            try:
                await source.cleanup()
                logger.info(f"Cleaned up source: {name}")
            except Exception as e:
                logger.error(f"Error cleaning up source {name}: {e}")
                
    def register_default_scrapers(self) -> None:
        """Register all default browser scrapers."""
        try:
            # Import scrapers - handle both relative and absolute imports
            try:
                from ..scrapers import (
                    IndeedScraper,
                    LinkedInScraper, 
                    ZipRecruiterScraper,
                    GreenhouseScraper
                )
            except ImportError:
                # Fallback for absolute import
                from tpm_job_finder_poc.scraping_service.scrapers import (
                    IndeedScraper,
                    LinkedInScraper,
                    ZipRecruiterScraper, 
                    GreenhouseScraper
                )
            
            # Register all browser scrapers
            scrapers = [
                IndeedScraper(),
                LinkedInScraper(),
                ZipRecruiterScraper(), 
                GreenhouseScraper()
            ]
            
            for scraper in scrapers:
                self.register_source(scraper)
                logger.info(f"Registered {scraper.name} scraper")
                
        except ImportError as e:
            logger.error(f"Failed to import scrapers: {e}")


# Global service registry instance
registry = ServiceRegistry()
