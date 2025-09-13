"""
Enhanced LLM Integration with Geographic Context for Global Career Intelligence.

This module provides sophisticated LLM integration with geographic awareness,
cultural context, and region-specific career guidance for international job seekers.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import json
import asyncio

logger = logging.getLogger(__name__)


class ContextType(Enum):
    """Types of geographic context for LLM integration."""
    CULTURAL = "cultural"
    ECONOMIC = "economic"
    LEGAL = "legal"
    INDUSTRY = "industry"
    CAREER = "career"
    SOCIAL = "social"


@dataclass
class GeographicContext:
    """Represents geographic context for LLM enhancement."""
    region: str
    country: str
    city: Optional[str]
    cultural_dimensions: Dict[str, float]
    economic_indicators: Dict[str, Any]
    legal_framework: Dict[str, str]
    industry_landscape: Dict[str, Any]
    language_context: Dict[str, str]
    time_zone: str
    currency: str


@dataclass
class LLMPromptTemplate:
    """Template for geographic-aware LLM prompts."""
    template_id: str
    category: str
    base_prompt: str
    cultural_modifiers: Dict[str, str]
    region_specific_context: Dict[str, str]
    examples: List[str]
    expected_output_format: str


@dataclass
class EnhancedLLMResponse:
    """Enhanced LLM response with geographic intelligence."""
    content: str
    confidence_score: float
    cultural_adaptations: List[str]
    regional_insights: List[str]
    actionable_recommendations: List[str]
    local_context_warnings: List[str]
    follow_up_suggestions: List[str]
    sources: List[str]


class GeographicLLMIntegrationService:
    """Advanced LLM integration service with geographic intelligence."""
    
    def __init__(self):
        """Initialize the geographic LLM integration service."""
        self.context_cache = {}
        self.prompt_templates = self._initialize_prompt_templates()
        self.cultural_adaptations = self._initialize_cultural_adaptations()
        self.regional_expertise_areas = self._initialize_regional_expertise()
        
        # Geographic context frameworks
        self.cultural_frameworks = {
            'hofstede': {
                'dimensions': ['power_distance', 'individualism', 'masculinity', 
                             'uncertainty_avoidance', 'long_term_orientation', 'indulgence'],
                'scale': (0, 100)
            },
            'globe': {
                'dimensions': ['performance_orientation', 'assertiveness', 'future_orientation',
                             'humane_orientation', 'institutional_collectivism', 'in_group_collectivism',
                             'gender_egalitarianism', 'power_distance', 'uncertainty_avoidance'],
                'scale': (1, 7)
            },
            'trompenaars': {
                'dimensions': ['universalism_particularism', 'individualism_communitarianism',
                             'specific_diffuse', 'achievement_ascription', 'sequential_synchronic'],
                'scale': (0, 1)
            }
        }
        
        # Regional LLM specializations
        self._regional_llm_configs = {
            'North America': {
                'communication_style': 'direct_and_results_oriented',
                'decision_factors': ['efficiency', 'innovation', 'individual_merit'],
                'cultural_sensitivity': 'moderate',
                'business_focus': 'entrepreneurial_and_competitive'
            },
            'Western Europe': {
                'communication_style': 'formal_and_structured',
                'decision_factors': ['consensus', 'sustainability', 'work_life_balance'],
                'cultural_sensitivity': 'high',
                'business_focus': 'collaborative_and_regulated'
            },
            'East Asia': {
                'communication_style': 'indirect_and_respectful',
                'decision_factors': ['harmony', 'long_term_thinking', 'group_consensus'],
                'cultural_sensitivity': 'very_high',
                'business_focus': 'hierarchical_and_relationship_based'
            },
            'Southeast Asia': {
                'communication_style': 'relationship_focused',
                'decision_factors': ['relationships', 'face_saving', 'flexibility'],
                'cultural_sensitivity': 'high',
                'business_focus': 'network_and_family_oriented'
            },
            'Middle East': {
                'communication_style': 'respectful_and_formal',
                'decision_factors': ['relationships', 'trust', 'tradition'],
                'cultural_sensitivity': 'very_high',
                'business_focus': 'relationship_and_trust_based'
            }
        }
    
    @property
    def regional_llm_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get the regional LLM configuration dictionary."""
        return self._regional_llm_configs
    
    def _initialize_prompt_templates(self) -> Dict[str, LLMPromptTemplate]:
        """Initialize geographic-aware prompt templates."""
        templates = {}
        
        # Career advice template
        templates['career_advice'] = LLMPromptTemplate(
            template_id='career_advice',
            category='career_guidance',
            base_prompt="""
            Provide career advice for a professional considering opportunities in {region}.
            Consider the following context:
            - Cultural dimensions: {cultural_context}
            - Industry landscape: {industry_context}
            - Economic conditions: {economic_context}
            - Local career patterns: {career_patterns}
            
            User profile: {user_profile}
            Specific question: {user_question}
            
            Provide advice that is culturally appropriate and practically actionable for this region.
            """,
            cultural_modifiers={
                'high_power_distance': 'Emphasize respect for hierarchy and formal channels',
                'low_power_distance': 'Highlight egalitarian approaches and direct communication',
                'high_uncertainty_avoidance': 'Focus on structured approaches and risk mitigation',
                'low_uncertainty_avoidance': 'Encourage flexibility and adaptive strategies'
            },
            region_specific_context={
                'North America': 'Focus on individual achievement and networking',
                'East Asia': 'Emphasize relationship building and long-term commitment',
                'Western Europe': 'Highlight work-life balance and structured career paths'
            },
            examples=[
                "Career transition advice for tech professional moving to Singapore",
                "Leadership development guidance for manager in Germany",
                "Entrepreneurship advice for startup founder in UAE"
            ],
            expected_output_format="Structured advice with cultural considerations and actionable steps"
        )
        
        # Salary negotiation template
        templates['salary_negotiation'] = LLMPromptTemplate(
            template_id='salary_negotiation',
            category='compensation',
            base_prompt="""
            Provide salary negotiation guidance for {region} considering:
            - Local negotiation customs: {negotiation_culture}
            - Market standards: {market_data}
            - Cultural expectations: {cultural_norms}
            - Legal considerations: {legal_context}
            
            Position: {job_role}
            Experience level: {experience}
            Current situation: {current_context}
            
            Provide culturally appropriate negotiation strategies.
            """,
            cultural_modifiers={
                'direct_culture': 'Straightforward negotiation approaches acceptable',
                'indirect_culture': 'Emphasize relationship preservation and subtle approaches',
                'hierarchical': 'Respect formal processes and authority levels',
                'egalitarian': 'Direct peer-to-peer negotiation strategies'
            },
            region_specific_context={
                'North America': 'Direct negotiation with clear value proposition',
                'East Asia': 'Respectful approach with relationship consideration',
                'Western Europe': 'Structured approach with legal awareness'
            },
            examples=[
                "Software engineer salary negotiation in Tokyo",
                "Marketing manager compensation discussion in London",
                "Consultant rate negotiation in New York"
            ],
            expected_output_format="Step-by-step negotiation strategy with cultural considerations"
        )
        
        # Interview preparation template
        templates['interview_prep'] = LLMPromptTemplate(
            template_id='interview_prep',
            category='interview',
            base_prompt="""
            Prepare interview guidance for {region} considering:
            - Interview culture: {interview_style}
            - Expected behaviors: {behavioral_norms}
            - Communication patterns: {communication_style}
            - Assessment criteria: {evaluation_factors}
            
            Position type: {job_category}
            Company culture: {company_type}
            Interview format: {interview_format}
            
            Provide culturally adapted interview preparation strategies.
            """,
            cultural_modifiers={
                'formal_culture': 'Structured responses and professional demeanor',
                'casual_culture': 'Authentic personality and conversational approach',
                'relationship_focused': 'Emphasize team fit and interpersonal skills',
                'task_focused': 'Highlight technical competencies and achievements'
            },
            region_specific_context={
                'North America': 'Confidence, achievements, and problem-solving focus',
                'East Asia': 'Humility, team harmony, and long-term commitment',
                'Western Europe': 'Competence, work-life balance, and cultural fit'
            },
            examples=[
                "Product manager interview in Silicon Valley",
                "Finance director interview in Frankfurt",
                "Sales lead interview in Singapore"
            ],
            expected_output_format="Comprehensive interview preparation with cultural insights"
        )
        
        return templates
    
    def _initialize_cultural_adaptations(self) -> Dict[str, Dict[str, str]]:
        """Initialize cultural adaptation guidelines for LLM responses."""
        return {
            'communication_styles': {
                'direct': 'Use clear, explicit language with specific examples',
                'indirect': 'Use diplomatic language with contextual suggestions',
                'formal': 'Maintain professional tone with proper titles and structure',
                'casual': 'Use conversational tone with practical examples'
            },
            'decision_making_approaches': {
                'individual': 'Focus on personal agency and self-directed actions',
                'consensus': 'Emphasize group harmony and collaborative decisions',
                'hierarchical': 'Respect authority levels and formal approval processes',
                'egalitarian': 'Highlight peer-level engagement and shared responsibility'
            },
            'relationship_orientations': {
                'task_focused': 'Prioritize efficiency and goal achievement',
                'relationship_focused': 'Emphasize trust building and long-term connections',
                'transactional': 'Focus on mutual benefit and clear exchanges',
                'relational': 'Highlight ongoing partnership and loyalty'
            }
        }
    
    def _initialize_regional_expertise(self) -> Dict[str, List[str]]:
        """Initialize regional expertise areas for specialized advice."""
        return {
            'North America': [
                'tech_entrepreneurship', 'venture_capital', 'remote_work',
                'personal_branding', 'networking', 'stock_options'
            ],
            'Western Europe': [
                'work_life_balance', 'labor_laws', 'eu_mobility',
                'sustainability_careers', 'multilingual_skills', 'social_benefits'
            ],
            'East Asia': [
                'guanxi_building', 'hierarchical_navigation', 'face_concepts',
                'long_term_relationships', 'group_harmony', 'seniority_systems'
            ],
            'Southeast Asia': [
                'cultural_diversity', 'family_business', 'expat_integration',
                'language_skills', 'regional_trade', 'emerging_markets'
            ],
            'Middle East': [
                'wasta_networks', 'cultural_sensitivity', 'business_etiquette',
                'religious_considerations', 'oil_gas_sectors', 'government_relations'
            ],
            'Latin America': [
                'personalismo', 'family_networks', 'informal_economy',
                'political_stability', 'cultural_warmth', 'spanish_portuguese'
            ],
            'Africa': [
                'ubuntu_philosophy', 'tribal_dynamics', 'development_sectors',
                'resource_industries', 'mobile_innovation', 'diaspora_networks'
            ]
        }
    
    async def generate_geographic_llm_response(self,
                                             user_query: str,
                                             region: str,
                                             context_type: ContextType,
                                             user_profile: Optional[Dict[str, Any]] = None,
                                             additional_context: Optional[Dict[str, Any]] = None) -> EnhancedLLMResponse:
        """Generate enhanced LLM response with geographic intelligence."""
        try:
            # Get geographic context
            geo_context = await self._build_geographic_context(region, context_type)
            
            # Select appropriate prompt template
            template = self._select_prompt_template(user_query, context_type)
            
            # Build culturally adapted prompt
            adapted_prompt = self._adapt_prompt_for_culture(
                template, geo_context, user_profile, additional_context
            )
            
            # Generate base LLM response (simulated)
            base_response = await self._generate_base_llm_response(adapted_prompt, region, geo_context.country)
            
            # Enhance with geographic intelligence
            enhanced_response = await self._enhance_with_geographic_intelligence(
                base_response, geo_context, region, user_query
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Failed to generate geographic LLM response: {e}")
            return self._create_fallback_response(user_query, region)
    
    async def _build_geographic_context(self, region: str, context_type: ContextType) -> GeographicContext:
        """Build comprehensive geographic context for LLM enhancement."""
        # Check cache first
        cache_key = f"{region}_{context_type.value}"
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]
        
        # Build context based on region
        context = GeographicContext(
            region=region,
            country=self._get_primary_country(region),
            city=None,  # Can be specified if needed
            cultural_dimensions=self._get_cultural_dimensions(region),
            economic_indicators=self._get_economic_indicators(region),
            legal_framework=self._get_legal_framework(region),
            industry_landscape=self._get_industry_landscape(region),
            language_context=self._get_language_context(region),
            time_zone=self._get_primary_timezone(region),
            currency=self._get_primary_currency(region)
        )
        
        # Cache for future use
        self.context_cache[cache_key] = context
        return context
    
    def _select_prompt_template(self, query: str, context_type: ContextType) -> LLMPromptTemplate:
        """Select the most appropriate prompt template based on query and context."""
        # Simple keyword-based selection (can be enhanced with ML)
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['salary', 'compensation', 'pay', 'negotiate']):
            return self.prompt_templates.get('salary_negotiation')
        elif any(word in query_lower for word in ['interview', 'preparation', 'questions']):
            return self.prompt_templates.get('interview_prep')
        else:
            return self.prompt_templates.get('career_advice')
    
    def _adapt_prompt_for_culture(self,
                                template: LLMPromptTemplate,
                                geo_context: GeographicContext,
                                user_profile: Optional[Dict],
                                additional_context: Optional[Dict]) -> str:
        """Adapt the prompt template for specific cultural context."""
        # Get regional LLM configuration
        regional_config = self.regional_llm_configs.get(geo_context.region, {})
        
        # Build cultural context string
        cultural_context = self._format_cultural_context(geo_context.cultural_dimensions)
        
        # Build industry context
        industry_context = json.dumps(geo_context.industry_landscape, indent=2)
        
        # Build economic context
        economic_context = json.dumps(geo_context.economic_indicators, indent=2)
        
        # Apply cultural modifiers
        try:
            adapted_prompt = template.base_prompt.format(
                region=geo_context.region,
                cultural_context=cultural_context,
                industry_context=industry_context,
                economic_context=economic_context,
                user_profile=json.dumps(user_profile or {}, indent=2),
                user_question=additional_context.get('user_query', 'General career guidance'),
                career_patterns='Regional career advancement patterns',
                **{k: v for k, v in (additional_context or {}).items() if k != 'user_query'}
            )
        except KeyError as e:
            # Handle missing template variables by using base prompt
            adapted_prompt = f"""
            Career guidance for {geo_context.region}:
            
            Cultural Context: {cultural_context}
            Industry Landscape: {industry_context}
            Economic Context: {economic_context}
            User Profile: {json.dumps(user_profile or {}, indent=2)}
            
            Please provide culturally appropriate career advice for this region.
            """
        
        # Add regional-specific instructions
        if geo_context.region in template.region_specific_context:
            regional_instruction = template.region_specific_context[geo_context.region]
            adapted_prompt += f"\n\nRegional Focus: {regional_instruction}"
        
        # Add cultural sensitivity instructions
        cultural_sensitivity = regional_config.get('cultural_sensitivity', 'moderate')
        if cultural_sensitivity == 'very_high':
            adapted_prompt += "\n\nIMPORTANT: Provide culturally sensitive advice that respects local customs and traditions."
        
        return adapted_prompt
    
    async def _generate_base_llm_response(self, prompt: str, region: str = None, country: str = None) -> str:
        """Generate base LLM response (simulated - replace with actual LLM integration)."""
        # This would integrate with actual LLM providers (OpenAI, Anthropic, etc.)
        # For now, return a structured placeholder
        
        # Simulate async LLM call
        await asyncio.sleep(0.1)
        
        # Include region and country information in the response
        region_context = f"for the {region} region" if region else ""
        country_context = f" (specifically {country})" if country else ""
        location_context = f"{region_context}{country_context}"
        
        return f"""
        Based on the cultural and regional context provided, here's my analysis and recommendations for {region or 'this region'} {country_context}:

        **Regional Analysis for {region or 'This Region'}:**
        Operating in {country or region or 'this area'} requires understanding of local market dynamics. The {region} region has distinct characteristics that influence professional success.

        **Cultural Considerations for {region or 'this region'}:**
        The regional context in {country or region or 'this area'} suggests specific approaches that align with local business practices and cultural expectations.

        **{region}-Specific Recommendations:**
        1. Adapt communication style to match {region or 'regional'} preferences
        2. Consider local business customs and etiquette in {country or region or 'the region'}
        3. Build relationships according to cultural norms prevalent in {region or 'this market'}
        4. Align career strategies with regional opportunities in {country or region or 'the local market'}

        **Market Insights for {country or region or 'This Location'}:**
        The {region} market shows specific patterns that professionals should understand. Success in {country or region} depends on adapting to local conditions.

        **Implementation Steps:**
        1. Research {region} business practices
        2. Network with {country or region} professionals
        3. Adapt approach based on cultural context
        4. Monitor progress and adjust strategies
        """
    
    async def _enhance_with_geographic_intelligence(self,
                                                  base_response: str,
                                                  geo_context: GeographicContext,
                                                  region: str,
                                                  original_query: str) -> EnhancedLLMResponse:
        """Enhance base LLM response with geographic intelligence."""
        # Analyze cultural adaptations needed
        cultural_adaptations = self._identify_cultural_adaptations(base_response, geo_context)
        
        # Generate regional insights
        regional_insights = self._generate_regional_insights(geo_context, original_query)
        
        # Extract actionable recommendations
        actionable_recommendations = self._extract_actionable_recommendations(base_response, geo_context)
        
        # Identify local context warnings
        local_warnings = self._identify_local_context_warnings(geo_context, original_query)
        
        # Generate follow-up suggestions
        follow_ups = self._generate_follow_up_suggestions(original_query, region)
        
        # Calculate confidence score
        confidence_score = self._calculate_response_confidence(geo_context, original_query)
        
        return EnhancedLLMResponse(
            content=base_response,
            confidence_score=confidence_score,
            cultural_adaptations=cultural_adaptations,
            regional_insights=regional_insights,
            actionable_recommendations=actionable_recommendations,
            local_context_warnings=local_warnings,
            follow_up_suggestions=follow_ups,
            sources=self._compile_information_sources(region)
        )
    
    def _format_cultural_context(self, cultural_dimensions: Dict[str, float]) -> str:
        """Format cultural dimensions for LLM context."""
        context_parts = []
        for dimension, value in cultural_dimensions.items():
            if value > 0.7:
                context_parts.append(f"High {dimension.replace('_', ' ')}")
            elif value < 0.3:
                context_parts.append(f"Low {dimension.replace('_', ' ')}")
            else:
                context_parts.append(f"Moderate {dimension.replace('_', ' ')}")
        
        return "; ".join(context_parts)
    
    def _get_cultural_dimensions(self, region: str) -> Dict[str, float]:
        """Get cultural dimensions for a region (simplified values)."""
        # Simplified cultural dimension values (in practice, use real cultural research data)
        cultural_data = {
            'North America': {
                'power_distance': 0.4,
                'individualism': 0.9,
                'uncertainty_avoidance': 0.3,
                'long_term_orientation': 0.5,
                'indulgence': 0.7
            },
            'Western Europe': {
                'power_distance': 0.3,
                'individualism': 0.7,
                'uncertainty_avoidance': 0.6,
                'long_term_orientation': 0.7,
                'indulgence': 0.6
            },
            'East Asia': {
                'power_distance': 0.8,
                'individualism': 0.2,
                'uncertainty_avoidance': 0.7,
                'long_term_orientation': 0.9,
                'indulgence': 0.3
            },
            'Southeast Asia': {
                'power_distance': 0.7,
                'individualism': 0.3,
                'uncertainty_avoidance': 0.5,
                'long_term_orientation': 0.6,
                'indulgence': 0.4
            },
            'Middle East': {
                'power_distance': 0.8,
                'individualism': 0.4,
                'uncertainty_avoidance': 0.6,
                'long_term_orientation': 0.7,
                'indulgence': 0.3
            }
        }
        
        return cultural_data.get(region, {
            'power_distance': 0.5,
            'individualism': 0.5,
            'uncertainty_avoidance': 0.5,
            'long_term_orientation': 0.5,
            'indulgence': 0.5
        })
    
    def _get_economic_indicators(self, region: str) -> Dict[str, Any]:
        """Get economic indicators for a region."""
        return {
            'gdp_growth_rate': 'Varies by country',
            'unemployment_rate': 'Region-specific',
            'inflation_rate': 'Current economic conditions',
            'currency_stability': 'Depends on local factors',
            'business_environment_rank': 'World Bank rankings',
            'key_industries': self._get_key_industries(region)
        }
    
    def _get_legal_framework(self, region: str) -> Dict[str, str]:
        """Get legal framework information for a region."""
        return {
            'employment_law': 'Region-specific labor regulations',
            'visa_requirements': 'Work permit and visa policies',
            'tax_structure': 'Personal and corporate tax rates',
            'business_registration': 'Company formation requirements',
            'intellectual_property': 'IP protection frameworks'
        }
    
    def _get_industry_landscape(self, region: str) -> Dict[str, Any]:
        """Get industry landscape for a region."""
        industry_data = {
            'North America': {
                'dominant_sectors': ['Technology', 'Finance', 'Healthcare', 'Entertainment'],
                'emerging_sectors': ['Renewable Energy', 'Biotech', 'AI/ML', 'Fintech'],
                'major_hubs': ['Silicon Valley', 'New York', 'Toronto', 'Austin'],
                'growth_outlook': 'Strong in tech and innovation sectors'
            },
            'Western Europe': {
                'dominant_sectors': ['Manufacturing', 'Finance', 'Tourism', 'Renewable Energy'],
                'emerging_sectors': ['Green Tech', 'Digital Health', 'Sustainability', 'AI'],
                'major_hubs': ['London', 'Berlin', 'Paris', 'Amsterdam', 'Zurich'],
                'growth_outlook': 'Focus on sustainability and digital transformation'
            },
            'East Asia': {
                'dominant_sectors': ['Manufacturing', 'Electronics', 'Automotive', 'Finance'],
                'emerging_sectors': ['AI', 'Robotics', 'Clean Energy', 'Gaming'],
                'major_hubs': ['Tokyo', 'Seoul', 'Shanghai', 'Shenzhen', 'Singapore'],
                'growth_outlook': 'Leading in technology and manufacturing innovation'
            }
        }
        
        return industry_data.get(region, {
            'dominant_sectors': ['Services', 'Technology', 'Finance'],
            'emerging_sectors': ['Digital Transformation', 'Sustainability'],
            'major_hubs': ['Major Cities'],
            'growth_outlook': 'Varies by local conditions'
        })
    
    def _get_language_context(self, region: str) -> Dict[str, str]:
        """Get language context for a region."""
        language_data = {
            'North America': {
                'primary': 'English',
                'secondary': 'Spanish, French',
                'business_language': 'English',
                'cultural_notes': 'Diverse linguistic landscape'
            },
            'Western Europe': {
                'primary': 'Multiple (English, German, French, etc.)',
                'secondary': 'Regional languages',
                'business_language': 'English, local languages',
                'cultural_notes': 'Multilingual environment essential'
            },
            'East Asia': {
                'primary': 'Chinese, Japanese, Korean',
                'secondary': 'English',
                'business_language': 'Local + English',
                'cultural_notes': 'Local language critical for integration'
            }
        }
        
        return language_data.get(region, {
            'primary': 'Local languages',
            'secondary': 'English',
            'business_language': 'English + Local',
            'cultural_notes': 'Language skills important for success'
        })
    
    def _identify_cultural_adaptations(self, response: str, geo_context: GeographicContext) -> List[str]:
        """Identify cultural adaptations needed for the response."""
        adaptations = []
        
        # Check cultural dimensions and suggest adaptations
        if geo_context.cultural_dimensions.get('power_distance', 0.5) > 0.7:
            adaptations.append("Show respect for hierarchy and formal authority structures")
        
        if geo_context.cultural_dimensions.get('individualism', 0.5) < 0.3:
            adaptations.append("Emphasize group harmony and collective success")
        
        if geo_context.cultural_dimensions.get('uncertainty_avoidance', 0.5) > 0.7:
            adaptations.append("Provide structured approaches with clear guidelines")
        
        return adaptations[:3]  # Limit to top 3
    
    def _generate_regional_insights(self, geo_context: GeographicContext, query: str) -> List[str]:
        """Generate region-specific insights."""
        insights = []
        
        region_expertise = self.regional_expertise_areas.get(geo_context.region, [])
        
        insights.append(f"Key success factors in {geo_context.region} include relationship building and cultural awareness")
        
        if 'networking' in region_expertise:
            insights.append("Professional networking is crucial for career advancement in this region")
        
        if 'work_life_balance' in region_expertise:
            insights.append("Work-life balance is highly valued and should be emphasized")
        
        return insights[:3]  # Limit to top 3
    
    def _extract_actionable_recommendations(self, response: str, geo_context: GeographicContext) -> List[str]:
        """Extract actionable recommendations from the response."""
        # Simple extraction (can be enhanced with NLP)
        recommendations = [
            f"Research business customs specific to {geo_context.region}",
            f"Connect with local professional networks and expatriate communities",
            f"Consider cultural training or mentorship programs",
            f"Adapt communication style to match regional preferences"
        ]
        
        return recommendations[:4]
    
    def _identify_local_context_warnings(self, geo_context: GeographicContext, query: str) -> List[str]:
        """Identify potential local context warnings."""
        warnings = []
        
        # Check for high cultural sensitivity regions
        regional_config = self.regional_llm_configs.get(geo_context.region, {})
        cultural_sensitivity = regional_config.get('cultural_sensitivity', 'moderate')
        
        if cultural_sensitivity in ['high', 'very_high']:
            warnings.append("High cultural sensitivity required - research local customs thoroughly")
        
        # Check for specific regional considerations
        if geo_context.region == 'East Asia':
            warnings.append("Face-saving and hierarchy respect are critical cultural factors")
        elif geo_context.region == 'Middle East':
            warnings.append("Religious and cultural considerations may impact business practices")
        
        return warnings[:2]  # Limit to top 2
    
    def _generate_follow_up_suggestions(self, query: str, region: str) -> List[str]:
        """Generate follow-up suggestions for deeper exploration."""
        suggestions = [
            f"Explore specific industry trends in {region}",
            f"Connect with professionals currently working in {region}",
            f"Research visa and legal requirements for {region}",
            f"Learn about cost of living and lifestyle in major {region} cities"
        ]
        
        return suggestions[:3]
    
    def _calculate_response_confidence(self, geo_context: GeographicContext, query: str) -> float:
        """Calculate confidence score for the response."""
        # Simple confidence calculation based on context completeness
        confidence_factors = []
        
        # Cultural context completeness
        if len(geo_context.cultural_dimensions) >= 3:
            confidence_factors.append(0.3)
        
        # Regional expertise availability
        if geo_context.region in self.regional_expertise_areas:
            confidence_factors.append(0.3)
        
        # Economic context availability
        if geo_context.economic_indicators:
            confidence_factors.append(0.2)
        
        # Base confidence
        confidence_factors.append(0.2)
        
        return sum(confidence_factors)
    
    def _compile_information_sources(self, region: str) -> List[str]:
        """Compile relevant information sources for the region."""
        return [
            f"Regional business culture research for {region}",
            f"Local professional associations and networks",
            f"Government economic and business development agencies",
            f"Expatriate communities and international business resources"
        ]
    
    def _create_fallback_response(self, query: str, region: str) -> EnhancedLLMResponse:
        """Create a fallback response when primary generation fails."""
        return EnhancedLLMResponse(
            content=f"I apologize, but I encountered an issue generating a detailed response for {region}. "
                   f"However, I recommend researching local business customs and connecting with "
                   f"professionals in the region for specific guidance.",
            confidence_score=0.3,
            cultural_adaptations=["Research local customs", "Seek cultural mentorship"],
            regional_insights=[f"Each region has unique business practices and cultural norms"],
            actionable_recommendations=[
                "Connect with local professional networks",
                "Research cultural business practices",
                "Consider cultural training programs"
            ],
            local_context_warnings=["Limited regional context available"],
            follow_up_suggestions=[f"Seek region-specific career guidance from local experts"],
            sources=["General business culture resources"]
        )
    
    # Helper methods for geographic data
    def _get_primary_country(self, region: str) -> str:
        """Get primary country for a region."""
        primary_countries = {
            'North America': 'United States',
            'Western Europe': 'Germany',
            'East Asia': 'China',
            'Southeast Asia': 'Singapore',
            'Middle East': 'UAE',
            'Latin America': 'Brazil',
            'Africa': 'South Africa'
        }
        return primary_countries.get(region, 'Various')
    
    def _get_primary_timezone(self, region: str) -> str:
        """Get primary timezone for a region."""
        timezones = {
            'North America': 'EST/PST',
            'Western Europe': 'CET',
            'East Asia': 'CST/JST',
            'Southeast Asia': 'SGT',
            'Middle East': 'GST',
            'Latin America': 'Various',
            'Africa': 'Various'
        }
        return timezones.get(region, 'Various')
    
    def _get_primary_currency(self, region: str) -> str:
        """Get primary currency for a region."""
        currencies = {
            'North America': 'USD',
            'Western Europe': 'EUR',
            'East Asia': 'Various (CNY, JPY, KRW)',
            'Southeast Asia': 'Various (SGD, THB, MYR)',
            'Middle East': 'Various (AED, SAR)',
            'Latin America': 'Various (BRL, MXN)',
            'Africa': 'Various (ZAR, NGN)'
        }
        return currencies.get(region, 'Various')
    
    def _get_key_industries(self, region: str) -> List[str]:
        """Get key industries for a region."""
        industries = {
            'North America': ['Technology', 'Finance', 'Healthcare', 'Entertainment'],
            'Western Europe': ['Manufacturing', 'Finance', 'Tourism', 'Renewable Energy'],
            'East Asia': ['Manufacturing', 'Electronics', 'Automotive', 'Finance'],
            'Southeast Asia': ['Manufacturing', 'Technology', 'Tourism', 'Agriculture'],
            'Middle East': ['Oil & Gas', 'Finance', 'Tourism', 'Construction'],
            'Latin America': ['Agriculture', 'Mining', 'Manufacturing', 'Services'],
            'Africa': ['Mining', 'Agriculture', 'Telecommunications', 'Banking']
        }
        return industries.get(region, ['Services', 'Technology', 'Manufacturing'])


# Global instance for use across the application
geographic_llm_service = GeographicLLMIntegrationService()
