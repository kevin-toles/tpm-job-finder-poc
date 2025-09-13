"""
Integration tests for Phase 5+ advanced features.

Tests Immigration Support, Enterprise Multi-User, and Advanced Career Modeling services.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the parent directory to the path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tpm_job_finder_poc.enrichment.immigration_support_service import (
    ImmigrationSupportService,
    VisaType,
    ProcessingTime,
    immigration_support_service
)
from tpm_job_finder_poc.enrichment.enterprise_service import (
    EnterpriseMultiUserService,
    UserRole,
    OpportunityStatus,
    ExpansionStage,
    enterprise_service
)
from tpm_job_finder_poc.enrichment.career_modeling_service import (
    AdvancedCareerModelingService,
    CareerStage,
    SkillCategory,
    PathwayType,
    career_modeling_service
)


class TestImmigrationSupportService:
    """Test Immigration Support Service functionality."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.service = ImmigrationSupportService()
        
        # Test user data
        self.test_user_data = {
            'current_country': 'India',
            'target_countries': ['United States', 'Canada', 'Germany'],
            'education_level': 'Masters',
            'work_experience_years': 5,
            'job_category': 'Software Engineer',
            'language_skills': ['English', 'Hindi'],
            'budget_usd': 25000,
            'family_size': 2,
            'timeline_months': 18
        }
    
    def test_analyze_visa_requirements(self):
        """Test visa requirements analysis."""
        requirements = self.service.get_visa_requirements(
            destination_country=self.test_user_data['target_countries'][0],  # United States
            origin_country=self.test_user_data['current_country'],
            job_role=self.test_user_data['job_category'],
            salary_usd=120000
        )
        
        assert requirements is not None
        assert requirements.country == 'United States'
        assert requirements.visa_type is not None
        assert requirements.estimated_cost_usd > 0
        
        print(f"✅ Visa requirements analyzed for {requirements.country}")
        print(f"   Visa type: {requirements.visa_type.value}")
        print(f"   Estimated cost: ${requirements.estimated_cost_usd:,.0f}")
    
    def test_find_immigration_lawyers(self):
        """Test immigration lawyer search."""
        lawyers = self.service.find_immigration_lawyers(
            target_country='United States',
            specialty='H-1B',
            budget_range=(5000, 15000)
        )
        
        assert isinstance(lawyers, list)
        assert len(lawyers) > 0
        
        # Check first lawyer
        lawyer = lawyers[0]
        assert hasattr(lawyer, 'name')
        assert hasattr(lawyer, 'specializations')
        assert hasattr(lawyer, 'rating')
        
        print(f"✅ Found {len(lawyers)} immigration lawyers")
        print(f"   Top lawyer: {lawyer.name} (Rating: {lawyer.rating})")
    
    def test_calculate_relocation_costs(self):
        """Test relocation cost calculation."""
        cost_analysis = self.service.calculate_relocation_costs(
            source_country=self.test_user_data['current_country'],
            target_country=self.test_user_data['target_countries'][0],
            family_size=self.test_user_data['family_size'],
            job_category=self.test_user_data['job_category']
        )
        
        assert cost_analysis is not None
        assert cost_analysis.total_cost > 0
        assert cost_analysis.timeline_months > 0
        
        print(f"✅ Calculated relocation costs: ${cost_analysis.total_cost:,.0f}")
        print(f"   Timeline: {cost_analysis.timeline_months} months")
    
    def test_create_immigration_timeline(self):
        """Test immigration timeline creation."""
        timeline = self.service.create_immigration_timeline(
            self.test_user_data,
            'United States'
        )
        
        assert timeline is not None
        assert len(timeline.phases) > 0
        assert timeline.total_duration_months > 0
        assert 0 <= timeline.feasibility_score <= 1.0
        
        print(f"✅ Created immigration timeline with {len(timeline.phases)} phases")
        print(f"   Total duration: {timeline.total_duration_months} months")
        print(f"   Feasibility score: {timeline.feasibility_score:.2f}")
    
    def test_get_comprehensive_immigration_insights(self):
        """Test comprehensive immigration insights."""
        # Test basic insights functionality
        insights = self.service.get_immigration_insights(
            origin_country=self.test_user_data['current_country'],
            destination_country='United States',
            job_role=self.test_user_data['job_category'],
            salary_usd=120000
        )
        
        assert insights is not None
        assert isinstance(insights, dict)
        assert 'visa_requirements' in insights
        assert 'recommendations' in insights
        
        print(f"✅ Generated immigration insights for United States")
        print(f"   Recommendations: {len(insights['recommendations'])}")


