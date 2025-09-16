#!/usr/bin/env python3
"""
Demo script for audit service functionality.

This script demonstrates the complete audit service functionality
including event logging, querying, and API operations.
"""

import asyncio
import json
from pathlib import Path
import tempfile

# Import our audit service
from tpm_job_finder_poc.audit_service import (
    create_default_audit_service,
    AuditLevel,
    AuditCategory
)


async def demo_audit_service():
    """Demonstrate audit service functionality."""
    print("🚀 Starting Audit Service Demo...")
    
    # Create a temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create audit service
        service = await create_default_audit_service(temp_path)
        
        print(f"📁 Using temporary audit storage: {temp_path}")
        
        # Start the service
        await service.start()
        print("✅ Audit service started")
        
        try:
            # Demo 1: Log a simple event
            print("\n📝 Demo 1: Logging a simple audit event")
            builder = service.create_event_builder()
            event = (builder
                    .action("user_login")
                    .level(AuditLevel.INFO)
                    .category(AuditCategory.USER_ACTION)
                    .user("user123")
                    .message("User logged in successfully")
                    .metadata(ip_address="192.168.1.100", user_agent="Chrome/96.0")
                    .build())
            
            await service.log_event(event)
            print(f"   ✅ Logged event: {event.event_id}")
            
            # Demo 2: Log multiple events in batch
            print("\n📝 Demo 2: Batch logging multiple events")
            events = []
            for i in range(5):
                builder = service.create_event_builder()
                event = (builder
                        .action("job_search")
                        .level(AuditLevel.INFO)
                        .category(AuditCategory.DATA_ACCESS)
                        .user(f"user{i+1}")
                        .message(f"User searched for jobs with query: Python Developer")
                        .metadata(query="Python Developer", results_count=25 + i)
                        .build())
                events.append(event)
            
            await service.log_events(events)
            print(f"   ✅ Logged {len(events)} events in batch")
            
            # Demo 3: Log an error event
            print("\n📝 Demo 3: Logging an error event")
            builder = service.create_event_builder()
            error_event = (builder
                          .action("job_scraping_failed")
                          .level(AuditLevel.ERROR)
                          .category(AuditCategory.ERROR_EVENT)
                          .message("Failed to scrape job from Indeed")
                          .error("SCRAPE_TIMEOUT", "Request timeout after 30 seconds")
                          .metadata(url="https://indeed.com/jobs?q=python", timeout=30)
                          .build())
            
            await service.log_event(error_event)
            print(f"   ✅ Logged error event: {error_event.event_id}")
            
            # Demo 4: Flush events to storage
            print("\n📝 Demo 4: Flushing events to storage")
            await service.flush()
            print("   ✅ Events flushed to storage")
            
            # Demo 5: Query events
            print("\n📝 Demo 5: Querying audit events")
            from tpm_job_finder_poc.shared.contracts.audit_service import AuditQuery
            
            # Query all events
            query = AuditQuery(limit=20, order_desc=True)
            result = await service.query_events(query)
            print(f"   📊 Found {result.total_count} total events")
            print(f"   📊 Returned {len(result.events)} events")
            
            # Query events by service
            query = AuditQuery(service_names=["audit_service"], limit=10)
            result = await service.query_events(query)
            print(f"   📊 Found {len(result.events)} audit_service events")
            
            # Query error events
            query = AuditQuery(levels=[AuditLevel.ERROR], limit=10)
            result = await service.query_events(query)
            print(f"   📊 Found {len(result.events)} error events")
            
            # Demo 6: Get specific event
            print("\n📝 Demo 6: Retrieving specific event")
            specific_event = await service.get_event(event.event_id)
            if specific_event:
                print(f"   ✅ Retrieved event: {specific_event.action} by {specific_event.user_id}")
            else:
                print("   ❌ Event not found")
            
            # Demo 7: Health check
            print("\n📝 Demo 7: Service health check")
            health = await service.health_check()
            print(f"   📊 Service status: {health['status']}")
            print(f"   📊 Events processed: {health['service']['events_processed']}")
            print(f"   📊 Storage status: {health['storage']['status']}")
            
            # Demo 8: Show actual stored data
            print("\n📝 Demo 8: Inspecting stored data")
            audit_file = temp_path / "audit.jsonl"
            if audit_file.exists():
                with open(audit_file, 'r') as f:
                    lines = f.readlines()
                print(f"   📊 {len(lines)} events written to {audit_file}")
                if lines:
                    # Show first event
                    first_event = json.loads(lines[0])
                    print(f"   📄 First event: {first_event['action']} at {first_event['timestamp']}")
        
        finally:
            # Stop the service
            await service.stop()
            print("\n🛑 Audit service stopped")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    asyncio.run(demo_audit_service())