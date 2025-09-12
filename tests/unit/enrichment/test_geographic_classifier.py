"""Unit tests for Geographic Classifier."""

import pytest
from tpm_job_finder_poc.enrichment.geographic_classifier import GeographicClassifier


class TestGeographicClassifier:
    """Test suite for GeographicClassifier."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.classifier = GeographicClassifier()
    
    def test_initialization(self):
        """Test classifier initialization."""
        assert len(self.classifier.regional_mapping) == 11
        assert len(self.classifier.country_to_region) > 0
        assert len(self.classifier.regional_metadata) == 10  # Excluding 'Other'
    
    def test_country_to_region_mapping(self):
        """Test country classification."""
        # Test North America
        assert self.classifier.classify_job_region('US') == 'North America'
        assert self.classifier.classify_job_region('CA') == 'North America'
        assert self.classifier.classify_job_region('MX') == 'North America'
        
        # Test Western Europe
        assert self.classifier.classify_job_region('GB') == 'Western Europe'
        assert self.classifier.classify_job_region('DE') == 'Western Europe'
        assert self.classifier.classify_job_region('FR') == 'Western Europe'
        
        # Test East Asia
        assert self.classifier.classify_job_region('JP') == 'East Asia'
        assert self.classifier.classify_job_region('KR') == 'East Asia'
        assert self.classifier.classify_job_region('CN') == 'East Asia'
        
        # Test case insensitive
        assert self.classifier.classify_job_region('us') == 'North America'
        assert self.classifier.classify_job_region('gb') == 'Western Europe'
        
        # Test unknown country
        assert self.classifier.classify_job_region('ZZ') == 'Other'
    
    def test_regional_metadata(self):
        """Test regional metadata retrieval."""
        # Test North America metadata
        na_metadata = self.classifier.get_regional_metadata('North America')
        assert na_metadata['timezone_range'] == 'UTC-8 to UTC-5'
        assert 'English' in na_metadata['primary_languages']
        assert na_metadata['avg_cost_of_living'] == 1.0
        assert 'San Francisco' in na_metadata['major_tech_hubs']
        
        # Test Western Europe metadata
        we_metadata = self.classifier.get_regional_metadata('Western Europe')
        assert we_metadata['timezone_range'] == 'UTC+0 to UTC+2'
        assert 'English' in we_metadata['primary_languages']
        assert we_metadata['work_visa_complexity'] == 'Medium'
        
        # Test unknown region
        unknown_metadata = self.classifier.get_regional_metadata('Unknown Region')
        assert unknown_metadata == {}
    
    def test_timezone_overlap_calculation(self):
        """Test timezone overlap assessment."""
        # Test excellent overlap (same timezone)
        overlap = self.classifier.calculate_timezone_overlap(-8, -8)
        assert 'Excellent' in overlap
        
        # Test good overlap (3 hour difference)
        overlap = self.classifier.calculate_timezone_overlap(-5, -8)
        assert 'Excellent' in overlap
        
        # Test fair overlap (6 hour difference)  
        overlap = self.classifier.calculate_timezone_overlap(-2, -8)
        assert 'Good' in overlap
        
        # Test challenging overlap (12+ hour difference)
        overlap = self.classifier.calculate_timezone_overlap(8, -8)
        assert 'Challenging' in overlap
    
    def test_visa_requirements_assessment(self):
        """Test visa requirements assessment."""
        # Test US (no visa needed)
        us_visa = self.classifier.assess_visa_requirements('US')
        assert us_visa['required'] is False
        assert us_visa['complexity'] == 'none'
        
        # Test Canada (NAFTA/USMCA)
        ca_visa = self.classifier.assess_visa_requirements('CA')
        assert ca_visa['required'] is False
        assert ca_visa['complexity'] == 'Low'
        
        # Test UK (visa required)
        uk_visa = self.classifier.assess_visa_requirements('GB')
        assert uk_visa['required'] is True
        assert 'Skilled Worker' in uk_visa['details']
        
        # Test unknown country
        unknown_visa = self.classifier.assess_visa_requirements('ZZ')
        assert unknown_visa['required'] is True
        assert unknown_visa['complexity'] == 'High'
    
    def test_cost_of_living_adjustment(self):
        """Test cost of living salary adjustment."""
        # Test North America (baseline)
        na_adjusted = self.classifier.get_cost_of_living_adjustment('North America', 100000)
        assert na_adjusted == 100000.0  # No adjustment
        
        # Test Eastern Europe (lower cost)
        ee_adjusted = self.classifier.get_cost_of_living_adjustment('Eastern Europe', 100000)
        assert ee_adjusted > 100000  # Higher purchasing power
        
        # Test East Asia (higher cost)
        ea_adjusted = self.classifier.get_cost_of_living_adjustment('East Asia', 100000)
        assert ea_adjusted < 100000  # Lower purchasing power
        
        # Test None salary
        none_adjusted = self.classifier.get_cost_of_living_adjustment('North America', None)
        assert none_adjusted is None
        
        # Test unknown region
        unknown_adjusted = self.classifier.get_cost_of_living_adjustment('Unknown', 100000)
        assert unknown_adjusted == 100000  # Default to no adjustment
    
    def test_organize_jobs_by_region(self):
        """Test job organization by region."""
        jobs = [
            {'title': 'TPM 1', 'country_code': 'US', 'match_score': 0.9, 'usd_equivalent': 150000},
            {'title': 'TPM 2', 'country_code': 'GB', 'match_score': 0.8, 'usd_equivalent': 120000},
            {'title': 'TPM 3', 'country_code': 'JP', 'match_score': 0.7, 'usd_equivalent': 140000},
            {'title': 'TPM 4', 'country_code': 'US', 'match_score': 0.6, 'usd_equivalent': 130000},
            {'title': 'TPM 5', 'region': 'North America', 'match_score': 0.5, 'usd_equivalent': 110000},
        ]
        
        regional_jobs = self.classifier.organize_jobs_by_region(jobs)
        
        # Check regions are created
        assert 'North America' in regional_jobs
        assert 'Western Europe' in regional_jobs
        assert 'East Asia' in regional_jobs
        
        # Check job counts
        assert len(regional_jobs['North America']) == 3  # US jobs + pre-classified
        assert len(regional_jobs['Western Europe']) == 1  # GB job
        assert len(regional_jobs['East Asia']) == 1  # JP job
        
        # Check sorting (by match score desc, then salary desc)
        na_jobs = regional_jobs['North America']
        assert na_jobs[0]['match_score'] == 0.9  # Highest score first
        assert na_jobs[1]['match_score'] == 0.6  # Second highest score
    
    def test_region_priority_order(self):
        """Test region priority ordering."""
        priority_order = self.classifier.get_region_priority_order()
        
        assert len(priority_order) == 11
        assert priority_order[0] == 'North America'  # Highest priority
        assert priority_order[1] == 'Western Europe'  # Second priority
        assert priority_order[-1] == 'Other'  # Lowest priority
        
        # Ensure all regions are included
        for region in self.classifier.regional_mapping.keys():
            assert region in priority_order
    
    def test_all_countries_have_regions(self):
        """Test that all countries in mapping have valid regions."""
        for region, countries in self.classifier.regional_mapping.items():
            for country in countries:
                # Each country should map back to its region
                classified_region = self.classifier.classify_job_region(country)
                assert classified_region == region
    
    def test_regional_metadata_completeness(self):
        """Test that all regions (except Other) have complete metadata."""
        expected_fields = [
            'timezone_range', 'primary_languages', 'business_culture',
            'work_visa_complexity', 'avg_cost_of_living', 'major_tech_hubs',
            'currency_stability', 'remote_work_acceptance'
        ]
        
        for region in self.classifier.regional_mapping.keys():
            if region != 'Other':  # Skip 'Other' region
                metadata = self.classifier.get_regional_metadata(region)
                for field in expected_fields:
                    assert field in metadata, f"Missing {field} in {region} metadata"


@pytest.fixture
def sample_jobs():
    """Sample jobs for testing."""
    return [
        {
            'title': 'Senior TPM',
            'company': 'Google',
            'country_code': 'US',
            'region': 'North America',
            'match_score': 0.95,
            'usd_equivalent': 180000,
            'location': 'Mountain View, CA'
        },
        {
            'title': 'Principal PM',
            'company': 'Spotify',
            'country_code': 'SE',
            'match_score': 0.85,
            'usd_equivalent': 140000,
            'location': 'Stockholm, Sweden'
        },
        {
            'title': 'TPM Lead',
            'company': 'Sony',
            'country_code': 'JP',
            'match_score': 0.75,
            'usd_equivalent': 160000,
            'location': 'Tokyo, Japan'
        }
    ]


class TestGeographicClassifierIntegration:
    """Integration tests for GeographicClassifier."""
    
    def test_complete_job_processing_workflow(self, sample_jobs):
        """Test complete job processing with geographic classification."""
        classifier = GeographicClassifier()
        
        # Organize jobs by region
        regional_jobs = classifier.organize_jobs_by_region(sample_jobs)
        
        # Should have three regions
        assert len(regional_jobs) == 3
        
        # Test North America job
        na_jobs = regional_jobs.get('North America', [])
        assert len(na_jobs) == 1
        na_job = na_jobs[0]
        assert na_job['title'] == 'Senior TPM'
        
        # Test visa requirements for each job
        for job in sample_jobs:
            country = job['country_code']
            visa_info = classifier.assess_visa_requirements(country)
            assert 'required' in visa_info
            assert 'complexity' in visa_info
        
        # Test cost of living adjustments
        for region, jobs in regional_jobs.items():
            for job in jobs:
                if job.get('usd_equivalent'):
                    adjusted = classifier.get_cost_of_living_adjustment(
                        region, job['usd_equivalent']
                    )
                    assert adjusted is not None
                    assert adjusted > 0
