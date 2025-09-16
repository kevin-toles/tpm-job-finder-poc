"""
Job Collection Service - Main CLI interface and application entry point.

Provides command-line interface for job collection operations.
"""

import asyncio
import logging
import sys
import json
from typing import Optional, List
import click
from datetime import datetime

from .builders import (
    create_job_collection_service,
    create_job_collection_api_app,
    create_development_service,
    create_production_service,
    create_test_service
)
from .config import JobCollectionConfig
from ..shared.contracts.job_collection_service import JobQuery

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config', '-c', help='Configuration file path')
@click.option('--storage', '-s', help='Storage directory path')
@click.pass_context
def cli(ctx, verbose, config, storage):
    """Job Collection Service CLI."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Store common options in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['storage'] = storage


@cli.command()
@click.argument('query')
@click.option('--sources', '-s', multiple=True, help='Specific sources to search')
@click.option('--max-jobs', '-m', type=int, help='Maximum number of jobs to collect')
@click.option('--location', '-l', help='Job location filter')
@click.option('--remote-only', '-r', is_flag=True, help='Filter for remote jobs only')
@click.option('--output', '-o', help='Output file path (JSON format)')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']), default='table', help='Output format')
@click.pass_context
def collect(ctx, query, sources, max_jobs, location, remote_only, output, format):
    """Collect jobs based on query."""
    
    async def run_collection():
        try:
            # Create service
            if ctx.obj['config']:
                service = create_job_collection_service(config_source=f"file:{ctx.obj['config']}")
            else:
                service = create_development_service(storage_path=ctx.obj['storage'])
            
            # Create job query
            job_query = JobQuery(
                keywords=query,
                location=location,
                remote_only=remote_only or False,
                max_results=max_jobs or 50
            )
            
            # Collect jobs
            click.echo(f"Collecting jobs for query: {query}")
            if sources:
                click.echo(f"Using sources: {', '.join(sources)}")
            
            result = await service.collect_jobs(
                query=job_query,
                sources=list(sources) if sources else None
            )
            
            if result.success:
                click.echo(f"✅ {result.message}")
                click.echo(f"Total jobs collected: {len(result.jobs)}")
                
                for source, count in result.jobs_by_source.items():
                    click.echo(f"  - {source}: {count} jobs")
                
                # Output results
                if output:
                    await _save_jobs_to_file(result.jobs, output, format)
                    click.echo(f"Results saved to: {output}")
                else:
                    _display_jobs(result.jobs, format)
                    
            else:
                click.echo(f"❌ Collection failed: {result.message}")
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"Collection failed: {e}")
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(run_collection())


@cli.command()
@click.option('--query', '-q', help='Search query filter')
@click.option('--source', '-s', help='Job source filter')
@click.option('--location', '-l', help='Location filter')
@click.option('--remote-only', '-r', is_flag=True, help='Remote jobs only')
@click.option('--limit', type=int, default=100, help='Maximum number of jobs to return')
@click.option('--offset', type=int, default=0, help='Number of jobs to skip')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'table']), default='table', help='Output format')
@click.pass_context
def search(ctx, query, source, location, remote_only, limit, offset, output, format):
    """Search stored jobs."""
    
    async def run_search():
        try:
            # Create service
            if ctx.obj['config']:
                service = create_job_collection_service(config_source=f"file:{ctx.obj['config']}")
            else:
                service = create_development_service(storage_path=ctx.obj['storage'])
            
            # Build filters
            filters = {}
            if query:
                filters['query'] = query
            if source:
                filters['source'] = source
            if location:
                filters['location'] = location
            if remote_only:
                filters['remote_only'] = True
            
            # Search jobs
            jobs = await service.search_jobs(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            click.echo(f"Found {len(jobs)} jobs")
            
            # Output results
            if output:
                await _save_jobs_to_file(jobs, output, format)
                click.echo(f"Results saved to: {output}")
            else:
                _display_jobs(jobs, format)
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(run_search())


@cli.command()
@click.pass_context
def sources(ctx):
    """List available job sources and their status."""
    
    async def run_sources():
        try:
            # Create service
            if ctx.obj['config']:
                service = create_job_collection_service(config_source=f"file:{ctx.obj['config']}")
            else:
                service = create_development_service(storage_path=ctx.obj['storage'])
            
            # Get source statuses
            statuses = await service.get_source_statuses()
            
            click.echo("Job Sources:")
            click.echo("=" * 50)
            
            for source_name, status in statuses.items():
                status_icon = "✅" if status.is_healthy else "❌"
                click.echo(f"{status_icon} {source_name}")
                click.echo(f"    Type: {status.source_type}")
                click.echo(f"    Status: {status.status}")
                if status.last_check:
                    click.echo(f"    Last Check: {status.last_check}")
                if status.error_message:
                    click.echo(f"    Error: {status.error_message}")
                click.echo()
                
        except Exception as e:
            logger.error(f"Failed to get sources: {e}")
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(run_sources())


@cli.command()
@click.pass_context
def stats(ctx):
    """Show collection statistics."""
    
    async def run_stats():
        try:
            # Create service
            if ctx.obj['config']:
                service = create_job_collection_service(config_source=f"file:{ctx.obj['config']}")
            else:
                service = create_development_service(storage_path=ctx.obj['storage'])
            
            # Get statistics
            statistics = await service.get_collection_statistics()
            
            click.echo("Collection Statistics:")
            click.echo("=" * 30)
            
            for key, value in statistics.items():
                if isinstance(value, dict):
                    click.echo(f"{key}:")
                    for sub_key, sub_value in value.items():
                        click.echo(f"  {sub_key}: {sub_value}")
                else:
                    click.echo(f"{key}: {value}")
                    
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(run_stats())


@cli.command()
@click.option('--port', '-p', type=int, default=8000, help='Port to run API server on')
@click.option('--host', '-h', default='127.0.0.1', help='Host to bind API server to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
@click.pass_context
def serve(ctx, port, host, reload):
    """Start API server."""
    try:
        import uvicorn
        
        # Create API app
        if ctx.obj['config']:
            app = create_job_collection_api_app(config_source=f"file:{ctx.obj['config']}")
        else:
            app = create_job_collection_api_app(storage_path=ctx.obj['storage'])
        
        click.echo(f"Starting API server on http://{host}:{port}")
        click.echo("Press Ctrl+C to stop")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload
        )
        
    except ImportError:
        click.echo("❌ uvicorn required for API server. Install with: pip install uvicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        click.echo(f"❌ Error: {e}")
        sys.exit(1)


@cli.command()
@click.option('--confirm', is_flag=True, help='Confirm deletion')
@click.pass_context
def clear(ctx, confirm):
    """Clear all stored jobs."""
    
    if not confirm:
        click.echo("⚠️  This will delete all stored jobs.")
        if not click.confirm("Are you sure?"):
            return
    
    async def run_clear():
        try:
            # Create service
            if ctx.obj['config']:
                service = create_job_collection_service(config_source=f"file:{ctx.obj['config']}")
            else:
                service = create_development_service(storage_path=ctx.obj['storage'])
            
            # Clear jobs
            await service.clear_all_jobs()
            click.echo("✅ All jobs cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear jobs: {e}")
            click.echo(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(run_clear())


@cli.command()
@click.pass_context
def health(ctx):
    """Check service health."""
    
    async def run_health():
        try:
            # Create service
            if ctx.obj['config']:
                service = create_job_collection_service(config_source=f"file:{ctx.obj['config']}")
            else:
                service = create_development_service(storage_path=ctx.obj['storage'])
            
            # Get source statuses
            statuses = await service.get_source_statuses()
            
            # Check overall health
            healthy_sources = sum(1 for status in statuses.values() if status.is_healthy)
            total_sources = len(statuses)
            
            if healthy_sources == total_sources:
                click.echo("✅ Service is healthy")
                sys.exit(0)
            elif healthy_sources > total_sources / 2:
                click.echo("⚠️  Service is degraded")
                sys.exit(1)
            else:
                click.echo("❌ Service is unhealthy")
                sys.exit(2)
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            click.echo(f"❌ Health check failed: {e}")
            sys.exit(2)
    
    asyncio.run(run_health())


async def _save_jobs_to_file(jobs: List[any], file_path: str, format: str):
    """Save jobs to file in specified format."""
    if format == 'json':
        with open(file_path, 'w') as f:
            json.dump([job.__dict__ if hasattr(job, '__dict__') else job for job in jobs], f, indent=2, default=str)
    elif format == 'csv':
        import csv
        if jobs:
            with open(file_path, 'w', newline='') as f:
                if hasattr(jobs[0], '__dict__'):
                    fieldnames = jobs[0].__dict__.keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for job in jobs:
                        writer.writerow(job.__dict__)
                else:
                    fieldnames = jobs[0].keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(jobs)


def _display_jobs(jobs: List[any], format: str):
    """Display jobs in specified format."""
    if format == 'json':
        print(json.dumps([job.__dict__ if hasattr(job, '__dict__') else job for job in jobs], indent=2, default=str))
    elif format == 'table':
        if not jobs:
            click.echo("No jobs found.")
            return
        
        # Simple table display
        for i, job in enumerate(jobs[:10]):  # Limit to first 10 for table view
            job_dict = job.__dict__ if hasattr(job, '__dict__') else job
            click.echo(f"\n--- Job {i+1} ---")
            click.echo(f"Title: {job_dict.get('title', 'N/A')}")
            click.echo(f"Company: {job_dict.get('company', 'N/A')}")
            click.echo(f"Location: {job_dict.get('location', 'N/A')}")
            click.echo(f"Remote: {job_dict.get('is_remote', 'N/A')}")
            click.echo(f"Source: {job_dict.get('source', 'N/A')}")
        
        if len(jobs) > 10:
            click.echo(f"\n... and {len(jobs) - 10} more jobs")


if __name__ == '__main__':
    cli()