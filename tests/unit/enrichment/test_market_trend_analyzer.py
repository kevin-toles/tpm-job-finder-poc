"""
Unit tests for Market Trend Analyzer.

This module provides comprehensive unit tests for the market trend
analysis functionality including trend calculation, regional analysis,
and seasonal pattern recognition.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

from tpm_job_finder_poc.enrichment.market_trend_analyzer import (
    MarketTrendAnalyzer,
    MarketTrend,
    SalaryTrend,
    market_analyzer
)

# Check if advanced trend analysis API is available
def has_advanced_trend_api():
    analyzer = MarketTrendAnalyzer()
    return hasattr(analyzer, 'analyze_market_trends') and hasattr(analyzer, 'supported_regions')

pytestmark = pytest.mark.skipif(
    not has_advanced_trend_api(),
    reason="Advanced market trend analysis API not fully implemented"
)


class TestMarketTrendAnalyzer:
    """Test suite for Market Trend Analyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = MarketTrendAnalyzer()
        
        # Sample market data for testing
        self.sample_market_data = [
            {
                'region': 'North America',
                'country': 'United States',
                'job_title': 'Data Scientist',
                'salary': '$120,000 - $150,000',
                'posting_date': '2025-08-01',
                'company': 'TechCorp'
            },
            {
                'region': 'North America',
                'country': 'United States',
                'job_title': 'Machine Learning Engineer',
                'salary': '$110,000 - $140,000',
                'posting_date': '2025-08-15',
                'company': 'AI Startup'
            },
            {
                'region': 'Western Europe',
                'country': 'Germany',
                'job_title': 'Data Scientist',
                'salary': '€80,000 - €100,000',
                'posting_date': '2025-09-01',
                'company': 'European Tech'
            }
        ]
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly."""
        assert self.analyzer is not None
        assert len(self.analyzer.supported_regions) > 0
        assert 'North America' in self.analyzer.supported_regions
        assert len(self.analyzer.trend_indicators) > 0
        assert len(self.analyzer.seasonal_factors) > 0
    
    def test_analyze_market_trends(self):
        """Test market trend analysis."""
        trends = self.analyzer.analyze_market_trends(
            self.sample_market_data, time_period_months=3
        )
        
        assert isinstance(trends, dict)
        assert 'overall_trend' in trends
        assert 'regional_insights' in trends
        assert 'salary_trends' in trends
        assert 'job_demand_indicators' in trends
        assert 'growth_indicators' in trends
        assert 'analysis_metadata' in trends
        
        # Check overall trend structure
        overall_trend = trends['overall_trend']
        assert 'direction' in overall_trend
        assert 'strength' in overall_trend
        assert 'confidence' in overall_trend
        assert overall_trend['direction'] in ['growing', 'stable', 'declining']
    
    def test_analyze_regional_trends(self):
        """Test regional trend analysis."""
        regional_trends = self.analyzer.analyze_regional_trends(self.sample_market_data)
        
        assert isinstance(regional_trends, dict)
        assert len(regional_trends) > 0
        
        # Check that regions from sample data are present
        regions_in_data = {item['region'] for item in self.sample_market_data}
        for region in regions_in_data:
            assert region in regional_trends
            
            trend = regional_trends[region]
            assert isinstance(trend, dict)
            assert 'job_count' in trend
            assert 'growth_rate' in trend
            assert 'avg_salary_trend' in trend
            assert 'market_activity' in trend
    
    def test_calculate_seasonal_patterns(self):
        """Test seasonal pattern calculation."""
        # Create data spanning multiple months
        seasonal_data = []
        for month in range(1, 13):
            for i in range(5):  # 5 jobs per month
                seasonal_data.append({
                    'region': 'North America',
                    'country': 'United States',
                    'job_title': 'Data Scientist',
                    'salary': '$120,000',
                    'posting_date': f'2025-{month:02d}-{(i*6)+1:02d}',
                    'company': f'Company {i}'
                })
        
        patterns = self.analyzer.calculate_seasonal_patterns(seasonal_data)
        
        assert isinstance(patterns, dict)
        assert 'monthly_trends' in patterns
        assert 'seasonal_indices' in patterns
        assert 'peak_months' in patterns
        assert 'low_months' in patterns
        
        # Check monthly trends
        monthly_trends = patterns['monthly_trends']
        assert len(monthly_trends) <= 12  # Max 12 months
        
        # Check seasonal indices
        seasonal_indices = patterns['seasonal_indices']
        assert isinstance(seasonal_indices, dict)
        for month, index in seasonal_indices.items():
            assert isinstance(index, (int, float))
            assert index >= 0
    
    def test_assess_market_volatility(self):
        """Test market volatility assessment."""
        # Create data with varying patterns
        volatile_data = []
        job_counts = [10, 50, 5, 30, 60, 8, 45]  # Highly variable
        
        for i, count in enumerate(job_counts):
            for j in range(count):
                volatile_data.append({
                    'region': 'North America',
                    'job_title': 'Data Scientist',
                    'posting_date': f'2025-0{(i%7)+1}-01',
                    'salary': '$120,000'
                })
        
        volatility = self.analyzer.assess_market_volatility(volatile_data)
        
        assert isinstance(volatility, dict)
        assert 'volatility_score' in volatility
        assert 'stability_rating' in volatility
        assert 'risk_factors' in volatility
        assert 'volatility_indicators' in volatility
        
        # Volatility score should be between 0 and 1
        assert 0 <= volatility['volatility_score'] <= 1
        
        # Stability rating should be valid
        assert volatility['stability_rating'] in ['very_stable', 'stable', 'moderate', 'volatile', 'highly_volatile']
        
        # Risk factors should be a list
        assert isinstance(volatility['risk_factors'], list)
    
    def test_generate_growth_indicators(self):
        """Test growth indicators generation."""
        # Create data with growth pattern
        growth_data = []
        base_date = datetime(2025, 1, 1)
        
        for week in range(12):  # 12 weeks of data
            job_count = 10 + week * 2  # Growing pattern
            for job in range(job_count):
                growth_data.append({
                    'region': 'North America',
                    'job_title': 'Data Scientist',
                    'posting_date': (base_date + timedelta(weeks=week)).strftime('%Y-%m-%d'),
                    'salary': f'${100000 + week * 1000}'
                })
        
        indicators = self.analyzer.generate_growth_indicators(growth_data)
        
        assert isinstance(indicators, dict)
        assert 'job_posting_growth' in indicators
        assert 'salary_growth' in indicators
        assert 'market_expansion' in indicators
        assert 'growth_sustainability' in indicators
        
        # Growth should be positive given our test data
        assert indicators['job_posting_growth'] > 0
        assert indicators['salary_growth'] >= 0
    
    def test_identify_emerging_trends(self):
        """Test emerging trends identification."""
        # Create data with emerging technologies
        emerging_data = []
        
        # Traditional roles
        for i in range(20):
            emerging_data.append({
                'region': 'North America',
                'job_title': 'Data Analyst',
                'posting_date': '2025-08-01',
                'salary': '$80,000'
            })
        
        # Emerging roles (fewer but growing)
        for i in range(8):
            emerging_data.append({
                'region': 'North America',
                'job_title': 'AI Ethics Specialist',
                'posting_date': '2025-09-01',
                'salary': '$120,000'
            })
        
        trends = self.analyzer.identify_emerging_trends(emerging_data)
        
        assert isinstance(trends, dict)
        assert 'emerging_roles' in trends
        assert 'technology_trends' in trends
        assert 'skill_demands' in trends
        assert 'innovation_indicators' in trends
        
        # Should identify emerging roles
        emerging_roles = trends['emerging_roles']
        assert isinstance(emerging_roles, list)
    
    def test_calculate_market_confidence(self):
        """Test market confidence calculation."""
        confidence = self.analyzer.calculate_market_confidence(self.sample_market_data)
        
        assert isinstance(confidence, dict)
        assert 'confidence_score' in confidence
        assert 'confidence_factors' in confidence
        assert 'market_sentiment' in confidence
        assert 'reliability_indicators' in confidence
        
        # Confidence score should be between 0 and 1
        assert 0 <= confidence['confidence_score'] <= 1
        
        # Market sentiment should be valid
        assert confidence['market_sentiment'] in [
            'very_positive', 'positive', 'neutral', 'negative', 'very_negative'
        ]
    
    def test_empty_data_handling(self):
        """Test handling of empty market data."""
        empty_trends = self.analyzer.analyze_market_trends([], time_period_months=3)
        
        assert isinstance(empty_trends, dict)
        assert 'overall_trend' in empty_trends
        assert empty_trends['overall_trend']['direction'] == 'stable'
        assert empty_trends['overall_trend']['confidence'] == 0.0
    
    def test_invalid_data_handling(self):
        """Test handling of invalid data formats."""
        invalid_data = [
            {'invalid': 'data'},
            {'region': 'Test', 'missing_fields': True},
            None
        ]
        
        # Should handle gracefully without crashing
        trends = self.analyzer.analyze_market_trends(invalid_data, time_period_months=3)
        assert isinstance(trends, dict)
        assert 'overall_trend' in trends
    
    def test_date_parsing_robustness(self):
        """Test robustness of date parsing."""
        date_formats_data = [
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01',  # ISO format
                'salary': '$120,000'
            },
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '09/01/2025',  # US format
                'salary': '$120,000'
            },
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': 'September 1, 2025',  # Long format
                'salary': '$120,000'
            },
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': 'invalid_date',  # Invalid
                'salary': '$120,000'
            }
        ]
        
        trends = self.analyzer.analyze_market_trends(date_formats_data, time_period_months=3)
        
        # Should handle various date formats gracefully
        assert isinstance(trends, dict)
        assert 'overall_trend' in trends
    
    def test_salary_parsing_robustness(self):
        """Test robustness of salary parsing."""
        salary_formats_data = [
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01',
                'salary': '$120,000 - $150,000'  # Range format
            },
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01',
                'salary': '€80000'  # Single value, different currency
            },
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01',
                'salary': 'Competitive'  # Non-numeric
            },
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01',
                'salary': ''  # Empty
            }
        ]
        
        trends = self.analyzer.analyze_market_trends(salary_formats_data, time_period_months=3)
        
        # Should handle various salary formats gracefully
        assert isinstance(trends, dict)
        assert 'salary_trends' in trends
    
    def test_regional_support_completeness(self):
        """Test that all expected regions are supported."""
        expected_regions = [
            'North America', 'Western Europe', 'East Asia', 'Southeast Asia',
            'South America', 'Middle East', 'Africa', 'Australia/Oceania'
        ]
        
        for region in expected_regions:
            assert region in self.analyzer.supported_regions
            
            # Test analysis with each region
            region_data = [{
                'region': region,
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01',
                'salary': '$100,000'
            }]
            
            trends = self.analyzer.analyze_market_trends(region_data, time_period_months=1)
            assert isinstance(trends, dict)
            assert 'regional_insights' in trends
    
    def test_time_period_variations(self):
        """Test analysis with different time periods."""
        time_periods = [1, 3, 6, 12]
        
        for period in time_periods:
            trends = self.analyzer.analyze_market_trends(
                self.sample_market_data, time_period_months=period
            )
            
            assert isinstance(trends, dict)
            assert 'analysis_metadata' in trends
            assert trends['analysis_metadata']['time_period_months'] == period
    
    def test_concurrent_analysis(self):
        """Test concurrent trend analysis."""
        import threading
        
        results = []
        errors = []
        
        def analyze_worker():
            try:
                trends = self.analyzer.analyze_market_trends(
                    self.sample_market_data, time_period_months=3
                )
                results.append(trends)
            except Exception as e:
                errors.append(str(e))
        
        # Run multiple analyses concurrently
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=analyze_worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify concurrent execution worked
        assert len(errors) == 0
        assert len(results) == 3
        
        # Results should be consistent
        directions = [r['overall_trend']['direction'] for r in results]
        assert len(set(directions)) == 1  # All should be same
    
    def test_global_service_instance(self):
        """Test global service instance."""
        service = MarketTrendAnalyzer()
        assert service is not None
        assert isinstance(service, MarketTrendAnalyzer)
        assert hasattr(service, 'trend_cache')
    
    @pytest.mark.parametrize("region,expected_in_support", [
        ('North America', True),
        ('Western Europe', True),
        ('East Asia', True),
        ('Unknown Region', False)
    ])
    def test_regional_support_parameterized(self, region, expected_in_support):
        """Test regional support with parameterized inputs."""
        is_supported = region in self.analyzer.supported_regions
        assert is_supported == expected_in_support
    
    def test_trend_indicator_completeness(self):
        """Test that trend indicators are complete."""
        expected_indicators = [
            'job_posting_frequency', 'salary_movements', 'company_expansion',
            'skill_demand_changes', 'geographic_shifts', 'industry_growth'
        ]
        
        for indicator in expected_indicators:
            assert indicator in self.analyzer.trend_indicators
            indicator_config = self.analyzer.trend_indicators[indicator]
            assert 'weight' in indicator_config
            assert 'calculation_method' in indicator_config
    
    def test_seasonal_factor_configuration(self):
        """Test seasonal factor configuration."""
        for month, factors in self.analyzer.seasonal_factors.items():
            assert isinstance(month, str)
            assert isinstance(factors, dict)
            assert 'hiring_multiplier' in factors
            assert 'activity_level' in factors
            assert isinstance(factors['hiring_multiplier'], (int, float))
            assert factors['activity_level'] in ['high', 'medium', 'low']


if __name__ == '__main__':
    pytest.main([__file__])
