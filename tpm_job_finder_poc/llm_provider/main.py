"""
LLM Provider Service Main Entry Point
Standalone microservice runner for LLM provider management
"""

import uvicorn
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for LLM Provider Service"""
    try:
        logger.info("Starting LLM Provider Service...")
        
        uvicorn.run(
            "tpm_job_finder_poc.llm_provider.api:app",
            host="0.0.0.0",
            port=8003,  # Unique port for LLM provider service
            reload=False,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"Failed to start LLM Provider Service: {e}")
        raise


if __name__ == "__main__":
    main()