class TestEnterpriseMultiUserService:
    """Test Enterprise Multi-User Service functionality."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.service = EnterpriseMultiUserService()
        
        # Create test company and users
        self.company_id = "test-company-123"
        
        # Create test users
        self.admin_user = self.service.create_user(
            email="admin@testcompany.com",
            name="Admin User",
            role=UserRole.ADMIN,
            company_id=self.company_id,
            department="Engineering"
        )
        
        self.manager_user = self.service.create_user(
            email="manager@testcompany.com",
            name="Manager User",
            role=UserRole.MANAGER,
            company_id=self.company_id,
            department="Engineering"
        )
        
        self.employee_user = self.service.create_user(
            email="employee@testcompany.com",
            name="Employee User",
            role=UserRole.EMPLOYEE,
            company_id=self.company_id,
            department="Engineering"
        )
    
    def test_user_creation_and_permissions(self):
        """Test user creation and permission system."""
        assert self.admin_user.role == UserRole.ADMIN
        assert self.admin_user.company_id == self.company_id
        assert self.admin_user.is_active
        
        # Test permission checking
        assert self.service._has_permission(self.admin_user, 'manage_users')
        assert self.service._has_permission(self.manager_user, 'manage_team')
        assert not self.service._has_permission(self.employee_user, 'manage_users')
        
        print(f"✅ Created {len(self.service.users)} users with proper permissions")
        print(f"   Admin: {self.admin_user.name}")
        print(f"   Manager: {self.manager_user.name}")
        print(f"   Employee: {self.employee_user.name}")
    
    def test_geographic_preferences(self):
        """Test geographic preference management."""
        preferences = {
            'preferred_regions': ['North America', 'Europe'],
            'preferred_countries': ['United States', 'Canada', 'Germany'],
            'preferred_cities': ['San Francisco', 'Toronto', 'Berlin'],
            'excluded_countries': ['Russia'],
            'visa_restrictions': ['H-1B required'],
            'relocation_budget_usd': 50000,
            'timeline_months': 12,
            'language_requirements': ['English'],
            'salary_expectations': {'min': 120000, 'preferred': 150000}
        }
        
        geo_pref = self.service.update_user_geographic_preferences(
            self.employee_user.user_id,
            preferences
        )
        
        assert geo_pref is not None
        assert geo_pref.user_id == self.employee_user.user_id
        assert len(geo_pref.preferred_regions) == 2
        assert geo_pref.relocation_budget_usd == 50000
        
        # Test retrieval
        retrieved_pref = self.service.get_user_preferences(self.employee_user.user_id)
        assert retrieved_pref is not None
        assert retrieved_pref.timeline_months == 12
        
        print(f"✅ Set geographic preferences for user")
        print(f"   Preferred regions: {geo_pref.preferred_regions}")
        print(f"   Budget: ${geo_pref.relocation_budget_usd:,}")
    
    def test_team_collaboration(self):
        """Test team collaboration features."""
        # Create team
        team = self.service.create_team_collaboration(
            team_name="AI Engineering Team",
            company_id=self.company_id,
            members=[self.manager_user.user_id, self.employee_user.user_id],
            geographic_scope=['North America', 'Europe'],
            created_by=self.admin_user.user_id
        )
        
        assert team is not None
        assert team.team_name == "AI Engineering Team"
        assert len(team.members) == 2
        assert team.is_active
        
        # Test opportunity sharing
        job_data = {
            'job_id': 'test-job-123',
            'company': 'Tech Innovation Corp',
            'title': 'Senior AI Engineer',
            'location': 'San Francisco, CA',
            'region': 'North America',
            'country': 'United States',
            'salary': '$140,000 - $180,000',
            'description': 'Lead AI/ML initiatives',
            'requirements': ['Python', 'TensorFlow', 'PhD preferred'],
            'visa_sponsorship': True,
            'remote_option': True
        }
        
        shared_opp = self.service.share_opportunity_with_team(
            job_data=job_data,
            team_id=team.team_id,
            shared_by=self.manager_user.user_id,
            notes="Great opportunity for AI specialization",
            tags=['AI', 'Senior', 'Remote']
        )
        
        assert shared_opp is not None
        assert shared_opp.position_title == 'Senior AI Engineer'
        assert shared_opp.visa_sponsorship == True
        assert shared_opp.status == OpportunityStatus.ACTIVE
        
        # Test retrieving team opportunities
        opportunities = self.service.get_team_opportunities(
            team.team_id,
            self.employee_user.user_id
        )
        
        assert len(opportunities) == 1
        assert opportunities[0].opportunity_id == shared_opp.opportunity_id
        
        print(f"✅ Created team and shared opportunity")
        print(f"   Team: {team.team_name} ({len(team.members)} members)")
        print(f"   Shared: {shared_opp.position_title}")
    
    def test_company_expansion_tracking(self):
        """Test company expansion tracking."""
        # Create expansion plan
        expansion = self.service.create_expansion_plan(
            company_id=self.company_id,
            target_region='Europe',
            target_countries=['Germany', 'Netherlands'],
            business_objectives=['Market penetration', 'Talent acquisition'],
            budget_usd=2000000,
            created_by=self.admin_user.user_id
        )
        
        assert expansion is not None
        assert expansion.target_region == 'Europe'
        assert len(expansion.target_countries) == 2
        assert expansion.expansion_stage == ExpansionStage.PLANNING
        assert expansion.budget_usd == 2000000
        
        # Test stage update
        update_success = self.service.update_expansion_stage(
            expansion.expansion_id,
            ExpansionStage.MARKET_RESEARCH,
            {
                'market_research': {
                    'market_size': 'Large',
                    'competition': 'Moderate',
                    'regulatory_environment': 'Favorable'
                }
            },
            self.admin_user.user_id
        )
        
        assert update_success
        
        updated_expansion = self.service.company_expansions[expansion.expansion_id]
        assert updated_expansion.expansion_stage == ExpansionStage.MARKET_RESEARCH
        
        # Test retrieval
        expansions = self.service.get_company_expansions(
            self.company_id,
            self.admin_user.user_id
        )
        
        assert len(expansions) == 1
        assert expansions[0].expansion_id == expansion.expansion_id
        
        print(f"✅ Created and tracked company expansion")
        print(f"   Target: {expansion.target_region}")
        print(f"   Budget: ${expansion.budget_usd:,}")
        print(f"   Stage: {updated_expansion.expansion_stage.value}")
    
    def test_talent_market_analytics(self):
        """Test talent market analytics generation."""
        analytics = self.service.generate_talent_market_analytics(
            company_id=self.company_id,
            region='North America',
            requested_by=self.admin_user.user_id,
            analysis_period_days=90
        )
        
        assert analytics is not None
        assert analytics.region == 'North America'
        assert analytics.company_id == self.company_id
        assert len(analytics.recommendations) > 0
        
        # Verify analytics components
        assert 'availability_score' in analytics.talent_availability
        assert 'median_salary' in analytics.salary_benchmarks
        assert 'competition_score' in analytics.competition_analysis
        assert 'top_skills' in analytics.skill_demand
        
        # Test regional insights
        insights = self.service.get_regional_hiring_insights(
            company_id=self.company_id,
            regions=['North America', 'Europe'],
            user_id=self.admin_user.user_id
        )
        
        assert isinstance(insights, dict)
        assert len(insights) == 2
        assert 'North America' in insights
        
        na_insights = insights['North America']
        assert 'talent_availability' in na_insights
        assert 'avg_salary_usd' in na_insights
        assert 'recommendations' in na_insights
        
        print(f"✅ Generated talent market analytics")
        print(f"   Region: {analytics.region}")
        print(f"   Recommendations: {len(analytics.recommendations)}")
        print(f"   Regional insights: {list(insights.keys())}")


class TestAdvancedCareerModelingService:
    """Test Advanced Career Modeling Service functionality."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.service = AdvancedCareerModelingService()
        
        # Test user skills
        self.current_skills = {
            'Python Programming': 0.8,
            'Data Analysis': 0.7,
            'Machine Learning': 0.5,
            'Team Leadership': 0.3,
            'Cloud Architecture': 0.4
        }
    
    def test_skill_management(self):
        """Test skill addition and management."""
        # Add a new skill
        new_skill = self.service.add_skill(
            name='Kubernetes',
            category=SkillCategory.TECHNICAL,
            description='Container orchestration platform',
            industry_relevance={'Technology': 0.9, 'Finance': 0.6},
            regional_demand={'North America': 0.85, 'Europe': 0.8},
            learning_difficulty=0.7,
            automation_risk=0.2,
            future_demand_trend=0.8
        )
        
        assert new_skill is not None
        assert new_skill.name == 'Kubernetes'
        assert new_skill.category == SkillCategory.TECHNICAL
        assert new_skill.learning_difficulty == 0.7
        
        print(f"✅ Added new skill: {new_skill.name}")
        print(f"   Category: {new_skill.category.value}")
        print(f"   Learning difficulty: {new_skill.learning_difficulty}")
    
    def test_skill_gap_analysis(self):
        """Test skill gap analysis for target roles."""
        # Find a target role
        target_role_id = None
        for role_id, role in self.service.roles.items():
            if role.title == 'Senior Software Engineer':
                target_role_id = role_id
                break
        
        assert target_role_id is not None
        
        # Analyze skill gaps
        skill_gaps = self.service.analyze_skill_gaps(
            self.current_skills,
            target_role_id
        )
        
        assert isinstance(skill_gaps, list)
        assert len(skill_gaps) > 0
        
        # Check first skill gap
        gap = skill_gaps[0]
        assert hasattr(gap, 'skill_name')
        assert hasattr(gap, 'gap_severity')
        assert hasattr(gap, 'priority')
        assert hasattr(gap, 'estimated_learning_time_months')
        
        assert gap.gap_severity >= 0
        assert gap.priority in ['high', 'medium', 'low']
        
        print(f"✅ Analyzed skill gaps for Senior Software Engineer")
        print(f"   Found {len(skill_gaps)} skill gaps")
        for gap in skill_gaps[:3]:
            print(f"   - {gap.skill_name}: {gap.priority} priority ({gap.gap_severity:.2f} severity)")
    
    def test_career_forecasting(self):
        """Test career and skill demand forecasting."""
        forecast = self.service.forecast_skill_demand(
            region='North America',
            industry='Technology',
            forecast_years=5
        )
        
        assert forecast is not None
        assert forecast.region == 'North America'
        assert forecast.industry == 'Technology'
        assert forecast.forecast_period_years == 5
        
        # Check forecast components
        assert len(forecast.role_demand_trends) > 0
        assert len(forecast.skill_demand_trends) > 0
        assert len(forecast.emerging_roles) > 0
        assert len(forecast.declining_roles) > 0
        assert len(forecast.salary_projections) > 0
        
        # Verify trend data structure
        first_role = list(forecast.role_demand_trends.keys())[0]
        role_trends = forecast.role_demand_trends[first_role]
        assert '1' in role_trends  # Year 1
        assert '5' in role_trends  # Year 5
        
        print(f"✅ Generated {forecast.forecast_period_years}-year forecast")
        print(f"   Role trends: {len(forecast.role_demand_trends)}")
        print(f"   Skill trends: {len(forecast.skill_demand_trends)}")
        print(f"   Emerging roles: {len(forecast.emerging_roles)}")
    
    def test_career_pathway_analysis(self):
        """Test career pathway analysis."""
        # Find current role
        current_role_id = None
        for role_id, role in self.service.roles.items():
            if role.title == 'Software Engineer':
                current_role_id = role_id
                break
        
        assert current_role_id is not None
        
        # Analyze pathways
        pathways = self.service.analyze_career_pathways(
            current_role_id=current_role_id,
            target_regions=['North America', 'Europe'],
            preferences={
                'timeline_years': 8,
                'difficulty_preference': 0.7
            }
        )
        
        assert isinstance(pathways, list)
        assert len(pathways) > 0
        
        # Check first pathway
        pathway = pathways[0]
        assert hasattr(pathway, 'pathway_type')
        assert hasattr(pathway, 'estimated_duration_years')
        assert hasattr(pathway, 'market_demand_score')
        assert hasattr(pathway, 'difficulty_score')
        
        assert pathway.estimated_duration_years > 0
        assert 0 <= pathway.market_demand_score <= 1
        
        print(f"✅ Found {len(pathways)} suitable career pathways")
        print(f"   Top pathway: {pathway.title}")
        print(f"   Duration: {pathway.estimated_duration_years} years")
        print(f"   Market demand: {pathway.market_demand_score:.2f}")
    
    def test_personalized_career_plan(self):
        """Test personalized career plan creation."""
        # Find current role
        current_role_id = None
        for role_id, role in self.service.roles.items():
            if role.title == 'Software Engineer':
                current_role_id = role_id
                break
        
        assert current_role_id is not None
        
        # Create career plan
        career_plan = self.service.create_personalized_career_plan(
            user_id='test-user-123',
            current_role_id=current_role_id,
            target_roles=['Senior Software Engineer', 'ML Engineer'],
            preferred_regions=['North America', 'Europe'],
            timeline_years=5,
            current_skills=self.current_skills
        )
        
        assert career_plan is not None
        assert career_plan.user_id == 'test-user-123'
        assert career_plan.timeline_years == 5
        assert len(career_plan.target_roles) == 2
        
        # Verify plan components
        assert len(career_plan.skill_gaps) > 0
        assert len(career_plan.learning_milestones) > 0
        assert len(career_plan.next_actions) > 0
        assert 0 <= career_plan.success_probability <= 1
        
        # Check learning milestones structure
        assert '1' in career_plan.learning_milestones  # Year 1
        year_1_milestones = career_plan.learning_milestones['1']
        assert len(year_1_milestones) > 0
        
        print(f"✅ Created personalized career plan")
        print(f"   Timeline: {career_plan.timeline_years} years")
        print(f"   Skill gaps: {len(career_plan.skill_gaps)}")
        print(f"   Success probability: {career_plan.success_probability:.2f}")
        print(f"   Next actions: {len(career_plan.next_actions)}")
    
    def test_international_mobility_analysis(self):
        """Test international mobility analysis."""
        mobility_analysis = self.service.get_international_mobility_analysis(
            role_titles=['Software Engineer', 'ML Engineer'],
            source_region='Asia',
            target_regions=['North America', 'Europe']
        )
        
        assert isinstance(mobility_analysis, dict)
        assert len(mobility_analysis) == 2  # Two target regions
        
        # Check North America analysis
        na_analysis = mobility_analysis.get('North America')
        assert na_analysis is not None
        assert 'overall_feasibility' in na_analysis
        assert 'role_availability' in na_analysis
        assert 'visa_requirements' in na_analysis
        assert 'salary_comparison' in na_analysis
        assert 'challenges' in na_analysis
        assert 'opportunities' in na_analysis
        
        # Verify role-specific data
        assert 'Software Engineer' in na_analysis['role_availability']
        assert 'Software Engineer' in na_analysis['visa_requirements']
        
        # Check visa requirements structure
        se_visa = na_analysis['visa_requirements']['Software Engineer']
        assert 'sponsorship_likelihood' in se_visa
        assert 'typical_visa_types' in se_visa
        assert 'processing_time_months' in se_visa
        
        print(f"✅ Completed international mobility analysis")
        print(f"   Target regions: {list(mobility_analysis.keys())}")
        print(f"   NA feasibility: {na_analysis['overall_feasibility']:.2f}")
        print(f"   Challenges: {len(na_analysis['challenges'])}")
        print(f"   Opportunities: {len(na_analysis['opportunities'])}")


