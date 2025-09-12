"""
Unit tests for CLI automation components.

Tests the automated CLI workflow:
- AutomatedJobSearchRunner
- AutomatedJobFinderCLI
- Configuration management
- Workflow orchestration
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from tpm_job_finder_poc.cli.runner import AutomatedJobSearchRunner
from tpm_job_finder_poc.cli.automated_cli import AutomatedJobFinderCLI


class TestAutomatedJobSearchRunner:
    """Test AutomatedJobSearchRunner functionality."""
    
    @pytest.fixture
    def runner(self):
        """Create runner instance."""
        return AutomatedJobSearchRunner()
        
    def test_initialization(self, runner):
        """Test runner initialization."""
        assert runner is not None
        assert hasattr(runner, 'job_aggregator')
        assert hasattr(runner, 'enrichment_service')
        assert hasattr(runner, 'resume_uploader')
        
    def test_config_loading(self):
        """Test configuration loading."""
        # Test with custom config
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                'search_params': {
                    'keywords': ['custom', 'test'],
                    'location': 'Test City'
                }
            }
            json.dump(config, f)
            config_path = f.name
            
        try:
            runner = AutomatedJobSearchRunner(config_path)
            assert runner.config['search_params']['location'] == 'Test City'
        finally:
            Path(config_path).unlink()
            
    @pytest.mark.asyncio
    async def test_process_resume(self, runner):
        """Test resume processing."""
        with patch.object(runner, 'resume_uploader') as mock_uploader:
            mock_uploader.upload_resume = AsyncMock(return_value={
                'success': True,
                'parsed_data': {
                    'skills': ['python', 'developer'],
                    'experience': ['programming', 'software engineering']
                }
            })

            result = await runner._process_resume('/path/to/resume.pdf')
            
            assert result['skills'] == ['python', 'developer']
            assert result['experience'] == ['programming', 'software engineering']
            assert result['file_path'] == '/path/to/resume.pdf'
            mock_uploader.upload_resume.assert_called_once_with('/path/to/resume.pdf')
    
    @pytest.mark.asyncio
    async def test_collect_jobs(self, runner):
        """Test job collection."""
        # Set up the config with search params
        runner.config = {
            'search_params': {
                'keywords': ['product manager'],
                'location': 'Remote',
                'max_jobs_per_source': 50
            }
        }
        
        with patch.object(runner, 'job_aggregator') as mock_aggregator:
            mock_jobs = [
                Mock(id="job1", title="Product Manager", company="Company A"),
                Mock(id="job2", title="Senior PM", company="Company B")
            ]
            mock_aggregator.run_daily_aggregation = AsyncMock(return_value=mock_jobs)
            
            jobs = await runner._collect_jobs()
            
            assert len(jobs) == 2
            mock_aggregator.run_daily_aggregation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_enrich_jobs(self, runner):
        """Test job enrichment."""
        jobs = [{"id": "job1", "title": "Developer", "company": "Tech Co"}]
        resume_data = {"skills": ["Python", "React"]}
        
        # Configure enrichment settings
        runner.config = {
            'enrichment': {'enable_scoring': True}
        }
        
        with patch.object(runner, 'enrichment_service') as mock_enrichment:
            mock_enrichment.score_job_match = AsyncMock(return_value={
                "score": 85,
                "feedback": "Good match"
            })
            
            enriched = await runner._enrich_and_score_jobs(jobs, resume_data)
            
            assert len(enriched) == 1
            assert enriched[0]["id"] == "job1"
            mock_enrichment.score_job_match.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_export_results(self, runner):
        """Test exporting results to Excel."""
        jobs = [
            {
                'id': "job1",
                'title': "Product Manager",
                'company': "Test Company",
                'location': "Remote",
                'url': "https://example.com/job1",
                'date_posted': datetime.now(),
                'match_score': 0.8,
                'recommended_action': 'High Priority',
                'fit_analysis': 'Great match for skills'
            }
        ]

        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
            output_path = f.name

        try:
            with patch('pandas.DataFrame.to_excel') as mock_to_excel:
                with patch('pandas.ExcelWriter') as mock_writer:
                    result_path = await runner._export_results(jobs, output_path)

                    assert result_path == output_path
                assert mock_to_excel.called
        finally:
            Path(output_path).unlink(missing_ok=True)
            
    @pytest.mark.asyncio
    async def test_run_daily_search_workflow(self, runner):
        """Test complete daily search workflow."""
        resume_path = "/path/to/resume.pdf"
        output_path = "/path/to/output.xlsx"
        
        # Mock all the components
        with patch.object(runner, '_process_resume') as mock_resume:
            with patch.object(runner, '_collect_jobs') as mock_collect:
                with patch.object(runner, '_enrich_and_score_jobs') as mock_enrich:
                    with patch.object(runner, '_export_results') as mock_export:
                        
                        mock_resume.return_value = {'success': True, 'keywords': ['pm']}
                        mock_collect.return_value = [Mock()]
                        mock_enrich.return_value = [Mock()]
                        mock_export.return_value = output_path
                        
                        result = await runner.run_daily_search_workflow(resume_path, output_path)
                        
                        assert result == output_path
                        assert mock_resume.called
                        assert mock_collect.called
                        assert mock_enrich.called
                        assert mock_export.called
                        
    @pytest.mark.asyncio
    async def test_run_quick_search(self, runner):
        """Test quick search without resume."""
        keywords = ['developer', 'python']
        location = 'San Francisco'

        with patch.object(runner.job_aggregator, 'run_daily_aggregation') as mock_aggregator:
            with patch.object(runner, '_export_results') as mock_export:

                mock_aggregator.return_value = [{'title': 'Test Job'}]
                mock_export.return_value = "/path/to/results.xlsx"

                result = await runner.run_quick_search(keywords, location)

                assert result is not None
                mock_aggregator.assert_called_once()
                mock_export.assert_called_once()
class TestAutomatedJobFinderCLI:
    """Test AutomatedJobFinderCLI functionality."""
    
    @pytest.fixture
    def cli(self):
        """Create CLI instance."""
        return AutomatedJobFinderCLI()
        
    def test_initialization(self, cli):
        """Test CLI initialization."""
        assert cli is not None
        assert hasattr(cli, 'config')
        assert isinstance(cli.config, dict)
        
    def test_config_loading(self):
        """Test configuration loading from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config = {
                'search_params': {
                    'keywords': ['test', 'engineer'],
                    'location': 'Test Location'
                },
                'output': {
                    'format': 'excel'
                }
            }
            json.dump(config, f)
            config_path = f.name
            
        try:
            cli = AutomatedJobFinderCLI(config_path)
            assert cli.config['search_params']['location'] == 'Test Location'
        finally:
            Path(config_path).unlink()
            
    def test_deep_merge_config(self, cli):
        """Test deep merging of configuration."""
        base = {
            'search_params': {'keywords': ['default']},
            'output': {'format': 'excel'}
        }
        
        override = {
            'search_params': {'location': 'Remote'},
            'new_section': {'value': 123}
        }
        
        cli._deep_merge_config(base, override)
        
        # Should merge nested dicts
        assert base['search_params']['keywords'] == ['default']
        assert base['search_params']['location'] == 'Remote'
        assert base['output']['format'] == 'excel'
        assert base['new_section']['value'] == 123
        
    @pytest.mark.asyncio
    async def test_run_daily_search(self, cli):
        """Test daily search command."""
        resume_path = "/path/to/resume.pdf"

        with patch('tpm_job_finder_poc.cli.runner.AutomatedJobSearchRunner') as mock_runner_class:
            mock_runner = Mock()
            mock_runner.run_daily_search_workflow = AsyncMock(return_value="/path/to/results.xlsx")
            mock_runner_class.return_value = mock_runner
            
            result = await cli.run_daily_search(resume_path)
            
            assert result == "/path/to/results.xlsx"
            assert mock_runner.run_daily_search_workflow.called
            
    @pytest.mark.asyncio
    async def test_run_quick_search(self, cli):
        """Test quick search command."""
        keywords = ['product', 'manager']
        location = 'Remote'

        with patch('tpm_job_finder_poc.cli.runner.AutomatedJobSearchRunner') as mock_runner_class:
            mock_runner = Mock()
            mock_runner.run_quick_search = AsyncMock(return_value="/path/to/quick_results.xlsx")
            mock_runner_class.return_value = mock_runner
            
            result = await cli.run_quick_search(keywords, location)
            
            assert result == "/path/to/quick_results.xlsx"
            assert mock_runner.run_quick_search.called
            
    def test_setup_cron_job(self, cli, capsys):
        """Test cron job setup."""
        resume_path = "/path/to/resume.pdf"
        cron_time = "09:00"
        
        cli.setup_cron_job(resume_path, cron_time)
        
        captured = capsys.readouterr()
        assert "cron" in captured.out.lower()
        assert "09:00" in captured.out or "9" in captured.out
        
    def test_setup_github_actions(self, cli):
        """Test GitHub Actions workflow generation."""
        resume_path = "/path/to/resume.pdf"
        
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                cli.setup_github_actions(resume_path)
                
                assert mock_mkdir.called
                assert mock_open.called
                
                # Check that workflow content was written
                written_content = ''.join([call[0][0] for call in mock_file.write.call_args_list])
                assert 'name: Daily Job Search' in written_content
                assert 'cron:' in written_content
                
    def test_create_sample_config(self, cli):
        """Test sample configuration creation."""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.dump') as mock_json_dump:
                    mock_file = MagicMock()
                    mock_open.return_value.__enter__.return_value = mock_file
                    
                    cli.create_sample_config()
                    
                    assert mock_mkdir.called
                    assert mock_open.called
                    assert mock_json_dump.called


