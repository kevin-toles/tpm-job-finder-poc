"""
End-to-End tests for Advanced Analytics Pipeline.

This module tests the complete flow from job search through Careerjet
to advanced analytics insights generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from datetime import datetime
import json
import os

from tpm_job_finder_poc.enrichment.market_trend_analyzer import MarketTrendAnalyzer
from tpm_job_finder_poc.enrichment.salary_benchmarking_service import SalaryBenchmarkingService
from tpm_job_finder_poc.enrichment.cultural_fit_service import CulturalFitAssessmentService
from tpm_job_finder_poc.enrichment.geographic_llm_integration import (
    GeographicLLMIntegrationService, ContextType
)
from tpm_job_finder_poc.job_aggregator.aggregators.careerjet import CareerjetConnector
from tpm_job_finder_poc.enrichment.geographic_classifier import GeographicClassifier


class TestAdvancedAnalyticsE2E:
    """End-to-end tests for the complete advanced analytics pipeline."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.careerjet = CareerjetConnector()
        self.geo_classifier = GeographicClassifier()
        self.market_analyzer = MarketTrendAnalyzer()
        self.salary_service = SalaryBenchmarkingService()
        self.cultural_service = CulturalFitAssessmentService()
        self.llm_service = GeographicLLMIntegrationService()
        
        # Test user profile
        self.user_profile = {
            'name': 'Test User',
            'experience_level': 'senior',
            'skills': ['Python', 'Data Science', 'Machine Learning', 'SQL'],
            'industry': 'technology',
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'team_oriented',
            'career_goals': 'leadership_role',
            'work_life_balance_importance': 'high'
        }
        
        # Test search parameters
        self.search_params = {
            'keywords': 'data scientist',
            'location': 'Singapore',
            'limit': 5
        }
    
    @pytest.mark.e2e
    def test_complete_job_search_to_insights_pipeline(self):
        """Test complete pipeline from job search to comprehensive insights."""
        # Step 1: Search for jobs using Careerjet
        with patch.object(self.careerjet, 'search_jobs') as mock_search:
            # Mock Careerjet response
            mock_jobs = [
                {
                    'title': 'Senior Data Scientist',
                    'company': 'TechCorp Singapore',
                    'location': 'Singapore',
                    'salary': 'S$120,000 - S$150,000',
                    'description': 'Lead data science initiatives in fintech environment',
                    'url': 'https://example.com/job1',
                    'date_posted': '2025-09-01'
                },
                {
                    'title': 'Machine Learning Engineer',
                    'company': 'AI Startup',
                    'location': 'Singapore',
                    'salary': 'S$100,000 - S$130,000',
                    'description': 'Build and deploy ML models at scale',
                    'url': 'https://example.com/job2',
                    'date_posted': '2025-09-05'
                },
                {
                    'title': 'Data Science Manager',
                    'company': 'Global Bank',
                    'location': 'Singapore',
                    'salary': 'S$160,000 - S$200,000',
                    'description': 'Manage data science team and strategy',
                    'url': 'https://example.com/job3',
                    'date_posted': '2025-09-08'
                }
            ]
            mock_search.return_value = mock_jobs
            
            # Execute search
            jobs = self.careerjet.search_jobs(
                keywords=self.search_params['keywords'],
                location=self.search_params['location'],
                limit=self.search_params['limit']
            )
            
            # Verify jobs retrieved
            assert len(jobs) > 0
            assert all('title' in job for job in jobs)
            assert all('location' in job for job in jobs)
            
            # Step 2: Classify geographic information
            enriched_jobs = []
            for job in jobs:
                geo_info = self.geo_classifier.classify_location(job['location'])
                enriched_job = {**job, 'geographic_info': geo_info}
                enriched_jobs.append(enriched_job)
            
            # Verify geographic classification
            for job in enriched_jobs:
                assert 'geographic_info' in job
                assert 'region' in job['geographic_info']
                assert 'country' in job['geographic_info']
                assert job['geographic_info']['region'] == 'Southeast Asia'
                assert job['geographic_info']['country'] == 'Singapore'
            
            # Step 3: Perform market trend analysis
            market_data = [
                {
                    'region': job['geographic_info']['region'],
                    'country': job['geographic_info']['country'],
                    'job_title': job['title'],
                    'salary': job['salary'],
                    'posting_date': job['date_posted'],
                    'company': job['company']
                }
                for job in enriched_jobs
            ]
            
            market_trends = self.market_analyzer.analyze_market_trends(
                market_data, time_period_months=3
            )
            
            # Verify market analysis
            assert market_trends is not None
            assert 'overall_trend' in market_trends
            assert 'regional_insights' in market_trends
            assert 'salary_trends' in market_trends
            assert 'job_demand_indicators' in market_trends
            
            # Step 4: Benchmark salaries for each job
            salary_benchmarks = []
            for job in enriched_jobs:
                benchmark = self.salary_service.benchmark_salary(
                    role=job['title'],
                    region=job['geographic_info']['region'],
                    country=job['geographic_info']['country'],
                    experience_level=self.user_profile['experience_level'],
                    salary_range=job['salary']
                )
                salary_benchmarks.append(benchmark)
            
            # Verify salary benchmarking
            assert len(salary_benchmarks) == len(enriched_jobs)
            for benchmark in salary_benchmarks:
                assert benchmark.market_position is not None
                assert benchmark.confidence_score > 0
                assert benchmark.regional_comparison is not None
            
            # Step 5: Assess cultural fit
            cultural_fit = self.cultural_service.assess_cultural_fit(
                user_profile=self.user_profile,
                job_region=enriched_jobs[0]['geographic_info']['region']
            )
            
            # Verify cultural assessment
            assert cultural_fit is not None
            assert 0 <= cultural_fit.overall_score <= 1
            assert cultural_fit.cultural_adaptation_difficulty in ['low', 'medium', 'high']
            assert len(cultural_fit.adaptation_recommendations) > 0
            
            # Step 6: Generate adaptation plan
            adaptation_plan = self.cultural_service.generate_cultural_adaptation_plan(
                user_profile=self.user_profile,
                target_region=enriched_jobs[0]['geographic_info']['region'],
                timeline_months=6
            )
            
            # Verify adaptation plan
            assert adaptation_plan is not None
            assert 'overall_assessment' in adaptation_plan
            assert 'preparation_phase' in adaptation_plan
            assert 'success_metrics' in adaptation_plan
            
            # Step 7: Generate comprehensive insights report
            insights_report = self._generate_comprehensive_report(
                jobs=enriched_jobs,
                market_trends=market_trends,
                salary_benchmarks=salary_benchmarks,
                cultural_fit=cultural_fit,
                adaptation_plan=adaptation_plan
            )
            
            # Verify comprehensive report
            assert insights_report is not None
            assert 'job_opportunities' in insights_report
            assert 'market_intelligence' in insights_report
            assert 'salary_insights' in insights_report
            assert 'cultural_guidance' in insights_report
            assert 'recommendations' in insights_report
            
            # Verify report completeness
            assert len(insights_report['job_opportunities']) > 0
            assert insights_report['market_intelligence']['trend_direction'] is not None
            assert insights_report['cultural_guidance']['adaptation_difficulty'] is not None
    
    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_ai_powered_career_guidance_e2e(self):
        """Test end-to-end AI-powered career guidance generation."""
        # Simulate job search results
        target_region = 'Southeast Asia'
        target_country = 'Singapore'
        
        # Step 1: Generate comprehensive career guidance
        career_query = f"I'm a {self.user_profile['experience_level']} professional with skills in {', '.join(self.user_profile['skills'])}. How can I succeed in the {target_country} job market?"
        
        # Additional context from our analytics
        additional_context = {
            'target_region': target_region,
            'target_country': target_country,
            'user_experience': self.user_profile['experience_level'],
            'skills': self.user_profile['skills'],
            'industry': self.user_profile['industry'],
            'user_query': career_query
        }
        
        # Generate AI-powered response
        ai_guidance = await self.llm_service.generate_geographic_llm_response(
            user_query=career_query,
            region=target_region,
            context_type=ContextType.CAREER,
            user_profile=self.user_profile,
            additional_context=additional_context
        )
        
        # Verify AI guidance
        assert ai_guidance is not None
        assert len(ai_guidance.content) > 0
        assert ai_guidance.confidence_score > 0
        assert len(ai_guidance.actionable_recommendations) > 0
        assert len(ai_guidance.cultural_adaptations) >= 0
        assert len(ai_guidance.follow_up_suggestions) > 0
        
        # Step 2: Generate specific interview preparation
        interview_query = f"How should I prepare for data science interviews in {target_country}?"
        
        interview_guidance = await self.llm_service.generate_geographic_llm_response(
            user_query=interview_query,
            region=target_region,
            context_type=ContextType.CULTURAL,
            user_profile=self.user_profile,
            additional_context={'interview_type': 'technical', 'role_level': 'senior'}
        )
        
        # Verify interview guidance
        assert interview_guidance is not None
        assert 'interview' in interview_guidance.content.lower() or 'preparation' in interview_guidance.content.lower()
        
        # Step 3: Generate salary negotiation advice
        salary_query = f"How should I approach salary negotiations for a senior data scientist role in {target_country}?"
        
        salary_guidance = await self.llm_service.generate_geographic_llm_response(
            user_query=salary_query,
            region=target_region,
            context_type=ContextType.ECONOMIC,
            user_profile=self.user_profile,
            additional_context={'negotiation_context': 'job_offer', 'role': 'Senior Data Scientist'}
        )
        
        # Verify salary guidance
        assert salary_guidance is not None
        assert 'salary' in salary_guidance.content.lower() or 'negotiation' in salary_guidance.content.lower()
        
        # Step 4: Compile comprehensive AI guidance report
        ai_report = {
            'career_guidance': ai_guidance,
            'interview_preparation': interview_guidance,
            'salary_negotiation': salary_guidance,
            'overall_confidence': (ai_guidance.confidence_score + 
                                 interview_guidance.confidence_score + 
                                 salary_guidance.confidence_score) / 3
        }
        
        # Verify AI report
        assert ai_report['overall_confidence'] > 0.5
        assert len(ai_report['career_guidance'].actionable_recommendations) > 0
    
    @pytest.mark.e2e
    def test_multi_region_comparison_e2e(self):
        """Test end-to-end multi-region job market comparison."""
        # Test regions for comparison
        regions_to_compare = ['North America', 'Western Europe', 'Southeast Asia', 'East Asia']
        
        # Step 1: Generate mock job data for each region
        regional_job_data = {}
        for region in regions_to_compare:
            # Get sample country for region
            sample_country = {
                'North America': 'United States',
                'Western Europe': 'Germany',
                'Southeast Asia': 'Singapore',
                'East Asia': 'Japan'
            }[region]
            
            # Create sample jobs
            regional_jobs = [
                {
                    'title': 'Senior Data Scientist',
                    'company': f'TechCorp {sample_country}',
                    'location': sample_country,
                    'salary': self._get_sample_salary(region),
                    'description': 'Data science role with ML focus',
                    'date_posted': '2025-09-01'
                }
            ]
            regional_job_data[region] = regional_jobs
        
        # Step 2: Analyze market trends for each region
        regional_trends = {}
        for region, jobs in regional_job_data.items():
            market_data = [
                {
                    'region': region,
                    'country': jobs[0]['location'],
                    'job_title': jobs[0]['title'],
                    'salary': jobs[0]['salary'],
                    'posting_date': jobs[0]['date_posted'],
                    'company': jobs[0]['company']
                }
            ]
            
            trends = self.market_analyzer.analyze_market_trends(
                market_data, time_period_months=3
            )
            regional_trends[region] = trends
        
        # Step 3: Compare salary benchmarks across regions
        regional_salaries = {}
        for region, jobs in regional_job_data.items():
            country = jobs[0]['location']
            benchmark = self.salary_service.benchmark_salary(
                role='Senior Data Scientist',
                region=region,
                country=country,
                experience_level='senior',
                salary_range=jobs[0]['salary']
            )
            regional_salaries[region] = benchmark
        
        # Step 4: Compare cultural fit across regions
        cultural_comparison = self.cultural_service.compare_regional_cultures(regions_to_compare)
        
        # Step 5: Generate comprehensive regional comparison
        regional_comparison = {
            'regions_analyzed': regions_to_compare,
            'market_trends': regional_trends,
            'salary_benchmarks': regional_salaries,
            'cultural_comparison': cultural_comparison,
            'recommendations': self._generate_regional_recommendations(
                regional_trends, regional_salaries, cultural_comparison
            )
        }
        
        # Verify regional comparison
        assert len(regional_comparison['regions_analyzed']) == len(regions_to_compare)
        assert len(regional_comparison['market_trends']) == len(regions_to_compare)
        assert len(regional_comparison['salary_benchmarks']) == len(regions_to_compare)
        assert 'cultural_dimensions' in regional_comparison['cultural_comparison']
        assert len(regional_comparison['recommendations']) > 0
        
        # Verify data quality across regions
        for region in regions_to_compare:
            assert region in regional_comparison['market_trends']
            assert region in regional_comparison['salary_benchmarks']
            assert regional_comparison['market_trends'][region] is not None
            assert regional_comparison['salary_benchmarks'][region] is not None
    
    @pytest.mark.e2e
    def test_performance_under_load_e2e(self):
        """Test system performance under realistic load conditions."""
        # Simulate realistic load
        num_concurrent_users = 10
        jobs_per_search = 20
        
        # Create test scenarios
        test_scenarios = [
            {'keywords': 'data scientist', 'location': 'Singapore'},
            {'keywords': 'software engineer', 'location': 'Berlin'},
            {'keywords': 'product manager', 'location': 'Tokyo'},
            {'keywords': 'machine learning engineer', 'location': 'New York'},
            {'keywords': 'data analyst', 'location': 'London'}
        ]
        
        def process_search_scenario(scenario):
            """Process a single search scenario with full analytics."""
            start_time = datetime.now()
            
            # Mock job search
            mock_jobs = [
                {
                    'title': f"{scenario['keywords'].title()} {i}",
                    'company': f'Company {i}',
                    'location': scenario['location'],
                    'salary': self._get_sample_salary_for_location(scenario['location']),
                    'description': f'Role description {i}',
                    'date_posted': '2025-09-01'
                }
                for i in range(jobs_per_search)
            ]
            
            # Process through analytics pipeline
            enriched_jobs = []
            for job in mock_jobs:
                geo_info = self.geo_classifier.classify_location(job['location'])
                enriched_job = {**job, 'geographic_info': geo_info}
                enriched_jobs.append(enriched_job)
            
            # Market analysis
            market_data = [
                {
                    'region': job['geographic_info']['region'],
                    'country': job['geographic_info']['country'],
                    'job_title': job['title'],
                    'salary': job['salary'],
                    'posting_date': job['date_posted'],
                    'company': job['company']
                }
                for job in enriched_jobs
            ]
            
            trends = self.market_analyzer.analyze_market_trends(
                market_data, time_period_months=1
            )
            
            # Cultural assessment
            cultural_fit = self.cultural_service.assess_cultural_fit(
                user_profile=self.user_profile,
                job_region=enriched_jobs[0]['geographic_info']['region']
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            return {
                'scenario': scenario,
                'jobs_processed': len(enriched_jobs),
                'processing_time': processing_time,
                'trends_generated': trends is not None,
                'cultural_assessment': cultural_fit is not None
            }
        
        # Process scenarios
        results = []
        for i in range(num_concurrent_users):
            scenario = test_scenarios[i % len(test_scenarios)]
            result = process_search_scenario(scenario)
            results.append(result)
        
        # Verify performance results
        assert len(results) == num_concurrent_users
        
        # Check processing times (should be under reasonable thresholds)
        avg_processing_time = sum(r['processing_time'] for r in results) / len(results)
        max_processing_time = max(r['processing_time'] for r in results)
        
        assert avg_processing_time < 3.0  # Average under 3 seconds
        assert max_processing_time < 5.0  # Max under 5 seconds
        
        # Verify all processing completed successfully
        assert all(r['trends_generated'] for r in results)
        assert all(r['cultural_assessment'] for r in results)
        assert all(r['jobs_processed'] == jobs_per_search for r in results)
    
    def _generate_comprehensive_report(self, jobs, market_trends, salary_benchmarks, 
                                     cultural_fit, adaptation_plan):
        """Generate comprehensive insights report."""
        return {
            'job_opportunities': [
                {
                    'title': job['title'],
                    'company': job['company'],
                    'location': job['location'],
                    'salary': job['salary'],
                    'cultural_fit_score': cultural_fit.overall_score,
                    'salary_competitiveness': salary_benchmarks[i].market_position
                }
                for i, job in enumerate(jobs)
            ],
            'market_intelligence': {
                'trend_direction': market_trends.get('overall_trend', {}).get('direction', 'stable'),
                'growth_rate': market_trends.get('growth_indicators', {}).get('job_posting_growth', 0),
                'salary_trend': market_trends.get('salary_trends', {}).get('direction', 'stable')
            },
            'salary_insights': {
                'market_position': salary_benchmarks[0].market_position if salary_benchmarks else 'unknown',
                'salary_range': salary_benchmarks[0].salary_range if salary_benchmarks else 'unknown',
                'regional_comparison': salary_benchmarks[0].regional_comparison if salary_benchmarks else {}
            },
            'cultural_guidance': {
                'adaptation_difficulty': cultural_fit.cultural_adaptation_difficulty,
                'key_strengths': cultural_fit.key_strengths,
                'challenges': cultural_fit.potential_challenges,
                'recommendations': cultural_fit.adaptation_recommendations
            },
            'recommendations': [
                'Focus on roles with high cultural fit scores',
                'Consider salary negotiation strategies based on market position',
                'Prepare for cultural adaptation with recommended timeline',
                'Leverage identified strengths in the target market'
            ]
        }
    
    def _get_sample_salary(self, region):
        """Get sample salary for region."""
        salary_ranges = {
            'North America': '$120,000 - $150,000',
            'Western Europe': '€90,000 - €110,000',
            'Southeast Asia': 'S$120,000 - S$150,000',
            'East Asia': '¥8,000,000 - ¥12,000,000'
        }
        return salary_ranges.get(region, '$100,000 - $130,000')
    
    def _get_sample_salary_for_location(self, location):
        """Get sample salary for specific location."""
        location_salaries = {
            'Singapore': 'S$120,000 - S$150,000',
            'Berlin': '€80,000 - €100,000',
            'Tokyo': '¥8,000,000 - ¥12,000,000',
            'New York': '$130,000 - $160,000',
            'London': '£80,000 - £100,000'
        }
        return location_salaries.get(location, '$100,000 - $130,000')
    
    def _generate_regional_recommendations(self, trends, salaries, cultural):
        """Generate recommendations based on regional analysis."""
        recommendations = []
        
        # Analyze trends across regions
        growth_regions = []
        for region, trend_data in trends.items():
            if trend_data and trend_data.get('growth_indicators', {}).get('job_posting_growth', 0) > 5:
                growth_regions.append(region)
        
        if growth_regions:
            recommendations.append(f"High growth opportunities in: {', '.join(growth_regions)}")
        
        # Salary recommendations
        high_salary_regions = []
        for region, salary_data in salaries.items():
            if salary_data and salary_data.market_position in ['above_market', 'top_tier']:
                high_salary_regions.append(region)
        
        if high_salary_regions:
            recommendations.append(f"Competitive salaries in: {', '.join(high_salary_regions)}")
        
        # Cultural recommendations
        if 'recommendations' in cultural:
            recommendations.extend(cultural['recommendations'][:2])
        
        return recommendations


if __name__ == '__main__':
    pytest.main([__file__])
