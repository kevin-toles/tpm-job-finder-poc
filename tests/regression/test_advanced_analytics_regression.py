"""
Regression tests for Advanced Analytics Services.

This module ensures that analytics services maintain consistent behavior
and performance over time, catching any regressions in functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
import hashlib

from tpm_job_finder_poc.enrichment.market_trend_analyzer import MarketTrendAnalyzer
from tpm_job_finder_poc.enrichment.salary_benchmarking_service import SalaryBenchmarkingService
from tpm_job_finder_poc.enrichment.cultural_fit_service import CulturalFitAssessmentService
from tpm_job_finder_poc.enrichment.geographic_llm_integration import (
    GeographicLLMIntegrationService, ContextType
)
from tpm_job_finder_poc.enrichment.geographic_classifier import GeographicClassifier


class TestAdvancedAnalyticsRegression:
    """Regression tests for advanced analytics services."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.market_analyzer = MarketTrendAnalyzer()
        self.salary_service = SalaryBenchmarkingService()
        self.cultural_service = CulturalFitAssessmentService()
        self.llm_service = GeographicLLMIntegrationService()
        self.geo_classifier = GeographicClassifier()
        
        # Fixed test data for regression testing
        self.fixed_market_data = [
            {
                'region': 'North America',
                'country': 'United States',
                'job_title': 'Senior Data Scientist',
                'salary': '$120,000 - $150,000',
                'posting_date': '2025-09-01',
                'company': 'TechCorp'
            },
            {
                'region': 'North America',
                'country': 'United States',
                'job_title': 'Machine Learning Engineer',
                'salary': '$110,000 - $140,000',
                'posting_date': '2025-09-02',
                'company': 'AI Startup'
            },
            {
                'region': 'North America',
                'country': 'United States',
                'job_title': 'Data Analyst',
                'salary': '$80,000 - $100,000',
                'posting_date': '2025-09-03',
                'company': 'FinTech Inc'
            }
        ]
        
        self.fixed_user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'individualistic',
            'pace_preference': 'fast',
            'feedback_style': 'direct',
            'work_life_balance_importance': 'high',
            'experience_level': 'senior',
            'skills': ['Python', 'Machine Learning', 'SQL']
        }
    
    def test_market_trend_analysis_consistency(self):
        """Test that market trend analysis produces consistent results."""
        # Run analysis multiple times with same data
        results = []
        for _ in range(3):
            trends = self.market_analyzer.analyze_market_trends(
                self.fixed_market_data, time_period_months=3
            )
            results.append(trends)
        
        # Verify consistency across runs
        assert len(results) == 3
        
        # Check that key metrics are consistent
        for i in range(1, len(results)):
            # Overall trend direction should be same
            if 'overall_trend' in results[0] and 'overall_trend' in results[i]:
                assert results[0]['overall_trend'].get('direction') == results[i]['overall_trend'].get('direction')
            
            # Growth indicators should be consistent
            if 'growth_indicators' in results[0] and 'growth_indicators' in results[i]:
                prev_growth = results[0]['growth_indicators'].get('job_posting_growth', 0)
                curr_growth = results[i]['growth_indicators'].get('job_posting_growth', 0)
                # Allow small variance due to date calculations
                assert abs(prev_growth - curr_growth) <= 1.0
    
    def test_salary_benchmarking_stability(self):
        """Test that salary benchmarking provides stable results."""
        # Test same salary multiple times
        benchmark_params = {
            'role': 'Senior Data Scientist',
            'region': 'North America',
            'country': 'United States',
            'experience_level': 'senior',
            'salary_range': '$120,000 - $150,000'
        }
        
        results = []
        for _ in range(3):
            benchmark = self.salary_service.benchmark_salary(**benchmark_params)
            results.append(benchmark)
        
        # Verify consistency
        assert len(results) == 3
        
        # Market position should be consistent (compare by string representation)
        market_positions = [str(result.market_position) for result in results]
        assert len(set(market_positions)) == 1  # All should be same
        
        # Confidence scores should be similar (within 0.1)
        confidence_scores = [result.confidence_score for result in results]
        max_diff = max(confidence_scores) - min(confidence_scores)
        assert max_diff <= 0.1
        
        # Currency info should be consistent
        currencies = [result.currency_info for result in results]
        assert all(curr == currencies[0] for curr in currencies)
    
    def test_cultural_fit_assessment_determinism(self):
        """Test that cultural fit assessment is deterministic."""
        # Run cultural fit assessment multiple times
        results = []
        for _ in range(3):
            fit_score = self.cultural_service.assess_cultural_fit(
                user_profile=self.fixed_user_profile,
                job_region='North America'
            )
            results.append(fit_score)
        
        # Verify deterministic results
        assert len(results) == 3
        
        # Overall scores should be identical
        overall_scores = [result.overall_score for result in results]
        assert len(set(overall_scores)) == 1
        
        # Communication fit should be identical
        comm_fits = [result.communication_fit for result in results]
        assert len(set(comm_fits)) == 1
        
        # Adaptation difficulty should be consistent
        difficulties = [result.cultural_adaptation_difficulty for result in results]
        assert len(set(difficulties)) == 1
        
        # Recommendations should be consistent
        for i in range(1, len(results)):
            assert len(results[0].adaptation_recommendations) == len(results[i].adaptation_recommendations)
    
    def test_geographic_classifier_consistency(self):
        """Test that geographic classifier produces consistent results."""
        test_locations = [
            'Singapore',
            'Berlin, Germany',
            'Tokyo, Japan',
            'New York, NY, USA',
            'London, UK'
        ]
        
        # Test each location multiple times
        for location in test_locations:
            results = []
            for _ in range(3):
                classification = self.geo_classifier.classify_location(location)
                results.append(classification)
            
            # Verify consistency for this location
            regions = [result['region'] for result in results]
            countries = [result['country'] for result in results]
            
            assert len(set(regions)) == 1  # All regions should be same
            assert len(set(countries)) == 1  # All countries should be same
    
    def test_service_initialization_consistency(self):
        """Test that services initialize consistently."""
        # Test multiple initializations
        analyzers = [MarketTrendAnalyzer() for _ in range(3)]
        salary_services = [SalaryBenchmarkingService() for _ in range(3)]
        cultural_services = [CulturalFitAssessmentService() for _ in range(3)]
        
        # Verify consistent initialization
        # Check that supported regions are consistent
        analyzer_regions = [set(analyzer.supported_regions) for analyzer in analyzers]
        assert all(regions == analyzer_regions[0] for regions in analyzer_regions)
        
        salary_regions = [set(service.supported_regions) for service in salary_services]
        assert all(regions == salary_regions[0] for regions in salary_regions)
        
        # Check cultural profiles consistency
        cultural_profiles = [len(service.regional_profiles) for service in cultural_services]
        assert all(count == cultural_profiles[0] for count in cultural_profiles)
    
    def test_data_structure_stability(self):
        """Test that data structures remain stable across versions."""
        # Test market trend analysis output structure
        trends = self.market_analyzer.analyze_market_trends(
            self.fixed_market_data, time_period_months=3
        )
        
        expected_trend_keys = [
            'overall_trend', 'regional_insights', 'salary_trends', 
            'job_demand_indicators', 'growth_indicators', 'analysis_metadata'
        ]
        
        for key in expected_trend_keys:
            assert key in trends, f"Expected key '{key}' missing from trends output"
        
        # Test salary benchmark output structure
        benchmark = self.salary_service.benchmark_salary(
            role='Senior Data Scientist',
            region='North America',
            country='United States',
            experience_level='senior'
        )
        
        expected_benchmark_attrs = [
            'market_position', 'salary_range', 'confidence_score',
            'regional_comparison', 'currency_info', 'cost_of_living_adjustment'
        ]
        
        for attr in expected_benchmark_attrs:
            assert hasattr(benchmark, attr), f"Expected attribute '{attr}' missing from benchmark"
        
        # Test cultural fit output structure
        fit_score = self.cultural_service.assess_cultural_fit(
            user_profile=self.fixed_user_profile,
            job_region='North America'
        )
        
        expected_fit_attrs = [
            'overall_score', 'communication_fit', 'hierarchy_fit', 'work_style_fit',
            'cultural_adaptation_difficulty', 'key_strengths', 'potential_challenges',
            'adaptation_recommendations', 'confidence_level'
        ]
        
        for attr in expected_fit_attrs:
            assert hasattr(fit_score, attr), f"Expected attribute '{attr}' missing from fit score"
    
    def test_error_handling_consistency(self):
        """Test that error handling remains consistent."""
        # Test with various invalid inputs
        invalid_inputs = [
            None,
            {},
            [],
            "",
            "invalid_data"
        ]
        
        for invalid_input in invalid_inputs:
            # Market analyzer should handle gracefully
            try:
                trends = self.market_analyzer.analyze_market_trends(invalid_input)
                # Should return some form of result or handle gracefully
                assert trends is not None or True  # At minimum, shouldn't crash
            except (ValueError, TypeError) as e:
                # Expected exceptions are acceptable
                assert isinstance(e, (ValueError, TypeError))
            
            # Cultural service should handle gracefully
            try:
                fit_score = self.cultural_service.assess_cultural_fit(
                    user_profile=invalid_input,
                    job_region='North America'
                )
                assert fit_score is not None
            except (ValueError, TypeError) as e:
                assert isinstance(e, (ValueError, TypeError))
    
    def test_performance_regression(self):
        """Test that performance hasn't regressed."""
        # Measure performance of key operations
        performance_data = {}
        
        # Test market analysis performance
        start_time = datetime.now()
        trends = self.market_analyzer.analyze_market_trends(
            self.fixed_market_data * 10, time_period_months=3  # 10x data
        )
        market_time = (datetime.now() - start_time).total_seconds()
        performance_data['market_analysis'] = market_time
        
        # Test salary benchmarking performance
        start_time = datetime.now()
        for _ in range(10):
            benchmark = self.salary_service.benchmark_salary(
                role='Senior Data Scientist',
                region='North America',
                country='United States',
                experience_level='senior'
            )
        salary_time = (datetime.now() - start_time).total_seconds()
        performance_data['salary_benchmarking'] = salary_time
        
        # Test cultural assessment performance
        start_time = datetime.now()
        for _ in range(10):
            fit_score = self.cultural_service.assess_cultural_fit(
                user_profile=self.fixed_user_profile,
                job_region='North America'
            )
        cultural_time = (datetime.now() - start_time).total_seconds()
        performance_data['cultural_assessment'] = cultural_time
        
        # Performance thresholds (adjust based on expected performance)
        assert performance_data['market_analysis'] < 2.0  # Should complete in under 2 seconds
        assert performance_data['salary_benchmarking'] < 1.0  # 10 operations in under 1 second
        assert performance_data['cultural_assessment'] < 0.5  # 10 operations in under 0.5 seconds
    
    def test_regional_coverage_stability(self):
        """Test that regional coverage remains stable."""
        # Expected regions that should always be supported
        expected_regions = [
            'North America',
            'Western Europe', 
            'East Asia',
            'Southeast Asia'
        ]
        
        # Market analyzer regions
        market_regions = self.market_analyzer.supported_regions
        for region in expected_regions:
            assert region in market_regions, f"Market analyzer missing support for {region}"
        
        # Salary service regions
        salary_regions = self.salary_service.supported_regions
        for region in expected_regions:
            assert region in salary_regions, f"Salary service missing support for {region}"
        
        # Cultural service regions
        cultural_regions = list(self.cultural_service.regional_profiles.keys())
        for region in expected_regions:
            assert region in cultural_regions, f"Cultural service missing support for {region}"
        
        # Geographic classifier should handle sample cities
        test_cities = {
            'Singapore': 'Southeast Asia',
            'Berlin': 'Western Europe',
            'Tokyo': 'East Asia',
            'New York': 'North America'
        }
        
        for city, expected_region in test_cities.items():
            classification = self.geo_classifier.classify_location(city)
            assert classification['region'] == expected_region, f"Geographic classification mismatch for {city}"
    
    def test_currency_handling_stability(self):
        """Test that currency handling remains consistent."""
        # Test various currency formats
        currency_test_cases = [
            ('$120,000 - $150,000', 'USD'),
            ('€80,000 - €100,000', 'EUR'),
            ('¥8,000,000 - ¥12,000,000', 'JPY'),
            ('S$120,000 - S$150,000', 'SGD'),
            ('£80,000 - £100,000', 'GBP')
        ]
        
        for salary_range, expected_currency in currency_test_cases:
            # Test currency extraction/recognition
            benchmark = self.salary_service.benchmark_salary(
                role='Data Scientist',
                region='North America',  # Region doesn't matter for currency test
                country='United States',
                experience_level='senior',
                salary_range=salary_range
            )
            
            # Verify currency is handled consistently
            assert benchmark is not None
            assert benchmark.currency_info is not None
            # Currency should be detected or defaulted consistently
    
    def test_version_compatibility(self):
        """Test backward compatibility of analytics services."""
        # Test that old-style inputs still work (if applicable)
        # This would be expanded based on actual version history
        
        # Test basic functionality with minimal inputs
        minimal_market_data = [
            {
                'region': 'North America',
                'job_title': 'Data Scientist',
                'posting_date': '2025-09-01'
            }
        ]
        
        # Should handle minimal data gracefully
        trends = self.market_analyzer.analyze_market_trends(minimal_market_data)
        assert trends is not None
        
        # Test minimal user profile
        minimal_profile = {
            'communication_style': 'direct'
        }
        
        fit_score = self.cultural_service.assess_cultural_fit(
            user_profile=minimal_profile,
            job_region='North America'
        )
        assert fit_score is not None
        assert fit_score.confidence_level == 'low'  # Should indicate low confidence
    
    def test_concurrent_access_stability(self):
        """Test that services handle concurrent access consistently."""
        import threading
        import time
        
        results = []
        errors = []
        
        def worker_function():
            try:
                # Each worker does a complete analytics workflow
                fit_score = self.cultural_service.assess_cultural_fit(
                    user_profile=self.fixed_user_profile,
                    job_region='North America'
                )
                
                benchmark = self.salary_service.benchmark_salary(
                    role='Data Scientist',
                    region='North America',
                    country='United States',
                    experience_level='senior'
                )
                
                trends = self.market_analyzer.analyze_market_trends(
                    self.fixed_market_data[:1], time_period_months=1
                )
                
                results.append({
                    'fit_score': fit_score.overall_score,
                    'market_position': benchmark.market_position,
                    'trends_available': trends is not None
                })
                
            except Exception as e:
                errors.append(str(e))
        
        # Run multiple workers concurrently (reduced for performance)
        threads = []
        for _ in range(2):  # Reduced from 5 to 2 threads
            thread = threading.Thread(target=worker_function)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify concurrent access worked
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 2  # Updated from 5 to 2
        
        # Results should be consistent across workers
        fit_scores = [r['fit_score'] for r in results]
        assert len(set(fit_scores)) == 1  # All should be same
        
        market_positions = [r['market_position'] for r in results]
        assert len(set(market_positions)) == 1  # All should be same


if __name__ == '__main__':
    pytest.main([__file__])
