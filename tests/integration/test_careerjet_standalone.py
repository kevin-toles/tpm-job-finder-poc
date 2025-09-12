"""Standalone integration tests for Careerjet connector and geographic functionality."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from tpm_job_finder_poc.job_aggregator.aggregators.careerjet import CareerjetConnector
from tpm_job_finder_poc.enrichment.geographic_classifier import GeographicClassifier
from tpm_job_finder_poc.cli.geographic_excel_exporter import GeographicExcelExporter


class TestCareerjetStandaloneIntegration:
    """Standalone integration tests for Careerjet connector."""
    
    @pytest.fixture
    def careerjet_connector(self):
        """Create a Careerjet connector for testing."""
        return CareerjetConnector(
            affiliate_id='test_affiliate_123',
            locales=['en_US', 'en_GB', 'en_CA']
        )
    
    @pytest.fixture
    def mock_careerjet_response(self):
        """Mock Careerjet API response."""
        return {
            'type': 'JOBS',
            'jobs': [
                {
                    'title': 'Senior Technical Program Manager',
                    'company': 'Google',
                    'locations': 'Mountain View, CA',
                    'date': '2025-09-12',
                    'url': 'https://careers.google.com/jobs/results/123',
                    'description': 'Lead cross-functional teams to deliver complex technical projects...',
                    'salary': '$180,000 - $220,000'
                },
                {
                    'title': 'Principal Product Manager',
                    'company': 'Spotify',
                    'locations': 'Stockholm',
                    'date': '2025-09-11',
                    'url': 'https://jobs.lever.co/spotify/123',
                    'description': 'Drive product strategy for our streaming platform...',
                    'salary': '1,200,000 - 1,500,000 SEK'
                }
            ]
        }
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.requests.get')
    def test_careerjet_fetch_since_integration(
        self, mock_requests_get, careerjet_connector, mock_careerjet_response
    ):
        """Test Careerjet fetch_since method with real connector logic."""
        def mock_response_side_effect(url, params=None, **kwargs):
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            
            # Check locale code in params to return different jobs
            locale_code = params.get('locale_code') if params else None
            
            if locale_code == 'en_US':  # US locale
                mock_response.json.return_value = {
                    'type': 'JOBS',
                    'jobs': [
                        {
                            'title': 'Senior Technical Program Manager',
                            'company': 'Google',
                            'locations': 'Mountain View, CA',
                            'date': '2025-09-12',
                            'url': 'https://careers.google.com/jobs/results/123',
                            'description': 'Lead cross-functional teams to deliver complex technical projects...',
                            'salary': '$180,000 - $220,000'
                        }
                    ]
                }
            elif locale_code == 'en_GB':  # UK locale
                mock_response.json.return_value = {
                    'type': 'JOBS',
                    'jobs': [
                        {
                            'title': 'Principal Product Manager',
                            'company': 'Spotify',
                            'locations': 'London',
                            'date': '2025-09-11',
                            'url': 'https://jobs.lever.co/spotify/123',
                            'description': 'Drive product strategy for our streaming platform...',
                            'salary': '£80,000 - £120,000'
                        }
                    ]
                }
            else:  # CA locale or other
                mock_response.json.return_value = {
                    'type': 'JOBS',
                    'jobs': []  # No jobs for CA to avoid confusion
                }
            
            return mock_response
        
        # Setup mock
        mock_requests_get.side_effect = mock_response_side_effect
        
        # Fetch jobs
        week_ago = datetime.utcnow() - timedelta(days=7)
        jobs = careerjet_connector.fetch_since(week_ago)
        
        # Verify results
        assert len(jobs) >= 2  # At least 2 jobs from our mock
        
        # Find our specific jobs
        google_job = None
        spotify_job = None
        
        for job in jobs:
            if job.get('company') == 'Google':
                google_job = job
            elif job.get('company') == 'Spotify':
                spotify_job = job
        
        # Verify Google job (US)
        assert google_job is not None
        assert google_job['title'] == 'Senior Technical Program Manager'
        assert google_job['source_site'] == 'careerjet'
        assert google_job['region'] == 'North America'
        assert google_job['country_code'] == 'US'
        assert google_job['currency'] == 'USD'
        assert google_job['visa_required'] is False
        
        # Verify Spotify job (UK)
        assert spotify_job is not None
        assert spotify_job['title'] == 'Principal Product Manager'
        assert spotify_job['region'] == 'Western Europe'
        assert spotify_job['country_code'] == 'GB'
        assert spotify_job['currency'] == 'GBP'
        assert spotify_job['visa_required'] is True
        
        # Verify API calls were made
        assert mock_requests_get.call_count >= 3  # One for each locale
    
    def test_careerjet_locale_configuration(self):
        """Test Careerjet connector with different locale configurations."""
        # Test with single locale
        connector_single = CareerjetConnector(
            affiliate_id='test',
            locales=['en_US']
        )
        assert len(connector_single.locale_urls) == 1
        assert 'en_US' in connector_single.locales
        
        # Test with multiple locales
        connector_multi = CareerjetConnector(
            affiliate_id='test',
            locales=['en_US', 'en_GB', 'de_DE', 'fr_FR']
        )
        assert len(connector_multi.locale_urls) == 4
        assert all(locale in connector_multi.locales for locale in ['en_US', 'en_GB', 'de_DE', 'fr_FR'])
        
        # Test with default locales
        connector_default = CareerjetConnector(affiliate_id='test')
        expected_defaults = ["en_US", "en_GB", "en_CA", "en_AU", "en_SG"]
        assert connector_default.locales == expected_defaults


class TestGeographicClassifierIntegration:
    """Integration tests for geographic classifier with real job data."""
    
    @pytest.fixture
    def classifier(self):
        """Create a geographic classifier."""
        return GeographicClassifier()
    
    @pytest.fixture
    def international_jobs(self):
        """Sample international job data for testing."""
        return [
            {
                'title': 'Senior TPM',
                'company': 'Google',
                'location': 'Mountain View, CA',
                'country_code': 'US',
                'match_score': 0.9,
                'salary_min': 180000,
                'currency': 'USD'
            },
            {
                'title': 'Product Manager',
                'company': 'Spotify',
                'location': 'Stockholm, Sweden',
                'country_code': 'SE',
                'match_score': 0.85,
                'salary_min': 120000,
                'currency': 'SEK'
            },
            {
                'title': 'Engineering Manager',
                'company': 'Toyota',
                'location': 'Tokyo, Japan',
                'country_code': 'JP',
                'match_score': 0.8,
                'salary_min': 8000000,
                'currency': 'JPY'
            },
            {
                'title': 'Data Scientist',
                'company': 'Shopify',
                'location': 'Toronto, Canada',
                'country_code': 'CA',
                'match_score': 0.75,
                'salary_min': 90000,
                'currency': 'CAD'
            }
        ]
    
    def test_regional_organization(self, classifier, international_jobs):
        """Test organizing jobs by geographic region."""
        regional_jobs = classifier.organize_jobs_by_region(international_jobs)
        
        # Verify all expected regions are present
        assert 'North America' in regional_jobs
        assert 'Western Europe' in regional_jobs
        assert 'East Asia' in regional_jobs
        
        # Verify job distribution
        assert len(regional_jobs['North America']) == 2  # US + CA
        assert len(regional_jobs['Western Europe']) == 1  # SE
        assert len(regional_jobs['East Asia']) == 1  # JP
        
        # Verify sorting by match score (descending)
        na_jobs = regional_jobs['North America']
        assert na_jobs[0]['match_score'] == 0.9  # Google (US)
        assert na_jobs[1]['match_score'] == 0.75  # Shopify (CA)
    
    def test_visa_assessment(self, classifier):
        """Test visa requirement assessment for different countries."""
        # Test US citizens don't need visas for US
        us_visa = classifier.assess_visa_requirements('US')
        assert us_visa['required'] is False
        assert us_visa['complexity'] == 'none'
        
        # Test visa required for other countries
        sweden_visa = classifier.assess_visa_requirements('SE')
        assert sweden_visa['required'] is True
        assert sweden_visa['complexity'].lower() in ['medium', 'high']
        
        japan_visa = classifier.assess_visa_requirements('JP')
        assert japan_visa['required'] is True
        assert japan_visa['complexity'].lower().replace('-', '') in ['medium', 'high', 'mediumhigh']
    
    def test_regional_metadata(self, classifier):
        """Test regional metadata generation."""
        metadata = classifier.get_regional_metadata('Western Europe')
        
        assert 'timezone_range' in metadata
        assert 'business_culture' in metadata
        assert 'avg_visa_complexity' in metadata
        assert 'avg_cost_of_living' in metadata
        
        # Verify timezone format
        assert 'UTC' in metadata['timezone_range']
        
        # Verify business culture is descriptive
        assert len(metadata['business_culture']) > 10


class TestGeographicExcelExportIntegration:
    """Integration tests for geographic Excel export functionality."""
    
    @pytest.fixture
    def exporter(self):
        """Create a geographic Excel exporter."""
        return GeographicExcelExporter()
    
    @pytest.fixture
    def classified_jobs(self):
        """Pre-classified job data for export testing."""
        return [
            {
                'title': 'Senior TPM',
                'company': 'Google',
                'location': 'Mountain View, CA',
                'region': 'North America',
                'country_code': 'US',
                'match_score': 0.9,
                'usd_equivalent': 200000,
                'visa_required': False,
                'currency': 'USD',
                'source_site': 'careerjet'
            },
            {
                'title': 'Product Manager',
                'company': 'Spotify',
                'location': 'Stockholm, Sweden',
                'region': 'Western Europe',
                'country_code': 'SE',
                'match_score': 0.85,
                'usd_equivalent': 135000,
                'visa_required': True,
                'currency': 'SEK',
                'source_site': 'careerjet'
            },
            {
                'title': 'Engineering Manager',
                'company': 'Toyota',
                'location': 'Tokyo, Japan',
                'region': 'East Asia',
                'country_code': 'JP',
                'match_score': 0.8,
                'usd_equivalent': 65000,
                'visa_required': True,
                'currency': 'JPY',
                'source_site': 'careerjet'
            }
        ]
    
    def test_regional_workbook_creation(self, exporter, classified_jobs):
        """Test creating regional workbook with geographic organization."""
        workbook = exporter.create_regional_workbook(classified_jobs)
        
        # Verify workbook structure
        sheet_names = [sheet.title for sheet in workbook.worksheets]
        
        # Should have summary sheet
        summary_sheets = [name for name in sheet_names if 'Summary' in name]
        assert len(summary_sheets) == 1
        
        # Should have regional sheets
        assert any('North America' in name for name in sheet_names)
        assert any('Western Europe' in name for name in sheet_names)
        assert any('East Asia' in name for name in sheet_names)
        
        # Verify minimum number of sheets (summary + 3 regions)
        assert len(workbook.worksheets) >= 4
    
    def test_regional_sheet_content(self, exporter, classified_jobs):
        """Test content of individual regional sheets."""
        workbook = exporter.create_regional_workbook(classified_jobs)
        
        # Find North America sheet
        na_sheet = None
        for sheet in workbook.worksheets:
            if 'North America' in sheet.title:
                na_sheet = sheet
                break
        
        assert na_sheet is not None
        
        # Verify sheet has content
        assert na_sheet.max_row > 1
        assert na_sheet.max_column >= 8  # Minimum expected columns
        
        # Verify regional intelligence section exists
        # Should have region name in first few rows
        region_found = False
        for row in range(1, 6):
            cell_value = na_sheet.cell(row=row, column=1).value
            if cell_value and 'North America' in str(cell_value):
                region_found = True
                break
        assert region_found
        
        # Verify job data headers exist
        header_row = None
        for row in range(1, 20):
            if na_sheet.cell(row=row, column=1).value == 'Title':
                header_row = row
                break
        
        assert header_row is not None
        
        # Verify expected headers
        expected_headers = ['Title', 'Company', 'Location', 'Match Score', 'USD Salary', 'Visa Required']
        for col, expected_header in enumerate(expected_headers, 1):
            actual_header = na_sheet.cell(row=header_row, column=col).value
            assert expected_header in str(actual_header)
    
    def test_summary_sheet_content(self, exporter, classified_jobs):
        """Test summary sheet content and statistics."""
        workbook = exporter.create_regional_workbook(classified_jobs)
        
        # Find summary sheet
        summary_sheet = None
        for sheet in workbook.worksheets:
            if 'Summary' in sheet.title:
                summary_sheet = sheet
                break
        
        assert summary_sheet is not None
        
        # Verify summary contains regional statistics
        # Should have region names and job counts
        content_found = {
            'North America': False,
            'Western Europe': False,
            'East Asia': False
        }
        
        for row in range(1, summary_sheet.max_row + 1):
            for col in range(1, summary_sheet.max_column + 1):
                cell_value = summary_sheet.cell(row=row, column=col).value
                if cell_value:
                    cell_str = str(cell_value)
                    for region in content_found:
                        if region in cell_str:
                            content_found[region] = True
        
        # Verify all regions are mentioned in summary
        assert all(content_found.values()), f"Missing regions in summary: {content_found}"


@pytest.mark.integration
class TestCareerjetEndToEndStandalone:
    """End-to-end integration tests for Careerjet workflow without service dependencies."""
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.requests.get')
    def test_complete_workflow_careerjet_to_excel(self, mock_requests_get):
        """Test complete workflow from Careerjet connector to Excel export."""
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
                },
                {
                    'title': 'Principal Product Manager',
                    'company': 'Global Innovations',
                    'locations': 'Berlin',
                    'date': '2025-09-11',
                    'url': 'https://example.com/job2',
                    'description': 'Drive product strategy for European markets...',
                    'salary': '€110,000 - €140,000'
                }
            ]
        }
        mock_requests_get.return_value = mock_response
        
        # Step 1: Fetch jobs from Careerjet
        connector = CareerjetConnector(
            affiliate_id='test_affiliate',
            locales=['en_GB', 'de_DE']
        )
        
        week_ago = datetime.utcnow() - timedelta(days=7)
        jobs = connector.fetch_since(week_ago)
        
        # Verify jobs were fetched and enriched
        assert len(jobs) >= 2
        
        # Step 2: Organize jobs geographically
        classifier = GeographicClassifier()
        regional_jobs = classifier.organize_jobs_by_region(jobs)
        
        # Verify geographic organization
        assert 'Western Europe' in regional_jobs
        we_jobs = regional_jobs['Western Europe']
        assert len(we_jobs) >= 2
        
        # Step 3: Create Excel workbook
        exporter = GeographicExcelExporter()
        
        # Flatten jobs for export
        all_jobs_for_export = []
        for region, region_jobs in regional_jobs.items():
            all_jobs_for_export.extend(region_jobs)
        
        workbook = exporter.create_regional_workbook(all_jobs_for_export)
        
        # Verify complete workflow results
        assert len(workbook.worksheets) >= 2  # Summary + Western Europe
        
        # Find Western Europe sheet
        we_sheet = None
        for sheet in workbook.worksheets:
            if 'Western Europe' in sheet.title:
                we_sheet = sheet
                break
        
        assert we_sheet is not None
        
        # Verify both jobs are in the Western Europe sheet
        # Look for job titles in the sheet
        titles_found = []
        for row in range(1, we_sheet.max_row + 1):
            for col in range(1, we_sheet.max_column + 1):
                cell_value = we_sheet.cell(row=row, column=col).value
                if cell_value:
                    cell_str = str(cell_value)
                    if 'Senior Technical Program Manager' in cell_str:
                        titles_found.append('Senior Technical Program Manager')
                    elif 'Principal Product Manager' in cell_str:
                        titles_found.append('Principal Product Manager')
        
        assert len(titles_found) >= 2  # Both jobs should be found
        
        # Verify regional intelligence is present
        intelligence_found = False
        for row in range(1, 10):  # Check first 10 rows for intelligence
            cell_value = we_sheet.cell(row=row, column=1).value
            if cell_value and ('Western Europe' in str(cell_value) or 'Regional Intelligence' in str(cell_value)):
                intelligence_found = True
                break
        
        assert intelligence_found