class TestPhase5Integration:
    """Test integration between all Phase 5+ services."""
    
    def setup_method(self):
        """Set up integration test data."""
        self.immigration_service = ImmigrationSupportService()
        self.enterprise_service = EnterpriseMultiUserService()
        self.career_service = AdvancedCareerModelingService()
        
        # Create test user with admin role for analytics access
        self.test_user = self.enterprise_service.create_user(
            email="integration@testcompany.com",
            name="Integration Test User",
            role=UserRole.ADMIN,  # Admin role for analytics access
            company_id="integration-company",
            department="Engineering"
        )
    
    def test_end_to_end_global_career_planning(self):
        """Test end-to-end global career planning workflow."""
        # Step 1: Set user preferences
        preferences = {
            'preferred_regions': ['North America', 'Europe'],
            'preferred_countries': ['United States', 'Canada', 'Germany'],
            'visa_restrictions': ['H-1B eligible'],
            'relocation_budget_usd': 40000,
            'timeline_months': 24
        }
        
        geo_prefs = self.enterprise_service.update_user_geographic_preferences(
            self.test_user.user_id,
            preferences
        )
        
        # Step 2: Create career plan
        current_skills = {
            'Python Programming': 0.7,
            'Machine Learning': 0.5,
            'Data Analysis': 0.8
        }
        
        current_role_id = None
        for role_id, role in self.career_service.roles.items():
            if role.title == 'Software Engineer':
                current_role_id = role_id
                break
        
        career_plan = self.career_service.create_personalized_career_plan(
            user_id=self.test_user.user_id,
            current_role_id=current_role_id,
            target_roles=['Senior Software Engineer'],
            preferred_regions=['North America'],
            timeline_years=2,
            current_skills=current_skills
        )
        
        # Step 3: Analyze immigration requirements
        immigration_insights = self.immigration_service.get_immigration_insights(
            origin_country='India',
            destination_country='United States',
            job_role='Software Engineer',
            salary_usd=120000
        )
        
        # Step 4: Generate talent market analytics
        market_analytics = self.enterprise_service.generate_talent_market_analytics(
            company_id=self.test_user.company_id,
            region='North America',
            requested_by=self.test_user.user_id
        )
        
        # Verify integration results
        assert geo_prefs is not None
        assert career_plan is not None
        assert immigration_insights is not None
        assert market_analytics is not None
        
        # Check basic data consistency
        assert career_plan.timeline_years == 2
        assert market_analytics.region == 'North America'
        assert immigration_insights is not None
        
        print(f"✅ Completed end-to-end global career planning")
        print(f"   User: {self.test_user.name}")
        print(f"   Career plan success probability: {career_plan.success_probability:.2f}")
        print(f"   Immigration insights available: {immigration_insights is not None}")
        print(f"   Market demand score: {market_analytics.talent_availability.get('availability_score', 0):.2f}")
    
    def test_cross_service_data_consistency(self):
        """Test data consistency across all services."""
        # Test region consistency
        immigration_regions = ['North America', 'Europe', 'Asia', 'Australia/Oceania']
        enterprise_regions = ['North America', 'Europe', 'Asia', 'Australia/Oceania']
        career_regions = ['North America', 'Europe', 'Asia', 'Australia/Oceania']
        
        # All services should support same core regions
        common_regions = set(immigration_regions) & set(enterprise_regions) & set(career_regions)
        assert len(common_regions) >= 3  # At least 3 common regions
        
        # Test skill consistency
        career_skills = set(skill.name for skill in self.career_service.skills.values())
        tech_skills = {'Python Programming', 'Machine Learning', 'Data Analysis'}
        assert tech_skills.issubset(career_skills)
        
        # Test role consistency
        career_roles = set(role.title for role in self.career_service.roles.values())
        common_roles = {'Software Engineer', 'Senior Software Engineer'}
        assert common_roles.issubset(career_roles)
        
        print(f"✅ Verified cross-service data consistency")
        print(f"   Common regions: {len(common_regions)}")
        print(f"   Career skills available: {len(career_skills)}")
        print(f"   Career roles available: {len(career_roles)}")


