"""
Unit tests for browser scrapers in tpm_job_finder_poc.scraping_service.

Tests the browser-based job scrapers:
- BaseScraper functionality
- Indeed scraper
- LinkedIn scraper  
- ZipRecruiter scraper
- Greenhouse scraper
"""

import pytest
import os
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List

# Fast mode check
FAST_MODE = os.getenv('PYTEST_FAST_MODE', '0') == '1'

# Skip all browser scraper tests in fast mode
pytestmark = pytest.mark.skipif(FAST_MODE, reason="Browser scraper tests use Selenium and are slow - skipped in fast mode")

from tpm_job_finder_poc.scraping_service.scrapers.base_scraper import BaseScraper, BrowserProfile
from tpm_job_finder_poc.scraping_service.scrapers.indeed.scraper import IndeedScraper
from tpm_job_finder_poc.scraping_service.scrapers.linkedin.scraper import LinkedInScraper
from tpm_job_finder_poc.scraping_service.scrapers.ziprecruiter.scraper import ZipRecruiterScraper
from tpm_job_finder_poc.scraping_service.scrapers.greenhouse.scraper import GreenhouseScraper
from tpm_job_finder_poc.scraping_service.core.base_job_source import (
    FetchParams, 
    JobPosting, 
    HealthStatus,
    SourceType,
    RateLimitConfig
)


class TestBrowserProfile:
    """Test BrowserProfile functionality."""
    
    def test_browser_profile_creation(self):
        """Test creating browser profile."""
        profile = BrowserProfile(
            user_agent="Mozilla/5.0 (Test Browser)",
            viewport=(1920, 1080)
        )
        
        assert profile.user_agent == "Mozilla/5.0 (Test Browser)"
        assert profile.viewport_width == 1920
        assert profile.viewport_height == 1080
        
    def test_random_profile_generation(self):
        """Test random profile generation."""
        profile = BrowserProfile.random_profile()
        
        assert profile.user_agent is not None
        assert profile.viewport_width > 0
        assert profile.viewport_height > 0


class TestBaseScraper:
    """Test BaseScraper base class."""
    
    class MockScraper(BaseScraper):
        """Mock implementation of BaseScraper for testing."""
        
        def __init__(self, name="mock_scraper"):
            super().__init__(name, "https://example.com")
            self.mock_jobs = []
            
        def get_search_url(self, **kwargs) -> str:
            return f"{self.base_url}/jobs?q={kwargs.get('q', '')}"
            
        def get_selectors(self) -> Dict[str, str]:
            return {
                'job_cards': '.job-card',
                'job_title': '.title', 
                'company': '.company'
            }
            
        async def parse_job_elements(self, driver) -> List[JobPosting]:
            return self.mock_jobs
    
    @pytest.fixture
    def mock_scraper(self):
        """Create mock scraper instance."""
        return self.MockScraper()
        
    def test_scraper_initialization(self, mock_scraper):
        """Test scraper initialization."""
        assert mock_scraper.name == "mock_scraper"
        assert mock_scraper.base_url == "https://example.com"
        assert mock_scraper.source_type == SourceType.BROWSER_SCRAPER
        
    def test_get_rate_limits(self, mock_scraper):
        """Test rate limit configuration."""
        rate_limits = mock_scraper.get_rate_limits()
        
        assert isinstance(rate_limits, RateLimitConfig)
        assert rate_limits.requests_per_minute == 10  # Default
        assert rate_limits.requests_per_hour == 300
        
    def test_build_search_url(self, mock_scraper):
        """Test search URL building."""
        params = FetchParams(keywords=["python", "developer"], location="Remote")
        url = mock_scraper._build_search_url(params)
        
        assert "python developer" in url
        
    @pytest.mark.asyncio
    @patch('selenium.webdriver.Chrome')
    @patch('tpm_job_finder_poc.scraping_service.scrapers.base_scraper.ChromeDriverManager')
    async def test_setup_browser(self, mock_driver_manager, mock_chrome, mock_scraper):
        """Test browser setup."""
        mock_driver = Mock()
        mock_chrome.return_value = mock_driver
        mock_driver_manager.return_value.install.return_value = "/path/to/chromedriver"
        
        driver = await mock_scraper.setup_browser()
        
        assert mock_chrome.called
        assert mock_driver.execute_script.called  # Anti-detection script
        
    @pytest.mark.asyncio
    @patch('tpm_job_finder_poc.scraping_service.scrapers.base_scraper.ChromeDriverManager')
    async def test_initialize_cleanup(self, mock_driver_manager, mock_scraper):
        """Test initialization and cleanup."""
        with patch.object(mock_scraper, 'setup_browser') as mock_setup:
            mock_driver = Mock()
            mock_setup.return_value = mock_driver
            
            # Test initialization
            success = await mock_scraper.initialize()
            assert success is True
            assert mock_scraper._driver is mock_driver
            
            # Test cleanup
            await mock_scraper.cleanup()
            assert mock_driver.quit.called


