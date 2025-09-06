"""
Main application entry point.

This module provides the main entry point for running the TPM Job Finder application.
"""

import asyncio
import argparse
from typing import Optional
from src.config.settings import settings, validate_settings
from src.core.search import JobSearchEngine
from src.models.job import SearchCriteria
from src.poc.sweep import JobSweeper


def setup_logging():
    """Set up application logging."""
    import logging
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


async def run_job_search(keywords: list, location: Optional[str] = None):
    """
    Run a job search with specified parameters.
    
    Args:
        keywords: List of search keywords
        location: Optional location filter
    """
    print("Starting TPM Job Finder...")
    
    # Create search criteria
    criteria = SearchCriteria(
        keywords=keywords,
        location=location,
        remote_allowed=True
    )
    
    # Initialize job sweeper
    sweeper = JobSweeper()
    
    # Perform search
    print(f"Searching for jobs with keywords: {keywords}")
    if location:
        print(f"Location filter: {location}")
    
    jobs = await sweeper.sweep_all_sources(criteria)
    
    print(f"Found {len(jobs)} job opportunities")
    
    # In a real implementation, this would:
    # 1. Display or save the results
    # 2. Send notifications if configured
    # 3. Update user preferences based on interactions


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="TPM Job Finder POC")
    parser.add_argument(
        "--keywords",
        nargs="+",
        default=["technical program manager", "tpm"],
        help="Search keywords (default: technical program manager tpm)"
    )
    parser.add_argument(
        "--location",
        help="Location filter (e.g., 'Remote', 'San Francisco', 'New York')"
    )
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Validate configuration if requested
    if args.validate_config:
        if validate_settings():
            print("✓ Configuration is valid")
            return 0
        else:
            print("✗ Configuration validation failed")
            return 1
    
    # Run job search
    try:
        asyncio.run(run_job_search(args.keywords, args.location))
        return 0
    except KeyboardInterrupt:
        print("\nSearch cancelled by user")
        return 0
    except Exception as e:
        print(f"Error during job search: {e}")
        return 1


if __name__ == "__main__":
    exit(main())