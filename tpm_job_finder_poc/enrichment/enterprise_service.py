"""
Enterprise Multi-User Features for Global Job Intelligence.

This module provides enterprise-level functionality including multi-user
geographic preferences, team-based opportunity sharing, and company
international expansion tracking.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles in enterprise system."""
    ADMIN = "admin"
    MANAGER = "manager"
    RECRUITER = "recruiter"
    EMPLOYEE = "employee"
    VIEWER = "viewer"


class OpportunityStatus(Enum):
    """Status of shared opportunities."""
    ACTIVE = "active"
    APPLIED = "applied"
    INTERVIEWED = "interviewed"
    OFFER_RECEIVED = "offer_received"
    DECLINED = "declined"
    HIRED = "hired"
    ARCHIVED = "archived"


class ExpansionStage(Enum):
    """Company expansion stages."""
    PLANNING = "planning"
    MARKET_RESEARCH = "market_research"
    LEGAL_SETUP = "legal_setup"
    HIRING = "hiring"
    OPERATIONAL = "operational"
    SCALING = "scaling"


@dataclass
class User:
    """Represents an enterprise user."""
    user_id: str
    email: str
    name: str
    role: UserRole
    company_id: str
    department: str
    geographic_preferences: Dict[str, Any]
    notification_preferences: Dict[str, bool]
    created_at: datetime
    last_active: datetime
    is_active: bool


@dataclass
class GeographicPreference:
    """Represents user's geographic preferences."""
    user_id: str
    preferred_regions: List[str]
    preferred_countries: List[str]
    preferred_cities: List[str]
    excluded_regions: List[str]
    excluded_countries: List[str]
    visa_restrictions: List[str]
    relocation_budget_usd: Optional[float]
    timeline_months: Optional[int]
    family_considerations: Dict[str, Any]
    language_requirements: List[str]
    salary_expectations: Dict[str, float]
    work_authorization: Dict[str, bool]
    last_updated: datetime


@dataclass
class SharedOpportunity:
    """Represents a shared job opportunity."""
    opportunity_id: str
    job_id: str
    shared_by: str
    shared_with: List[str]
    company_name: str
    position_title: str
    location: str
    region: str
    country: str
    salary_range: str
    description: str
    requirements: List[str]
    visa_sponsorship: bool
    remote_option: bool
    status: OpportunityStatus
    notes: str
    tags: List[str]
    shared_at: datetime
    expires_at: Optional[datetime]
    application_deadline: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class TeamCollaboration:
    """Represents team collaboration settings."""
    team_id: str
    team_name: str
    company_id: str
    members: List[str]
    geographic_scope: List[str]
    shared_preferences: Dict[str, Any]
    collaboration_rules: Dict[str, Any]
    notification_settings: Dict[str, bool]
    created_by: str
    created_at: datetime
    is_active: bool


@dataclass
class CompanyExpansion:
    """Represents company international expansion tracking."""
    expansion_id: str
    company_id: str
    target_region: str
    target_countries: List[str]
    target_cities: List[str]
    expansion_stage: ExpansionStage
    business_objectives: List[str]
    target_roles: List[str]
    hiring_timeline: Dict[str, datetime]
    budget_usd: float
    market_research: Dict[str, Any]
    legal_requirements: Dict[str, Any]
    talent_pipeline: List[str]
    success_metrics: Dict[str, Any]
    stakeholders: List[str]
    created_at: datetime
    last_updated: datetime
    is_active: bool


@dataclass
class TalentMarketAnalytics:
    """Represents talent market analytics."""
    analytics_id: str
    company_id: str
    region: str
    analysis_period: Tuple[datetime, datetime]
    talent_availability: Dict[str, Any]
    salary_benchmarks: Dict[str, Any]
    competition_analysis: Dict[str, Any]
    skill_demand: Dict[str, Any]
    hiring_velocity: Dict[str, Any]
    retention_rates: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime


