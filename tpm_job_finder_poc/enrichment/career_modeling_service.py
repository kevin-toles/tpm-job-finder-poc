"""
Advanced Career Modeling for International Career Pathway Analysis.

This module provides sophisticated career modeling including international
career pathway analysis, long-term skill demand forecasting, and
personalized career development recommendations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import json
import uuid
import math

logger = logging.getLogger(__name__)


class CareerStage(Enum):
    """Career development stages."""
    ENTRY_LEVEL = "entry_level"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class SkillCategory(Enum):
    """Skill categories for modeling."""
    TECHNICAL = "technical"
    LEADERSHIP = "leadership"
    DOMAIN = "domain"
    SOFT = "soft"
    LANGUAGE = "language"
    CERTIFICATION = "certification"


class PathwayType(Enum):
    """Types of career pathways."""
    TECHNICAL_TRACK = "technical_track"
    MANAGEMENT_TRACK = "management_track"
    HYBRID_TRACK = "hybrid_track"
    ENTREPRENEURIAL = "entrepreneurial"
    CONSULTING = "consulting"
    ACADEMIC = "academic"


@dataclass
class Skill:
    """Represents a professional skill."""
    skill_id: str
    name: str
    category: SkillCategory
    description: str
    industry_relevance: Dict[str, float]  # Industry -> relevance score
    regional_demand: Dict[str, float]     # Region -> demand score
    learning_difficulty: float           # 0-1 scale
    automation_risk: float               # 0-1 scale
    future_demand_trend: float           # -1 to 1 scale
    prerequisite_skills: List[str]
    related_skills: List[str]
    certifications: List[str]
    last_updated: datetime


@dataclass
class CareerRole:
    """Represents a career role/position."""
    role_id: str
    title: str
    career_stage: CareerStage
    industry: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    regional_availability: Dict[str, float]  # Region -> availability score
    salary_ranges: Dict[str, Tuple[float, float]]  # Region -> (min, max)
    growth_potential: float               # 0-1 scale
    remote_feasibility: float            # 0-1 scale
    visa_sponsorship_likelihood: Dict[str, float]  # Country -> likelihood
    typical_progression_roles: List[str]
    last_updated: datetime


@dataclass
class CareerPathway:
    """Represents a complete career pathway."""
    pathway_id: str
    pathway_type: PathwayType
    title: str
    description: str
    industry: str
    roles: List[str]                     # Role IDs in progression order
    skill_progression: Dict[str, List[str]]  # Stage -> required skills
    geographic_feasibility: Dict[str, float]  # Region -> feasibility score
    estimated_duration_years: float
    difficulty_score: float              # 0-1 scale
    market_demand_score: float           # 0-1 scale
    salary_progression: Dict[str, Dict[str, float]]  # Region -> Stage -> Salary
    success_factors: List[str]
    potential_obstacles: List[str]
    created_at: datetime


@dataclass
class SkillGap:
    """Represents a skill gap analysis."""
    skill_id: str
    skill_name: str
    current_level: float                 # 0-1 scale
    required_level: float                # 0-1 scale
    gap_severity: float                  # 0-1 scale
    priority: str                        # high, medium, low
    learning_resources: List[str]
    estimated_learning_time_months: float
    learning_path: List[str]
    market_urgency: float                # 0-1 scale


@dataclass
class CareerForecast:
    """Represents career and skill demand forecasting."""
    forecast_id: str
    region: str
    industry: str
    forecast_period_years: int
    role_demand_trends: Dict[str, Dict[str, float]]  # Role -> Year -> demand score
    skill_demand_trends: Dict[str, Dict[str, float]]  # Skill -> Year -> demand score
    emerging_roles: List[Dict[str, Any]]
    declining_roles: List[Dict[str, Any]]
    salary_projections: Dict[str, Dict[str, float]]  # Role -> Year -> projected salary
    automation_impact: Dict[str, float]  # Role -> automation risk
    market_disruptions: List[Dict[str, Any]]
    confidence_score: float              # 0-1 scale
    generated_at: datetime


@dataclass
class PersonalizedCareerPlan:
    """Represents a personalized career development plan."""
    plan_id: str
    user_id: str
    current_role: str
    target_roles: List[str]
    preferred_regions: List[str]
    timeline_years: int
    skill_gaps: List[SkillGap]
    recommended_pathways: List[str]
    learning_milestones: Dict[str, List[str]]  # Year -> milestones
    geographic_moves: List[Dict[str, Any]]
    salary_projections: Dict[str, float]  # Year -> projected salary
    risk_assessment: Dict[str, Any]
    success_probability: float           # 0-1 scale
    next_actions: List[str]
    created_at: datetime
    last_updated: datetime


class AdvancedCareerModelingService:
    """Advanced career modeling and forecasting service."""
    
    def __init__(self):
        """Initialize the career modeling service."""
        self.skills = {}
        self.roles = {}
        self.pathways = {}
        self.forecasts = {}
        self.career_plans = {}
        self.skill_relationships = {}
        self.market_data = {}
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample skills, roles, and pathways."""
        try:
            # Sample skills
            self._create_sample_skills()
            
            # Sample roles
            self._create_sample_roles()
            
            # Sample pathways
            self._create_sample_pathways()
            
            logger.info("Initialized career modeling with sample data")
            
        except Exception as e:
            logger.error(f"Failed to initialize sample data: {e}")
    
    def _create_sample_skills(self):
        """Create sample skills for modeling."""
        sample_skills = [
            {
                'name': 'Python Programming',
                'category': SkillCategory.TECHNICAL,
                'description': 'Proficiency in Python programming language',
                'industry_relevance': {'Technology': 0.9, 'Finance': 0.8, 'Healthcare': 0.7},
                'regional_demand': {'North America': 0.9, 'Europe': 0.8, 'Asia': 0.85},
                'learning_difficulty': 0.6,
                'automation_risk': 0.2,
                'future_demand_trend': 0.8
            },
            {
                'name': 'Machine Learning',
                'category': SkillCategory.TECHNICAL,
                'description': 'Knowledge of ML algorithms and frameworks',
                'industry_relevance': {'Technology': 0.95, 'Finance': 0.85, 'Healthcare': 0.8},
                'regional_demand': {'North America': 0.95, 'Europe': 0.85, 'Asia': 0.9},
                'learning_difficulty': 0.8,
                'automation_risk': 0.1,
                'future_demand_trend': 0.9
            },
            {
                'name': 'Team Leadership',
                'category': SkillCategory.LEADERSHIP,
                'description': 'Ability to lead and manage technical teams',
                'industry_relevance': {'Technology': 0.9, 'Finance': 0.85, 'Healthcare': 0.8},
                'regional_demand': {'North America': 0.9, 'Europe': 0.85, 'Asia': 0.8},
                'learning_difficulty': 0.7,
                'automation_risk': 0.05,
                'future_demand_trend': 0.7
            },
            {
                'name': 'Cloud Architecture',
                'category': SkillCategory.TECHNICAL,
                'description': 'Design and implementation of cloud solutions',
                'industry_relevance': {'Technology': 0.95, 'Finance': 0.8, 'Healthcare': 0.75},
                'regional_demand': {'North America': 0.9, 'Europe': 0.85, 'Asia': 0.8},
                'learning_difficulty': 0.75,
                'automation_risk': 0.15,
                'future_demand_trend': 0.85
            },
            {
                'name': 'Data Analysis',
                'category': SkillCategory.TECHNICAL,
                'description': 'Statistical analysis and data interpretation',
                'industry_relevance': {'Technology': 0.85, 'Finance': 0.9, 'Healthcare': 0.85},
                'regional_demand': {'North America': 0.85, 'Europe': 0.8, 'Asia': 0.9},
                'learning_difficulty': 0.6,
                'automation_risk': 0.3,
                'future_demand_trend': 0.6
            }
        ]
        
        for skill_data in sample_skills:
            skill_id = str(uuid.uuid4())
            skill = Skill(
                skill_id=skill_id,
                name=skill_data['name'],
                category=skill_data['category'],
                description=skill_data['description'],
                industry_relevance=skill_data['industry_relevance'],
                regional_demand=skill_data['regional_demand'],
                learning_difficulty=skill_data['learning_difficulty'],
                automation_risk=skill_data['automation_risk'],
                future_demand_trend=skill_data['future_demand_trend'],
                prerequisite_skills=[],
                related_skills=[],
                certifications=[],
                last_updated=datetime.now()
            )
            self.skills[skill_id] = skill
    
    def _create_sample_roles(self):
        """Create sample roles for modeling."""
        sample_roles = [
            {
                'title': 'Software Engineer',
                'stage': CareerStage.MID_LEVEL,
                'industry': 'Technology',
                'description': 'Develops software applications and systems',
                'required_skills': ['Python Programming', 'Data Analysis'],
                'salary_ranges': {'North America': (80000, 130000), 'Europe': (60000, 100000)},
                'growth_potential': 0.8,
                'remote_feasibility': 0.9
            },
            {
                'title': 'Senior Software Engineer',
                'stage': CareerStage.SENIOR,
                'industry': 'Technology',
                'description': 'Senior-level software development with mentoring responsibilities',
                'required_skills': ['Python Programming', 'Machine Learning', 'Team Leadership'],
                'salary_ranges': {'North America': (120000, 180000), 'Europe': (90000, 140000)},
                'growth_potential': 0.7,
                'remote_feasibility': 0.85
            },
            {
                'title': 'ML Engineer',
                'stage': CareerStage.MID_LEVEL,
                'industry': 'Technology',
                'description': 'Specializes in machine learning model development',
                'required_skills': ['Machine Learning', 'Python Programming', 'Data Analysis'],
                'salary_ranges': {'North America': (100000, 160000), 'Europe': (75000, 120000)},
                'growth_potential': 0.9,
                'remote_feasibility': 0.8
            },
            {
                'title': 'Principal Engineer',
                'stage': CareerStage.PRINCIPAL,
                'industry': 'Technology',
                'description': 'Technical leadership and architecture design',
                'required_skills': ['Cloud Architecture', 'Team Leadership', 'Machine Learning'],
                'salary_ranges': {'North America': (180000, 280000), 'Europe': (140000, 220000)},
                'growth_potential': 0.6,
                'remote_feasibility': 0.7
            }
        ]
        
        for role_data in sample_roles:
            role_id = str(uuid.uuid4())
            role = CareerRole(
                role_id=role_id,
                title=role_data['title'],
                career_stage=role_data['stage'],
                industry=role_data['industry'],
                description=role_data['description'],
                required_skills=role_data['required_skills'],
                preferred_skills=[],
                regional_availability={'North America': 0.8, 'Europe': 0.7, 'Asia': 0.75},
                salary_ranges=role_data['salary_ranges'],
                growth_potential=role_data['growth_potential'],
                remote_feasibility=role_data['remote_feasibility'],
                visa_sponsorship_likelihood={'US': 0.7, 'Canada': 0.8, 'UK': 0.6},
                typical_progression_roles=[],
                last_updated=datetime.now()
            )
            self.roles[role_id] = role
    
    def _create_sample_pathways(self):
        """Create sample career pathways."""
        # Find role IDs for pathway creation
        role_mapping = {role.title: role_id for role_id, role in self.roles.items()}
        
        technical_pathway = CareerPathway(
            pathway_id=str(uuid.uuid4()),
            pathway_type=PathwayType.TECHNICAL_TRACK,
            title='AI/ML Technical Track',
            description='Technical career path specializing in AI/ML',
            industry='Technology',
            roles=[
                role_mapping.get('Software Engineer', ''),
                role_mapping.get('ML Engineer', ''),
                role_mapping.get('Senior Software Engineer', ''),
                role_mapping.get('Principal Engineer', '')
            ],
            skill_progression={
                'entry': ['Python Programming', 'Data Analysis'],
                'mid': ['Machine Learning', 'Cloud Architecture'],
                'senior': ['Team Leadership', 'Advanced ML']
            },
            geographic_feasibility={'North America': 0.9, 'Europe': 0.8, 'Asia': 0.85},
            estimated_duration_years=8,
            difficulty_score=0.7,
            market_demand_score=0.9,
            salary_progression={
                'North America': {'entry': 80000, 'mid': 130000, 'senior': 200000},
                'Europe': {'entry': 60000, 'mid': 100000, 'senior': 150000}
            },
            success_factors=['Strong technical skills', 'Continuous learning', 'Industry networking'],
            potential_obstacles=['Rapid technology changes', 'High competition', 'Automation risk'],
            created_at=datetime.now()
        )
        
        self.pathways[technical_pathway.pathway_id] = technical_pathway
    
    # Skill Analysis Methods
    def add_skill(self, 
                  name: str,
                  category: SkillCategory,
                  description: str,
                  **kwargs) -> Skill:
        """Add a new skill to the knowledge base."""
        try:
            skill_id = str(uuid.uuid4())
            
            skill = Skill(
                skill_id=skill_id,
                name=name,
                category=category,
                description=description,
                industry_relevance=kwargs.get('industry_relevance', {}),
                regional_demand=kwargs.get('regional_demand', {}),
                learning_difficulty=kwargs.get('learning_difficulty', 0.5),
                automation_risk=kwargs.get('automation_risk', 0.3),
                future_demand_trend=kwargs.get('future_demand_trend', 0.5),
                prerequisite_skills=kwargs.get('prerequisite_skills', []),
                related_skills=kwargs.get('related_skills', []),
                certifications=kwargs.get('certifications', []),
                last_updated=datetime.now()
            )
            
            self.skills[skill_id] = skill
            logger.info(f"Added skill: {name}")
            
            return skill
            
        except Exception as e:
            logger.error(f"Failed to add skill: {e}")
            raise
    
    def analyze_skill_gaps(self,
                          current_skills: Dict[str, float],
                          target_role_id: str) -> List[SkillGap]:
        """Analyze skill gaps for a target role."""
        try:
            if target_role_id not in self.roles:
                raise ValueError(f"Role {target_role_id} not found")
            
            target_role = self.roles[target_role_id]
            skill_gaps = []
            
            # Get skill name to ID mapping
            skill_name_to_id = {skill.name: skill_id for skill_id, skill in self.skills.items()}
            
            # Analyze required skills
            for skill_name in target_role.required_skills:
                skill_id = skill_name_to_id.get(skill_name)
                if not skill_id or skill_id not in self.skills:
                    continue
                
                skill = self.skills[skill_id]
                current_level = current_skills.get(skill_name, 0.0)
                required_level = self._get_required_skill_level(skill, target_role.career_stage)
                
                if current_level < required_level:
                    gap_severity = (required_level - current_level) / required_level
                    priority = self._calculate_skill_priority(skill, gap_severity)
                    
                    skill_gap = SkillGap(
                        skill_id=skill_id,
                        skill_name=skill_name,
                        current_level=current_level,
                        required_level=required_level,
                        gap_severity=gap_severity,
                        priority=priority,
                        learning_resources=self._get_learning_resources(skill_name),
                        estimated_learning_time_months=self._estimate_learning_time(skill, gap_severity),
                        learning_path=self._generate_learning_path(skill_id),
                        market_urgency=skill.future_demand_trend
                    )
                    
                    skill_gaps.append(skill_gap)
            
            # Sort by priority and gap severity
            skill_gaps.sort(key=lambda x: (x.priority == 'high', x.gap_severity), reverse=True)
            
            logger.info(f"Analyzed {len(skill_gaps)} skill gaps for role {target_role.title}")
            return skill_gaps
            
        except Exception as e:
            logger.error(f"Failed to analyze skill gaps: {e}")
            return []
    
    def forecast_skill_demand(self,
                            region: str,
                            industry: str,
                            forecast_years: int = 5) -> CareerForecast:
        """Forecast skill and role demand trends."""
        try:
            forecast_id = str(uuid.uuid4())
            
            # Generate role demand trends
            role_demand_trends = {}
            for role_id, role in self.roles.items():
                if role.industry == industry:
                    trends = {}
                    base_demand = role.regional_availability.get(region, 0.5)
                    
                    for year in range(1, forecast_years + 1):
                        # Apply growth/decline based on automation risk and market trends
                        automation_impact = 1 - (role.growth_potential * year * 0.1)
                        market_growth = 1 + (0.05 * year)  # Assume 5% annual growth
                        
                        demand = base_demand * automation_impact * market_growth
                        trends[str(year)] = max(0.1, min(1.0, demand))
                    
                    role_demand_trends[role.title] = trends
            
            # Generate skill demand trends
            skill_demand_trends = {}
            for skill_id, skill in self.skills.items():
                trends = {}
                base_demand = skill.regional_demand.get(region, 0.5)
                
                for year in range(1, forecast_years + 1):
                    # Apply future demand trend
                    trend_factor = 1 + (skill.future_demand_trend * year * 0.1)
                    automation_factor = 1 - (skill.automation_risk * year * 0.05)
                    
                    demand = base_demand * trend_factor * automation_factor
                    trends[str(year)] = max(0.1, min(1.0, demand))
                
                skill_demand_trends[skill.name] = trends
            
            # Identify emerging and declining roles
            emerging_roles = [
                {'role': 'AI Ethics Specialist', 'growth_rate': 0.4, 'confidence': 0.7},
                {'role': 'Quantum Computing Engineer', 'growth_rate': 0.6, 'confidence': 0.5},
                {'role': 'Extended Reality Developer', 'growth_rate': 0.3, 'confidence': 0.8}
            ]
            
            declining_roles = [
                {'role': 'Manual QA Tester', 'decline_rate': -0.2, 'confidence': 0.8},
                {'role': 'Basic Data Entry', 'decline_rate': -0.4, 'confidence': 0.9},
                {'role': 'Legacy System Maintenance', 'decline_rate': -0.15, 'confidence': 0.7}
            ]
            
            # Generate salary projections
            salary_projections = {}
            for role_id, role in self.roles.items():
                if role.industry == industry and region in role.salary_ranges:
                    min_salary, max_salary = role.salary_ranges[region]
                    median_salary = (min_salary + max_salary) / 2
                    
                    projections = {}
                    for year in range(1, forecast_years + 1):
                        # Assume 3% annual salary growth with market adjustments
                        growth_rate = 0.03 + (role.growth_potential * 0.02)
                        projected_salary = median_salary * ((1 + growth_rate) ** year)
                        projections[str(year)] = projected_salary
                    
                    salary_projections[role.title] = projections
            
            forecast = CareerForecast(
                forecast_id=forecast_id,
                region=region,
                industry=industry,
                forecast_period_years=forecast_years,
                role_demand_trends=role_demand_trends,
                skill_demand_trends=skill_demand_trends,
                emerging_roles=emerging_roles,
                declining_roles=declining_roles,
                salary_projections=salary_projections,
                automation_impact=self._calculate_automation_impact(),
                market_disruptions=self._identify_market_disruptions(industry),
                confidence_score=0.75,
                generated_at=datetime.now()
            )
            
            self.forecasts[forecast_id] = forecast
            logger.info(f"Generated {forecast_years}-year forecast for {region} {industry}")
            
            return forecast
            
        except Exception as e:
            logger.error(f"Failed to generate forecast: {e}")
            raise
    
    # Career Pathway Methods
    def analyze_career_pathways(self,
                              current_role_id: str,
                              target_regions: List[str],
                              preferences: Dict[str, Any]) -> List[CareerPathway]:
        """Analyze possible career pathways from current role."""
        try:
            if current_role_id not in self.roles:
                raise ValueError(f"Current role {current_role_id} not found")
            
            current_role = self.roles[current_role_id]
            suitable_pathways = []
            
            for pathway_id, pathway in self.pathways.items():
                if self._is_pathway_suitable(pathway, current_role, target_regions, preferences):
                    suitable_pathways.append(pathway)
            
            # Score and sort pathways
            scored_pathways = []
            for pathway in suitable_pathways:
                score = self._score_pathway(pathway, target_regions, preferences)
                scored_pathways.append((score, pathway))
            
            # Sort by score descending
            scored_pathways.sort(key=lambda x: x[0], reverse=True)
            
            result = [pathway for score, pathway in scored_pathways[:10]]  # Top 10
            logger.info(f"Found {len(result)} suitable pathways")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze career pathways: {e}")
            return []
    
    def create_personalized_career_plan(self,
                                      user_id: str,
                                      current_role_id: str,
                                      target_roles: List[str],
                                      preferred_regions: List[str],
                                      timeline_years: int,
                                      current_skills: Dict[str, float]) -> PersonalizedCareerPlan:
        """Create a personalized career development plan."""
        try:
            plan_id = str(uuid.uuid4())
            
            # Analyze skill gaps for all target roles
            all_skill_gaps = []
            for target_role in target_roles:
                target_role_id = self._find_role_by_title(target_role)
                if target_role_id:
                    gaps = self.analyze_skill_gaps(current_skills, target_role_id)
                    all_skill_gaps.extend(gaps)
            
            # Deduplicate and prioritize skill gaps
            unique_gaps = self._deduplicate_skill_gaps(all_skill_gaps)
            
            # Find recommended pathways
            current_role = self.roles.get(current_role_id)
            recommended_pathways = []
            if current_role:
                pathways = self.analyze_career_pathways(
                    current_role_id,
                    preferred_regions,
                    {'timeline_years': timeline_years}
                )
                recommended_pathways = [p.pathway_id for p in pathways[:3]]
            
            # Create learning milestones
            learning_milestones = self._create_learning_milestones(unique_gaps, timeline_years)
            
            # Plan geographic moves if needed
            geographic_moves = self._plan_geographic_moves(
                preferred_regions,
                target_roles,
                timeline_years
            )
            
            # Project salary progression
            salary_projections = self._project_salary_progression(
                current_role_id,
                target_roles,
                preferred_regions,
                timeline_years
            )
            
            # Assess risks
            risk_assessment = self._assess_career_risks(
                current_role_id,
                target_roles,
                unique_gaps,
                timeline_years
            )
            
            # Calculate success probability
            success_probability = self._calculate_success_probability(
                unique_gaps,
                timeline_years,
                risk_assessment
            )
            
            # Generate next actions
            next_actions = self._generate_next_actions(unique_gaps, learning_milestones)
            
            career_plan = PersonalizedCareerPlan(
                plan_id=plan_id,
                user_id=user_id,
                current_role=current_role_id,
                target_roles=target_roles,
                preferred_regions=preferred_regions,
                timeline_years=timeline_years,
                skill_gaps=unique_gaps,
                recommended_pathways=recommended_pathways,
                learning_milestones=learning_milestones,
                geographic_moves=geographic_moves,
                salary_projections=salary_projections,
                risk_assessment=risk_assessment,
                success_probability=success_probability,
                next_actions=next_actions,
                created_at=datetime.now(),
                last_updated=datetime.now()
            )
            
            self.career_plans[plan_id] = career_plan
            logger.info(f"Created personalized career plan for user {user_id}")
            
            return career_plan
            
        except Exception as e:
            logger.error(f"Failed to create career plan: {e}")
            raise
    
    def get_international_mobility_analysis(self,
                                          role_titles: List[str],
                                          source_region: str,
                                          target_regions: List[str]) -> Dict[str, Any]:
        """Analyze international mobility for specific roles."""
        try:
            mobility_analysis = {}
            
            for target_region in target_regions:
                region_analysis = {
                    'overall_feasibility': 0.0,
                    'role_availability': {},
                    'visa_requirements': {},
                    'salary_comparison': {},
                    'cultural_adaptation': {},
                    'recommended_timeline': '',
                    'challenges': [],
                    'opportunities': []
                }
                
                role_scores = []
                
                for role_title in role_titles:
                    role_id = self._find_role_by_title(role_title)
                    if not role_id or role_id not in self.roles:
                        continue
                    
                    role = self.roles[role_id]
                    
                    # Analyze role availability
                    availability = role.regional_availability.get(target_region, 0.3)
                    region_analysis['role_availability'][role_title] = availability
                    
                    # Visa sponsorship likelihood
                    visa_likelihood = self._get_visa_likelihood(target_region, role)
                    region_analysis['visa_requirements'][role_title] = {
                        'sponsorship_likelihood': visa_likelihood,
                        'typical_visa_types': self._get_typical_visa_types(target_region, role),
                        'processing_time_months': self._get_visa_processing_time(target_region)
                    }
                    
                    # Salary comparison
                    salary_comparison = self._compare_salaries(role, source_region, target_region)
                    region_analysis['salary_comparison'][role_title] = salary_comparison
                    
                    # Cultural adaptation requirements
                    cultural_factors = self._analyze_cultural_factors(source_region, target_region, role)
                    region_analysis['cultural_adaptation'][role_title] = cultural_factors
                    
                    role_scores.append(availability * visa_likelihood)
                
                # Calculate overall feasibility
                if role_scores:
                    region_analysis['overall_feasibility'] = sum(role_scores) / len(role_scores)
                
                # Generate recommendations
                region_analysis['recommended_timeline'] = self._recommend_mobility_timeline(
                    region_analysis['overall_feasibility']
                )
                
                region_analysis['challenges'] = self._identify_mobility_challenges(
                    source_region, target_region, role_titles
                )
                
                region_analysis['opportunities'] = self._identify_mobility_opportunities(
                    source_region, target_region, role_titles
                )
                
                mobility_analysis[target_region] = region_analysis
            
            logger.info(f"Completed international mobility analysis for {len(target_regions)} regions")
            return mobility_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze international mobility: {e}")
            return {}
    
    # Utility and Helper Methods
    def _get_required_skill_level(self, skill: Skill, career_stage: CareerStage) -> float:
        """Get required skill level for a career stage."""
        stage_multipliers = {
            CareerStage.ENTRY_LEVEL: 0.4,
            CareerStage.JUNIOR: 0.5,
            CareerStage.MID_LEVEL: 0.7,
            CareerStage.SENIOR: 0.8,
            CareerStage.LEAD: 0.85,
            CareerStage.PRINCIPAL: 0.9,
            CareerStage.DIRECTOR: 0.7,  # More leadership, less technical
            CareerStage.EXECUTIVE: 0.5   # Strategic, less hands-on
        }
        
        base_requirement = 0.7  # Default requirement level
        return base_requirement * stage_multipliers.get(career_stage, 0.7)
    
    def _calculate_skill_priority(self, skill: Skill, gap_severity: float) -> str:
        """Calculate skill learning priority."""
        # High priority: high demand, high gap severity
        priority_score = (skill.future_demand_trend + gap_severity) / 2
        
        if priority_score > 0.7:
            return 'high'
        elif priority_score > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_learning_resources(self, skill_name: str) -> List[str]:
        """Get learning resources for a skill."""
        # Mock implementation - would integrate with learning platforms
        resource_mapping = {
            'Python Programming': [
                'Python.org official tutorial',
                'Coursera Python for Everybody',
                'LeetCode Python practice'
            ],
            'Machine Learning': [
                'Andrew Ng Machine Learning Course',
                'Kaggle Learn ML',
                'Fast.ai practical deep learning'
            ],
            'Team Leadership': [
                'Harvard Business Review Leadership articles',
                'LinkedIn Learning Leadership courses',
                'Local management training programs'
            ]
        }
        
        return resource_mapping.get(skill_name, ['Online courses', 'Books', 'Practice projects'])
    
    def _estimate_learning_time(self, skill: Skill, gap_severity: float) -> float:
        """Estimate time needed to learn a skill."""
        base_time_months = skill.learning_difficulty * 6  # 6 months for fully difficult skill
        gap_factor = gap_severity * 2  # Double time for larger gaps
        
        return min(18, base_time_months * gap_factor)  # Cap at 18 months
    
    def _generate_learning_path(self, skill_id: str) -> List[str]:
        """Generate a learning path for a skill."""
        if skill_id not in self.skills:
            return []
        
        skill = self.skills[skill_id]
        
        # Basic learning path structure
        path = [
            f"Fundamentals of {skill.name}",
            f"Intermediate {skill.name} concepts",
            f"Advanced {skill.name} applications",
            f"Real-world {skill.name} projects"
        ]
        
        # Add prerequisites if any
        if skill.prerequisite_skills:
            prerequisite_path = [f"Learn {prereq}" for prereq in skill.prerequisite_skills[:2]]
            path = prerequisite_path + path
        
        return path
    
    def _is_pathway_suitable(self,
                           pathway: CareerPathway,
                           current_role: CareerRole,
                           target_regions: List[str],
                           preferences: Dict[str, Any]) -> bool:
        """Check if a pathway is suitable for the user."""
        # Check industry match
        if pathway.industry != current_role.industry:
            return False
        
        # Check geographic feasibility
        avg_feasibility = sum(
            pathway.geographic_feasibility.get(region, 0.3)
            for region in target_regions
        ) / len(target_regions)
        
        if avg_feasibility < 0.4:
            return False
        
        # Check timeline compatibility
        if preferences.get('timeline_years', 10) < pathway.estimated_duration_years:
            return False
        
        return True
    
    def _score_pathway(self,
                      pathway: CareerPathway,
                      target_regions: List[str],
                      preferences: Dict[str, Any]) -> float:
        """Score a pathway based on user preferences."""
        score = 0.0
        
        # Market demand score (30%)
        score += pathway.market_demand_score * 0.3
        
        # Geographic feasibility (25%)
        avg_feasibility = sum(
            pathway.geographic_feasibility.get(region, 0.3)
            for region in target_regions
        ) / len(target_regions)
        score += avg_feasibility * 0.25
        
        # Timeline fit (20%)
        timeline_fit = min(1.0, preferences.get('timeline_years', 10) / pathway.estimated_duration_years)
        score += timeline_fit * 0.2
        
        # Difficulty vs preference (15%)
        difficulty_preference = preferences.get('difficulty_preference', 0.5)  # 0=easy, 1=challenging
        difficulty_score = 1 - abs(pathway.difficulty_score - difficulty_preference)
        score += difficulty_score * 0.15
        
        # Salary potential (10%)
        avg_salary = self._calculate_pathway_avg_salary(pathway, target_regions)
        salary_score = min(1.0, avg_salary / 200000)  # Normalize to $200k
        score += salary_score * 0.1
        
        return score
    
    def _find_role_by_title(self, title: str) -> Optional[str]:
        """Find role ID by title."""
        for role_id, role in self.roles.items():
            if role.title.lower() == title.lower():
                return role_id
        return None
    
    def _deduplicate_skill_gaps(self, skill_gaps: List[SkillGap]) -> List[SkillGap]:
        """Remove duplicate skill gaps and merge similar ones."""
        seen_skills = {}
        for gap in skill_gaps:
            if gap.skill_name not in seen_skills:
                seen_skills[gap.skill_name] = gap
            else:
                # Keep the one with higher gap severity
                if gap.gap_severity > seen_skills[gap.skill_name].gap_severity:
                    seen_skills[gap.skill_name] = gap
        
        return list(seen_skills.values())
    
    def _create_learning_milestones(self,
                                  skill_gaps: List[SkillGap],
                                  timeline_years: int) -> Dict[str, List[str]]:
        """Create year-by-year learning milestones."""
        milestones = {str(year): [] for year in range(1, timeline_years + 1)}
        
        # Sort gaps by priority and learning time
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        sorted_gaps = sorted(
            skill_gaps,
            key=lambda x: (priority_order.get(x.priority, 0), -x.estimated_learning_time_months)
        )
        
        current_year = 1
        for gap in sorted_gaps:
            learning_years = max(1, math.ceil(gap.estimated_learning_time_months / 12))
            
            for year_offset in range(learning_years):
                year = min(current_year + year_offset, timeline_years)
                if year <= timeline_years:
                    if year_offset == 0:
                        milestones[str(year)].append(f"Begin learning {gap.skill_name}")
                    elif year_offset == learning_years - 1:
                        milestones[str(year)].append(f"Master {gap.skill_name}")
                    else:
                        milestones[str(year)].append(f"Continue {gap.skill_name} development")
            
            current_year += 1
            if current_year > timeline_years:
                break
        
        return milestones
    
    def _plan_geographic_moves(self,
                             preferred_regions: List[str],
                             target_roles: List[str],
                             timeline_years: int) -> List[Dict[str, Any]]:
        """Plan potential geographic moves."""
        moves = []
        
        if len(preferred_regions) > 1:
            # Plan moves based on career progression
            years_per_region = timeline_years // len(preferred_regions)
            
            for i, region in enumerate(preferred_regions):
                if i > 0:  # Skip first region (current location)
                    move_year = (i * years_per_region) + 1
                    if move_year <= timeline_years:
                        moves.append({
                            'year': move_year,
                            'target_region': region,
                            'purpose': f"Career advancement in {target_roles[0] if target_roles else 'target role'}",
                            'preparation_months': 6,
                            'estimated_cost_usd': self._estimate_relocation_cost(region)
                        })
        
        return moves
    
    def _project_salary_progression(self,
                                  current_role_id: str,
                                  target_roles: List[str],
                                  preferred_regions: List[str],
                                  timeline_years: int) -> Dict[str, float]:
        """Project salary progression over time."""
        projections = {}
        
        if current_role_id in self.roles:
            current_role = self.roles[current_role_id]
            current_region = preferred_regions[0] if preferred_regions else 'North America'
            
            if current_region in current_role.salary_ranges:
                min_salary, max_salary = current_role.salary_ranges[current_region]
                current_salary = (min_salary + max_salary) / 2
                
                for year in range(1, timeline_years + 1):
                    # Basic salary growth: 5% annual + career progression bonuses
                    base_growth = current_salary * ((1.05) ** year)
                    
                    # Add progression bonuses for role changes
                    if year > 2 and target_roles:  # Assume role change after 2+ years
                        progression_bonus = base_growth * 0.2  # 20% bonus for progression
                        base_growth += progression_bonus
                    
                    projections[str(year)] = base_growth
        
        return projections
    
    def _assess_career_risks(self,
                           current_role_id: str,
                           target_roles: List[str],
                           skill_gaps: List[SkillGap],
                           timeline_years: int) -> Dict[str, Any]:
        """Assess risks in the career plan."""
        risks = {
            'automation_risk': 0.0,
            'market_saturation_risk': 0.0,
            'skill_obsolescence_risk': 0.0,
            'geographic_risk': 0.0,
            'timeline_risk': 0.0,
            'overall_risk': 0.0,
            'mitigation_strategies': []
        }
        
        # Calculate automation risk
        if current_role_id in self.roles:
            current_role = self.roles[current_role_id]
            for skill_gap in skill_gaps:
                if skill_gap.skill_id in self.skills:
                    skill = self.skills[skill_gap.skill_id]
                    risks['automation_risk'] += skill.automation_risk
        
        if skill_gaps:
            risks['automation_risk'] /= len(skill_gaps)
        
        # Timeline risk based on skill gaps and learning time
        total_learning_time = sum(gap.estimated_learning_time_months for gap in skill_gaps)
        available_time_months = timeline_years * 12
        risks['timeline_risk'] = min(1.0, total_learning_time / available_time_months)
        
        # Overall risk calculation
        risk_weights = {
            'automation_risk': 0.3,
            'timeline_risk': 0.4,
            'market_saturation_risk': 0.2,
            'geographic_risk': 0.1
        }
        
        risks['overall_risk'] = sum(
            risks[risk_type] * weight
            for risk_type, weight in risk_weights.items()
        )
        
        # Generate mitigation strategies
        if risks['automation_risk'] > 0.5:
            risks['mitigation_strategies'].append("Focus on human-centric skills and creativity")
        
        if risks['timeline_risk'] > 0.7:
            risks['mitigation_strategies'].append("Prioritize highest-impact skills first")
        
        return risks
    
    def _calculate_success_probability(self,
                                     skill_gaps: List[SkillGap],
                                     timeline_years: int,
                                     risk_assessment: Dict[str, Any]) -> float:
        """Calculate probability of career plan success."""
        # Base probability
        base_probability = 0.7
        
        # Adjust for skill gap difficulty
        if skill_gaps:
            avg_gap_severity = sum(gap.gap_severity for gap in skill_gaps) / len(skill_gaps)
            base_probability *= (1 - avg_gap_severity * 0.3)
        
        # Adjust for timeline realism
        timeline_factor = min(1.0, timeline_years / 5)  # Longer timelines are more realistic
        base_probability *= (0.5 + timeline_factor * 0.5)
        
        # Adjust for overall risk
        overall_risk = risk_assessment.get('overall_risk', 0.5)
        base_probability *= (1 - overall_risk * 0.4)
        
        return max(0.1, min(0.95, base_probability))
    
    def _generate_next_actions(self,
                             skill_gaps: List[SkillGap],
                             learning_milestones: Dict[str, List[str]]) -> List[str]:
        """Generate immediate next actions."""
        actions = []
        
        # Focus on first year milestones
        first_year_milestones = learning_milestones.get('1', [])
        if first_year_milestones:
            actions.extend(first_year_milestones[:3])  # Top 3 actions
        
        # Add skill-specific actions
        high_priority_gaps = [gap for gap in skill_gaps if gap.priority == 'high']
        for gap in high_priority_gaps[:2]:  # Top 2 high-priority gaps
            actions.append(f"Start learning {gap.skill_name} using {gap.learning_resources[0]}")
        
        # Add general actions
        actions.extend([
            "Update LinkedIn profile with career goals",
            "Join professional communities in target field",
            "Set up monthly progress review meetings"
        ])
        
        return actions[:10]  # Limit to 10 actions
    
    # International mobility helper methods
    def _get_visa_likelihood(self, target_region: str, role: CareerRole) -> float:
        """Get visa sponsorship likelihood for role in region."""
        # Mock implementation based on role and region
        base_likelihood = 0.6
        
        # Adjust based on role level
        stage_multipliers = {
            CareerStage.SENIOR: 1.2,
            CareerStage.PRINCIPAL: 1.3,
            CareerStage.DIRECTOR: 1.1,
            CareerStage.EXECUTIVE: 1.4
        }
        
        multiplier = stage_multipliers.get(role.career_stage, 1.0)
        return min(0.95, base_likelihood * multiplier)
    
    def _get_typical_visa_types(self, target_region: str, role: CareerRole) -> List[str]:
        """Get typical visa types for role in region."""
        visa_mapping = {
            'North America': ['H-1B', 'TN', 'O-1'],
            'Europe': ['Blue Card', 'Skilled Worker Visa', 'ICT'],
            'Asia': ['Employment Pass', 'Work Permit', 'Skilled Visa'],
            'Australia/Oceania': ['Temporary Skill Shortage', 'Employer Nomination Scheme']
        }
        
        return visa_mapping.get(target_region, ['Work Permit'])
    
    def _get_visa_processing_time(self, target_region: str) -> int:
        """Get typical visa processing time in months."""
        processing_times = {
            'North America': 6,
            'Europe': 3,
            'Asia': 2,
            'Australia/Oceania': 4
        }
        
        return processing_times.get(target_region, 4)
    
    def _compare_salaries(self, role: CareerRole, source_region: str, target_region: str) -> Dict[str, Any]:
        """Compare salaries between regions."""
        source_salary = role.salary_ranges.get(source_region, (50000, 100000))
        target_salary = role.salary_ranges.get(target_region, (50000, 100000))
        
        source_median = (source_salary[0] + source_salary[1]) / 2
        target_median = (target_salary[0] + target_salary[1]) / 2
        
        return {
            'source_median_usd': source_median,
            'target_median_usd': target_median,
            'change_percentage': ((target_median - source_median) / source_median) * 100,
            'cost_of_living_adjusted': target_median * 0.9,  # Mock cost adjustment
            'net_benefit_usd': target_median - source_median
        }
    
    def _analyze_cultural_factors(self, source_region: str, target_region: str, role: CareerRole) -> Dict[str, Any]:
        """Analyze cultural adaptation factors."""
        return {
            'language_barrier': 0.3 if source_region != target_region else 0.0,
            'work_culture_difference': 0.4,
            'adaptation_time_months': 6,
            'networking_difficulty': 0.5,
            'family_impact': 0.6,
            'support_systems': ['Expat communities', 'Company mentorship', 'Cultural training']
        }
    
    def _recommend_mobility_timeline(self, feasibility_score: float) -> str:
        """Recommend timeline for international mobility."""
        if feasibility_score > 0.8:
            return "6-12 months with proper preparation"
        elif feasibility_score > 0.6:
            return "12-18 months with skill development"
        elif feasibility_score > 0.4:
            return "18-24 months with significant preparation"
        else:
            return "2+ years with extensive skill and network development"
    
    def _identify_mobility_challenges(self, source_region: str, target_region: str, role_titles: List[str]) -> List[str]:
        """Identify mobility challenges."""
        challenges = [
            "Visa application process and requirements",
            "Professional network establishment",
            "Cultural and work style adaptation"
        ]
        
        if source_region != target_region:
            challenges.extend([
                "Language proficiency requirements",
                "Credential recognition and validation",
                "Cost of living and salary adjustments"
            ])
        
        return challenges
    
    def _identify_mobility_opportunities(self, source_region: str, target_region: str, role_titles: List[str]) -> List[str]:
        """Identify mobility opportunities."""
        return [
            "Access to larger job markets",
            "Exposure to diverse work cultures",
            "Enhanced global network",
            "Career acceleration opportunities",
            "Higher compensation potential",
            "New technology and industry exposure"
        ]
    
    def _calculate_automation_impact(self) -> Dict[str, float]:
        """Calculate automation impact by role."""
        impact = {}
        for role_id, role in self.roles.items():
            # Mock calculation based on role type
            if 'Engineer' in role.title:
                impact[role.title] = 0.3
            elif 'Manager' in role.title:
                impact[role.title] = 0.1
            else:
                impact[role.title] = 0.2
        
        return impact
    
    def _identify_market_disruptions(self, industry: str) -> List[Dict[str, Any]]:
        """Identify potential market disruptions."""
        disruptions = [
            {
                'disruption': 'AI/ML Automation',
                'impact_level': 'high',
                'timeline_years': 3,
                'affected_roles': ['Data Analyst', 'Junior Developer'],
                'mitigation': 'Focus on AI collaboration skills'
            },
            {
                'disruption': 'Remote Work Normalization',
                'impact_level': 'medium',
                'timeline_years': 2,
                'affected_roles': ['All roles'],
                'mitigation': 'Develop strong remote collaboration skills'
            }
        ]
        
        return disruptions
    
    def _calculate_pathway_avg_salary(self, pathway: CareerPathway, regions: List[str]) -> float:
        """Calculate average salary for pathway across regions."""
        total_salary = 0
        count = 0
        
        for region in regions:
            if region in pathway.salary_progression:
                region_salaries = pathway.salary_progression[region]
                avg_salary = sum(region_salaries.values()) / len(region_salaries)
                total_salary += avg_salary
                count += 1
        
        return total_salary / count if count > 0 else 0
    
    def _estimate_relocation_cost(self, region: str) -> float:
        """Estimate relocation cost to region."""
        costs = {
            'North America': 15000,
            'Europe': 12000,
            'Asia': 8000,
            'Australia/Oceania': 18000
        }
        
        return costs.get(region, 10000)


# Global instance for use across the application
career_modeling_service = AdvancedCareerModelingService()
