"""
Cultural Fit Assessment Service for Global Job Intelligence.

This module provides comprehensive cultural fit analysis for international
job opportunities, including work culture assessment, adaptation guidance,
and cultural intelligence scoring.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


@dataclass
class CulturalProfile:
    """Represents a cultural profile for a region or company."""
    region: str
    communication_style: str  # 'direct', 'indirect', 'formal', 'casual'
    hierarchy_level: str  # 'flat', 'moderate', 'hierarchical'
    work_life_balance: str  # 'excellent', 'good', 'moderate', 'demanding'
    collaboration_style: str  # 'individualistic', 'team_oriented', 'consensus_driven'
    decision_making: str  # 'fast', 'moderate', 'deliberate', 'consensus'
    innovation_culture: str  # 'high', 'medium', 'low'
    risk_tolerance: str  # 'high', 'medium', 'low'
    meeting_culture: str  # 'efficient', 'formal', 'extensive', 'casual'
    feedback_style: str  # 'direct', 'diplomatic', 'structured', 'informal'
    career_development: str  # 'merit_based', 'tenure_based', 'relationship_based'


@dataclass
class CulturalFitScore:
    """Represents a cultural fit assessment result."""
    overall_score: float  # 0-1 scale
    communication_fit: float
    hierarchy_fit: float
    work_style_fit: float
    cultural_adaptation_difficulty: str  # 'low', 'medium', 'high'
    key_strengths: List[str]
    potential_challenges: List[str]
    adaptation_recommendations: List[str]
    confidence_level: str


@dataclass
class WorkCultureInsight:
    """Represents insights about work culture in a specific context."""
    region: str
    company_type: str
    typical_work_hours: str
    vacation_culture: str
    remote_work_acceptance: str
    professional_dress_code: str
    social_expectations: str
    language_requirements: str
    networking_importance: str
    performance_evaluation: str


class CulturalFitAssessmentService:
    """Advanced cultural fit assessment and analysis service."""
    
    def __init__(self):
        """Initialize the cultural fit assessment service."""
        self._regional_profiles = self._initialize_regional_profiles()
        self.company_culture_data = {}
        self.user_preferences = {}
        self.assessment_cache = {}
        
        # Cultural dimensions framework (based on Hofstede + modern research)
        self.cultural_dimensions = {
            'power_distance': {
                'description': 'Acceptance of hierarchical differences',
                'high_characteristics': ['Formal titles important', 'Clear hierarchies', 'Deference to authority'],
                'low_characteristics': ['Informal interactions', 'Flat structures', 'Questioning authority accepted']
            },
            'individualism': {
                'description': 'Individual vs collective focus',
                'high_characteristics': ['Individual achievements valued', 'Personal responsibility', 'Direct communication'],
                'low_characteristics': ['Team harmony important', 'Group decisions', 'Indirect communication']
            },
            'uncertainty_avoidance': {
                'description': 'Comfort with ambiguity and change',
                'high_characteristics': ['Detailed planning', 'Risk aversion', 'Structured processes'],
                'low_characteristics': ['Flexibility valued', 'Risk tolerance', 'Adaptability important']
            },
            'long_term_orientation': {
                'description': 'Focus on future vs present',
                'high_characteristics': ['Long-term planning', 'Patience valued', 'Tradition respected'],
                'low_characteristics': ['Quick results expected', 'Adaptability', 'Innovation focus']
            }
        }
        
        # Work style preferences mapping
        self.work_style_factors = {
            'communication_preference': ['direct', 'diplomatic', 'collaborative', 'structured'],
            'hierarchy_comfort': ['flat', 'moderate', 'structured', 'formal'],
            'pace_preference': ['fast', 'steady', 'deliberate', 'flexible'],
            'feedback_style': ['frequent', 'formal_reviews', 'peer_based', 'self_directed'],
            'work_life_balance': ['strict_separation', 'flexible', 'integrated', 'demanding'],
            'innovation_approach': ['disruptive', 'incremental', 'collaborative', 'methodical']
        }
    
    @property
    def regional_profiles(self) -> Dict[str, CulturalProfile]:
        """Get the regional cultural profiles dictionary."""
        return self._regional_profiles
    
    def _initialize_regional_profiles(self) -> Dict[str, CulturalProfile]:
        """Initialize cultural profiles for different regions."""
        return {
            'North America': CulturalProfile(
                region='North America',
                communication_style='direct',
                hierarchy_level='moderate',
                work_life_balance='moderate',
                collaboration_style='individualistic',
                decision_making='fast',
                innovation_culture='high',
                risk_tolerance='high',
                meeting_culture='efficient',
                feedback_style='direct',
                career_development='merit_based'
            ),
            'Western Europe': CulturalProfile(
                region='Western Europe',
                communication_style='formal',
                hierarchy_level='moderate',
                work_life_balance='excellent',
                collaboration_style='consensus_driven',
                decision_making='deliberate',
                innovation_culture='medium',
                risk_tolerance='medium',
                meeting_culture='formal',
                feedback_style='structured',
                career_development='merit_based'
            ),
            'East Asia': CulturalProfile(
                region='East Asia',
                communication_style='indirect',
                hierarchy_level='hierarchical',
                work_life_balance='demanding',
                collaboration_style='team_oriented',
                decision_making='consensus',
                innovation_culture='medium',
                risk_tolerance='low',
                meeting_culture='formal',
                feedback_style='diplomatic',
                career_development='tenure_based'
            ),
            'Southeast Asia': CulturalProfile(
                region='Southeast Asia',
                communication_style='indirect',
                hierarchy_level='hierarchical',
                work_life_balance='moderate',
                collaboration_style='team_oriented',
                decision_making='moderate',
                innovation_culture='medium',
                risk_tolerance='medium',
                meeting_culture='formal',
                feedback_style='diplomatic',
                career_development='relationship_based'
            ),
            'South America': CulturalProfile(
                region='South America',
                communication_style='indirect',
                hierarchy_level='hierarchical',
                work_life_balance='good',
                collaboration_style='team_oriented',
                decision_making='moderate',
                innovation_culture='medium',
                risk_tolerance='medium',
                meeting_culture='extensive',
                feedback_style='diplomatic',
                career_development='relationship_based'
            ),
            'Middle East': CulturalProfile(
                region='Middle East',
                communication_style='formal',
                hierarchy_level='hierarchical',
                work_life_balance='moderate',
                collaboration_style='relationship_based',
                decision_making='deliberate',
                innovation_culture='medium',
                risk_tolerance='medium',
                meeting_culture='formal',
                feedback_style='diplomatic',
                career_development='relationship_based'
            ),
            'Africa': CulturalProfile(
                region='Africa',
                communication_style='indirect',
                hierarchy_level='hierarchical',
                work_life_balance='good',
                collaboration_style='team_oriented',
                decision_making='consensus',
                innovation_culture='medium',
                risk_tolerance='medium',
                meeting_culture='extensive',
                feedback_style='diplomatic',
                career_development='relationship_based'
            ),
            'Australia/Oceania': CulturalProfile(
                region='Australia/Oceania',
                communication_style='direct',
                hierarchy_level='flat',
                work_life_balance='excellent',
                collaboration_style='team_oriented',
                decision_making='fast',
                innovation_culture='high',
                risk_tolerance='high',
                meeting_culture='casual',
                feedback_style='direct',
                career_development='merit_based'
            )
        }
    
    def assess_cultural_fit(self, 
                           user_profile: Dict[str, Any],
                           job_region: str,
                           company_culture: Optional[Dict[str, Any]] = None) -> CulturalFitScore:
        """Assess cultural fit between user preferences and job context."""
        try:
            # Get regional cultural profile
            regional_profile = self.regional_profiles.get(job_region)
            if not regional_profile:
                return self._create_default_fit_score()
            
            # Extract user preferences
            user_comm_style = user_profile.get('communication_style', 'direct')
            user_hierarchy_pref = user_profile.get('hierarchy_preference', 'moderate')
            user_work_style = user_profile.get('work_style', 'individualistic')
            user_pace_pref = user_profile.get('pace_preference', 'fast')
            user_feedback_pref = user_profile.get('feedback_style', 'direct')
            user_wlb_importance = user_profile.get('work_life_balance_importance', 'high')
            
            # Calculate fit scores for different dimensions
            communication_fit = self._calculate_communication_fit(
                user_comm_style, regional_profile.communication_style
            )
            
            hierarchy_fit = self._calculate_hierarchy_fit(
                user_hierarchy_pref, regional_profile.hierarchy_level
            )
            
            work_style_fit = self._calculate_work_style_fit(
                user_work_style, regional_profile.collaboration_style
            )
            
            # Calculate overall fit score
            overall_score = (communication_fit + hierarchy_fit + work_style_fit) / 3
            
            # Assess adaptation difficulty
            adaptation_difficulty = self._assess_adaptation_difficulty(overall_score)
            
            # Generate insights
            key_strengths = self._identify_cultural_strengths(user_profile, regional_profile)
            potential_challenges = self._identify_cultural_challenges(user_profile, regional_profile)
            recommendations = self._generate_adaptation_recommendations(
                user_profile, regional_profile, overall_score
            )
            
            # Determine confidence level
            confidence_level = self._calculate_assessment_confidence(user_profile)
            
            return CulturalFitScore(
                overall_score=overall_score,
                communication_fit=communication_fit,
                hierarchy_fit=hierarchy_fit,
                work_style_fit=work_style_fit,
                cultural_adaptation_difficulty=adaptation_difficulty,
                key_strengths=key_strengths,
                potential_challenges=potential_challenges,
                adaptation_recommendations=recommendations,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error(f"Failed to assess cultural fit: {e}")
            return self._create_default_fit_score()
    
    def get_work_culture_insights(self, 
                                region: str,
                                company_type: str = 'technology') -> WorkCultureInsight:
        """Get detailed work culture insights for a region."""
        try:
            # Regional work culture data
            culture_data = {
                'North America': {
                    'typical_work_hours': '9 AM - 6 PM, flexibility common',
                    'vacation_culture': '2-4 weeks annually, encouraged usage',
                    'remote_work_acceptance': 'High, hybrid models common',
                    'professional_dress_code': 'Business casual to casual',
                    'social_expectations': 'Networking important, work relationships',
                    'language_requirements': 'English proficiency essential',
                    'networking_importance': 'High, key for career advancement',
                    'performance_evaluation': 'Annual reviews, goal-oriented'
                },
                'Western Europe': {
                    'typical_work_hours': '9 AM - 5 PM, strict work-life boundaries',
                    'vacation_culture': '4-6 weeks mandated, fully utilized',
                    'remote_work_acceptance': 'Moderate to high, country-dependent',
                    'professional_dress_code': 'Business formal to business casual',
                    'social_expectations': 'Professional relationships separate',
                    'language_requirements': 'English + local language helpful',
                    'networking_importance': 'Moderate, relationship building valued',
                    'performance_evaluation': 'Structured, competency-based'
                },
                'East Asia': {
                    'typical_work_hours': '9 AM - 7 PM+, long hours expected',
                    'vacation_culture': '2-3 weeks, often unused',
                    'remote_work_acceptance': 'Low to moderate, changing post-COVID',
                    'professional_dress_code': 'Business formal, conservative',
                    'social_expectations': 'After-work socializing important',
                    'language_requirements': 'English + local language advantage',
                    'networking_importance': 'Very high, relationship critical',
                    'performance_evaluation': 'Hierarchical, tenure consideration'
                },
                'Southeast Asia': {
                    'typical_work_hours': '9 AM - 6 PM, some flexibility',
                    'vacation_culture': '2-4 weeks, moderate usage',
                    'remote_work_acceptance': 'Moderate, increasing acceptance',
                    'professional_dress_code': 'Business casual, climate-appropriate',
                    'social_expectations': 'Team harmony very important',
                    'language_requirements': 'English common, local language bonus',
                    'networking_importance': 'High, relationships matter',
                    'performance_evaluation': 'Group consideration, individual merit'
                },
                'Australia/Oceania': {
                    'typical_work_hours': '9 AM - 5 PM, flexible arrangements',
                    'vacation_culture': '4 weeks mandated, actively encouraged',
                    'remote_work_acceptance': 'Very high, flexible work culture',
                    'professional_dress_code': 'Casual to business casual',
                    'social_expectations': 'Egalitarian, informal relationships',
                    'language_requirements': 'English essential',
                    'networking_importance': 'Moderate, merit-focused culture',
                    'performance_evaluation': 'Direct feedback, achievement-based'
                }
            }
            
            regional_data = culture_data.get(region, culture_data['North America'])
            
            return WorkCultureInsight(
                region=region,
                company_type=company_type,
                **regional_data
            )
            
        except Exception as e:
            logger.error(f"Failed to get work culture insights: {e}")
            return self._create_default_culture_insight(region, company_type)
    
    def generate_cultural_adaptation_plan(self, 
                                        user_profile: Dict[str, Any],
                                        target_region: str,
                                        timeline_months: int = 6) -> Dict[str, Any]:
        """Generate a comprehensive cultural adaptation plan."""
        try:
            # Assess current fit
            fit_score = self.assess_cultural_fit(user_profile, target_region)
            work_insights = self.get_work_culture_insights(target_region)
            
            # Generate timeline-based adaptation plan
            adaptation_plan = {
                'overall_assessment': {
                    'cultural_fit_score': fit_score.overall_score,
                    'adaptation_difficulty': fit_score.cultural_adaptation_difficulty,
                    'timeline_assessment': self._assess_adaptation_timeline(fit_score.overall_score)
                },
                'preparation_phase': self._generate_preparation_recommendations(
                    user_profile, target_region, fit_score
                ),
                'first_month_priorities': self._generate_first_month_plan(
                    fit_score, work_insights
                ),
                'ongoing_development': self._generate_ongoing_development_plan(
                    fit_score, target_region
                ),
                'success_metrics': self._define_adaptation_success_metrics(),
                'resources': self._compile_cultural_resources(target_region),
                'potential_mentorship': self._suggest_mentorship_approaches(target_region),
                'language_considerations': self._assess_language_requirements(target_region)
            }
            
            return adaptation_plan
            
        except Exception as e:
            logger.error(f"Failed to generate adaptation plan: {e}")
            return {'error': 'Unable to generate adaptation plan', 'region': target_region}
    
    def compare_regional_cultures(self, regions: List[str]) -> Dict[str, Any]:
        """Compare cultural characteristics across multiple regions."""
        comparison = {
            'regions': regions,
            'cultural_dimensions': {},
            'work_characteristics': {},
            'adaptation_complexity': {},
            'recommendations': {}
        }
        
        try:
            for region in regions:
                if region in self.regional_profiles:
                    profile = self.regional_profiles[region]
                    work_insights = self.get_work_culture_insights(region)
                    
                    comparison['cultural_dimensions'][region] = {
                        'communication': profile.communication_style,
                        'hierarchy': profile.hierarchy_level,
                        'decision_making': profile.decision_making,
                        'work_life_balance': profile.work_life_balance
                    }
                    
                    comparison['work_characteristics'][region] = {
                        'work_hours': work_insights.typical_work_hours,
                        'vacation': work_insights.vacation_culture,
                        'remote_work': work_insights.remote_work_acceptance,
                        'dress_code': work_insights.professional_dress_code
                    }
                    
                    # Calculate adaptation complexity (from US perspective)
                    us_profile = self.regional_profiles.get('North America')
                    if us_profile:
                        complexity = self._calculate_cultural_distance(us_profile, profile)
                        comparison['adaptation_complexity'][region] = complexity
            
            # Generate comparative insights
            comparison['recommendations'] = self._generate_regional_comparison_insights(comparison)
            
        except Exception as e:
            logger.error(f"Failed to compare regional cultures: {e}")
            comparison['error'] = str(e)
            
        return comparison
    
    # Helper methods
    def _calculate_communication_fit(self, user_style: str, regional_style: str) -> float:
        """Calculate communication style fit score."""
        # Define compatibility matrix
        compatibility = {
            ('direct', 'direct'): 1.0,
            ('direct', 'indirect'): 0.3,
            ('direct', 'formal'): 0.6,
            ('direct', 'casual'): 0.8,
            ('indirect', 'indirect'): 1.0,
            ('indirect', 'direct'): 0.4,
            ('indirect', 'formal'): 0.8,
            ('formal', 'formal'): 1.0,
            ('formal', 'direct'): 0.7,
            ('formal', 'indirect'): 0.8,
            ('casual', 'casual'): 1.0,
            ('casual', 'direct'): 0.9,
            ('casual', 'formal'): 0.5
        }
        
        return compatibility.get((user_style, regional_style), 0.5)
    
    def _calculate_hierarchy_fit(self, user_pref: str, regional_style: str) -> float:
        """Calculate hierarchy preference fit score."""
        compatibility = {
            ('flat', 'flat'): 1.0,
            ('flat', 'moderate'): 0.7,
            ('flat', 'hierarchical'): 0.3,
            ('moderate', 'flat'): 0.8,
            ('moderate', 'moderate'): 1.0,
            ('moderate', 'hierarchical'): 0.7,
            ('hierarchical', 'flat'): 0.4,
            ('hierarchical', 'moderate'): 0.8,
            ('hierarchical', 'hierarchical'): 1.0
        }
        
        return compatibility.get((user_pref, regional_style), 0.5)
    
    def _calculate_work_style_fit(self, user_style: str, regional_style: str) -> float:
        """Calculate work style fit score."""
        compatibility = {
            ('individualistic', 'individualistic'): 1.0,
            ('individualistic', 'team_oriented'): 0.6,
            ('individualistic', 'consensus_driven'): 0.4,
            ('team_oriented', 'team_oriented'): 1.0,
            ('team_oriented', 'individualistic'): 0.7,
            ('team_oriented', 'consensus_driven'): 0.9,
            ('consensus_driven', 'consensus_driven'): 1.0,
            ('consensus_driven', 'team_oriented'): 0.8,
            ('consensus_driven', 'individualistic'): 0.3
        }
        
        return compatibility.get((user_style, regional_style), 0.5)
    
    def _assess_adaptation_difficulty(self, overall_score: float) -> str:
        """Assess cultural adaptation difficulty based on fit score."""
        if overall_score >= 0.8:
            return 'low'
        elif overall_score >= 0.6:
            return 'medium'
        else:
            return 'high'
    
    def _identify_cultural_strengths(self, user_profile: Dict, regional_profile: CulturalProfile) -> List[str]:
        """Identify cultural strengths and advantages."""
        strengths = []
        
        # Communication alignment
        if user_profile.get('communication_style') == regional_profile.communication_style:
            strengths.append(f"Communication style alignment ({regional_profile.communication_style})")
        
        # Work style compatibility
        if user_profile.get('work_style') == regional_profile.collaboration_style:
            strengths.append(f"Work style compatibility ({regional_profile.collaboration_style})")
        
        # Decision making alignment
        if user_profile.get('decision_preference') == regional_profile.decision_making:
            strengths.append(f"Decision-making style match ({regional_profile.decision_making})")
        
        # Innovation culture fit
        if regional_profile.innovation_culture == 'high':
            strengths.append("High innovation culture environment")
        
        return strengths[:4]  # Limit to top 4
    
    def _identify_cultural_challenges(self, user_profile: Dict, regional_profile: CulturalProfile) -> List[str]:
        """Identify potential cultural challenges."""
        challenges = []
        
        # Communication mismatches
        user_comm = user_profile.get('communication_style', 'direct')
        if user_comm == 'direct' and regional_profile.communication_style == 'indirect':
            challenges.append("Direct communication may be perceived as aggressive")
        elif user_comm == 'indirect' and regional_profile.communication_style == 'direct':
            challenges.append("May need to be more direct and explicit")
        
        # Hierarchy challenges
        user_hierarchy = user_profile.get('hierarchy_preference', 'moderate')
        if user_hierarchy == 'flat' and regional_profile.hierarchy_level == 'hierarchical':
            challenges.append("Formal hierarchy and protocol expectations")
        
        # Work-life balance challenges
        if regional_profile.work_life_balance == 'demanding':
            challenges.append("Long work hours and high intensity culture")
        
        # Decision making challenges
        if regional_profile.decision_making == 'consensus' and user_profile.get('decision_preference') == 'fast':
            challenges.append("Slower consensus-based decision making")
        
        return challenges[:4]  # Limit to top 4
    
    def _generate_adaptation_recommendations(self, user_profile: Dict, 
                                           regional_profile: CulturalProfile,
                                           fit_score: float) -> List[str]:
        """Generate specific adaptation recommendations."""
        recommendations = []
        
        # Communication recommendations
        if regional_profile.communication_style == 'indirect':
            recommendations.append("Practice indirect communication and reading between the lines")
        elif regional_profile.communication_style == 'formal':
            recommendations.append("Adopt formal communication protocols and titles")
        
        # Hierarchy recommendations
        if regional_profile.hierarchy_level == 'hierarchical':
            recommendations.append("Show respect for seniority and follow formal channels")
        
        # Work style recommendations
        if regional_profile.collaboration_style == 'consensus_driven':
            recommendations.append("Build consensus before major decisions and allow time for input")
        
        # Meeting culture recommendations
        if regional_profile.meeting_culture == 'formal':
            recommendations.append("Prepare thoroughly for formal meeting structures")
        
        # Relationship building
        if regional_profile.career_development == 'relationship_based':
            recommendations.append("Invest time in building personal relationships with colleagues")
        
        return recommendations[:5]  # Limit to top 5
    
    def _calculate_assessment_confidence(self, user_profile: Dict) -> str:
        """Calculate confidence level of the assessment."""
        profile_completeness = len([v for v in user_profile.values() if v is not None])
        
        if profile_completeness >= 8:
            return 'high'
        elif profile_completeness >= 5:
            return 'medium'
        else:
            return 'low'
    
    def _create_default_fit_score(self) -> CulturalFitScore:
        """Create a default cultural fit score when assessment fails."""
        return CulturalFitScore(
            overall_score=0.6,
            communication_fit=0.6,
            hierarchy_fit=0.6,
            work_style_fit=0.6,
            cultural_adaptation_difficulty='medium',
            key_strengths=['Adaptability', 'Global perspective'],
            potential_challenges=['Cultural adjustment period', 'Communication style differences'],
            adaptation_recommendations=['Observe local customs', 'Build relationships gradually'],
            confidence_level='low'
        )
    
    def _create_default_culture_insight(self, region: str, company_type: str) -> WorkCultureInsight:
        """Create default work culture insight."""
        return WorkCultureInsight(
            region=region,
            company_type=company_type,
            typical_work_hours='9 AM - 6 PM',
            vacation_culture='2-4 weeks annually',
            remote_work_acceptance='Moderate',
            professional_dress_code='Business casual',
            social_expectations='Professional relationships',
            language_requirements='English proficiency',
            networking_importance='Moderate',
            performance_evaluation='Annual reviews'
        )
    
    def _assess_adaptation_timeline(self, fit_score: float) -> str:
        """Assess expected adaptation timeline."""
        if fit_score >= 0.8:
            return '2-3 months for basic adaptation'
        elif fit_score >= 0.6:
            return '4-6 months for comfortable integration'
        else:
            return '6-12 months for full cultural adaptation'
    
    def _generate_preparation_recommendations(self, user_profile: Dict, 
                                            target_region: str,
                                            fit_score: CulturalFitScore) -> List[str]:
        """Generate pre-relocation preparation recommendations."""
        return [
            "Research regional business etiquette and customs",
            "Connect with expatriate communities online",
            "Practice communication style adjustments",
            "Learn basic phrases in local language if applicable",
            "Understand workplace hierarchy and protocols"
        ]
    
    def _generate_first_month_plan(self, fit_score: CulturalFitScore, 
                                 work_insights: WorkCultureInsight) -> List[str]:
        """Generate first month priority plan."""
        return [
            "Observe meeting and communication patterns",
            "Identify key stakeholders and relationship dynamics",
            "Understand decision-making processes",
            "Learn unwritten rules and social expectations",
            "Build initial professional relationships"
        ]
    
    def _generate_ongoing_development_plan(self, fit_score: CulturalFitScore, 
                                         target_region: str) -> List[str]:
        """Generate ongoing cultural development plan."""
        return [
            "Seek feedback on cultural integration",
            "Join local professional networks",
            "Find a cultural mentor or buddy",
            "Continue language learning if applicable",
            "Participate in team social activities"
        ]
    
    def _define_adaptation_success_metrics(self) -> List[str]:
        """Define metrics for successful cultural adaptation."""
        return [
            "Comfortable participating in meetings",
            "Building productive working relationships",
            "Understanding implicit communication",
            "Navigating workplace hierarchy effectively",
            "Feeling included in team activities"
        ]
    
    def _compile_cultural_resources(self, region: str) -> List[str]:
        """Compile useful cultural resources."""
        return [
            f"Country-specific business culture guides",
            f"Local expatriate communities and forums",
            f"Language learning resources if applicable",
            f"Professional networking groups in {region}",
            f"Cultural mentorship programs"
        ]
    
    def _suggest_mentorship_approaches(self, region: str) -> List[str]:
        """Suggest mentorship approaches."""
        return [
            "Find a local colleague as informal mentor",
            "Join formal mentorship programs if available",
            "Connect with other expatriates in similar roles",
            "Engage with cultural integration consultants",
            "Participate in reverse mentoring (teaching your culture)"
        ]
    
    def _assess_language_requirements(self, region: str) -> Dict[str, str]:
        """Assess language requirements for the region."""
        language_data = {
            'North America': {
                'primary': 'English',
                'requirement_level': 'Native/Fluent',
                'additional_languages': 'Spanish helpful in some areas',
                'business_impact': 'Critical for all business functions'
            },
            'Western Europe': {
                'primary': 'English + Local Language',
                'requirement_level': 'English fluent, local language helpful',
                'additional_languages': 'Country-specific',
                'business_impact': 'English for international business, local for integration'
            },
            'East Asia': {
                'primary': 'English + Local Language',
                'requirement_level': 'English business level, local language advantage',
                'additional_languages': 'Mandarin valuable across region',
                'business_impact': 'English for tech roles, local for relationships'
            }
        }
        
        return language_data.get(region, {
            'primary': 'English',
            'requirement_level': 'Business level',
            'additional_languages': 'Local language helpful',
            'business_impact': 'English typically sufficient for international roles'
        })
    
    def _calculate_cultural_distance(self, profile1: CulturalProfile, profile2: CulturalProfile) -> str:
        """Calculate cultural distance between two profiles."""
        differences = 0
        total_dimensions = 6  # Number of key dimensions to compare
        
        dimensions = [
            'communication_style', 'hierarchy_level', 'collaboration_style',
            'decision_making', 'work_life_balance', 'feedback_style'
        ]
        
        for dimension in dimensions:
            if getattr(profile1, dimension) != getattr(profile2, dimension):
                differences += 1
        
        distance_ratio = differences / total_dimensions
        
        if distance_ratio <= 0.3:
            return 'low'
        elif distance_ratio <= 0.6:
            return 'medium'
        else:
            return 'high'
    
    def _generate_regional_comparison_insights(self, comparison: Dict) -> List[str]:
        """Generate insights from regional comparison."""
        insights = []
        
        # Identify most/least hierarchical
        hierarchies = comparison['cultural_dimensions']
        if hierarchies:
            hierarchy_levels = {region: data['hierarchy'] for region, data in hierarchies.items()}
            most_hierarchical = max(hierarchy_levels, key=hierarchy_levels.get)
            least_hierarchical = min(hierarchy_levels, key=hierarchy_levels.get)
            
            insights.append(f"Most hierarchical: {most_hierarchical}, Least hierarchical: {least_hierarchical}")
        
        # Work-life balance comparison
        wlb_data = {region: data['work_life_balance'] for region, data in hierarchies.items()}
        best_wlb = max(wlb_data, key=lambda x: {'excellent': 4, 'good': 3, 'moderate': 2, 'demanding': 1}.get(wlb_data[x], 0))
        insights.append(f"Best work-life balance: {best_wlb}")
        
        return insights


# Global instance for use across the application
cultural_fit_service = CulturalFitAssessmentService()
