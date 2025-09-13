"""
Tests for Geographic LLM Integration Service.

This module provides comprehensive tests for the geographic LLM integration
functionality including context building, prompt adaptation, and enhanced
response generation.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import json

from tpm_job_finder_poc.enrichment.geographic_llm_integration import (
    GeographicLLMIntegrationService,
    GeographicContext,
    LLMPromptTemplate,
    EnhancedLLMResponse,
    ContextType,
    geographic_llm_service
)


class TestGeographicLLMIntegrationService:
    """Test suite for Geographic LLM Integration Service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = GeographicLLMIntegrationService()
        
        # Sample user profile for testing
        self.sample_user_profile = {
            'name': 'Test User',
            'experience_level': 'senior',
            'skills': ['Python', 'Data Science', 'Machine Learning'],
            'industry': 'technology',
            'communication_style': 'direct',
            'career_goals': 'leadership_role'
        }
        
        # Sample additional context
        self.sample_additional_context = {
            'job_role': 'Senior Data Scientist',
            'company_size': 'large',
            'industry_focus': 'fintech'
        }
    
    def test_service_initialization(self):
        """Test service initializes correctly."""
        assert self.service is not None
        assert len(self.service.prompt_templates) > 0
        assert len(self.service.cultural_adaptations) > 0
        assert len(self.service.regional_expertise_areas) > 0
        assert len(self.service.cultural_frameworks) > 0
        assert len(self.service.regional_llm_configs) > 0
    
    def test_cultural_frameworks_structure(self):
        """Test cultural frameworks are properly structured."""
        for framework_name, framework in self.service.cultural_frameworks.items():
            assert 'dimensions' in framework
            assert 'scale' in framework
            assert isinstance(framework['dimensions'], list)
            assert isinstance(framework['scale'], tuple)
            assert len(framework['scale']) == 2
    
    def test_regional_llm_configs_completeness(self):
        """Test regional LLM configurations are complete."""
        required_keys = ['communication_style', 'decision_factors', 'cultural_sensitivity', 'business_focus']
        
        for region, config in self.service.regional_llm_configs.items():
            for key in required_keys:
                assert key in config
                assert config[key] is not None
    
    def test_prompt_templates_structure(self):
        """Test prompt templates are properly structured."""
        for template_id, template in self.service.prompt_templates.items():
            assert isinstance(template, LLMPromptTemplate)
            assert template.template_id == template_id
            assert template.category is not None
            assert template.base_prompt is not None
            assert isinstance(template.cultural_modifiers, dict)
            assert isinstance(template.region_specific_context, dict)
            assert isinstance(template.examples, list)
    
    @pytest.mark.asyncio
    async def test_build_geographic_context(self):
        """Test geographic context building."""
        context = await self.service._build_geographic_context('North America', ContextType.CULTURAL)
        
        assert isinstance(context, GeographicContext)
        assert context.region == 'North America'
        assert context.country is not None
        assert isinstance(context.cultural_dimensions, dict)
        assert isinstance(context.economic_indicators, dict)
        assert isinstance(context.legal_framework, dict)
        assert isinstance(context.industry_landscape, dict)
        assert isinstance(context.language_context, dict)
        assert context.time_zone is not None
        assert context.currency is not None
    
    @pytest.mark.asyncio
    async def test_build_geographic_context_caching(self):
        """Test geographic context caching."""
        # First call
        context1 = await self.service._build_geographic_context('Western Europe', ContextType.ECONOMIC)
        
        # Second call should use cache
        context2 = await self.service._build_geographic_context('Western Europe', ContextType.ECONOMIC)
        
        assert context1 is context2  # Same object from cache
    
    def test_select_prompt_template(self):
        """Test prompt template selection."""
        # Salary-related query
        template = self.service._select_prompt_template(
            "How should I negotiate my salary in Japan?", 
            ContextType.CULTURAL
        )
        assert template.template_id == 'salary_negotiation'
        
        # Interview-related query
        template = self.service._select_prompt_template(
            "How do I prepare for interviews in Germany?", 
            ContextType.CULTURAL
        )
        assert template.template_id == 'interview_prep'
        
        # General career query
        template = self.service._select_prompt_template(
            "What are the best career opportunities in Singapore?", 
            ContextType.CAREER
        )
        assert template.template_id == 'career_advice'
    
    @pytest.mark.asyncio
    async def test_adapt_prompt_for_culture(self):
        """Test prompt adaptation for cultural context."""
        # Build context
        geo_context = await self.service._build_geographic_context('East Asia', ContextType.CULTURAL)
        
        # Get template
        template = self.service.prompt_templates['career_advice']
        
        # Adapt prompt
        adapted_prompt = self.service._adapt_prompt_for_culture(
            template, geo_context, self.sample_user_profile, self.sample_additional_context
        )
        
        assert isinstance(adapted_prompt, str)
        assert 'East Asia' in adapted_prompt
        assert 'cultural_context' in adapted_prompt or 'East Asia' in adapted_prompt
        assert len(adapted_prompt) > len(template.base_prompt)
    
    @pytest.mark.asyncio
    async def test_generate_base_llm_response(self):
        """Test base LLM response generation."""
        prompt = "Test prompt for career advice"
        response = await self.service._generate_base_llm_response(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert 'Cultural Considerations' in response or 'recommendations' in response.lower()
    
    @pytest.mark.asyncio
    async def test_enhance_with_geographic_intelligence(self):
        """Test enhancement with geographic intelligence."""
        base_response = "Sample career advice response"
        geo_context = await self.service._build_geographic_context('North America', ContextType.CAREER)
        
        enhanced_response = await self.service._enhance_with_geographic_intelligence(
            base_response, geo_context, 'North America', 'Career advice query'
        )
        
        assert isinstance(enhanced_response, EnhancedLLMResponse)
        assert enhanced_response.content == base_response
        assert isinstance(enhanced_response.confidence_score, float)
        assert 0 <= enhanced_response.confidence_score <= 1
        assert isinstance(enhanced_response.cultural_adaptations, list)
        assert isinstance(enhanced_response.regional_insights, list)
        assert isinstance(enhanced_response.actionable_recommendations, list)
        assert isinstance(enhanced_response.local_context_warnings, list)
        assert isinstance(enhanced_response.follow_up_suggestions, list)
        assert isinstance(enhanced_response.sources, list)
    
    @pytest.mark.asyncio
    async def test_generate_geographic_llm_response_complete(self):
        """Test complete geographic LLM response generation."""
        user_query = "How can I advance my career in data science in Singapore?"
        
        response = await self.service.generate_geographic_llm_response(
            user_query=user_query,
            region='Southeast Asia',
            context_type=ContextType.CAREER,
            user_profile=self.sample_user_profile,
            additional_context=self.sample_additional_context
        )
        
        assert isinstance(response, EnhancedLLMResponse)
        assert len(response.content) > 0
        assert response.confidence_score > 0
        assert len(response.cultural_adaptations) >= 0
        assert len(response.regional_insights) >= 0
        assert len(response.actionable_recommendations) > 0
    
    def test_get_cultural_dimensions(self):
        """Test cultural dimensions retrieval."""
        # Test known regions
        na_dimensions = self.service._get_cultural_dimensions('North America')
        assert isinstance(na_dimensions, dict)
        assert 'power_distance' in na_dimensions
        assert 'individualism' in na_dimensions
        assert all(0 <= value <= 1 for value in na_dimensions.values())
        
        # Test East Asia
        ea_dimensions = self.service._get_cultural_dimensions('East Asia')
        assert ea_dimensions['individualism'] < 0.5  # Collectivist culture
        assert ea_dimensions['power_distance'] > 0.5  # High power distance
        
        # Test unknown region (should return defaults)
        unknown_dimensions = self.service._get_cultural_dimensions('Unknown Region')
        assert all(value == 0.5 for value in unknown_dimensions.values())
    
    def test_get_economic_indicators(self):
        """Test economic indicators retrieval."""
        indicators = self.service._get_economic_indicators('North America')
        
        assert isinstance(indicators, dict)
        expected_keys = ['gdp_growth_rate', 'unemployment_rate', 'inflation_rate', 
                        'currency_stability', 'business_environment_rank', 'key_industries']
        
        for key in expected_keys:
            assert key in indicators
    
    def test_get_legal_framework(self):
        """Test legal framework information retrieval."""
        legal_info = self.service._get_legal_framework('Western Europe')
        
        assert isinstance(legal_info, dict)
        expected_keys = ['employment_law', 'visa_requirements', 'tax_structure', 
                        'business_registration', 'intellectual_property']
        
        for key in expected_keys:
            assert key in legal_info
            assert isinstance(legal_info[key], str)
    
    def test_get_industry_landscape(self):
        """Test industry landscape retrieval."""
        landscape = self.service._get_industry_landscape('East Asia')
        
        assert isinstance(landscape, dict)
        expected_keys = ['dominant_sectors', 'emerging_sectors', 'major_hubs', 'growth_outlook']
        
        for key in expected_keys:
            assert key in landscape
        
        assert isinstance(landscape['dominant_sectors'], list)
        assert isinstance(landscape['emerging_sectors'], list)
        assert isinstance(landscape['major_hubs'], list)
    
    def test_get_language_context(self):
        """Test language context retrieval."""
        lang_context = self.service._get_language_context('North America')
        
        assert isinstance(lang_context, dict)
        expected_keys = ['primary', 'secondary', 'business_language', 'cultural_notes']
        
        for key in expected_keys:
            assert key in lang_context
            assert isinstance(lang_context[key], str)
    
    def test_format_cultural_context(self):
        """Test cultural context formatting."""
        dimensions = {
            'power_distance': 0.8,
            'individualism': 0.2,
            'uncertainty_avoidance': 0.5
        }
        
        formatted = self.service._format_cultural_context(dimensions)
        
        assert isinstance(formatted, str)
        assert 'High power distance' in formatted
        assert 'Low individualism' in formatted
        assert 'Moderate uncertainty avoidance' in formatted
    
    def test_identify_cultural_adaptations(self):
        """Test cultural adaptations identification."""
        response = "Sample response text"
        
        # High power distance context
        geo_context = GeographicContext(
            region='East Asia',
            country='China',
            city=None,
            cultural_dimensions={'power_distance': 0.8, 'individualism': 0.2},
            economic_indicators={},
            legal_framework={},
            industry_landscape={},
            language_context={},
            time_zone='CST',
            currency='CNY'
        )
        
        adaptations = self.service._identify_cultural_adaptations(response, geo_context)
        
        assert isinstance(adaptations, list)
        assert len(adaptations) <= 3
        
        # Should include hierarchy-related adaptation
        hierarchy_adaptation = any('hierarchy' in adaptation.lower() for adaptation in adaptations)
        assert hierarchy_adaptation
    
    def test_generate_regional_insights(self):
        """Test regional insights generation."""
        geo_context = GeographicContext(
            region='North America',
            country='United States',
            city=None,
            cultural_dimensions={},
            economic_indicators={},
            legal_framework={},
            industry_landscape={},
            language_context={},
            time_zone='EST',
            currency='USD'
        )
        
        insights = self.service._generate_regional_insights(geo_context, 'career advice')
        
        assert isinstance(insights, list)
        assert len(insights) <= 3
        assert all(isinstance(insight, str) for insight in insights)
        
        # Should mention the region
        region_mentioned = any('North America' in insight for insight in insights)
        assert region_mentioned
    
    def test_extract_actionable_recommendations(self):
        """Test actionable recommendations extraction."""
        response = "Sample career advice response"
        geo_context = GeographicContext(
            region='Western Europe',
            country='Germany',
            city=None,
            cultural_dimensions={},
            economic_indicators={},
            legal_framework={},
            industry_landscape={},
            language_context={},
            time_zone='CET',
            currency='EUR'
        )
        
        recommendations = self.service._extract_actionable_recommendations(response, geo_context)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 4
        assert all(isinstance(rec, str) for rec in recommendations)
        
        # Should include region-specific recommendations
        region_specific = any('Western Europe' in rec for rec in recommendations)
        assert region_specific
    
    def test_identify_local_context_warnings(self):
        """Test local context warnings identification."""
        geo_context = GeographicContext(
            region='Middle East',
            country='UAE',
            city=None,
            cultural_dimensions={},
            economic_indicators={},
            legal_framework={},
            industry_landscape={},
            language_context={},
            time_zone='GST',
            currency='AED'
        )
        
        warnings = self.service._identify_local_context_warnings(geo_context, 'career advice')
        
        assert isinstance(warnings, list)
        assert len(warnings) <= 2
        
        # Middle East should have cultural/religious warnings
        cultural_warning = any('cultural' in warning.lower() or 'religious' in warning.lower() 
                              for warning in warnings)
        assert cultural_warning
    
    def test_generate_follow_up_suggestions(self):
        """Test follow-up suggestions generation."""
        suggestions = self.service._generate_follow_up_suggestions(
            'career advice query', 'Southeast Asia'
        )
        
        assert isinstance(suggestions, list)
        assert len(suggestions) <= 3
        assert all(isinstance(suggestion, str) for suggestion in suggestions)
        
        # Should mention the region
        region_mentioned = any('Southeast Asia' in suggestion for suggestion in suggestions)
        assert region_mentioned
    
    def test_calculate_response_confidence(self):
        """Test response confidence calculation."""
        # Complete context
        complete_context = GeographicContext(
            region='North America',
            country='United States',
            city='New York',
            cultural_dimensions={'power_distance': 0.4, 'individualism': 0.9, 'uncertainty_avoidance': 0.3},
            economic_indicators={'gdp': 'high', 'unemployment': 'low'},
            legal_framework={'employment_law': 'at_will'},
            industry_landscape={'tech': 'strong'},
            language_context={'primary': 'English'},
            time_zone='EST',
            currency='USD'
        )
        
        confidence = self.service._calculate_response_confidence(complete_context, 'career advice')
        assert isinstance(confidence, float)
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be reasonably confident with complete context
    
    def test_compile_information_sources(self):
        """Test information sources compilation."""
        sources = self.service._compile_information_sources('East Asia')
        
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert all(isinstance(source, str) for source in sources)
        
        # Should mention the region
        region_mentioned = any('East Asia' in source for source in sources)
        assert region_mentioned
    
    def test_create_fallback_response(self):
        """Test fallback response creation."""
        fallback = self.service._create_fallback_response('test query', 'Unknown Region')
        
        assert isinstance(fallback, EnhancedLLMResponse)
        assert 'Unknown Region' in fallback.content
        assert fallback.confidence_score < 0.5  # Should have low confidence
        assert len(fallback.actionable_recommendations) > 0
        assert len(fallback.follow_up_suggestions) > 0
    
    def test_helper_methods(self):
        """Test various helper methods."""
        # Test primary country retrieval
        country = self.service._get_primary_country('North America')
        assert country == 'United States'
        
        # Test timezone retrieval
        timezone = self.service._get_primary_timezone('Western Europe')
        assert timezone == 'CET'
        
        # Test currency retrieval
        currency = self.service._get_primary_currency('East Asia')
        assert 'CNY' in currency or 'JPY' in currency or 'KRW' in currency
        
        # Test key industries retrieval
        industries = self.service._get_key_industries('North America')
        assert isinstance(industries, list)
        assert 'Technology' in industries
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with None user profile
        response = await self.service.generate_geographic_llm_response(
            user_query="test query",
            region='North America',
            context_type=ContextType.CAREER,
            user_profile=None
        )
        assert isinstance(response, EnhancedLLMResponse)
        
        # Test with empty query
        response = await self.service.generate_geographic_llm_response(
            user_query="",
            region='North America',
            context_type=ContextType.CAREER
        )
        assert isinstance(response, EnhancedLLMResponse)
    
    def test_global_service_instance(self):
        """Test global service instance."""
        assert geographic_llm_service is not None
        assert isinstance(geographic_llm_service, GeographicLLMIntegrationService)
        assert len(geographic_llm_service.prompt_templates) > 0
    
    @pytest.mark.parametrize("region,expected_primary_country", [
        ('North America', 'United States'),
        ('Western Europe', 'Germany'),
        ('East Asia', 'China'),
        ('Southeast Asia', 'Singapore'),
        ('Middle East', 'UAE')
    ])
    def test_regional_primary_countries(self, region, expected_primary_country):
        """Test expected primary countries for regions."""
        country = self.service._get_primary_country(region)
        assert country == expected_primary_country
    
    @pytest.mark.parametrize("context_type", [
        ContextType.CULTURAL,
        ContextType.ECONOMIC,
        ContextType.LEGAL,
        ContextType.INDUSTRY,
        ContextType.CAREER,
        ContextType.SOCIAL
    ])
    @pytest.mark.asyncio
    async def test_context_types_handling(self, context_type):
        """Test handling of different context types."""
        context = await self.service._build_geographic_context('North America', context_type)
        assert isinstance(context, GeographicContext)
        assert context.region == 'North America'
    
    def test_cultural_adaptations_structure(self):
        """Test cultural adaptations structure."""
        adaptations = self.service.cultural_adaptations
        
        expected_categories = ['communication_styles', 'decision_making_approaches', 'relationship_orientations']
        
        for category in expected_categories:
            assert category in adaptations
            assert isinstance(adaptations[category], dict)
            assert len(adaptations[category]) > 0
    
    def test_regional_expertise_areas_completeness(self):
        """Test regional expertise areas completeness."""
        for region, expertise_list in self.service.regional_expertise_areas.items():
            assert isinstance(expertise_list, list)
            assert len(expertise_list) > 0
            assert all(isinstance(expertise, str) for expertise in expertise_list)
    
    @pytest.mark.asyncio
    async def test_integration_potential_with_other_services(self):
        """Test integration potential with other enrichment services."""
        # This would test integration with other services like cultural fit assessment
        
        # Simulate geographic context that could be shared
        geo_context = await self.service._build_geographic_context('East Asia', ContextType.CULTURAL)
        
        # Check that context has all necessary information for other services
        assert geo_context.cultural_dimensions is not None
        assert geo_context.region in ['East Asia']  # Should match cultural fit service regions
        assert isinstance(geo_context.cultural_dimensions, dict)
        
        # Check cultural dimensions compatibility
        for dimension, value in geo_context.cultural_dimensions.items():
            assert isinstance(value, (int, float))
            assert 0 <= value <= 1


if __name__ == '__main__':
    pytest.main([__file__])