class TestIndeedScraper:
    """Test Indeed scraper implementation."""
    
    @pytest.fixture
    def indeed_scraper(self):
        """Create Indeed scraper instance."""
        return IndeedScraper()
        
    def test_indeed_initialization(self, indeed_scraper):
        """Test Indeed scraper initialization."""
        assert indeed_scraper.name == "indeed"
        assert "indeed.com" in indeed_scraper.base_url
        
    def test_get_search_url(self, indeed_scraper):
        """Test Indeed search URL generation."""
        url = indeed_scraper.get_search_url(q="python developer", l="San Francisco")
        
        # URL encode spaces as + in query parameters
        assert "python+developer" in url
        assert "San+Francisco" in url
        assert "sort=date" in url
        
    def test_get_selectors(self, indeed_scraper):
        """Test Indeed CSS selectors."""
        selectors = indeed_scraper.get_selectors()
        
        required_selectors = [
            'job_cards', 'job_title', 'company_name', 
            'location', 'date_posted', 'next_button'
        ]
        
        for selector in required_selectors:
            assert selector in selectors
            assert selectors[selector]  # Not empty
            
    def test_extract_job_id_from_url(self, indeed_scraper):
        """Test job ID extraction from Indeed URLs."""
        url = "https://www.indeed.com/viewjob?jk=abc123def456"
        job_id = indeed_scraper._extract_job_id_from_url(url)
        
        assert job_id == "indeed_abc123def456"
        
    def test_parse_posted_date(self, indeed_scraper):
        """Test date parsing logic."""
        # Mock element with date text
        mock_element = Mock()
        mock_element.text.strip.return_value = "2 days ago"
        
        selectors = {
            'date_posted': '.date-posted',
            'date_posted_fallback': '.post-date'
        }
        
        with patch.object(indeed_scraper, '_find_element_with_fallback') as mock_find:
            mock_find.return_value = mock_element
            
            date = indeed_scraper._parse_posted_date(mock_element, selectors)
            
            assert date is not None
            assert isinstance(date, datetime)
            
    def test_supported_params(self, indeed_scraper):
        """Test supported parameters."""
        params = indeed_scraper.get_supported_params()
        
        assert "keywords" in params
        assert "location" in params
        assert "limit" in params


