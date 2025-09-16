"""
Job Aggregator Service - Main entry point.

FastAPI service for multi-source job collection and aggregation.
"""

import logging
import uvicorn
from typing import Dict, Any, Optional

from .api import app, set_service
from .service import JobAggregatorService

logger = logging.getLogger(__name__)


def create_service(config: Optional[Dict[str, Any]] = None) -> JobAggregatorService:
    """
    Create and configure the job aggregator service.
    
    Args:
        config: Service configuration
        
    Returns:
        Configured JobAggregatorService instance
    """
    return JobAggregatorService(config)


def main():
    """Main entry point for the service."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration (could be from environment, file, etc.)
    config = {
        'greenhouse_companies': [
            'airbnb', 'stripe', 'gitlab', 'dropbox', 'shopify'
        ],
        'lever_companies': [],
        'max_workers': 5
    }
    
    # Create and configure service
    service = create_service(config)
    set_service(service)
    
    # Start the server
    logger.info("Starting Job Aggregator Service...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )


if __name__ == "__main__":
    main()