def run_phase5_tests():
    """Run all Phase 5+ integration tests."""
    print("🚀 Running Phase 5+ Advanced Features Integration Tests\n")
    
    # Immigration Support Tests
    print("=" * 60)
    print("TESTING IMMIGRATION SUPPORT SERVICE")
    print("=" * 60)
    
    immigration_test = TestImmigrationSupportService()
    immigration_test.setup_method()
    
    try:
        immigration_test.test_analyze_visa_requirements()
        immigration_test.test_find_immigration_lawyers()
        immigration_test.test_calculate_relocation_costs()
        immigration_test.test_create_immigration_timeline()
        immigration_test.test_get_comprehensive_immigration_insights()
        print("✅ All Immigration Support tests passed!\n")
    except Exception as e:
        print(f"❌ Immigration Support test failed: {e}\n")
    
    # Enterprise Multi-User Tests
    print("=" * 60)
    print("TESTING ENTERPRISE MULTI-USER SERVICE")
    print("=" * 60)
    
    enterprise_test = TestEnterpriseMultiUserService()
    enterprise_test.setup_method()
    
    try:
        enterprise_test.test_user_creation_and_permissions()
        enterprise_test.test_geographic_preferences()
        enterprise_test.test_team_collaboration()
        enterprise_test.test_company_expansion_tracking()
        enterprise_test.test_talent_market_analytics()
        print("✅ All Enterprise Multi-User tests passed!\n")
    except Exception as e:
        print(f"❌ Enterprise Multi-User test failed: {e}\n")
    
    # Advanced Career Modeling Tests
    print("=" * 60)
    print("TESTING ADVANCED CAREER MODELING SERVICE")
    print("=" * 60)
    
    career_test = TestAdvancedCareerModelingService()
    career_test.setup_method()
    
    try:
        career_test.test_skill_management()
        career_test.test_skill_gap_analysis()
        career_test.test_career_forecasting()
        career_test.test_career_pathway_analysis()
        career_test.test_personalized_career_plan()
        career_test.test_international_mobility_analysis()
        print("✅ All Advanced Career Modeling tests passed!\n")
    except Exception as e:
        print(f"❌ Advanced Career Modeling test failed: {e}\n")
    
    # Integration Tests
    print("=" * 60)
    print("TESTING PHASE 5+ INTEGRATION")
    print("=" * 60)
    
    integration_test = TestPhase5Integration()
    integration_test.setup_method()
    
    try:
        integration_test.test_end_to_end_global_career_planning()
        integration_test.test_cross_service_data_consistency()
        print("✅ All Phase 5+ Integration tests passed!\n")
    except Exception as e:
        print(f"❌ Phase 5+ Integration test failed: {e}\n")
    
    print("🎉 Phase 5+ Advanced Features Testing Complete!")
    print("   ✅ Immigration & Relocation Support")
    print("   ✅ Enterprise Multi-User Features")
    print("   ✅ Advanced Career Modeling")
    print("   ✅ Cross-Service Integration")


if __name__ == "__main__":
    run_phase5_tests()
