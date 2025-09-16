#!/usr/bin/env python3
"""
Job Collection Service - Demo script.

Demonstrates the key features of the job collection service.
"""

import asyncio
import json
import logging
from typing import List

from tpm_job_finder_poc.job_collection_service import (
    create_development_service,
    JobCollectionConfig
)
from tpm_job_finder_poc.shared.contracts.job_collection_service import JobQuery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def demo_job_collection():
    """Demonstrate job collection functionality."""
    
    print("🚀 Job Collection Service Demo")
    print("=" * 50)
    
    # Create development service with RemoteOK enabled
    print("\n1. Setting up development service...")
    service = create_development_service(
        enable_sources=['remoteok'],
        storage_path='./demo_job_storage'
    )
    
    # Show initial source statuses
    print("\n2. Checking source status...")
    statuses = await service.get_source_statuses()
    for status in statuses:
        status_icon = "✅" if status.healthy else "❌"
        print(f"   {status_icon} {status.name}: {status.type.value}")
    
    # Collect jobs for TPM roles
    print("\n3. Collecting Technical Project Manager jobs...")
    tpm_query = JobQuery(
        keywords=["Technical Project Manager"],
        include_remote=True,
        max_jobs_per_source=20
    )
    
    result = await service.collect_jobs(query=tpm_query)
    
    # Determine success based on results
    success = result.total_jobs > 0 or len(result.errors) == 0
    
    if success:
        message = f"Successfully collected {result.total_jobs} jobs"
        print(f"   ✅ {message}")
        print(f"   📊 Total jobs: {result.total_jobs}")
        
        for source in result.successful_sources:
            job_count = sum(1 for job in result.jobs if job.source == source)
            print(f"   📋 {source}: {job_count} jobs")
        
        # Show first few jobs
        print("\n📋 Sample Jobs:")
        for i, job in enumerate(result.jobs[:3]):
            print(f"\n   Job {i+1}:")
            print(f"   📝 Title: {job.title}")
            print(f"   🏢 Company: {job.company}")
            print(f"   📍 Location: {job.location}")
            print(f"   🏠 Remote: {'Yes' if job.remote_friendly else 'No'}")
            print(f"   🔗 Source: {job.source}")
            if hasattr(job, 'tpm_score') and job.tpm_score:
                print(f"   ⭐ TPM Score: {job.tpm_score}/10")
    else:
        error_messages = list(result.errors.values()) if result.errors else ["Unknown error"]
        print(f"   ❌ Collection failed: {'; '.join(error_messages)}")
    
    # Search stored jobs
    print("\n4. Searching stored jobs...")
    search_query = JobQuery(
        keywords=['project manager'],
        include_remote=True,
        max_jobs_per_source=5
    )
    
    search_results = await service.search_jobs(query=search_query)
    print(f"   🔍 Found {len(search_results)} jobs matching 'project manager' + remote")
    
    # Show collection statistics
    print("\n5. Collection statistics...")
    stats = await service.get_collection_stats()
    print("   📈 Stats:")
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for sub_key, sub_value in value.items():
                print(f"     {sub_key}: {sub_value}")
        else:
            print(f"   {key}: {value}")
    
    # Test different queries
    print("\n6. Testing different job queries...")
    
    test_queries = [
        JobQuery(keywords=["Product Manager"], location="San Francisco", max_jobs_per_source=10),
        JobQuery(keywords=["Software Engineer"], include_remote=True, max_jobs_per_source=15),
        JobQuery(keywords=["Data Scientist"], location="New York", max_jobs_per_source=8)
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query.keywords[0] if query.keywords else 'No keywords'}")
        if query.location:
            print(f"   📍 Location: {query.location}")
        if query.include_remote:
            print(f"   🏠 Remote friendly")
        
        query_result = await service.collect_jobs(query=query)
        query_success = query_result.total_jobs > 0 or len(query_result.errors) == 0
        if query_success:
            print(f"   ✅ Found {query_result.total_jobs} jobs")
        else:
            error_messages = list(query_result.errors.values()) if query_result.errors else ["Unknown error"]
            print(f"   ❌ Failed: {'; '.join(error_messages)}")
    
    # Final statistics
    print("\n7. Final statistics...")
    final_stats = await service.get_collection_stats()
    print(f"   📊 Total jobs collected: {final_stats.get('total_jobs', 0)}")
    print(f"   📊 Total sources: {final_stats.get('total_sources', 0)}")
    
    print("\n✅ Demo completed successfully!")
    print("\n💡 Try the CLI:")
    print("   python -m tpm_job_finder_poc.job_collection_service.main collect 'Technical Project Manager' --remote-only")
    print("\n💡 Try the API:")
    print("   python -m tpm_job_finder_poc.job_collection_service.main serve")
    print("   curl http://localhost:8000/health")