class TestCLIIntegration:
    """Integration tests for CLI components."""
    
    def test_cli_parser_creation(self):
        """Test CLI argument parser creation."""
        from tpm_job_finder_poc.cli.automated_cli import create_parser
        
        parser = create_parser()
        
        # Test daily-search command
        args = parser.parse_args(['daily-search', '--resume', '/path/to/resume.pdf'])
        assert args.command == 'daily-search'
        assert args.resume == '/path/to/resume.pdf'
        
        # Test quick-search command
        args = parser.parse_args(['quick-search', '--keywords', 'python', 'developer'])
        assert args.command == 'quick-search'
        assert args.keywords == ['python', 'developer']
        
        # Test setup-cron command
        args = parser.parse_args(['setup-cron', '--resume', '/path/to/resume.pdf', '--time', '08:30'])
        assert args.command == 'setup-cron'
        assert args.time == '08:30'
        
    @pytest.mark.asyncio
    async def test_runner_with_real_config(self):
        """Test runner with realistic configuration."""
        config = {
            'search_params': {
                'keywords': ['technical product manager', 'tpm'],
                'location': 'Remote',
                'max_jobs_per_source': 10
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
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_path = f.name
            
        try:
            runner = AutomatedJobSearchRunner(config_path)
            
            # Should load configuration correctly
            assert runner.config['search_params']['location'] == 'Remote'
            assert len(runner.config['search_params']['keywords']) == 2
            
        finally:
            Path(config_path).unlink()


class TestErrorHandling:
    """Test error handling in CLI components."""
    
    def test_runner_with_invalid_config(self):
        """Test runner with invalid configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_path = f.name
            
        try:
            # Should not crash, should use defaults
            runner = AutomatedJobSearchRunner(config_path)
            assert runner.config is not None
        finally:
            Path(config_path).unlink()
            
    def test_cli_with_missing_config(self):
        """Test CLI with non-existent config file."""
        # Should not crash, should use defaults
        cli = AutomatedJobFinderCLI("/path/that/does/not/exist.json")
        assert cli.config is not None
        
    @pytest.mark.asyncio
    async def test_runner_error_handling(self):
        """Test error handling in runner workflows."""
        runner = AutomatedJobSearchRunner()
        
        # Test with failing components
        with patch.object(runner, 'job_aggregator') as mock_aggregator:
            mock_aggregator.run_daily_aggregation = AsyncMock(side_effect=Exception("Test error"))
            
            # Should handle errors gracefully
            with pytest.raises(Exception):
                await runner._collect_jobs({'keywords': ['test']})


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