class TestLinkedInScraper:
    """Test LinkedIn scraper implementation."""
    
    @pytest.fixture
    def linkedin_scraper(self):
        """Create LinkedIn scraper instance."""
        return LinkedInScraper()
        
    def test_linkedin_initialization(self, linkedin_scraper):
        """Test LinkedIn scraper initialization."""
        assert linkedin_scraper.name == "linkedin"
        assert "linkedin.com" in linkedin_scraper.base_url
        assert linkedin_scraper.authenticated is False
        
    def test_linkedin_with_credentials(self):
        """Test LinkedIn scraper with credentials."""
        scraper = LinkedInScraper(email="test@example.com", password="password")
        
        assert scraper.email == "test@example.com"
        assert scraper.password == "password"
        
    def test_get_search_url(self, linkedin_scraper):
        """Test LinkedIn search URL generation."""
        url = linkedin_scraper.get_search_url(q="product manager", location="Remote")
        
        assert "jobs/search" in url
        assert "keywords=product+manager" in url or "product manager" in url
        assert "location=Remote" in url
        
    def test_extract_job_id(self, linkedin_scraper):
        """Test LinkedIn job ID extraction."""
        # Test with data attribute only
        mock_element = Mock()
        mock_element.get_attribute.return_value = "urn:li:fsd_jobPosting:123456789"
        
        job_id = linkedin_scraper._extract_linkedin_job_id(mock_element, None)
        assert job_id == "linkedin_123456789"
        
        # Test with URL (should override data attribute)
        mock_element2 = Mock()
        mock_element2.get_attribute.return_value = None  # No data attribute, so use URL
        url = "https://www.linkedin.com/jobs/view/987654321"
        job_id = linkedin_scraper._extract_linkedin_job_id(mock_element2, url)
        assert job_id == "linkedin_987654321"
        
    def test_parse_linkedin_date(self, linkedin_scraper):
        """Test LinkedIn date parsing."""
        mock_element = Mock()
        mock_element.text.strip.return_value = "1 hour ago"
        
        selectors = {
            'date_posted': '.job-post-date',
            'date_posted_fallback': '.post-time'
        }
        
        with patch.object(linkedin_scraper, '_find_element_with_fallback') as mock_find:
            mock_find.return_value = mock_element
            
            date = linkedin_scraper._parse_linkedin_date(mock_element, selectors)
            
            assert date is not None
            assert isinstance(date, datetime)


class TestZipRecruiterScraper:
    """Test ZipRecruiter scraper implementation."""
    
    @pytest.fixture
    def ziprecruiter_scraper(self):
        """Create ZipRecruiter scraper instance."""
        return ZipRecruiterScraper()
        
    def test_ziprecruiter_initialization(self, ziprecruiter_scraper):
        """Test ZipRecruiter scraper initialization."""
        assert ziprecruiter_scraper.name == "ziprecruiter"
        assert "ziprecruiter.com" in ziprecruiter_scraper.base_url
        
    def test_get_search_url(self, ziprecruiter_scraper):
        """Test ZipRecruiter search URL generation."""
        url = ziprecruiter_scraper.get_search_url(q="data scientist", location="New York")
        
        assert "search=data+scientist" in url or "data scientist" in url
        assert "location=New+York" in url or "New York" in url
        
    def test_extract_job_id(self, ziprecruiter_scraper):
        """Test ZipRecruiter job ID extraction."""
        # Test with URL pattern
        url = "https://www.ziprecruiter.com/jobs/software-engineer-abc123"
        job_id = ziprecruiter_scraper._extract_ziprecruiter_job_id(Mock(), url)
        
        assert "ziprecruiter_" in job_id
        
    def test_parse_date(self, ziprecruiter_scraper):
        """Test ZipRecruiter date parsing."""
        mock_element = Mock()
        mock_element.text.strip.return_value = "just posted"
        
        selectors = {
            'date_posted': '.posted-time',
            'date_posted_fallback': '.job-date'
        }
        
        with patch.object(ziprecruiter_scraper, '_find_element_with_fallback') as mock_find:
            mock_find.return_value = mock_element
            
            date = ziprecruiter_scraper._parse_ziprecruiter_date(mock_element, selectors)
            
            assert date is not None
            assert isinstance(date, datetime)


