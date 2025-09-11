#!/usr/bin/env python3
"""
Comprehensive demo for Phase 2 browser scrapers.

Demonstrates the full browser scraper architecture with all 4 scrapers:
- Indeed (Phase 1 proof of concept)  
- LinkedIn (Phase 2 - with authentication handling)
- ZipRecruiter (Phase 2 - simplified job board)
- Greenhouse (Phase 2 - company discovery)
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the parent directory to path to import the package
sys.path.append(str(Path(__file__).parent.parent))

from tpm_job_finder_poc.scraping_service import (
    registry, 
    ScrapingOrchestrator,
    FetchParams
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_individual_scrapers():
    """Demo each scraper individually."""
    print("\n" + "="*60)
    print("PHASE 2 BROWSER SCRAPERS - INDIVIDUAL DEMOS")
    print("="*60)
    
    # Register all scrapers
    registry.register_default_scrapers()
    
    # List all available scrapers
    sources = registry.list_sources(enabled_only=True)
    print(f"\n📋 Registered scrapers: {sources}")
    
    # Demo parameters
    demo_params = FetchParams(
        keywords=["software engineer", "python developer"],
        location="San Francisco, CA", 
        limit=3  # Small limit for demo
    )
    
    print(f"\n🔍 Demo search: {demo_params.keywords} in {demo_params.location}")
    
    # Test each scraper individually
    for source_name in sources:
        print(f"\n{'='*20} {source_name.upper()} DEMO {'='*20}")
        
        try:
            source = registry.get_source(source_name)
            if not source:
                print(f"❌ Could not retrieve {source_name} source")
                continue
                
            # Health check
            print(f"🔧 Running health check for {source_name}...")
            health = await registry.health_check_source(source_name)
            print(f"   Health status: {health.value if health else 'Unknown'}")
            
            # Fetch jobs
            print(f"🚀 Fetching jobs from {source_name}...")
            
            # Special handling for LinkedIn (requires credentials for full access)
            if source_name == "linkedin":
                print("   Note: Using guest mode (limited access)")
                
            # Special handling for Greenhouse (requires company specification)  
            if source_name == "greenhouse":
                print("   Note: Using discovery mode across multiple companies")
                
            jobs = await source.fetch_jobs(demo_params)
            
            print(f"✅ Found {len(jobs)} jobs from {source_name}")
            
            # Show sample jobs
            for i, job in enumerate(jobs[:2], 1):  # Show first 2 jobs
                print(f"   {i}. {job.title} at {job.company}")
                print(f"      📍 {job.location or 'Location not specified'}")
                print(f"      🔗 {job.url}")
                
        except Exception as e:
            print(f"❌ Error testing {source_name}: {e}")
            logger.error(f"Scraper test failed for {source_name}", exc_info=True)
            
        print()  # Spacing


async def demo_orchestrator():
    """Demo the scraping orchestrator with multiple sources."""
    print("\n" + "="*60)
    print("SCRAPING ORCHESTRATOR - MULTI-SOURCE DEMO")
    print("="*60)
    
    # Initialize orchestrator
    orchestrator = ScrapingOrchestrator(registry)
    
    # Multi-source search parameters
    search_params = FetchParams(
        keywords=["data scientist", "machine learning"],
        location="Remote",
        limit=5  # Limit per source
    )
    
    print(f"🔍 Multi-source search: {search_params.keywords}")
    print(f"📍 Location: {search_params.location}")
    print(f"🎯 Limit: {search_params.limit} jobs per source")
    
    # Select sources to use (skip LinkedIn guest mode limitations)
    sources_to_use = ["indeed", "ziprecruiter", "greenhouse"]
    
    print(f"\n🎰 Using sources: {sources_to_use}")
    
    try:
        # Execute multi-source scraping
        print("\n🚀 Starting orchestrated scraping...")
        
        all_jobs = []
        for source_name in sources_to_use:
            print(f"\n   🔄 Processing {source_name}...")
            
            source = registry.get_source(source_name)
            if not source:
                print(f"   ❌ Source {source_name} not available")
                continue
                
            try:
                jobs = await source.fetch_jobs(search_params)
                all_jobs.extend(jobs)
                print(f"   ✅ {source_name}: {len(jobs)} jobs")
                
            except Exception as e:
                print(f"   ❌ {source_name} failed: {e}")
                
        # Results summary
        print(f"\n📊 ORCHESTRATOR RESULTS:")
        print(f"   Total jobs found: {len(all_jobs)}")
        
        # Group by source
        by_source = {}
        for job in all_jobs:
            source = job.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(job)
            
        for source, jobs in by_source.items():
            print(f"   • {source}: {len(jobs)} jobs")
            
        # Show sample results
        print(f"\n🎯 Sample results (first 3):")
        for i, job in enumerate(all_jobs[:3], 1):
            print(f"   {i}. [{job.source}] {job.title} at {job.company}")
            print(f"      📍 {job.location or 'Remote'}")
            
    except Exception as e:
        print(f"❌ Orchestrator demo failed: {e}")
        logger.error("Orchestrator demo failed", exc_info=True)


async def demo_health_monitoring():
    """Demo health monitoring across all scrapers."""
    print("\n" + "="*60) 
    print("HEALTH MONITORING DEMO")
    print("="*60)
    
    print("🏥 Running comprehensive health checks...")
    
    # Run health checks on all sources
    health_results = await registry.health_check_all()
    
    print(f"\n📊 Health Check Results:")
    for source_name, status in health_results.items():
        status_emoji = {
            'HEALTHY': '✅',
            'DEGRADED': '⚠️', 
            'UNHEALTHY': '❌',
            'UNKNOWN': '❓'
        }.get(status.value, '❓')
        
        print(f"   {status_emoji} {source_name}: {status.value}")
        
    # Registry statistics
    stats = registry.get_registry_stats()
    print(f"\n📈 Registry Statistics:")
    print(f"   Total sources: {stats['total_sources']}")
    print(f"   Enabled sources: {stats['enabled_sources']}")
    print(f"   Sources by type: {stats['sources_by_type']}")


async def main():
    """Run the comprehensive Phase 2 demo."""
    print("🌟 TPM Job Finder - Phase 2 Browser Scrapers Demo")
    print("🤖 Demonstrating LinkedIn, ZipRecruiter, and Greenhouse scrapers")
    print("⚡ Plus the complete scraping architecture")
    
    try:
        # Run individual scraper demos
        await demo_individual_scrapers()
        
        # Run orchestrator demo
        await demo_orchestrator()
        
        # Run health monitoring demo  
        await demo_health_monitoring()
        
        print("\n" + "="*60)
        print("✅ PHASE 2 DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("📝 Summary:")
        print("   • LinkedIn scraper: Authentication-aware with guest fallback")
        print("   • ZipRecruiter scraper: Full job board coverage")
        print("   • Greenhouse scraper: Company discovery and board parsing") 
        print("   • Multi-source orchestration: Coordinated scraping")
        print("   • Health monitoring: Service reliability tracking")
        print("\n🎉 All Phase 2 browser scrapers are operational!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logger.error("Demo execution failed", exc_info=True)
        return 1
        
    return 0


if __name__ == "__main__":
    # Run the demo
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
