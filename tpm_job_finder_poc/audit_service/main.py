"""
Audit Service Main Entry Point

Provides main function and CLI for running the audit service.
"""

import asyncio
import logging
import sys
from pathlib import Path

from .config import load_config
from .storage import JsonFileAuditStorage
from .service import AuditService
from .api import run_server


def setup_logging(level: str = "info") -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, level.upper())
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/audit_service.log")
        ]
    )


async def create_service_from_config():
    """Create audit service from configuration."""
    config = load_config()
    
    # Create storage
    if config.storage.type == "file":
        storage = JsonFileAuditStorage(
            file_path=config.storage.file_path,
            max_file_size_mb=config.storage.max_file_size_mb,
            backup_count=config.storage.backup_count
        )
    else:
        raise ValueError(f"Unsupported storage type: {config.storage.type}")
    
    # Create service
    service = AuditService(
        storage=storage,
        service_name=config.service.service_name,
        batch_size=config.service.batch_size,
        flush_interval_seconds=config.service.flush_interval_seconds
    )
    
    return service, config


async def main():
    """Main entry point for audit service."""
    try:
        # Load config and setup logging
        config = load_config()
        setup_logging(config.api.log_level)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting audit service...")
        
        # Create service
        service, config = await create_service_from_config()
        
        # Run API server
        logger.info(f"Starting API server on {config.api.host}:{config.api.port}")
        run_server(
            audit_service=service,
            host=config.api.host,
            port=config.api.port,
            log_level=config.api.log_level
        )
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to start audit service: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())