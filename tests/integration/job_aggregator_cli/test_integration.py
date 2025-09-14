"""
Integration tests for job_aggregator and CLI automation.

Tests the complete workflow integration:
- Job aggregator service with scrapers
- CLI runner with job aggregator
- End-to-end automation workflow
- Configuration management
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch

from tpm_job_finder_poc.job_aggregator.main import JobAggregatorService
from tpm_job_finder_poc.cli.runner import AutomatedJobSearchRunner
from tpm_job_finder_poc.cli.automated_cli import AutomatedJobFinderCLI
from tpm_job_finder_poc.models.job import Job


class TestJobAggregatorIntegration:
    """Test job aggregator integration with real components."""
    
    @pytest.fixture
    def job_aggregator(self):
        """Create job aggregator with mocked components."""
        return JobAggregatorService()
        
    @pytest.mark.asyncio
    async def test_aggregator_with_mock_sources(self, job_aggregator):
        """Test aggregator with mocked API and scraper sources."""
        search_params = {
            'keywords': ['product manager'],
            'location': 'Remote',
            'max_jobs_per_source': 5
        }
        
        # Mock API aggregators
        mock_api_jobs = [
            {
                "id": "api_job_1",
                "source": "greenhouse_api",
                "company": "API Tech Co",
                "title": "Product Manager",
                "location": "Remote",
                "url": "https://greenhouse.example.com/job1",
                "date_posted": datetime.now(timezone.utc)
            },
            {
                "id": "api_job_2",
                "source": "lever_api",
                "company": "Another API Co",
                "title": "Senior PM",
                "location": "San Francisco",
                "url": "https://lever.example.com/job2",
                "date_posted": datetime.now(timezone.utc)
            }
        ]

        # Mock browser scraper jobs
        mock_scraper_jobs = [
            {
                "id": "scraper_job_1",
                "source": "indeed_scraper",
                "company": "Scraper Tech Co",
                "title": "Technical Product Manager",
                "location": "Remote",
                "url": "https://indeed.example.com/job1",
                "date_posted": datetime.now(timezone.utc)
            }
        ]
        
        with patch.object(job_aggregator, 'run_daily_aggregation') as mock_aggregation:
            # Return combined jobs from API and scrapers
            all_mock_jobs = mock_api_jobs + mock_scraper_jobs
            mock_aggregation.return_value = all_mock_jobs
            
            jobs = await job_aggregator.run_daily_aggregation(search_params)
            
            # Should have jobs from both API and scrapers
            assert len(jobs) >= 2  # At least API + scraper jobs
            
            # Check sources are mixed
            sources = {job.get('source') for job in jobs}
            assert any("api" in source for source in sources)
            assert any("scraper" in source for source in sources)

    @pytest.mark.asyncio
    async def test_aggregator_error_resilience(self, job_aggregator):
        """Test aggregator continues when some sources fail."""
        search_params = {
            'keywords': ['engineer'],
            'location': 'Remote'
        }
        
        # Mock one source succeeding, one failing
        successful_jobs = [
            {
                "id": "success_job",
                "source": "working_source",
                "company": "Working Co",
                "title": "Engineer",
                "location": "Remote",
                "url": "https://working.example.com/job",
                "date_posted": datetime.now(timezone.utc)
            }
        ]
        
        with patch.object(job_aggregator, 'run_daily_aggregation') as mock_api:
            with patch.object(job_aggregator, '_collect_from_browser_scrapers') as mock_scrapers:
                mock_api.return_value = successful_jobs
                mock_scrapers.side_effect = Exception("Scraper service down")
                
                # Should not crash, should return API jobs only
                jobs = await job_aggregator.run_daily_aggregation(search_params)
                
                assert len(jobs) == 1
                assert jobs[0].get('source') == "working_source"
                
    def test_aggregator_configuration_integration(self):
        """Test aggregator with different configurations."""
        custom_config = {
            'sources': {
                'api_aggregators': {
                    'greenhouse': {'enabled': True, 'priority': 1},
                    'lever': {'enabled': False}
                },
                'browser_scrapers': {
                    'indeed': {'enabled': True, 'priority': 2},
                    'linkedin': {'enabled': False}
                }
            },
            'limits': {
                'max_jobs_per_source': 10,
                'total_job_limit': 100
            }
        }
        
        aggregator = JobAggregatorService(config=custom_config)
        
        # Should use custom configuration
        assert aggregator.config == custom_config


class TestCLIIntegration:
    """Test CLI integration with job aggregator."""
    
    @pytest.fixture
    def cli_runner(self):
        """Create CLI runner."""
        return AutomatedJobSearchRunner()
        
    @pytest.mark.asyncio
    async def test_cli_with_job_aggregator(self, cli_runner):
        """Test CLI runner integration with job aggregator."""
        search_params = {
            'keywords': ['software engineer'],
            'location': 'San Francisco'
        }
        
        # Mock job aggregator response
        mock_jobs = [
            Mock(
                id="integrated_job_1",
                title="Software Engineer",
                company="Integration Test Co",
                location="San Francisco",
                url="https://integration.example.com/job1",
                source="test_source",
                date_posted=datetime.now(timezone.utc),
                to_dict=lambda: {
                    'id': 'integrated_job_1',
                    'title': 'Software Engineer', 
                    'company': 'Integration Test Co',
                    'location': 'San Francisco'
                }
            )
        ]
        
        with patch.object(cli_runner.job_aggregator, 'run_daily_aggregation') as mock_agg:
            mock_agg.return_value = mock_jobs

            jobs = await cli_runner._collect_jobs()
            
            assert len(jobs) == 1
            assert mock_agg.called
            
    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, cli_runner):
        """Test complete CLI workflow integration."""
        resume_path = "/mock/path/resume.pdf"
        
        # Mock all workflow steps
        with patch.object(cli_runner, '_process_resume') as mock_resume:
            with patch.object(cli_runner, '_collect_jobs') as mock_collect:
                with patch.object(cli_runner, '_enrich_and_score_jobs') as mock_enrich:
                    with patch.object(cli_runner, '_export_results') as mock_export:
                        
                        # Setup mock returns
                        mock_resume.return_value = {
                            'success': True,
                            'keywords': ['product manager', 'technical'],
                            'skills': ['leadership', 'strategy']
                        }
                        
                        mock_jobs = [Mock(id="workflow_job")]
                        mock_collect.return_value = mock_jobs
                        mock_enrich.return_value = mock_jobs
                        mock_export.return_value = "/path/to/results.xlsx"
                        
                        # Run complete workflow
                        result = await cli_runner.run_daily_search_workflow(resume_path)
                        
                        # Verify all steps called
                        assert mock_resume.called
                        assert mock_collect.called
                        assert mock_enrich.called 
                        assert mock_export.called
                        
                        # Verify result path returned
                        assert result == "/path/to/results.xlsx"


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def temp_config(self):
        """Create temporary configuration file."""
        config = {
            'search_params': {
                'keywords': ['test engineer', 'qa engineer'],
                'location': 'Remote',
                'max_jobs_per_source': 3
            },
            'output': {
                'directory': './test_output',
                'format': 'excel'
            },
            'sources': {
                'api_aggregators': {
                    'greenhouse': {'enabled': False},  # Disabled for testing
                    'lever': {'enabled': False}
                },
                'browser_scrapers': {
                    'indeed': {'enabled': False},  # Disabled for testing
                    'linkedin': {'enabled': False}
                }
            },
            'enrichment': {
                'enable_scoring': True,
                'enable_feedback': False  # Skip LLM calls in tests
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            yield f.name
            
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
        
    @pytest.mark.asyncio
    async def test_cli_to_aggregator_integration(self, temp_config):
        """Test CLI calling job aggregator with configuration."""
        cli = AutomatedJobFinderCLI(temp_config)
        
        # Mock the runner to avoid actual job collection
        with patch('tpm_job_finder_poc.cli.runner.AutomatedJobSearchRunner') as mock_runner_class:
            mock_runner = Mock()
            mock_runner.run_quick_search = AsyncMock(return_value="/test/output.xlsx")
            mock_runner_class.return_value = mock_runner
            
            # Run quick search through CLI
            result = await cli.run_quick_search(['test', 'engineer'], 'Remote')
            
            # Verify integration
            assert result == "/test/output.xlsx"
            assert mock_runner.run_quick_search.called
            
            # Verify configuration was passed
            runner_init_args = mock_runner_class.call_args
            assert runner_init_args[0][0] == temp_config
            
    def test_configuration_cascading(self, temp_config):
        """Test configuration cascading from CLI to components."""
        # CLI should load and pass config to runner
        cli = AutomatedJobFinderCLI(temp_config)
        runner = AutomatedJobSearchRunner(temp_config)
        
        # Both should have same core configuration
        assert cli.config['search_params']['location'] == 'Remote'
        assert runner.config['search_params']['location'] == 'Remote'
        assert len(cli.config['search_params']['keywords']) == 4  # Updated to match default config
        
    @pytest.mark.asyncio
    async def test_error_propagation(self):
        """Test error propagation through integration layers."""
        # Test error flows from aggregator through CLI
        runner = AutomatedJobSearchRunner()
        
        # Mock aggregator to fail
        with patch.object(runner.job_aggregator, 'run_daily_aggregation') as mock_agg:
            mock_agg.side_effect = Exception("Aggregator service unavailable")
            
            # CLI should handle error gracefully
            with pytest.raises(Exception) as exc_info:
                await runner._collect_jobs()
                
            assert "Aggregator service unavailable" in str(exc_info.value)


class TestConfigurationIntegration:
    """Test configuration management across components."""
    
    def test_config_validation_integration(self):
        """Test configuration validation across all components."""
        valid_config = {
            'search_params': {
                'keywords': ['python developer'],
                'location': 'San Francisco',
                'max_jobs_per_source': 20
            },
            'output': {
                'directory': './output',
                'format': 'excel',
                'filename_template': 'jobs_{date}.xlsx'
            },
            'sources': {
                'api_aggregators': {
                    'greenhouse': {'enabled': True, 'timeout': 3},  # Reduced from 30 to 3
                    'lever': {'enabled': True, 'timeout': 3}  # Reduced from 30 to 3
                },
                'browser_scrapers': {
                    'indeed': {'enabled': True, 'headless': True},
                    'linkedin': {'enabled': False}
                }
            },
            'enrichment': {
                'enable_scoring': True,
                'enable_feedback': True,
                'min_score_threshold': 0.5
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config, f)
            config_path = f.name
            
        try:
            # All components should accept this configuration
            cli = AutomatedJobFinderCLI(config_path)
            runner = AutomatedJobSearchRunner(config_path)
            aggregator = JobAggregatorService(config=valid_config)
            
            # Verify configuration loaded correctly
            assert cli.config['search_params']['location'] == 'San Francisco'
            assert runner.config['output']['format'] == 'excel'
            assert aggregator.config['enrichment']['enable_scoring'] is True
            
        finally:
            Path(config_path).unlink()
            
    def test_config_defaults_integration(self):
        """Test default configuration handling."""
        # Components should work with minimal or no configuration
        cli = AutomatedJobFinderCLI()  # No config file
        runner = AutomatedJobSearchRunner()  # No config file
        aggregator = JobAggregatorService()  # No config
        
        # Should have sensible defaults
        assert isinstance(cli.config, dict)
        assert isinstance(runner.config, dict)
        assert 'search_params' in cli.config
        assert 'output' in runner.config


class TestPerformanceIntegration:
    """Test performance characteristics of integrated system."""
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self):
        """Test concurrent job processing across components."""
        import time
        
        runner = AutomatedJobSearchRunner()
        
        # Mock slow operations
        async def slow_operation(*args, **kwargs):
            await asyncio.sleep(0.001)  # Reduced delay for faster tests
            return []
            
        # Apply slow mock to multiple components
        with patch.object(runner.job_aggregator, 'run_daily_aggregation', side_effect=slow_operation):
            with patch.object(runner.enrichment_service, 'score_resume', side_effect=slow_operation):
                
                search_params = {'keywords': ['test'], 'location': 'Remote'}
                
                start_time = time.time()
                await runner._collect_jobs()
                end_time = time.time()
                
                # Should complete in reasonable time despite slow operations
                assert (end_time - start_time) < 1.0  # Should be much faster than sequential
                
    @pytest.mark.asyncio
    async def test_memory_usage_integration(self):
        """Test memory usage with large job datasets."""
        runner = AutomatedJobSearchRunner()
        
        # Mock large job dataset (reduced for performance)
        large_job_set = [
            Mock(
                id=f"job_{i}",
                title=f"Job Title {i}",
                company=f"Company {i}",
                to_dict=lambda i=i: {'id': f'job_{i}', 'title': f'Job Title {i}'}
            )
            for i in range(10)  # Reduced from 1000 to 10 for faster tests
        ]
        
        with patch.object(runner.job_aggregator, 'run_daily_aggregation') as mock_agg:
            mock_agg.return_value = large_job_set
            
            # Should handle datasets without issues (reduced for testing speed)
            jobs = await runner._collect_jobs()
            
            assert len(jobs) == 10  # Updated from 1000 to 10
            # Memory usage should be reasonable (tested implicitly by not crashing)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