async def demo_api_endpoints():
    """Demonstrate API endpoints (requires API server to be running)."""
    
    print("\n🌐 API Endpoints Demo")
    print("=" * 30)
    print("Start the API server first:")
    print("python -m tpm_job_finder_poc.job_collection_service.main serve\n")
    
    print("Available endpoints:")
    endpoints = [
        "GET  /health - Health check",
        "POST /collect - Collect jobs",
        "GET  /jobs - List stored jobs",
        "GET  /jobs/{id} - Get specific job",
        "GET  /sources - List job sources",
        "PUT  /sources/{name} - Configure source",
        "GET  /statistics - Collection stats",
        "POST /background-collect - Background collection",
        "DELETE /jobs?confirm=true - Clear all jobs"
    ]
    
    for endpoint in endpoints:
        print(f"   {endpoint}")
    
    print("\nExample API calls:")
    
    api_examples = [
        {
            "description": "Collect TPM jobs",
            "method": "POST",
            "url": "http://localhost:8000/collect",
            "data": {
                "query": "Technical Project Manager",
                "remote_only": True,
                "max_jobs": 25
            }
        },
        {
            "description": "Get stored jobs",
            "method": "GET", 
            "url": "http://localhost:8000/jobs?remote_only=true&limit=10"
        },
        {
            "description": "Check health",
            "method": "GET",
            "url": "http://localhost:8000/health"
        },
        {
            "description": "Get statistics",
            "method": "GET",
            "url": "http://localhost:8000/statistics"
        },
        {
            "description": "List sources",
            "method": "GET",
            "url": "http://localhost:8000/sources"
        }
    ]
    
    for example in api_examples:
        print(f"\n   {example['description']}:")
        if example['method'] == 'POST' and 'data' in example:
            print(f"   curl -X {example['method']} \"{example['url']}\" \\")
            print(f"     -H \"Content-Type: application/json\" \\")
            print(f"     -d '{json.dumps(example['data'])}'")
        else:
            print(f"   curl {example['url']}")


async def demo_configuration():
    """Demonstrate configuration options."""
    
    print("\n⚙️  Configuration Demo")
    print("=" * 25)
    
    # Default configuration
    print("\n1. Default configuration:")
    default_config = JobCollectionConfig()
    print(f"   Max jobs per source: {default_config.max_jobs_per_source}")
    print(f"   Collection timeout: {default_config.collection_timeout_seconds}s")
    print(f"   Deduplication: {default_config.enable_deduplication}")
    print(f"   Enrichment: {default_config.enable_enrichment}")
    
    # Enabled sources
    print(f"\n   Enabled API aggregators: {default_config.get_enabled_api_aggregators()}")
    print(f"   Enabled browser scrapers: {default_config.get_enabled_browser_scrapers()}")
    
    # Custom configuration
    print("\n2. Custom configuration example:")
    custom_config_dict = {
        'max_jobs_per_source': 100,
        'collection_timeout_seconds': 60,
        'enable_deduplication': True,
        'enable_enrichment': True,
        'api_aggregators': {
            'remoteok': {'enabled': True},
            'greenhouse': {'enabled': True},
            'lever': {'enabled': False}
        },
        'storage': {
            'backend': 'file',
            'path': './custom_storage'
        }
    }
    
    custom_config = JobCollectionConfig.from_dict(custom_config_dict)
    print(f"   Max jobs per source: {custom_config.max_jobs_per_source}")
    print(f"   Enabled sources: {custom_config.get_all_enabled_sources()}")
    
    # Environment configuration
    print("\n3. Environment variable configuration:")
    print("   Set these environment variables:")
    env_vars = [
        "JOB_COLLECTION_MAX_JOBS_PER_SOURCE=50",
        "JOB_COLLECTION_ENABLE_REMOTEOK=true",
        "JOB_COLLECTION_ENABLE_GREENHOUSE=false",
        "JOB_COLLECTION_STORAGE_PATH=./job_storage"
    ]
    
    for var in env_vars:
        print(f"   export {var}")


async def main():
    """Run the complete demo."""
    try:
        await demo_job_collection()
        await demo_api_endpoints()
        await demo_configuration()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")


if __name__ == '__main__':
    asyncio.run(main())