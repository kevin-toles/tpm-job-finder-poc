"""
Tests for Cultural Fit Assessment Service.

This module provides comprehensive tests for the cultural fit assessment
functionality including cultural profiling, adaptation analysis, and
regional work culture insights.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import json

from tpm_job_finder_poc.enrichment.cultural_fit_service import (
    CulturalFitAssessmentService,
    CulturalProfile,
    CulturalFitScore,
    WorkCultureInsight,
    cultural_fit_service
)


class TestCulturalFitAssessmentService:
    """Test suite for Cultural Fit Assessment Service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CulturalFitAssessmentService()
        
        # Sample user profile for testing
        self.sample_user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'individualistic',
            'pace_preference': 'fast',
            'feedback_style': 'direct',
            'work_life_balance_importance': 'high',
            'decision_preference': 'fast',
            'innovation_preference': 'high'
        }
        
        # Sample company culture data
        self.sample_company_culture = {
            'size': 'large',
            'industry': 'technology',
            'culture_type': 'innovative',
            'remote_policy': 'hybrid'
        }
    
    def test_service_initialization(self):
        """Test service initializes correctly."""
        assert self.service is not None
        assert len(self.service.regional_profiles) > 0
        assert 'North America' in self.service.regional_profiles
        assert len(self.service.cultural_dimensions) > 0
        assert len(self.service.work_style_factors) > 0
    
    def test_cultural_profile_creation(self):
        """Test cultural profile creation for different regions."""
        # Test North America profile
        na_profile = self.service.regional_profiles['North America']
        assert na_profile.region == 'North America'
        assert na_profile.communication_style == 'direct'
        assert na_profile.hierarchy_level == 'moderate'
        assert na_profile.innovation_culture == 'high'
        
        # Test East Asia profile
        ea_profile = self.service.regional_profiles['East Asia']
        assert ea_profile.region == 'East Asia'
        assert ea_profile.communication_style == 'indirect'
        assert ea_profile.hierarchy_level == 'hierarchical'
        assert ea_profile.career_development == 'tenure_based'
    
    def test_assess_cultural_fit_high_compatibility(self):
        """Test cultural fit assessment with high compatibility."""
        # User profile aligned with North American culture
        user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'individualistic',
            'pace_preference': 'fast',
            'feedback_style': 'direct'
        }
        
        fit_score = self.service.assess_cultural_fit(
            user_profile=user_profile,
            job_region='North America'
        )
        
        assert isinstance(fit_score, CulturalFitScore)
        assert fit_score.overall_score > 0.7  # High compatibility
        assert fit_score.cultural_adaptation_difficulty == 'low'
        assert len(fit_score.key_strengths) > 0
        assert fit_score.confidence_level in ['low', 'medium', 'high']
    
    def test_assess_cultural_fit_low_compatibility(self):
        """Test cultural fit assessment with low compatibility."""
        # User profile misaligned with East Asian culture
        user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'flat',
            'work_style': 'individualistic',
            'pace_preference': 'fast',
            'feedback_style': 'direct'
        }
        
        fit_score = self.service.assess_cultural_fit(
            user_profile=user_profile,
            job_region='East Asia'
        )
        
        assert isinstance(fit_score, CulturalFitScore)
        assert fit_score.overall_score < 0.6  # Low compatibility
        assert fit_score.cultural_adaptation_difficulty in ['medium', 'high']
        assert len(fit_score.potential_challenges) > 0
        assert len(fit_score.adaptation_recommendations) > 0
    
    def test_assess_cultural_fit_unknown_region(self):
        """Test cultural fit assessment with unknown region."""
        fit_score = self.service.assess_cultural_fit(
            user_profile=self.sample_user_profile,
            job_region='Unknown Region'
        )
        
        assert isinstance(fit_score, CulturalFitScore)
        assert fit_score.overall_score == 0.6  # Default score
        assert fit_score.confidence_level == 'low'
    
    def test_get_work_culture_insights(self):
        """Test work culture insights retrieval."""
        insights = self.service.get_work_culture_insights(
            region='North America',
            company_type='technology'
        )
        
        assert isinstance(insights, WorkCultureInsight)
        assert insights.region == 'North America'
        assert insights.company_type == 'technology'
        assert 'AM' in insights.typical_work_hours
        assert 'weeks' in insights.vacation_culture
        assert insights.remote_work_acceptance is not None
    
    def test_get_work_culture_insights_different_regions(self):
        """Test work culture insights for different regions."""
        regions = ['Western Europe', 'East Asia', 'Southeast Asia']
        
        for region in regions:
            insights = self.service.get_work_culture_insights(region)
            assert isinstance(insights, WorkCultureInsight)
            assert insights.region == region
            assert insights.typical_work_hours is not None
            assert insights.vacation_culture is not None
    
    def test_generate_cultural_adaptation_plan(self):
        """Test cultural adaptation plan generation."""
        adaptation_plan = self.service.generate_cultural_adaptation_plan(
            user_profile=self.sample_user_profile,
            target_region='East Asia',
            timeline_months=6
        )
        
        assert isinstance(adaptation_plan, dict)
        assert 'overall_assessment' in adaptation_plan
        assert 'preparation_phase' in adaptation_plan
        assert 'first_month_priorities' in adaptation_plan
        assert 'ongoing_development' in adaptation_plan
        assert 'success_metrics' in adaptation_plan
        
        # Check overall assessment
        overall = adaptation_plan['overall_assessment']
        assert 'cultural_fit_score' in overall
        assert 'adaptation_difficulty' in overall
        assert 'timeline_assessment' in overall
    
    def test_compare_regional_cultures(self):
        """Test regional culture comparison."""
        regions = ['North America', 'Western Europe', 'East Asia']
        comparison = self.service.compare_regional_cultures(regions)
        
        assert isinstance(comparison, dict)
        assert 'regions' in comparison
        assert 'cultural_dimensions' in comparison
        assert 'work_characteristics' in comparison
        assert 'adaptation_complexity' in comparison
        assert 'recommendations' in comparison
        
        # Check all regions are included
        assert comparison['regions'] == regions
        
        # Check cultural dimensions for each region
        for region in regions:
            assert region in comparison['cultural_dimensions']
            dimensions = comparison['cultural_dimensions'][region]
            assert 'communication' in dimensions
            assert 'hierarchy' in dimensions
            assert 'decision_making' in dimensions
    
    def test_communication_fit_calculation(self):
        """Test communication style fit calculation."""
        # Perfect match
        fit_score = self.service._calculate_communication_fit('direct', 'direct')
        assert fit_score == 1.0
        
        # Poor match
        fit_score = self.service._calculate_communication_fit('direct', 'indirect')
        assert fit_score < 0.5
        
        # Moderate match
        fit_score = self.service._calculate_communication_fit('direct', 'formal')
        assert 0.5 <= fit_score <= 0.8
    
    def test_hierarchy_fit_calculation(self):
        """Test hierarchy preference fit calculation."""
        # Perfect match
        fit_score = self.service._calculate_hierarchy_fit('flat', 'flat')
        assert fit_score == 1.0
        
        # Poor match
        fit_score = self.service._calculate_hierarchy_fit('flat', 'hierarchical')
        assert fit_score < 0.5
        
        # Moderate match
        fit_score = self.service._calculate_hierarchy_fit('moderate', 'flat')
        assert fit_score > 0.7
    
    def test_work_style_fit_calculation(self):
        """Test work style fit calculation."""
        # Perfect match
        fit_score = self.service._calculate_work_style_fit('team_oriented', 'team_oriented')
        assert fit_score == 1.0
        
        # Good match
        fit_score = self.service._calculate_work_style_fit('team_oriented', 'consensus_driven')
        assert fit_score > 0.8
        
        # Poor match
        fit_score = self.service._calculate_work_style_fit('individualistic', 'consensus_driven')
        assert fit_score < 0.5
    
    def test_adaptation_difficulty_assessment(self):
        """Test adaptation difficulty assessment."""
        # High fit score -> low difficulty
        difficulty = self.service._assess_adaptation_difficulty(0.9)
        assert difficulty == 'low'
        
        # Medium fit score -> medium difficulty
        difficulty = self.service._assess_adaptation_difficulty(0.7)
        assert difficulty == 'medium'
        
        # Low fit score -> high difficulty
        difficulty = self.service._assess_adaptation_difficulty(0.4)
        assert difficulty == 'high'
    
    def test_cultural_strengths_identification(self):
        """Test cultural strengths identification."""
        user_profile = {
            'communication_style': 'direct',
            'work_style': 'individualistic',
            'decision_preference': 'fast'
        }
        
        na_profile = self.service.regional_profiles['North America']
        strengths = self.service._identify_cultural_strengths(user_profile, na_profile)
        
        assert isinstance(strengths, list)
        assert len(strengths) <= 4  # Limited to top 4
        
        # Should identify communication alignment
        communication_match = any('Communication style alignment' in strength for strength in strengths)
        work_style_match = any('Work style compatibility' in strength for strength in strengths)
        
        assert communication_match or work_style_match
    
    def test_cultural_challenges_identification(self):
        """Test cultural challenges identification."""
        user_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'flat',
            'decision_preference': 'fast'
        }
        
        ea_profile = self.service.regional_profiles['East Asia']
        challenges = self.service._identify_cultural_challenges(user_profile, ea_profile)
        
        assert isinstance(challenges, list)
        assert len(challenges) <= 4  # Limited to top 4
        
        # Should identify hierarchy challenges
        hierarchy_challenge = any('hierarchy' in challenge.lower() for challenge in challenges)
        assert hierarchy_challenge
    
    def test_adaptation_recommendations_generation(self):
        """Test adaptation recommendations generation."""
        user_profile = self.sample_user_profile
        ea_profile = self.service.regional_profiles['East Asia']
        
        recommendations = self.service._generate_adaptation_recommendations(
            user_profile, ea_profile, 0.5
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) <= 5  # Limited to top 5
        assert all(isinstance(rec, str) for rec in recommendations)
        
        # Should include relevant recommendations for East Asia
        indirect_comm = any('indirect' in rec.lower() for rec in recommendations)
        hierarchy_resp = any('hierarchy' in rec.lower() or 'seniority' in rec.lower() for rec in recommendations)
        
        assert indirect_comm or hierarchy_resp
    
    def test_assessment_confidence_calculation(self):
        """Test assessment confidence calculation."""
        # Complete profile
        complete_profile = {
            'communication_style': 'direct',
            'hierarchy_preference': 'moderate',
            'work_style': 'individualistic',
            'pace_preference': 'fast',
            'feedback_style': 'direct',
            'work_life_balance_importance': 'high',
            'decision_preference': 'fast',
            'innovation_preference': 'high',
            'experience_level': 'senior'
        }
        
        confidence = self.service._calculate_assessment_confidence(complete_profile)
        assert confidence == 'high'
        
        # Incomplete profile
        incomplete_profile = {
            'communication_style': 'direct',
            'work_style': 'individualistic'
        }
        
        confidence = self.service._calculate_assessment_confidence(incomplete_profile)
        assert confidence == 'low'
    
    def test_error_handling(self):
        """Test error handling in various scenarios."""
        # Test with None user profile
        fit_score = self.service.assess_cultural_fit(
            user_profile=None,
            job_region='North America'
        )
        assert isinstance(fit_score, CulturalFitScore)
        
        # Test with empty user profile
        fit_score = self.service.assess_cultural_fit(
            user_profile={},
            job_region='North America'
        )
        assert isinstance(fit_score, CulturalFitScore)
    
    def test_global_service_instance(self):
        """Test global service instance."""
        assert cultural_fit_service is not None
        assert isinstance(cultural_fit_service, CulturalFitAssessmentService)
        assert len(cultural_fit_service.regional_profiles) > 0
    
    @pytest.mark.parametrize("region,expected_communication", [
        ('North America', 'direct'),
        ('Western Europe', 'formal'),
        ('East Asia', 'indirect'),
        ('Southeast Asia', 'indirect'),
        ('Australia/Oceania', 'direct')
    ])
    def test_regional_communication_styles(self, region, expected_communication):
        """Test expected communication styles for different regions."""
        if region in self.service.regional_profiles:
            profile = self.service.regional_profiles[region]
            assert profile.communication_style == expected_communication
    
    @pytest.mark.parametrize("region,expected_hierarchy", [
        ('North America', 'moderate'),
        ('Western Europe', 'moderate'),
        ('East Asia', 'hierarchical'),
        ('Australia/Oceania', 'flat')
    ])
    def test_regional_hierarchy_levels(self, region, expected_hierarchy):
        """Test expected hierarchy levels for different regions."""
        if region in self.service.regional_profiles:
            profile = self.service.regional_profiles[region]
            assert profile.hierarchy_level == expected_hierarchy
    
    def test_cultural_framework_completeness(self):
        """Test that cultural frameworks are complete."""
        # Test cultural dimensions framework
        for dimension_name, dimension in self.service.cultural_dimensions.items():
            assert 'description' in dimension
            assert 'high_characteristics' in dimension
            assert 'low_characteristics' in dimension
            assert isinstance(dimension['high_characteristics'], list)
            assert isinstance(dimension['low_characteristics'], list)
    
    def test_work_style_factors_completeness(self):
        """Test that work style factors are complete."""
        expected_factors = [
            'communication_preference', 'hierarchy_comfort', 'pace_preference',
            'feedback_style', 'work_life_balance', 'innovation_approach'
        ]
        
        for factor in expected_factors:
            assert factor in self.service.work_style_factors
            assert len(self.service.work_style_factors[factor]) > 0
    
    def test_integration_with_geographic_classifier(self):
        """Test integration potential with geographic classifier."""
        # This would test integration with the geographic classifier
        # For now, test that regions match expected formats
        
        expected_regions = [
            'North America', 'Western Europe', 'East Asia', 'Southeast Asia',
            'South America', 'Middle East', 'Africa', 'Australia/Oceania'
        ]
        
        for region in expected_regions:
            assert region in self.service.regional_profiles
            profile = self.service.regional_profiles[region]
            assert isinstance(profile, CulturalProfile)
            assert profile.region == region


if __name__ == '__main__':
    pytest.main([__file__])
