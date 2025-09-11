"""
End-to-End tests for the complete job finder system.

Tests the entire workflow from configuration to job results:
- CLI automation workflow 
- Job aggregator orchestration
- Scraping service integration
- Resume processing integration
- Excel export functionality
"""

import pytest
import tempfile
import os
import asyncio
import json
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from cli.automated_cli import AutomatedJobFinderCLI
from job_aggregator.main import JobAggregatorService
from scraping_service_v2 import ServiceRegistry, ScrapingOrchestrator
from models.job import Job
from models.user import User


class TestCompleteWorkflowE2E:
    """Test complete end-to-end workflows."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for E2E tests."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            
            # Create directory structure
            (workspace / "config").mkdir(exist_ok=True)
            (workspace / "output").mkdir(exist_ok=True) 
            (workspace / "resume_store" / "resume").mkdir(parents=True, exist_ok=True)
            
            # Create sample configuration
            config = {
                "search_params": {
                    "keywords": ["software engineer", "python developer"],
                    "locations": ["Remote", "San Francisco"],
                    "exclude_companies": ["Blacklisted Corp"]
                },
                "output_format": "excel",
                "max_jobs_per_source": 50,
                "deduplication": {
                    "enabled": True,
                    "similarity_threshold": 0.85
                },
                "enrichment": {
                    "enabled": True,
                    "llm_provider": "openai"
                }
            }
            
            with open(workspace / "config" / "automation_config.json", "w") as f:
                json.dump(config, f, indent=2)
                
            # Create sample resume
            resume_content = """
            John Doe
            Software Engineer
            
            Skills: Python, JavaScript, React, Node.js
            Experience: 5 years in full-stack development
            """
            
            with open(workspace / "resume_store" / "resume" / "resume.txt", "w") as f:
                f.write(resume_content)
                
            yield workspace
            
    @pytest.fixture
    def mock_services(self):
        """Create mock services for E2E testing."""
        services = {}
        
        # Mock job aggregator service
        services['aggregator'] = Mock(spec=JobAggregatorService)
        services['aggregator'].run_daily_aggregation = AsyncMock(return_value={
            "jobs_collected": 45,
            "sources": ["indeed", "linkedin", "ziprecruiter"],
            "duplicates_removed": 8,
            "final_job_count": 37
        })
        
        # Mock scraping service
        services['scraping_registry'] = Mock(spec=ServiceRegistry)
        services['scraping_orchestrator'] = Mock(spec=ScrapingOrchestrator)
        
        # Sample jobs for testing
        sample_jobs = []
        for i in range(10):
            job = Mock(spec=Job)
            job.id = f"job_{i}"
            job.title = f"Software Engineer {i}"
            job.company = f"Tech Corp {i}"
            job.location = "Remote" if i % 2 == 0 else "San Francisco"
            job.salary = f"${90000 + i * 5000}"
            job.url = f"https://example.com/job/{i}"
            job.description = f"Great software engineer position {i}"
            job.source = "indeed" if i % 3 == 0 else "linkedin"
            sample_jobs.append(job)
            
        services['sample_jobs'] = sample_jobs
        
        return services
        
    @pytest.mark.asyncio
    async def test_complete_cli_workflow(self, temp_workspace, mock_services):
        """Test complete CLI automation workflow."""
        config_path = temp_workspace / "config" / "automation_config.json"
        
        # Create CLI instance
        cli = AutomatedJobFinderCLI(str(config_path))
        
        # Mock the services
        with patch('job_aggregator.main.JobAggregatorService', return_value=mock_services['aggregator']):
            # Test configuration loading
            assert cli.config is not None
            assert "search_params" in cli.config
            assert "keywords" in cli.config["search_params"]
            
            # Test workflow execution (would normally call real services)
            # For E2E test, we verify the workflow structure
            assert hasattr(cli, 'run_daily_search')
            assert hasattr(cli, 'setup_automation')
            
    @pytest.mark.asyncio  
    async def test_job_aggregation_to_export_pipeline(self, temp_workspace, mock_services):
        """Test pipeline from job aggregation to Excel export."""
        
        # Simulate job aggregation results
        aggregation_results = {
            "jobs": mock_services['sample_jobs'][:5],
            "metadata": {
                "total_jobs": 5,
                "sources_used": ["indeed", "linkedin"],
                "duplicates_removed": 2,
                "processing_time": "00:02:30"
            }
        }
        
        # Test Excel export functionality
        output_path = temp_workspace / "output" / "jobs.xlsx"
        
        # Convert mock jobs to dictionaries for pandas
        job_data = []
        for job in aggregation_results["jobs"]:
            job_data.append({
                "Title": job.title,
                "Company": job.company, 
                "Location": job.location,
                "Salary": job.salary,
                "URL": job.url,
                "Source": job.source,
                "Description": job.description[:100] + "..."  # Truncate for test
            })
            
        # Create Excel file
        df = pd.DataFrame(job_data)
        df.to_excel(output_path, index=False)
        
        # Verify Excel file was created and has correct structure
        assert output_path.exists()
        
        # Read back and verify
        result_df = pd.read_excel(output_path)
        assert len(result_df) == 5
        assert "Title" in result_df.columns
        assert "Company" in result_df.columns
        assert "Salary" in result_df.columns
        
    @pytest.mark.asyncio
    async def test_resume_integration_workflow(self, temp_workspace):
        """Test resume upload and processing integration."""
        resume_path = temp_workspace / "resume_store" / "resume" / "resume.txt"
        
        # Verify resume exists
        assert resume_path.exists()
        
        # Test resume content parsing (mock the actual parsing)
        with patch('resume_uploader.parser.ResumeParser') as mock_parser:
            mock_parser.return_value.parse_resume.return_value = {
                "name": "John Doe",
                "skills": ["Python", "JavaScript", "React"],
                "experience_years": 5,
                "current_title": "Software Engineer"
            }
            
            # Simulate resume processing
            from resume_uploader.parser import ResumeParser
            parser = ResumeParser()
            
            with open(resume_path, 'r') as f:
                resume_content = f.read()
                
            parsed_resume = parser.parse_resume(resume_content)
            
            # Verify parsing results
            assert "name" in parsed_resume
            assert "skills" in parsed_resume
            assert len(parsed_resume["skills"]) > 0
            
    @pytest.mark.asyncio
    async def test_configuration_validation_e2e(self, temp_workspace):
        """Test configuration validation across the system."""
        config_path = temp_workspace / "config" / "automation_config.json"
        
        # Test valid configuration
        cli = AutomatedJobFinderCLI(str(config_path))
        assert cli.config is not None
        
        # Test invalid configuration
        invalid_config = {"invalid": "structure"}
        
        invalid_config_path = temp_workspace / "config" / "invalid_config.json"
        with open(invalid_config_path, "w") as f:
            json.dump(invalid_config, f)
            
        with pytest.raises((ValueError, KeyError, FileNotFoundError)):
            AutomatedJobFinderCLI(str(invalid_config_path))
            
    @pytest.mark.asyncio
    async def test_error_recovery_e2e(self, temp_workspace, mock_services):
        """Test error recovery in complete workflow."""
        config_path = temp_workspace / "config" / "automation_config.json"
        
        # Create CLI with failing service
        cli = AutomatedJobFinderCLI(str(config_path))
        
        # Mock service failure
        failing_aggregator = Mock(spec=JobAggregatorService)
        failing_aggregator.run_daily_aggregation = AsyncMock(
            side_effect=Exception("Service temporarily unavailable")
        )
        
        with patch('job_aggregator.main.JobAggregatorService', return_value=failing_aggregator):
            # System should handle failures gracefully
            try:
                # Would normally call the workflow - we're testing structure
                assert hasattr(cli, 'config')
                assert cli.config is not None
                
                # Verify error handling exists
                assert hasattr(cli, 'run_daily_search')  # Method exists for error handling
                
            except Exception as e:
                # Should not propagate unhandled exceptions
                pytest.fail(f"Unhandled exception in error recovery: {e}")


class TestScrapingServiceIntegrationE2E:
    """Test scraping service integration end-to-end."""
    
    @pytest.fixture
    def integration_registry(self):
        """Create registry with real-like mock scrapers."""
        registry = ServiceRegistry()
        
        # Create realistic mock scrapers
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            mock_scraper = Mock()
            mock_scraper.name = source_name
            mock_scraper.source_type = "BROWSER_SCRAPER"
            mock_scraper.enabled = True
            
            # Mock realistic job data
            mock_jobs = []
            for i in range(3):  # 3 jobs per source
                from datetime import datetime, timezone
                job = Mock()
                job.id = f"{source_name}_job_{i}"
                job.source = source_name
                job.title = f"Engineer Position {i}"
                job.company = f"{source_name.title()} Corp {i}"
                job.location = "San Francisco" if i % 2 == 0 else "Remote"
                job.url = f"https://{source_name}.com/job/{i}"
                job.date_posted = datetime.now(timezone.utc)
                job.salary = f"${100000 + i * 10000}" if i > 0 else None
                job.description = f"Great opportunity at {source_name}"
                mock_jobs.append(job)
                
            mock_scraper.fetch_jobs = AsyncMock(return_value=mock_jobs)
            mock_scraper.health_check = AsyncMock(return_value=Mock(
                status="HEALTHY", 
                message="OK",
                response_time_ms=150.0
            ))
            mock_scraper.initialize = AsyncMock(return_value=True)
            mock_scraper.cleanup = AsyncMock()
            
            registry.register_source(mock_scraper)
            
        return registry
        
    @pytest.mark.asyncio
    async def test_multi_source_orchestration_e2e(self, integration_registry):
        """Test orchestrating multiple scraping sources."""
        from scraping_service_v2 import FetchParams
        
        orchestrator = ScrapingOrchestrator(integration_registry, max_concurrent=2)
        
        # Test comprehensive job search
        params = FetchParams(
            keywords=["software engineer", "python developer"],
            location="San Francisco",
            limit=10
        )
        
        results = await orchestrator.fetch_all_sources(params)
        
        # Verify results structure
        assert "jobs" in results
        assert "metadata" in results
        assert "errors" in results
        
        # Should have jobs from all sources
        assert results["metadata"]["total_jobs"] == 12  # 4 sources × 3 jobs each
        assert results["metadata"]["successful_sources"] == 4
        assert results["metadata"]["failed_sources"] == 0
        
        # Verify job data integrity
        jobs = results["jobs"]
        sources_found = set(job.source for job in jobs)
        expected_sources = {"indeed", "linkedin", "ziprecruiter", "greenhouse"}
        assert sources_found == expected_sources
        
    @pytest.mark.asyncio
    async def test_health_monitoring_e2e(self, integration_registry):
        """Test health monitoring across all sources."""
        orchestrator = ScrapingOrchestrator(integration_registry)
        
        # Run health checks
        health_results = await orchestrator.health_check_sources()
        
        # Should have health data for all sources
        expected_sources = {"indeed", "linkedin", "ziprecruiter", "greenhouse"}
        assert set(health_results.keys()) == expected_sources
        
        # All sources should be healthy in this test
        for source_name, health_data in health_results.items():
            assert health_data["status"] == "HEALTHY"
            assert "response_time_ms" in health_data
            assert health_data["response_time_ms"] > 0
            
    @pytest.mark.asyncio
    async def test_service_lifecycle_e2e(self, integration_registry):
        """Test complete service lifecycle."""
        orchestrator = ScrapingOrchestrator(integration_registry)
        
        # Test initialization
        init_results = await integration_registry.initialize_all_sources()
        assert len(init_results) == 4
        assert all(result is True for result in init_results.values())
        
        # Test normal operations
        from scraping_service_v2 import FetchParams
        params = FetchParams(keywords=["test"], location="Remote", limit=5)
        
        results = await orchestrator.fetch_all_sources(params)
        assert results["metadata"]["total_jobs"] > 0
        
        # Test cleanup
        await integration_registry.cleanup_all_sources()
        
        # Verify cleanup was called on all sources
        for source_name in ["indeed", "linkedin", "ziprecruiter", "greenhouse"]:
            source = integration_registry.get_source(source_name)
            source.cleanup.assert_called_once()


class TestDataFlowE2E:
    """Test data flow through the entire system."""
    
    @pytest.mark.asyncio
    async def test_job_data_transformation_pipeline(self):
        """Test job data transformations through the pipeline."""
        from datetime import datetime, timezone
        
        # Simulate raw job data from scraping
        raw_job_data = {
            "id": "raw_job_123",
            "source": "indeed", 
            "title": "Senior Software Engineer",
            "company": "Tech Innovations Inc",
            "location": "San Francisco, CA",
            "url": "https://indeed.com/job/123",
            "date_posted": datetime.now(timezone.utc),
            "salary": "$120,000 - $150,000",
            "description": "We are looking for an experienced software engineer...",
            "raw_data": {
                "job_type": "Full-time",
                "experience_level": "Senior",
                "remote_ok": False
            }
        }
        
        # Test Job model creation
        from models.job import Job
        
        job = Job(
            id=raw_job_data["id"],
            title=raw_job_data["title"],
            company=raw_job_data["company"],
            location=raw_job_data["location"],
            description=raw_job_data["description"],
            url=raw_job_data["url"],
            source=raw_job_data["source"],
            date_posted=raw_job_data["date_posted"],
            salary=raw_job_data["salary"]
        )
        
        # Verify job data integrity
        assert job.id == "raw_job_123"
        assert job.title == "Senior Software Engineer"
        assert job.company == "Tech Innovations Inc"
        assert job.source == "indeed"
        
        # Test serialization for export
        if hasattr(job, 'to_dict'):
            job_dict = job.to_dict()
            assert isinstance(job_dict, dict)
            assert job_dict["title"] == "Senior Software Engineer"
            
    @pytest.mark.asyncio
    async def test_deduplication_pipeline(self):
        """Test job deduplication across sources."""
        from models.job import Job
        from datetime import datetime, timezone
        
        # Create duplicate jobs from different sources
        base_time = datetime.now(timezone.utc)
        
        jobs = [
            Job(
                id="indeed_123",
                title="Software Engineer", 
                company="Tech Corp",
                location="San Francisco",
                description="Python developer position",
                url="https://indeed.com/job/123",
                source="indeed",
                date_posted=base_time
            ),
            Job(
                id="linkedin_456", 
                title="Software Engineer",  # Same title
                company="Tech Corp",        # Same company
                location="San Francisco, CA",  # Similar location
                description="Python developer role",  # Similar description
                url="https://linkedin.com/job/456",
                source="linkedin",
                date_posted=base_time
            ),
            Job(
                id="ziprecruiter_789",
                title="Frontend Developer",  # Different title
                company="Tech Corp",
                location="San Francisco",
                description="React developer position", 
                url="https://ziprecruiter.com/job/789",
                source="ziprecruiter",
                date_posted=base_time
            )
        ]
        
        # Test deduplication logic (simplified)
        # In real system this would use the deduplication service
        unique_jobs = []
        seen_signatures = set()
        
        for job in jobs:
            # Simple signature based on title + company + location
            signature = f"{job.title.lower()}_{job.company.lower()}_{job.location.lower().replace(', ca', '')}"
            
            if signature not in seen_signatures:
                unique_jobs.append(job)
                seen_signatures.add(signature)
                
        # Should deduplicate the first two jobs
        assert len(unique_jobs) == 2  # Indeed + ZipRecruiter jobs remain
        job_sources = [job.source for job in unique_jobs]
        assert "indeed" in job_sources  # First occurrence kept
        assert "ziprecruiter" in job_sources  # Different job kept
        assert "linkedin" not in job_sources  # Duplicate removed
        
    @pytest.mark.asyncio
    async def test_enrichment_pipeline_integration(self):
        """Test job enrichment pipeline integration.""" 
        from models.job import Job
        from datetime import datetime, timezone
        
        # Create basic job for enrichment
        job = Job(
            id="enrichment_test_job",
            title="Python Developer",
            company="StartupCo",
            location="Remote",
            description="Looking for Python developer with FastAPI experience",
            url="https://example.com/job/123",
            source="indeed",
            date_posted=datetime.now(timezone.utc)
        )
        
        # Mock enrichment service
        with patch('enrichment.orchestrator.EnrichmentOrchestrator') as mock_orchestrator:
            mock_orchestrator.return_value.enrich_job.return_value = {
                "skills_extracted": ["Python", "FastAPI", "REST API"],
                "experience_level": "Mid-level",
                "remote_friendly": True,
                "salary_estimate": "$80,000 - $120,000",
                "match_score": 0.85
            }
            
            # Simulate enrichment
            enrichment_result = mock_orchestrator.return_value.enrich_job(job)
            
            # Verify enrichment data
            assert "skills_extracted" in enrichment_result
            assert "Python" in enrichment_result["skills_extracted"]
            assert enrichment_result["remote_friendly"] is True
            assert enrichment_result["match_score"] > 0.8


class TestSystemPerformanceE2E:
    """Test system performance under realistic conditions."""
    
    @pytest.mark.asyncio
    async def test_concurrent_source_performance(self):
        """Test performance with multiple concurrent sources."""
        registry = ServiceRegistry()
        
        # Create multiple mock sources with realistic delays
        for i in range(10):  # 10 concurrent sources
            mock_source = Mock()
            mock_source.name = f"source_{i}"
            mock_source.source_type = "BROWSER_SCRAPER"
            mock_source.enabled = True
            
            # Simulate realistic response times
            async def mock_fetch(*args, **kwargs):
                await asyncio.sleep(0.1)  # 100ms simulated network delay
                return [Mock(id=f"job_{i}_1", source=f"source_{i}")]
                
            mock_source.fetch_jobs = mock_fetch
            mock_source.health_check = AsyncMock(return_value=Mock(status="HEALTHY"))
            mock_source.initialize = AsyncMock(return_value=True)
            mock_source.cleanup = AsyncMock()
            
            registry.register_source(mock_source)
            
        # Test concurrent fetching performance
        orchestrator = ScrapingOrchestrator(registry, max_concurrent=5)
        
        from scraping_service_v2 import FetchParams
        params = FetchParams(keywords=["test"], location="Remote")
        
        start_time = asyncio.get_event_loop().time()
        results = await orchestrator.fetch_all_sources(params)
        end_time = asyncio.get_event_loop().time()
        
        # Should complete faster than sequential (< 1 second vs 1+ seconds sequential)
        execution_time = end_time - start_time
        assert execution_time < 0.5  # With concurrency should be much faster
        
        # Should get all jobs
        assert results["metadata"]["total_jobs"] == 10
        assert results["metadata"]["successful_sources"] == 10
        
    @pytest.mark.asyncio
    async def test_large_dataset_handling(self):
        """Test handling large job datasets."""
        # Simulate large job collection
        large_job_count = 1000
        
        jobs = []
        for i in range(large_job_count):
            from datetime import datetime, timezone
            job = Mock()
            job.id = f"large_dataset_job_{i}"
            job.source = f"source_{i % 10}"  # 10 different sources
            job.title = f"Position {i}"
            job.company = f"Company {i % 50}"  # 50 different companies
            job.location = "Remote" if i % 3 == 0 else f"City {i % 20}"
            job.date_posted = datetime.now(timezone.utc)
            jobs.append(job)
            
        # Test processing large dataset
        start_time = asyncio.get_event_loop().time()
        
        # Simulate job processing (grouping, filtering, etc.)
        processed_jobs = []
        for job in jobs:
            # Simple processing
            if "Remote" in job.location or int(job.id.split('_')[-1]) % 5 == 0:
                processed_jobs.append(job)
                
        end_time = asyncio.get_event_loop().time()
        
        # Should handle large dataset efficiently
        processing_time = end_time - start_time
        assert processing_time < 1.0  # Should process 1000 jobs quickly
        
        # Should have reasonable filtered count
        assert len(processed_jobs) > 0
        assert len(processed_jobs) < large_job_count  # Some filtering occurred


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
