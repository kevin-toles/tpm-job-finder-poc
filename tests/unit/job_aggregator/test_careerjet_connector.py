"""Unit tests for Careerjet connector."""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from tpm_job_finder_poc.job_aggregator.aggregators.careerjet import CareerjetConnector

# Fast mode check
FAST_MODE = os.getenv('PYTEST_FAST_MODE', '0') == '1'

@pytest.mark.skipif(FAST_MODE, reason="Careerjet tests involve currency conversion and network calls - skipped in fast mode")
class TestCareerjetConnector:
    """Test suite for CareerjetConnector."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.affiliate_id = "test_affiliate_123"
        self.locales = ["en_US", "en_GB", "en_CA"]
        self.connector = CareerjetConnector(self.affiliate_id, self.locales)
    
    def test_initialization(self):
        """Test connector initialization."""
        assert self.connector.affiliate_id == self.affiliate_id
        assert self.connector.locales == self.locales
        assert self.connector.source == "careerjet"
        assert len(self.connector.locale_urls) == 3
    
    def test_default_locales(self):
        """Test default locale initialization."""
        connector = CareerjetConnector("test_id")
        expected_locales = ["en_US", "en_GB", "en_CA", "en_AU", "en_SG"]
        assert connector.locales == expected_locales
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.requests.get')
    def test_fetch_since_success(self, mock_get):
        """Test successful job fetching."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            'type': 'JOBS',
            'jobs': [
                {
                    'title': 'Senior Technical Program Manager',
                    'company': 'TechCorp',
                    'locations': 'San Francisco, CA',
                    'date': '2025-09-12',
                    'url': 'https://example.com/job1',
                    'description': 'Great TPM role...',
                    'salary': '$150,000 - $180,000'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        since = datetime.now() - timedelta(days=1)
        jobs = self.connector.fetch_since(since)
        
        assert len(jobs) > 0
        job = jobs[0]
        assert job['title'] == 'Senior Technical Program Manager'
        assert job['company'] == 'TechCorp'
        assert job['source_site'] == 'careerjet'
        assert 'region' in job
        assert 'country_code' in job
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.requests.get')
    def test_fetch_since_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_get.side_effect = Exception("API Error")
        
        since = datetime.now() - timedelta(days=1)
        jobs = self.connector.fetch_since(since)
        
        # Should return empty list on error
        assert jobs == []
    
    def test_normalize_job(self):
        """Test job normalization."""
        job_data = {
            'title': 'Principal TPM',
            'company': 'MegaCorp',
            'locations': 'London',
            'date': '2025-09-12',
            'url': 'https://example.com/job2',
            'description': 'Excellent opportunity...',
            'salary': '£120,000'
        }
        
        locale = 'en_GB'
        region_info = self.connector.LOCALE_REGIONS[locale]
        search_term = 'technical program manager'
        
        normalized = self.connector._normalize_job(job_data, locale, region_info, search_term)
        
        assert normalized is not None
        assert normalized['title'] == 'Principal TPM'
        assert normalized['company'] == 'MegaCorp'
        assert normalized['locale'] == 'en_GB'
        assert normalized['region'] == 'Western Europe'
        assert normalized['country_code'] == 'GB'
        assert normalized['visa_required'] is True
        assert normalized['search_term'] == search_term
    
    def test_extract_salary(self):
        """Test salary extraction."""
        # Test salary range
        job_data = {'salary': '$120,000 - $150,000'}
        min_sal, max_sal, local_sal = self.connector._extract_salary(job_data)
        assert min_sal == 120000
        assert max_sal == 150000
        assert local_sal == '$120,000 - $150,000'
        
        # Test single salary
        job_data = {'salary': '€80,000'}
        min_sal, max_sal, local_sal = self.connector._extract_salary(job_data)
        assert min_sal == 80000
        assert max_sal == 80000
        
        # Test no salary
        job_data = {'salary': ''}
        min_sal, max_sal, local_sal = self.connector._extract_salary(job_data)
        assert min_sal is None
        assert max_sal is None
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.CurrencyRates')
    def test_convert_to_usd(self, mock_currency_rates):
        """Test currency conversion."""
        mock_converter = Mock()
        mock_converter.convert.return_value = 125000.0
        self.connector.currency_converter = mock_converter
        
        # Test conversion
        usd_amount = self.connector._convert_to_usd(100000, 'EUR')
        assert usd_amount == 125000.0
        mock_converter.convert.assert_called_with('EUR', 'USD', 100000)
        
        # Test USD to USD (no conversion)
        usd_amount = self.connector._convert_to_usd(100000, 'USD')
        assert usd_amount == 100000
        
        # Test None amount
        usd_amount = self.connector._convert_to_usd(None, 'EUR')
        assert usd_amount is None
    
    def test_get_country_name(self):
        """Test country name resolution."""
        # Test valid country code
        name = self.connector._get_country_name('US')
        assert 'United States' in name or 'US' in name
        
        # Test invalid country code
        name = self.connector._get_country_name('XX')
        assert name == 'XX'
    
    def test_requires_visa(self):
        """Test visa requirement assessment."""
        # US citizens don't need visa for US
        assert self.connector._requires_visa('US') is False
        
        # Canada has special arrangement
        assert self.connector._requires_visa('CA') is False
        
        # Other countries require visa
        assert self.connector._requires_visa('GB') is True
        assert self.connector._requires_visa('DE') is True
    
    def test_is_recent_job(self):
        """Test recent job filtering."""
        since = datetime.now() - timedelta(days=1)
        
        # Test recent job
        recent_job = {'posted_date': datetime.now().isoformat()}
        assert self.connector._is_recent_job(recent_job, since) is True
        
        # Test old job
        old_job = {'posted_date': (datetime.now() - timedelta(days=5)).isoformat()}
        assert self.connector._is_recent_job(old_job, since) is False
        
        # Test job without date (should be included)
        no_date_job = {'posted_date': ''}
        assert self.connector._is_recent_job(no_date_job, since) is True
    
    def test_locale_regions_mapping(self):
        """Test that all defined locales have region mappings."""
        for locale in self.connector.LOCALE_REGIONS:
            region_info = self.connector.LOCALE_REGIONS[locale]
            assert 'region' in region_info
            assert 'country' in region_info
            assert 'currency' in region_info
            assert region_info['region'] in [
                'North America', 'Western Europe', 'Eastern Europe', 
                'East Asia', 'Southeast Asia', 'South Asia', 
                'South America', 'Africa', 'Australia/Oceania', 
                'Central America'
            ]


@pytest.fixture
def mock_careerjet_response():
    """Mock Careerjet API response for testing."""
    return {
        'type': 'JOBS',
        'jobs': [
            {
                'title': 'Senior Technical Program Manager',
                'company': 'Google',
                'locations': 'Mountain View, CA',
                'date': '2025-09-12',
                'url': 'https://careers.google.com/jobs/results/123',
                'description': 'Lead cross-functional teams...',
                'salary': '$180,000 - $220,000'
            },
            {
                'title': 'Principal Product Manager',
                'company': 'Microsoft',
                'locations': 'Redmond, WA',
                'date': '2025-09-11',
                'url': 'https://careers.microsoft.com/jobs/123',
                'description': 'Drive product strategy...',
                'salary': '$160,000 - $200,000'
            }
        ]
    }


@pytest.mark.skipif(FAST_MODE, reason="Integration tests with network calls - skipped in fast mode")
class TestCareerjetIntegration:
    """Integration tests for Careerjet connector."""
    
    @patch('tpm_job_finder_poc.job_aggregator.aggregators.careerjet.requests.get')
    def test_end_to_end_job_collection(self, mock_get, mock_careerjet_response):
        """Test complete job collection workflow."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_careerjet_response
        mock_get.return_value = mock_response
        
        connector = CareerjetConnector("test_affiliate", ["en_US"])
        since = datetime.now() - timedelta(days=1)
        
        jobs = connector.fetch_since(since)
        
        assert len(jobs) > 0
        
        # Check that jobs have all required fields
        for job in jobs:
            assert 'title' in job
            assert 'company' in job
            assert 'source_site' in job
            assert job['source_site'] == 'careerjet'
            assert 'region' in job
            assert 'country_code' in job
            assert 'visa_required' in job
