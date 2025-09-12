"""Integration tests for Careerjet integration with job aggregation service."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from tpm_job_finder_poc.job_aggregator.services.job_aggregation_service import JobAggregationService


class TestCareerjetIntegration:
    """Integration tests for Careerjet with job aggregation service."""
    
    @pytest.fixture
    def careerjet_config(self):
        """Configuration for Careerjet testing."""
        return {
            'careerjet': {
                'affiliate_id': 'test_affiliate_123',
                'locales': ['en_US', 'en_GB', 'en_CA']
            }
        }
    
    @pytest.fixture
    def mock_careerjet_jobs(self):
        """Mock job data from Careerjet."""
        return [
            {
                'title': 'Senior Technical Program Manager',
                'company': 'Google',
                'location': 'Mountain View, CA, United States',
                'posted_date': '2025-09-12',
                'canonical_url': 'https://careers.google.com/jobs/results/123',
                'source_site': 'careerjet',
                'salary_min': 180000,
                'salary_max': 220000,
                'local_salary': '$180,000 - $220,000',
                'usd_equivalent': 200000,
                'description': 'Lead cross-functional teams to deliver complex technical projects...',
                'locale': 'en_US',
                'region': 'North America',
                'country_code': 'US',
                'currency': 'USD',
                'visa_required': False,
                'search_term': 'technical program manager'
            },
            {
                'title': 'Principal Product Manager',
                'company': 'Spotify',
                'location': 'Stockholm, Sweden',
                'posted_date': '2025-09-11',
                'canonical_url': 'https://jobs.lever.co/spotify/123',
                'source_site': 'careerjet',
                'salary_min': 120000,
                'salary_max': 150000,
                'local_salary': '1,200,000 - 1,500,000 SEK',
                'usd_equivalent': 135000,
                'description': 'Drive product strategy for our streaming platform...',
                'locale': 'sv_SE',
                'region': 'Western Europe',
                'country_code': 'SE',
                'currency': 'SEK',
                'visa_required': True,
                'search_term': 'product manager'
            },
            {
                'title': 'TPM - Mobile Platform',
                'company': 'Rakuten',
                'location': 'Tokyo, Japan',
                'posted_date': '2025-09-10',
                'canonical_url': 'https://rakuten.careers/job/123',
                'source_site': 'careerjet',
                'salary_min': 8000000,
                'salary_max': 12000000,
                'local_salary': '¥8,000,000 - ¥12,000,000',
                'usd_equivalent': 70000,
                'description': 'Technical program management for mobile applications...',
                'locale': 'ja_JP',
                'region': 'East Asia',
                'country_code': 'JP',
                'currency': 'JPY',
                'visa_required': True,
                'search_term': 'technical program manager'
            }
        ]
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.CareerjetConnector.fetch_since')
    async def test_careerjet_integration_with_aggregation_service(
        self, mock_fetch_since, careerjet_config, mock_careerjet_jobs
    ):
        """Test Careerjet integration with JobAggregationService."""
        # Setup mock
        mock_fetch_since.return_value = mock_careerjet_jobs
        
        # Initialize service with Careerjet config
        service = JobAggregationService(
            search_terms=['technical program manager', 'product manager'],
            location='Remote',
            api_config=careerjet_config
        )
        
        # Mock the scraping service to avoid dependencies
        service.scraping_service.fetch_all_jobs = AsyncMock(return_value=[])
        
        # Fetch jobs
        jobs = await service.fetch_all_jobs()
        
        # Verify Careerjet jobs are included
        careerjet_jobs = [job for job in jobs if job.get('source_site') == 'careerjet']
        assert len(careerjet_jobs) == 3
        
        # Verify geographic data is present
        for job in careerjet_jobs:
            assert 'region' in job
            assert 'country_code' in job
            assert 'visa_required' in job
            assert job['region'] in ['North America', 'Western Europe', 'East Asia']
        
        # Verify different currencies are handled
        currencies = set(job['currency'] for job in careerjet_jobs)
        assert 'USD' in currencies
        assert 'SEK' in currencies
        assert 'JPY' in currencies
        
        # Verify USD equivalents are calculated
        for job in careerjet_jobs:
            if job['currency'] != 'USD':
                assert job.get('usd_equivalent') is not None
    
    def test_careerjet_connector_initialization_in_service(self, careerjet_config):
        """Test that CareerjetConnector is properly initialized in service."""
        service = JobAggregationService(
            search_terms=['technical program manager'],
            api_config=careerjet_config
        )
        
        # Find Careerjet connector
        careerjet_connectors = [
            conn for conn in service.api_connectors 
            if hasattr(conn, 'source') and conn.source == 'careerjet'
        ]
        
        assert len(careerjet_connectors) == 1
        
        connector = careerjet_connectors[0]
        assert connector.affiliate_id == 'test_affiliate_123'
        assert connector.locales == ['en_US', 'en_GB', 'en_CA']
    
    def test_careerjet_service_without_config(self):
        """Test that service works without Careerjet config."""
        service = JobAggregationService(
            search_terms=['technical program manager'],
            api_config={}  # No Careerjet config
        )
        
        # Should not have any Careerjet connectors
        careerjet_connectors = [
            conn for conn in service.api_connectors 
            if hasattr(conn, 'source') and conn.source == 'careerjet'
        ]
        
        assert len(careerjet_connectors) == 0
    
    def test_careerjet_with_default_locales(self):
        """Test Careerjet with default locale configuration."""
        config = {
            'careerjet': {
                'affiliate_id': 'test_affiliate_123'
                # No locales specified - should use defaults
            }
        }
        
        service = JobAggregationService(
            search_terms=['technical program manager'],
            api_config=config
        )
        
        careerjet_connector = None
        for conn in service.api_connectors:
            if hasattr(conn, 'source') and conn.source == 'careerjet':
                careerjet_connector = conn
                break
        
        assert careerjet_connector is not None
        # Should use default locales
        expected_defaults = ["en_US", "en_GB", "en_CA", "en_AU", "en_SG"]
        assert careerjet_connector.locales == expected_defaults


class TestGeographicExcelExportIntegration:
    """Integration tests for geographic Excel export with Careerjet jobs."""
    
    @pytest.fixture
    def mixed_international_jobs(self):
        """Mixed job data with international jobs from multiple sources."""
        return [
            # Careerjet jobs
            {
                'title': 'Senior TPM',
                'company': 'Google',
                'location': 'Mountain View, CA',
                'source_site': 'careerjet',
                'region': 'North America',
                'country_code': 'US',
                'match_score': 0.9,
                'usd_equivalent': 200000,
                'visa_required': False
            },
            {
                'title': 'Product Manager',
                'company': 'Spotify',
                'location': 'Stockholm, Sweden',
                'source_site': 'careerjet',
                'region': 'Western Europe',
                'country_code': 'SE',
                'match_score': 0.8,
                'usd_equivalent': 135000,
                'visa_required': True
            },
            # Existing API jobs
            {
                'title': 'TPM Lead',
                'company': 'Microsoft',
                'location': 'Seattle, WA',
                'source_site': 'adzuna',
                'region': 'North America',
                'country_code': 'US',
                'match_score': 0.85,
                'usd_equivalent': 180000,
                'visa_required': False
            }
        ]
    
    def test_geographic_excel_export_with_careerjet_jobs(self, mixed_international_jobs):
        """Test that geographic Excel export works with Careerjet jobs."""
        from tpm_job_finder_poc.cli.geographic_excel_exporter import GeographicExcelExporter
        
        exporter = GeographicExcelExporter()
        workbook = exporter.create_regional_workbook(mixed_international_jobs)
        
        # Check that workbook is created with expected sheets
        sheet_names = [sheet.title for sheet in workbook.worksheets]
        
        # Should have summary sheet
        assert any('Summary' in name for name in sheet_names)
        
        # Should have regional sheets
        assert any('North America' in name for name in sheet_names)
        assert any('Western Europe' in name for name in sheet_names)
        
        # Check that North America sheet has both US jobs
        na_sheet = None
        for sheet in workbook.worksheets:
            if 'North America' in sheet.title:
                na_sheet = sheet
                break
        
        assert na_sheet is not None
        
        # Should have 2 jobs in North America (Google + Microsoft)
        # Count non-empty rows (excluding headers and intelligence section)
        data_rows = 0
        for row in range(9, na_sheet.max_row + 1):  # Start after intelligence section
            if na_sheet.cell(row=row, column=1).value:  # If title cell has value
                data_rows += 1
        
        assert data_rows == 2
    
    def test_geographic_classifier_with_careerjet_data(self, mixed_international_jobs):
        """Test geographic classifier with Careerjet job data."""
        from tpm_job_finder_poc.enrichment.geographic_classifier import GeographicClassifier
        
        classifier = GeographicClassifier()
        regional_jobs = classifier.organize_jobs_by_region(mixed_international_jobs)
        
        # Check regional organization
        assert 'North America' in regional_jobs
        assert 'Western Europe' in regional_jobs
        
        # Check job counts
        assert len(regional_jobs['North America']) == 2  # Google + Microsoft
        assert len(regional_jobs['Western Europe']) == 1  # Spotify
        
        # Check sorting (highest match score first)
        na_jobs = regional_jobs['North America']
        assert na_jobs[0]['match_score'] == 0.9  # Google job
        assert na_jobs[1]['match_score'] == 0.85  # Microsoft job
        
        # Test visa requirements
        for job in mixed_international_jobs:
            country = job['country_code']
            visa_info = classifier.assess_visa_requirements(country)
            
            if country == 'US':
                assert visa_info['required'] is False
            else:
                assert visa_info['required'] is True


@pytest.mark.integration
class TestCareerjetEndToEndWorkflow:
    """End-to-end integration tests for Careerjet workflow."""
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.requests.get')
    async def test_complete_careerjet_workflow(self, mock_requests_get):
        """Test complete workflow from Careerjet API to Excel export."""
        # Mock Careerjet API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'type': 'JOBS',
            'jobs': [
                {
                    'title': 'Senior Technical Program Manager',
                    'company': 'TechCorp International',
                    'locations': 'London',
                    'date': '2025-09-12',
                    'url': 'https://example.com/job1',
                    'description': 'Lead technical programs across EMEA...',
                    'salary': '£120,000 - £150,000'
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Configure job aggregation service with Careerjet
        config = {
            'careerjet': {
                'affiliate_id': 'test_affiliate',
                'locales': ['en_GB']
            }
        }
        
        service = JobAggregationService(
            search_terms=['technical program manager'],
            api_config=config
        )
        
        # Mock scraping service
        service.scraping_service.fetch_all_jobs = AsyncMock(return_value=[])
        
        # Fetch jobs
        jobs = await service.fetch_all_jobs()
        
        # Should have Careerjet jobs
        assert len(jobs) > 0
        careerjet_job = jobs[0]
        assert careerjet_job['source_site'] == 'careerjet'
        assert careerjet_job['region'] == 'Western Europe'
        assert careerjet_job['country_code'] == 'GB'
        
        # Test geographic Excel export
        from tpm_job_finder_poc.cli.geographic_excel_exporter import GeographicExcelExporter
        
        exporter = GeographicExcelExporter()
        workbook = exporter.create_regional_workbook(jobs)
        
        # Verify workbook structure
        assert len(workbook.worksheets) >= 2  # At least summary + one region
        
        # Find Western Europe sheet
        we_sheet = None
        for sheet in workbook.worksheets:
            if 'Western Europe' in sheet.title:
                we_sheet = sheet
                break
        
        assert we_sheet is not None
        
        # Verify regional intelligence is present
        assert we_sheet.cell(row=1, column=1).value is not None  # Title
        assert 'Western Europe' in str(we_sheet.cell(row=1, column=1).value)
        
        # Verify job data is present
        # Find the header row (should be around row 8)
        header_row = None
        for row in range(1, 15):
            if we_sheet.cell(row=row, column=1).value == 'Title':
                header_row = row
                break
        
        assert header_row is not None
        
        # Check that job data follows
        job_row = header_row + 1
        assert we_sheet.cell(row=job_row, column=1).value == 'Senior Technical Program Manager'
