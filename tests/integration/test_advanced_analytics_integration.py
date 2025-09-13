"""
Integration tests for Advanced Analytics Services.

This module tests the integration between different analytics services
and their interaction with the Careerjet connector and geographic classifier.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import json

from tpm_job_finder_poc.enrichment.market_trend_analyzer import MarketTrendAnalyzer
from tpm_job_finder_poc.enrichment.salary_benchmarking_service import SalaryBenchmarkingService
from tpm_job_finder_poc.enrichment.cultural_fit_service import CulturalFitAssessmentService
from tpm_job_finder_poc.enrichment.geographic_llm_integration import (
    GeographicLLMIntegrationService, ContextType
)
from tpm_job_finder_poc.job_aggregator.aggregators.careerjet import CareerjetConnector
from tpm_job_finder_poc.enrichment.geographic_classifier import GeographicClassifier


class TestAdvancedAnalyticsIntegration:
    """Integration tests for advanced analytics services."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.market_analyzer = MarketTrendAnalyzer()
        self.salary_service = SalaryBenchmarkingService()
        self.cultural_service = CulturalFitAssessmentService()
        self.llm_service = GeographicLLMIntegrationService()
        self.careerjet_connector = CareerjetConnector("test_affiliate_123")
        self.geo_classifier = GeographicClassifier()
        
        # Sample job data for testing
        self.sample_jobs = [
            {
                'title': 'Senior Data Scientist',
                'company': 'Tech Corp',
                'location': 'Singapore',
                'salary': '120000-150000 SGD',
                'description': 'Leading data science initiatives',
                'posting_date': '2025-09-01',
                'url': 'https://example.com/job1'
            },
            {
                'title': 'Machine Learning Engineer',
                'company': 'AI Startup',
                'location': 'Berlin, Germany',
                'salary': '€80000-€100000',
                'description': 'Building ML models and pipelines',
                'posting_date': '2025-09-05',
                'url': 'https://example.com/job2'
            },
            {
                'title': 'Software Engineer',
                'company': 'Global Tech',
                'location': 'Tokyo, Japan',
                'salary': '¥8000000-¥12000000',
                'description': 'Full-stack development role',
                'posting_date': '2025-09-10',
                'url': 'https://example.com/job3'
            }
        ]
    
    def test_careerjet_to_geographic_classifier_integration(self):
        """Test integration between Careerjet connector and geographic classifier."""
        # Test location classification
        singapore_data = self.geo_classifier.classify_location('Singapore')
        assert singapore_data['region'] == 'Southeast Asia'
        assert singapore_data['country'] == 'Singapore'
        
        berlin_data = self.geo_classifier.classify_location('Berlin, Germany')
        assert berlin_data['region'] == 'Western Europe'
        assert berlin_data['country'] == 'Germany'
        
        tokyo_data = self.geo_classifier.classify_location('Tokyo, Japan')
        assert tokyo_data['region'] == 'East Asia'
        assert tokyo_data['country'] == 'Japan'
    
    def test_market_analyzer_with_careerjet_data(self):
        """Test market trend analyzer with Careerjet job data."""
        # Prepare market data from job samples
        market_data = []
        for job in self.sample_jobs:
            geo_info = self.geo_classifier.classify_location(job['location'])
            market_data.append({
                'region': geo_info['region'],
                'country': geo_info['country'],
                'job_title': job['title'],
                'salary': job['salary'],
                'posting_date': job['posting_date'],
                'company': job['company']
            })
        
        # Analyze trends
        trends = self.market_analyzer.analyze_market_trends(
            market_data, time_period_months=3
        )
        
        assert trends is not None
        assert 'overall_trend' in trends
        assert 'regional_insights' in trends
        assert 'growth_indicators' in trends
        
        # Verify regional analysis
        regional_trends = self.market_analyzer.analyze_regional_trends(market_data)
        assert len(regional_trends) > 0
        
        # Check that all regions from our sample are represented
        regions_found = {trend['region'] for trend in regional_trends.values()}
        expected_regions = {'Southeast Asia', 'Western Europe', 'East Asia'}
        assert regions_found.intersection(expected_regions)
    
    def test_salary_benchmarking_with_geographic_context(self):
        """Test salary benchmarking service with geographic classification."""
        # Test salary analysis for different regions
        singapore_job = self.sample_jobs[0]
        geo_info = self.geo_classifier.classify_location(singapore_job['location'])
        
        salary_analysis = self.salary_service.benchmark_salary(
            role=singapore_job['title'],
            region=geo_info['region'],
            country=geo_info['country'],
            experience_level='senior',
            salary_range=singapore_job['salary']
        )
        
        assert salary_analysis is not None
        assert salary_analysis.market_position is not None
        assert salary_analysis.regional_comparison is not None
        assert salary_analysis.confidence_score > 0
        
        # Test currency handling for different regions
        berlin_job = self.sample_jobs[1]
        berlin_geo = self.geo_classifier.classify_location(berlin_job['location'])
        
        berlin_analysis = self.salary_service.benchmark_salary(
            role=berlin_job['title'],
            region=berlin_geo['region'],
            country=berlin_geo['country'],
            experience_level='mid',
            salary_range=berlin_job['salary']
        )
        
        assert berlin_analysis is not None
        assert 'EUR' in str(berlin_analysis.salary_range) or 'Euro' in str(berlin_analysis.currency_info)
    
    def test_cultural_fit_with_job_locations(self):
        """Test cultural fit assessment with job location data."""
        # User profile for testing
        user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'individualistic',
            'pace_preference': 'fast',
            'feedback_style': 'direct',
            'work_life_balance_importance': 'high'
        }
        
        # Test cultural fit for each job location
        for job in self.sample_jobs:
            geo_info = self.geo_classifier.classify_location(job['location'])
            
            fit_score = self.cultural_service.assess_cultural_fit(
                user_profile=user_profile,
                job_region=geo_info['region']
            )
            
            assert fit_score is not None
            assert 0 <= fit_score.overall_score <= 1
            assert fit_score.cultural_adaptation_difficulty in ['low', 'medium', 'high']
            assert len(fit_score.adaptation_recommendations) > 0
            
            # Get work culture insights
            work_insights = self.cultural_service.get_work_culture_insights(
                region=geo_info['region']
            )
            
            assert work_insights is not None
            assert work_insights.region == geo_info['region']
            assert work_insights.typical_work_hours is not None
    
    @pytest.mark.asyncio
    async def test_llm_integration_with_job_context(self):
        """Test LLM integration with job and geographic context."""
        # Test career advice generation for different locations
        for job in self.sample_jobs:
            geo_info = self.geo_classifier.classify_location(job['location'])
            
            user_query = f"How can I succeed in a {job['title']} role in {job['location']}?"
            
            # Additional context from job data
            additional_context = {
                'job_role': job['title'],
                'company_type': 'technology',
                'salary_range': job['salary'],
                'user_query': user_query
            }
            
            user_profile = {
                'experience_level': 'senior',
                'skills': ['Python', 'Machine Learning', 'Data Analysis'],
                'industry': 'technology'
            }
            
            response = await self.llm_service.generate_geographic_llm_response(
                user_query=user_query,
                region=geo_info['region'],
                context_type=ContextType.CAREER,
                user_profile=user_profile,
                additional_context=additional_context
            )
            
            assert response is not None
            assert len(response.content) > 0
            assert response.confidence_score > 0
            assert len(response.actionable_recommendations) > 0
            assert geo_info['region'] in response.content or geo_info['country'] in response.content
    
    def test_end_to_end_analytics_pipeline(self):
        """Test complete analytics pipeline from job data to insights."""
        # Step 1: Process job data through geographic classifier
        processed_jobs = []
        for job in self.sample_jobs:
            geo_info = self.geo_classifier.classify_location(job['location'])
            processed_job = {**job, 'geographic_info': geo_info}
            processed_jobs.append(processed_job)
        
        # Step 2: Generate market trends
        market_data = [
            {
                'region': job['geographic_info']['region'],
                'country': job['geographic_info']['country'],
                'job_title': job['title'],
                'salary': job['salary'],
                'posting_date': job['posting_date'],
                'company': job['company']
            }
            for job in processed_jobs
        ]
        
        trends = self.market_analyzer.analyze_market_trends(
            market_data, time_period_months=3
        )
        
        # Step 3: Benchmark salaries
        salary_insights = []
        for job in processed_jobs:
            salary_analysis = self.salary_service.benchmark_salary(
                role=job['title'],
                region=job['geographic_info']['region'],
                country=job['geographic_info']['country'],
                experience_level='senior',
                salary_range=job['salary']
            )
            salary_insights.append(salary_analysis)
        
        # Step 4: Assess cultural fit
        user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'team_oriented'
        }
        
        cultural_assessments = []
        for job in processed_jobs:
            fit_score = self.cultural_service.assess_cultural_fit(
                user_profile=user_profile,
                job_region=job['geographic_info']['region']
            )
            cultural_assessments.append(fit_score)
        
        # Verify complete pipeline results
        assert trends is not None
        assert len(salary_insights) == len(self.sample_jobs)
        assert len(cultural_assessments) == len(self.sample_jobs)
        assert all(assessment.overall_score is not None for assessment in cultural_assessments)
        assert all(salary.market_position is not None for salary in salary_insights)
    
    def test_cross_service_data_consistency(self):
        """Test data consistency across different analytics services."""
        # Test region consistency
        test_location = 'Singapore'
        geo_info = self.geo_classifier.classify_location(test_location)
        
        # Verify region is consistently recognized across services
        region = geo_info['region']
        
        # Market analyzer should recognize the region
        market_regions = self.market_analyzer.supported_regions
        assert region in market_regions
        
        # Cultural service should have regional profile
        assert region in self.cultural_service.regional_profiles
        
        # Salary service should support the region
        salary_regions = self.salary_service.supported_regions
        assert region in salary_regions
        
        # LLM service should have regional configuration
        assert region in self.llm_service.regional_llm_configs
    
    def test_error_handling_across_services(self):
        """Test error handling consistency across analytics services."""
        # Test with invalid/unknown locations
        invalid_location = 'Unknown City, Nonexistent Country'
        
        # Geographic classifier should handle gracefully
        geo_result = self.geo_classifier.classify_location(invalid_location)
        assert geo_result is not None  # Should return default classification
        
        # Services should handle unknown regions gracefully
        unknown_region = 'Unknown Region'
        
        # Market analyzer
        try:
            trends = self.market_analyzer.analyze_market_trends([], time_period_months=1)
            assert trends is not None
        except Exception as e:
            assert "No data available" in str(e) or isinstance(e, ValueError)
        
        # Cultural service
        user_profile = {'communication_style': 'direct'}
        fit_score = self.cultural_service.assess_cultural_fit(
            user_profile=user_profile,
            job_region=unknown_region
        )
        assert fit_score is not None  # Should return default score
        
        # Salary service
        salary_analysis = self.salary_service.benchmark_salary(
            role='Test Role',
            region=unknown_region,
            country='Unknown',
            experience_level='mid'
        )
        assert salary_analysis is not None  # Should return default analysis
    
    def test_performance_with_large_datasets(self):
        """Test performance of analytics services with larger datasets."""
        # Create larger dataset
        large_job_dataset = []
        for i in range(100):
            job = {
                'title': f'Data Scientist {i}',
                'company': f'Company {i}',
                'location': ['Singapore', 'Berlin, Germany', 'Tokyo, Japan'][i % 3],
                'salary': f'{100000 + i * 1000}-{150000 + i * 1000} USD',
                'posting_date': f'2025-09-{(i % 30) + 1:02d}',
                'url': f'https://example.com/job{i}'
            }
            large_job_dataset.append(job)
        
        # Test market analysis performance
        market_data = []
        for job in large_job_dataset[:50]:  # Subset for testing
            geo_info = self.geo_classifier.classify_location(job['location'])
            market_data.append({
                'region': geo_info['region'],
                'country': geo_info['country'],
                'job_title': job['title'],
                'salary': job['salary'],
                'posting_date': job['posting_date'],
                'company': job['company']
            })
        
        start_time = datetime.now()
        trends = self.market_analyzer.analyze_market_trends(
            market_data, time_period_months=3
        )
        end_time = datetime.now()
        
        # Performance should be reasonable (under 5 seconds for 50 jobs)
        processing_time = (end_time - start_time).total_seconds()
        assert processing_time < 5.0
        assert trends is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_analytics_processing(self):
        """Test concurrent processing of analytics services."""
        # Test concurrent execution of different analytics services
        tasks = []
        
        # Market analysis task
        market_data = [
            {
                'region': 'North America',
                'country': 'United States',
                'job_title': 'Data Scientist',
                'salary': '120000-150000 USD',
                'posting_date': '2025-09-01',
                'company': 'Tech Corp'
            }
        ]
        
        async def analyze_market():
            return self.market_analyzer.analyze_market_trends(market_data, time_period_months=3)
        
        # Cultural assessment task
        async def assess_culture():
            user_profile = {'communication_style': 'direct'}
            return self.cultural_service.assess_cultural_fit(
                user_profile=user_profile,
                job_region='North America'
            )
        
        # LLM integration task
        async def generate_advice():
            return await self.llm_service.generate_geographic_llm_response(
                user_query="Career advice needed",
                region='North America',
                context_type=ContextType.CAREER
            )
        
        # Execute concurrently
        tasks = [analyze_market(), assess_culture(), generate_advice()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Verify all tasks completed successfully
        assert len(results) == 3
        assert all(not isinstance(result, Exception) for result in results)
        
        market_result, cultural_result, llm_result = results
        assert market_result is not None
        assert cultural_result is not None
        assert llm_result is not None


if __name__ == '__main__':
    pytest.main([__file__])