class TestGreenhouseScraper:
    """Test Greenhouse scraper implementation."""
    
    @pytest.fixture
    def greenhouse_scraper(self):
        """Create Greenhouse scraper instance."""
        return GreenhouseScraper()
        
    def test_greenhouse_initialization(self, greenhouse_scraper):
        """Test Greenhouse scraper initialization."""
        assert greenhouse_scraper.name == "greenhouse"
        assert "greenhouse.io" in greenhouse_scraper.base_url
        assert len(greenhouse_scraper.known_companies) > 0
        
    def test_get_search_url(self, greenhouse_scraper):
        """Test Greenhouse search URL generation."""
        # Test with company
        url = greenhouse_scraper.get_search_url(company="airbnb", q="engineer")
        assert "airbnb.greenhouse.io" in url
        
        # Test without company (discovery mode)
        url = greenhouse_scraper.get_search_url()
        assert "greenhouse.io/companies" in url
        
    def test_extract_job_id(self, greenhouse_scraper):
        """Test Greenhouse job ID extraction."""
        url = "https://boards.greenhouse.io/airbnb/jobs/123456789"
        job_id = greenhouse_scraper._extract_greenhouse_job_id(url)
        
        assert job_id == "greenhouse_123456789"
        
    def test_extract_company_name(self, greenhouse_scraper):
        """Test company name extraction."""
        # Mock driver with URL
        mock_driver = Mock()
        mock_driver.current_url = "https://airbnb.greenhouse.io/jobs"
        greenhouse_scraper._driver = mock_driver
        
        company = greenhouse_scraper._extract_company_name()
        assert company == "Airbnb"
        
    def test_default_companies(self, greenhouse_scraper):
        """Test default company list."""
        companies = greenhouse_scraper._get_default_greenhouse_companies()
        
        # Should include major tech companies
        expected_companies = ['airbnb', 'stripe', 'gitlab', 'dropbox']
        for company in expected_companies:
            assert company in companies


class TestScraperIntegration:
    """Test scraper integration and common functionality."""
    
    @pytest.mark.asyncio
    async def test_all_scrapers_implement_interface(self):
        """Test that all scrapers properly implement the base interface."""
        scrapers = [
            IndeedScraper(),
            LinkedInScraper(), 
            ZipRecruiterScraper(),
            GreenhouseScraper()
        ]
        
        for scraper in scrapers:
            # Test required methods exist
            assert hasattr(scraper, 'get_search_url')
            assert hasattr(scraper, 'get_selectors')
            assert hasattr(scraper, 'parse_job_elements')
            assert hasattr(scraper, 'get_supported_params')
            
            # Test selectors are defined
            selectors = scraper.get_selectors()
            assert isinstance(selectors, dict)
            assert len(selectors) > 0
            
            # Test supported params
            params = scraper.get_supported_params()
            assert isinstance(params, dict)
            assert "keywords" in params or "limit" in params
            
    def test_scraper_rate_limits(self):
        """Test that all scrapers have appropriate rate limits."""
        scrapers = [
            IndeedScraper(),
            LinkedInScraper(),
            ZipRecruiterScraper(), 
            GreenhouseScraper()
        ]
        
        for scraper in scrapers:
            rate_limits = scraper.get_rate_limits()
            
            # LinkedIn should be most restrictive
            if scraper.name == "linkedin":
                assert rate_limits.requests_per_minute <= 5
            # Indeed should be conservative
            elif scraper.name == "indeed":
                assert rate_limits.requests_per_minute <= 10
            # ZipRecruiter can be more permissive
            elif scraper.name == "ziprecruiter":
                assert rate_limits.requests_per_minute >= 10
                
    def test_scraper_anti_detection_setup(self):
        """Test that scrapers have anti-detection measures."""
        scrapers = [IndeedScraper(), LinkedInScraper()]
        
        for scraper in scrapers:
            # Should have browser profile
            assert hasattr(scraper, '_profile')
            
            # Profile should have realistic user agent
            profile = scraper._profile
            assert "Mozilla" in profile.user_agent
            assert "Chrome" in profile.user_agent
            
    @pytest.mark.asyncio
    async def test_scraper_health_checks(self):
        """Test health check implementation for all scrapers."""
        scrapers = [
            IndeedScraper(),
            LinkedInScraper(),
            ZipRecruiterScraper(), 
            GreenhouseScraper()
        ]
        
        for scraper in scrapers:
            with patch.object(scraper, '_driver') as mock_driver:
                mock_driver.get = Mock()
                mock_driver.current_url = scraper.base_url
                mock_driver.page_source = "normal page content"
                mock_driver.execute_script.return_value = "complete"
                
                health = await scraper.health_check()
                
                assert health.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]
                assert health.message is not None
                assert health.timestamp is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
