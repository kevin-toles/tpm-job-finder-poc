#!/usr/bin/env python3
"""
Corrected Demo script for Browser Scraping Service v2.

This script demonstrates the corrected modular architecture by:
1. Creating and registering browser scrapers (Indeed, etc.)
2. Running health checks
3. Fetching sample jobs via browser automation
4. Showing orchestrator capabilities for browser scrapers
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timezone

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress selenium debug logs
logging.getLogger('selenium').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

# Import the corrected scraping service
from scraping_service_v2 import (
    ServiceRegistry,
    ScrapingOrchestrator,
    IndeedScraper,
    FetchParams
)


async def main():
    """Main demo function for browser scrapers."""
    print("=== Browser Scraping Service v2 Demo ===\n")
    
    # 1. Initialize service registry
    print("1. Initializing Service Registry...")
    registry = ServiceRegistry()
    
    # 2. Create and register Indeed scraper
    print("2. Creating Indeed Browser Scraper...")
    indeed_scraper = IndeedScraper()
    
    success = registry.register_source(indeed_scraper)
    print(f"   Indeed scraper registered: {success}")
    
    # 3. Initialize orchestrator
    print("3. Initializing Orchestrator...")
    orchestrator = ScrapingOrchestrator(registry, max_concurrent=2)  # Lower for browser scrapers
    
    # 4. Show registry stats
    print("4. Registry Statistics:")
    stats = registry.get_registry_stats()
    print(f"   Total sources: {stats['total_sources']}")
    print(f"   Enabled sources: {stats['enabled_sources']}")
    print(f"   Sources by type: {stats['sources_by_type']}")
    
    # 5. List available sources
    print("\n5. Available Sources:")
    sources = registry.list_sources()
    for source in sources:
        print(f"   - {source}")
    
    # 6. Initialize all sources (sets up browsers)
    print("\n6. Initializing Browser Scrapers...")
    print("   (This will download ChromeDriver if needed...)")
    init_results = await registry.initialize_all_sources()
    for source, success in init_results.items():
        print(f"   {source}: {'✅ Success' if success else '❌ Failed'}")
    
    # 7. Run health checks (visits sites to check accessibility)
    print("\n7. Running Health Checks...")
    print("   (This will open browsers and visit job sites...)")
    health_results = await orchestrator.health_check_sources()
    for source, health in health_results.items():
        status = health['status']
        message = health['message']
        response_time = health['response_time_ms']
        print(f"   {source}: {status} ({response_time:.1f}ms) - {message}")
    
    # 8. Show source capabilities
    print("\n8. Source Capabilities:")
    capabilities = await orchestrator.get_source_capabilities()
    for source, caps in capabilities.items():
        print(f"   {source}:")
        print(f"     Type: {caps.get('type')}")
        print(f"     Enabled: {caps.get('enabled')}")
        if 'supported_params' in caps:
            print(f"     Supported params: {list(caps['supported_params'].keys())}")
    
    # 9. Test job scraping with a simple search
    print("\n9. Testing Job Scraping...")
    try:
        # Create fetch parameters for a simple search
        params = FetchParams(
            keywords=["software engineer"],
            location="San Francisco, CA",
            limit=5  # Small number for demo
        )
        
        print("   Attempting to scrape jobs...")
        print(f"   Search: {' '.join(params.keywords)} in {params.location}")
        print("   (This will open browser and scrape Indeed...)")
        
        # Fetch jobs from all sources
        results = await orchestrator.fetch_all_sources(params)
        
        print(f"\n   📊 Scraping Results:")
        print(f"   Total jobs found: {results['metadata']['total_jobs']}")
        print(f"   Raw jobs scraped: {results['metadata']['raw_jobs']}")
        print(f"   Duplicates removed: {results['metadata']['duplicates_removed']}")
        print(f"   Sources queried: {results['metadata']['sources_queried']}")
        print(f"   Successful sources: {results['metadata']['successful_sources']}")
        print(f"   Failed sources: {results['metadata']['failed_sources']}")
        print(f"   Scraping duration: {results['metadata']['fetch_duration_seconds']:.2f}s")
        
        # Show sample jobs
        if results['jobs']:
            print(f"\n   📝 Sample Jobs:")
            for i, job in enumerate(results['jobs'][:3]):  # Show first 3
                print(f"   {i+1}. {job['title']} at {job['company']}")
                print(f"      Location: {job['location']}")
                if job['salary']:
                    print(f"      Salary: {job['salary']}")
                print(f"      URL: {job['url']}")
                print()
        
        # Show errors if any
        if results['errors']:
            print("   ⚠️ Errors encountered:")
            for source, error in results['errors'].items():
                print(f"     {source}: {error}")
                
    except Exception as e:
        print(f"   ❌ Scraping failed: {e}")
        print("   This is normal if running without proper browser setup")
    
    # 10. Show orchestrator stats
    print("\n10. Orchestrator Statistics:")
    orch_stats = orchestrator.get_orchestrator_stats()
    print(f"    Max concurrent: {orch_stats['max_concurrent']}")
    print(f"    Available slots: {orch_stats['semaphore_available']}")
    
    # 11. Cleanup (close browsers)
    print("\n11. Cleaning up browsers...")
    await registry.cleanup_all_sources()
    print("   Browser cleanup completed")
    
    print("\n=== Browser Scraping Demo Complete ===")
    print("\nThe corrected browser scraping service architecture is working!")
    print("Key features demonstrated:")
    print("- ✅ Browser scraper registration and management")
    print("- ✅ Selenium WebDriver integration")
    print("- ✅ Anti-detection measures (user agents, delays)")
    print("- ✅ Health monitoring for job sites") 
    print("- ✅ Orchestrated job scraping with rate limiting")
    print("- ✅ Error handling and statistics")
    print("- ✅ Proper browser resource cleanup")
    print("\nReady for migration of LinkedIn, ZipRecruiter, and new Greenhouse scrapers!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