class EnterpriseMultiUserService:
    """Enterprise multi-user features service."""
    
    def __init__(self):
        """Initialize the enterprise multi-user service."""
        self.users = {}
        self.companies = {}
        self.geographic_preferences = {}
        self.shared_opportunities = {}
        self.team_collaborations = {}
        self.company_expansions = {}
        self.talent_analytics = {}
        self.notification_queue = []
        
        # Permission matrix
        self.permissions = {
            UserRole.ADMIN: [
                'manage_users', 'manage_teams', 'view_analytics', 'manage_expansions',
                'share_opportunities', 'view_all_opportunities', 'manage_preferences'
            ],
            UserRole.MANAGER: [
                'manage_team', 'view_team_analytics', 'share_opportunities',
                'view_team_opportunities', 'manage_team_preferences'
            ],
            UserRole.RECRUITER: [
                'share_opportunities', 'view_opportunities', 'manage_own_preferences',
                'view_basic_analytics'
            ],
            UserRole.EMPLOYEE: [
                'view_shared_opportunities', 'manage_own_preferences', 'apply_to_opportunities'
            ],
            UserRole.VIEWER: [
                'view_shared_opportunities', 'view_basic_analytics'
            ]
        }
    
    # User Management
    def create_user(self, 
                   email: str,
                   name: str,
                   role: UserRole,
                   company_id: str,
                   department: str) -> User:
        """Create a new enterprise user."""
        try:
            user_id = str(uuid.uuid4())
            
            user = User(
                user_id=user_id,
                email=email,
                name=name,
                role=role,
                company_id=company_id,
                department=department,
                geographic_preferences={},
                notification_preferences={
                    'new_opportunities': True,
                    'team_updates': True,
                    'expansion_updates': True,
                    'analytics_reports': True
                },
                created_at=datetime.now(),
                last_active=datetime.now(),
                is_active=True
            )
            
            self.users[user_id] = user
            logger.info(f"Created user {name} ({email}) with role {role.value}")
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise
    
    def update_user_geographic_preferences(self,
                                         user_id: str,
                                         preferences: Dict[str, Any]) -> GeographicPreference:
        """Update user's geographic preferences."""
        try:
            geographic_pref = GeographicPreference(
                user_id=user_id,
                preferred_regions=preferences.get('preferred_regions', []),
                preferred_countries=preferences.get('preferred_countries', []),
                preferred_cities=preferences.get('preferred_cities', []),
                excluded_regions=preferences.get('excluded_regions', []),
                excluded_countries=preferences.get('excluded_countries', []),
                visa_restrictions=preferences.get('visa_restrictions', []),
                relocation_budget_usd=preferences.get('relocation_budget_usd'),
                timeline_months=preferences.get('timeline_months'),
                family_considerations=preferences.get('family_considerations', {}),
                language_requirements=preferences.get('language_requirements', []),
                salary_expectations=preferences.get('salary_expectations', {}),
                work_authorization=preferences.get('work_authorization', {}),
                last_updated=datetime.now()
            )
            
            self.geographic_preferences[user_id] = geographic_pref
            
            # Update user object
            if user_id in self.users:
                self.users[user_id].geographic_preferences = preferences
            
            logger.info(f"Updated geographic preferences for user {user_id}")
            return geographic_pref
            
        except Exception as e:
            logger.error(f"Failed to update geographic preferences: {e}")
            raise
    
    def get_user_preferences(self, user_id: str) -> Optional[GeographicPreference]:
        """Get user's geographic preferences."""
        return self.geographic_preferences.get(user_id)
    
    # Team Collaboration
    def create_team_collaboration(self,
                                team_name: str,
                                company_id: str,
                                members: List[str],
                                geographic_scope: List[str],
                                created_by: str) -> TeamCollaboration:
        """Create a team collaboration workspace."""
        try:
            team_id = str(uuid.uuid4())
            
            # Validate members exist and have appropriate permissions
            valid_members = []
            for member_id in members:
                if member_id in self.users:
                    user = self.users[member_id]
                    if user.company_id == company_id:
                        valid_members.append(member_id)
            
            team = TeamCollaboration(
                team_id=team_id,
                team_name=team_name,
                company_id=company_id,
                members=valid_members,
                geographic_scope=geographic_scope,
                shared_preferences={
                    'auto_share_matching_opportunities': True,
                    'notification_frequency': 'daily',
                    'quality_threshold': 0.7
                },
                collaboration_rules={
                    'require_approval_for_sharing': False,
                    'allow_external_sharing': False,
                    'auto_archive_after_days': 30
                },
                notification_settings={
                    'new_member_joins': True,
                    'opportunity_shared': True,
                    'opportunity_applied': True,
                    'weekly_summary': True
                },
                created_by=created_by,
                created_at=datetime.now(),
                is_active=True
            )
            
            self.team_collaborations[team_id] = team
            logger.info(f"Created team collaboration '{team_name}' with {len(valid_members)} members")
            
            return team
            
        except Exception as e:
            logger.error(f"Failed to create team collaboration: {e}")
            raise
    
    def share_opportunity_with_team(self,
                                  job_data: Dict[str, Any],
                                  team_id: str,
                                  shared_by: str,
                                  notes: str = "",
                                  tags: List[str] = None) -> SharedOpportunity:
        """Share a job opportunity with a team."""
        try:
            if team_id not in self.team_collaborations:
                raise ValueError(f"Team {team_id} not found")
            
            team = self.team_collaborations[team_id]
            
            # Check if user has permission to share with this team
            if shared_by not in team.members:
                user = self.users.get(shared_by)
                if not user or not self._has_permission(user, 'share_opportunities'):
                    raise PermissionError("User does not have permission to share opportunities")
            
            opportunity_id = str(uuid.uuid4())
            
            shared_opportunity = SharedOpportunity(
                opportunity_id=opportunity_id,
                job_id=job_data.get('job_id', str(uuid.uuid4())),
                shared_by=shared_by,
                shared_with=team.members.copy(),
                company_name=job_data.get('company', 'Unknown'),
                position_title=job_data.get('title', 'Unknown Position'),
                location=job_data.get('location', 'Unknown'),
                region=job_data.get('region', 'Unknown'),
                country=job_data.get('country', 'Unknown'),
                salary_range=job_data.get('salary', 'Not specified'),
                description=job_data.get('description', ''),
                requirements=job_data.get('requirements', []),
                visa_sponsorship=job_data.get('visa_sponsorship', False),
                remote_option=job_data.get('remote_option', False),
                status=OpportunityStatus.ACTIVE,
                notes=notes,
                tags=tags or [],
                shared_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=30),
                application_deadline=job_data.get('application_deadline'),
                metadata=job_data
            )
            
            self.shared_opportunities[opportunity_id] = shared_opportunity
            
            # Send notifications to team members
            self._notify_team_members(team.members, f"New opportunity shared: {shared_opportunity.position_title}")
            
            logger.info(f"Shared opportunity {opportunity_id} with team {team_id}")
            return shared_opportunity
            
        except Exception as e:
            logger.error(f"Failed to share opportunity with team: {e}")
            raise
    
    def get_team_opportunities(self, 
                             team_id: str,
                             user_id: str,
                             filters: Dict[str, Any] = None) -> List[SharedOpportunity]:
        """Get opportunities shared with a team."""
        try:
            if team_id not in self.team_collaborations:
                return []
            
            team = self.team_collaborations[team_id]
            
            # Check if user is a team member or has appropriate permissions
            user = self.users.get(user_id)
            if not user:
                return []
            
            if user_id not in team.members and not self._has_permission(user, 'view_all_opportunities'):
                return []
            
            # Get opportunities shared with this team
            opportunities = [
                opp for opp in self.shared_opportunities.values()
                if any(member in opp.shared_with for member in team.members)
            ]
            
            # Apply filters
            if filters:
                opportunities = self._filter_opportunities(opportunities, filters)
            
            # Sort by shared date (most recent first)
            opportunities.sort(key=lambda x: x.shared_at, reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error(f"Failed to get team opportunities: {e}")
            return []
    
    def update_opportunity_status(self,
                                opportunity_id: str,
                                user_id: str,
                                status: OpportunityStatus,
                                notes: str = "") -> bool:
        """Update the status of a shared opportunity."""
        try:
            if opportunity_id not in self.shared_opportunities:
                return False
            
            opportunity = self.shared_opportunities[opportunity_id]
            
            # Check if user has permission to update this opportunity
            user = self.users.get(user_id)
            if not user:
                return False
            
            if user_id not in opportunity.shared_with and opportunity.shared_by != user_id:
                if not self._has_permission(user, 'manage_opportunities'):
                    return False
            
            opportunity.status = status
            if notes:
                opportunity.notes += f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {notes}"
            
            logger.info(f"Updated opportunity {opportunity_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update opportunity status: {e}")
            return False
    
    # Company Expansion Tracking
    def create_expansion_plan(self,
                            company_id: str,
                            target_region: str,
                            target_countries: List[str],
                            business_objectives: List[str],
                            budget_usd: float,
                            created_by: str) -> CompanyExpansion:
        """Create a company international expansion plan."""
        try:
            expansion_id = str(uuid.uuid4())
            
            expansion = CompanyExpansion(
                expansion_id=expansion_id,
                company_id=company_id,
                target_region=target_region,
                target_countries=target_countries,
                target_cities=[],  # To be determined during planning
                expansion_stage=ExpansionStage.PLANNING,
                business_objectives=business_objectives,
                target_roles=[],
                hiring_timeline={},
                budget_usd=budget_usd,
                market_research={},
                legal_requirements={},
                talent_pipeline=[],
                success_metrics={
                    'target_hires_year_1': 0,
                    'target_revenue_year_1': 0,
                    'market_penetration_target': 0
                },
                stakeholders=[created_by],
                created_at=datetime.now(),
                last_updated=datetime.now(),
                is_active=True
            )
            
            self.company_expansions[expansion_id] = expansion
            logger.info(f"Created expansion plan for {target_region} with budget ${budget_usd:,.0f}")
            
            return expansion
            
        except Exception as e:
            logger.error(f"Failed to create expansion plan: {e}")
            raise
    
    def update_expansion_stage(self,
                             expansion_id: str,
                             new_stage: ExpansionStage,
                             update_data: Dict[str, Any],
                             updated_by: str) -> bool:
        """Update the stage of a company expansion."""
        try:
            if expansion_id not in self.company_expansions:
                return False
            
            expansion = self.company_expansions[expansion_id]
            
            # Check permissions
            user = self.users.get(updated_by)
            if not user or not self._has_permission(user, 'manage_expansions'):
                return False
            
            expansion.expansion_stage = new_stage
            expansion.last_updated = datetime.now()
            
            # Update stage-specific data
            if new_stage == ExpansionStage.MARKET_RESEARCH:
                expansion.market_research.update(update_data.get('market_research', {}))
            elif new_stage == ExpansionStage.LEGAL_SETUP:
                expansion.legal_requirements.update(update_data.get('legal_requirements', {}))
            elif new_stage == ExpansionStage.HIRING:
                expansion.target_roles = update_data.get('target_roles', [])
                expansion.hiring_timeline = update_data.get('hiring_timeline', {})
            
            logger.info(f"Updated expansion {expansion_id} to stage {new_stage.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update expansion stage: {e}")
            return False
    
    def get_company_expansions(self, 
                             company_id: str,
                             user_id: str) -> List[CompanyExpansion]:
        """Get all expansion plans for a company."""
        try:
            user = self.users.get(user_id)
            if not user or user.company_id != company_id:
                if not self._has_permission(user, 'view_all_expansions'):
                    return []
            
            expansions = [
                exp for exp in self.company_expansions.values()
                if exp.company_id == company_id and exp.is_active
            ]
            
            return sorted(expansions, key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to get company expansions: {e}")
            return []
    
    # Talent Market Analytics
    def generate_talent_market_analytics(self,
                                       company_id: str,
                                       region: str,
                                       requested_by: str,
                                       analysis_period_days: int = 90) -> TalentMarketAnalytics:
        """Generate comprehensive talent market analytics."""
        try:
            user = self.users.get(requested_by)
            if not user or not self._has_permission(user, 'view_analytics'):
                raise PermissionError("User does not have permission to view analytics")
            
            analytics_id = str(uuid.uuid4())
            end_date = datetime.now()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            # Generate analytics data
            talent_availability = self._analyze_talent_availability(region, start_date, end_date)
            salary_benchmarks = self._analyze_salary_benchmarks(region, start_date, end_date)
            competition_analysis = self._analyze_competition(region, company_id, start_date, end_date)
            skill_demand = self._analyze_skill_demand(region, start_date, end_date)
            hiring_velocity = self._analyze_hiring_velocity(region, start_date, end_date)
            retention_rates = self._analyze_retention_rates(region, start_date, end_date)
            cost_analysis = self._analyze_hiring_costs(region, start_date, end_date)
            recommendations = self._generate_market_recommendations(region, {
                'talent_availability': talent_availability,
                'competition': competition_analysis,
                'costs': cost_analysis
            })
            
            analytics = TalentMarketAnalytics(
                analytics_id=analytics_id,
                company_id=company_id,
                region=region,
                analysis_period=(start_date, end_date),
                talent_availability=talent_availability,
                salary_benchmarks=salary_benchmarks,
                competition_analysis=competition_analysis,
                skill_demand=skill_demand,
                hiring_velocity=hiring_velocity,
                retention_rates=retention_rates,
                cost_analysis=cost_analysis,
                recommendations=recommendations,
                generated_at=datetime.now()
            )
            
            self.talent_analytics[analytics_id] = analytics
            logger.info(f"Generated talent market analytics for {region}")
            
            return analytics
            
        except Exception as e:
            logger.error(f"Failed to generate talent market analytics: {e}")
            raise
    
    def get_regional_hiring_insights(self,
                                   company_id: str,
                                   regions: List[str],
                                   user_id: str) -> Dict[str, Any]:
        """Get hiring insights across multiple regions."""
        try:
            user = self.users.get(user_id)
            if not user or not self._has_permission(user, 'view_analytics'):
                return {}
            
            insights = {}
            
            for region in regions:
                # Get recent analytics for this region
                region_analytics = [
                    analytics for analytics in self.talent_analytics.values()
                    if (analytics.company_id == company_id and 
                        analytics.region == region and
                        (datetime.now() - analytics.generated_at).days <= 30)
                ]
                
                if region_analytics:
                    latest_analytics = max(region_analytics, key=lambda x: x.generated_at)
                    
                    insights[region] = {
                        'talent_availability': latest_analytics.talent_availability.get('availability_score', 0.5),
                        'avg_salary_usd': latest_analytics.salary_benchmarks.get('median_salary', 0),
                        'competition_level': latest_analytics.competition_analysis.get('competition_score', 0.5),
                        'hiring_velocity_days': latest_analytics.hiring_velocity.get('avg_time_to_hire', 45),
                        'cost_per_hire_usd': latest_analytics.cost_analysis.get('avg_cost_per_hire', 15000),
                        'retention_rate': latest_analytics.retention_rates.get('twelve_month_retention', 0.85),
                        'top_skills_demand': latest_analytics.skill_demand.get('top_skills', []),
                        'recommendations': latest_analytics.recommendations[:3],
                        'last_updated': latest_analytics.generated_at
                    }
                else:
                    # Generate basic insights if no recent analytics
                    insights[region] = self._generate_basic_regional_insights(region)
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get regional hiring insights: {e}")
            return {}
    
    # Permission and utility methods
    def _has_permission(self, user: User, permission: str) -> bool:
        """Check if user has a specific permission."""
        if not user:
            return False
        
        user_permissions = self.permissions.get(user.role, [])
        return permission in user_permissions
    
    def _filter_opportunities(self, 
                            opportunities: List[SharedOpportunity],
                            filters: Dict[str, Any]) -> List[SharedOpportunity]:
        """Filter opportunities based on criteria."""
        filtered = opportunities
        
        if 'region' in filters:
            filtered = [opp for opp in filtered if opp.region == filters['region']]
        
        if 'country' in filters:
            filtered = [opp for opp in filtered if opp.country == filters['country']]
        
        if 'visa_sponsorship' in filters:
            filtered = [opp for opp in filtered if opp.visa_sponsorship == filters['visa_sponsorship']]
        
        if 'remote_option' in filters:
            filtered = [opp for opp in filtered if opp.remote_option == filters['remote_option']]
        
        if 'status' in filters:
            filtered = [opp for opp in filtered if opp.status == filters['status']]
        
        if 'salary_min' in filters:
            # Basic salary filtering (would need more sophisticated parsing)
            salary_min = filters['salary_min']
            filtered = [opp for opp in filtered if self._extract_min_salary(opp.salary_range) >= salary_min]
        
        return filtered
    
    def _extract_min_salary(self, salary_range: str) -> float:
        """Extract minimum salary from salary range string."""
        import re
        numbers = re.findall(r'\d+', salary_range.replace(',', ''))
        if numbers:
            return float(numbers[0])
        return 0
    
    def _notify_team_members(self, member_ids: List[str], message: str) -> None:
        """Send notifications to team members."""
        for member_id in member_ids:
            if member_id in self.users:
                user = self.users[member_id]
                if user.notification_preferences.get('new_opportunities', True):
                    self.notification_queue.append({
                        'user_id': member_id,
                        'message': message,
                        'timestamp': datetime.now(),
                        'type': 'opportunity_shared'
                    })
    
    # Analytics helper methods
    def _analyze_talent_availability(self, region: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze talent availability in region."""
        # Mock implementation - would integrate with job market data
        return {
            'availability_score': 0.7,  # 0-1 scale
            'active_candidates': 15000,
            'passive_candidates': 45000,
            'skill_shortage_areas': ['AI/ML', 'Cybersecurity', 'DevOps'],
            'skill_surplus_areas': ['Web Development', 'Project Management'],
            'seasonal_trends': {
                'q1': 0.8, 'q2': 0.9, 'q3': 0.6, 'q4': 0.7
            }
        }
    
    def _analyze_salary_benchmarks(self, region: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze salary benchmarks for region."""
        # Regional salary estimates
        regional_medians = {
            'North America': 120000,
            'Western Europe': 85000,
            'East Asia': 75000,
            'Southeast Asia': 55000,
            'Australia/Oceania': 95000
        }
        
        median_salary = regional_medians.get(region, 70000)
        
        return {
            'median_salary': median_salary,
            'percentile_25': median_salary * 0.75,
            'percentile_75': median_salary * 1.35,
            'growth_rate_annual': 0.08,
            'top_paying_roles': ['AI Engineer', 'Security Architect', 'Principal Engineer'],
            'salary_by_experience': {
                'junior': median_salary * 0.6,
                'mid': median_salary,
                'senior': median_salary * 1.5,
                'principal': median_salary * 2.2
            }
        }
    
    def _analyze_competition(self, region: str, company_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze hiring competition in region."""
        return {
            'competition_score': 0.6,  # 0-1 scale (higher = more competitive)
            'active_employers': 250,
            'top_competitors': ['TechCorp', 'GlobalSoft', 'InnovateLab'],
            'average_interview_processes': 4.2,
            'offer_acceptance_rate': 0.73,
            'time_to_decision_days': 12,
            'signing_bonus_prevalence': 0.45
        }
    
    def _analyze_skill_demand(self, region: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze skill demand in region."""
        return {
            'top_skills': [
                {'skill': 'Python', 'demand_score': 0.9, 'growth_rate': 0.15},
                {'skill': 'React', 'demand_score': 0.8, 'growth_rate': 0.12},
                {'skill': 'AWS', 'demand_score': 0.85, 'growth_rate': 0.18},
                {'skill': 'Machine Learning', 'demand_score': 0.75, 'growth_rate': 0.25}
            ],
            'emerging_skills': ['GPT Integration', 'Rust', 'Edge Computing'],
            'declining_skills': ['jQuery', 'PHP', 'Legacy Java'],
            'skill_gaps': ['AI Ethics', 'Quantum Computing', 'Blockchain']
        }
    
    def _analyze_hiring_velocity(self, region: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze hiring velocity in region."""
        return {
            'avg_time_to_hire': 35,  # days
            'fastest_roles': ['Frontend Developer', 'Product Manager'],
            'slowest_roles': ['Senior Architect', 'Security Engineer'],
            'interview_stages_avg': 3.5,
            'offer_response_time_days': 5,
            'background_check_days': 7
        }
    
    def _analyze_retention_rates(self, region: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze employee retention rates in region."""
        return {
            'twelve_month_retention': 0.87,
            'six_month_retention': 0.93,
            'retention_by_role': {
                'Engineer': 0.89,
                'Product Manager': 0.84,
                'Data Scientist': 0.91,
                'Designer': 0.82
            },
            'top_retention_factors': ['Remote Flexibility', 'Career Growth', 'Compensation'],
            'churn_risk_indicators': ['Low engagement', 'No promotion in 2 years', 'Below market salary']
        }
    
    def _analyze_hiring_costs(self, region: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Analyze hiring costs in region."""
        # Regional cost estimates
        regional_costs = {
            'North America': 18000,
            'Western Europe': 15000,
            'East Asia': 12000,
            'Southeast Asia': 8000,
            'Australia/Oceania': 16000
        }
        
        base_cost = regional_costs.get(region, 12000)
        
        return {
            'avg_cost_per_hire': base_cost,
            'cost_breakdown': {
                'recruitment_agencies': base_cost * 0.4,
                'internal_recruiting': base_cost * 0.3,
                'advertising': base_cost * 0.1,
                'interviewing_time': base_cost * 0.15,
                'onboarding': base_cost * 0.05
            },
            'cost_by_role_level': {
                'junior': base_cost * 0.6,
                'mid': base_cost,
                'senior': base_cost * 1.5,
                'executive': base_cost * 3.0
            }
        }
    
    def _generate_market_recommendations(self, region: str, analytics_data: Dict[str, Any]) -> List[str]:
        """Generate market-specific recommendations."""
        recommendations = []
        
        talent_score = analytics_data['talent_availability']['availability_score']
        competition_score = analytics_data['competition']['competition_score']
        
        if talent_score < 0.5:
            recommendations.append("Consider expanding search to nearby regions due to limited talent pool")
        
        if competition_score > 0.7:
            recommendations.append("Increase compensation packages to remain competitive in this market")
        
        recommendations.extend([
            f"Focus recruiting on high-demand skills: {', '.join(analytics_data.get('skill_demand', {}).get('top_skills', [])[:3])}",
            "Implement remote work options to access broader talent pool",
            "Develop strong employer branding to attract top talent"
        ])
        
        return recommendations
    
    def _generate_basic_regional_insights(self, region: str) -> Dict[str, Any]:
        """Generate basic insights when detailed analytics unavailable."""
        return {
            'talent_availability': 0.5,
            'avg_salary_usd': 80000,
            'competition_level': 0.5,
            'hiring_velocity_days': 45,
            'cost_per_hire_usd': 15000,
            'retention_rate': 0.85,
            'top_skills_demand': ['Software Development', 'Data Analysis', 'Project Management'],
            'recommendations': ['Conduct detailed market research', 'Establish local recruiting presence'],
            'last_updated': datetime.now()
        }


# Global instance for use across the application
enterprise_service = EnterpriseMultiUserService()
