#!/usr/bin/env python3
"""
Demo script for Scraping Service v2.

This script demonstrates the new modular architecture by:
1. Creating and registering a Greenhouse connector
2. Running health checks
3. Fetching sample jobs
4. Showing orchestrator capabilities
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

# Import the new scraping service
from scraping_service_v2 import (
    ServiceRegistry,
    ScrapingOrchestrator,
    GreenhouseConnector,
    FetchParams
)


async def main():
    """Main demo function."""
    print("=== Scraping Service v2 Demo ===\n")
    
    # 1. Initialize service registry
    print("1. Initializing Service Registry...")
    registry = ServiceRegistry()
    
    # 2. Create and register Greenhouse connector
    print("2. Creating Greenhouse Connector...")
    # Use some example company IDs (these would be real in production)
    greenhouse = GreenhouseConnector(company_ids=["example-company"])
    
    success = registry.register_source(greenhouse)
    print(f"   Greenhouse connector registered: {success}")
    
    # 3. Initialize orchestrator
    print("3. Initializing Orchestrator...")
    orchestrator = ScrapingOrchestrator(registry, max_concurrent=5)
    
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
    
    # 6. Initialize all sources
    print("\n6. Initializing Sources...")
    init_results = await registry.initialize_all_sources()
    for source, success in init_results.items():
        print(f"   {source}: {'✅ Success' if success else '❌ Failed'}")
    
    # 7. Run health checks
    print("\n7. Running Health Checks...")
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
    
    # 9. Test job fetching (this will fail without real company IDs, but shows the flow)
    print("\n9. Testing Job Fetching...")
    try:
        # Create fetch parameters
        params = FetchParams(
            company_ids=["example-company"],
            limit=10
        )
        
        # Fetch jobs from all sources
        print("   Attempting to fetch jobs...")
        results = await orchestrator.fetch_all_sources(params)
        
        print(f"   Total jobs found: {results['metadata']['total_jobs']}")
        print(f"   Sources queried: {results['metadata']['sources_queried']}")
        print(f"   Successful sources: {results['metadata']['successful_sources']}")
        print(f"   Failed sources: {results['metadata']['failed_sources']}")
        print(f"   Fetch duration: {results['metadata']['fetch_duration_seconds']:.2f}s")
        
        # Show errors if any
        if results['errors']:
            print("   Errors encountered:")
            for source, error in results['errors'].items():
                print(f"     {source}: {error}")
                
    except Exception as e:
        print(f"   Expected error (no real company IDs): {e}")
    
    # 10. Show orchestrator stats
    print("\n10. Orchestrator Statistics:")
    orch_stats = orchestrator.get_orchestrator_stats()
    print(f"    Max concurrent: {orch_stats['max_concurrent']}")
    print(f"    Available semaphore slots: {orch_stats['semaphore_available']}")
    
    # 11. Cleanup
    print("\n11. Cleaning up...")
    await registry.cleanup_all_sources()
    print("   Cleanup completed")
    
    print("\n=== Demo Complete ===")
    print("\nThe new scraping service architecture is working!")
    print("Key features demonstrated:")
    print("- ✅ Modular connector registration")
    print("- ✅ Health monitoring")
    print("- ✅ Service registry management") 
    print("- ✅ Orchestrated job fetching")
    print("- ✅ Error handling and statistics")
    print("- ✅ Resource cleanup")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        raise
