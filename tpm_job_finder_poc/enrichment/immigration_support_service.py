"""
Immigration Support Service for Global Job Intelligence.

This module provides comprehensive immigration and relocation support
including lawyer network integration, visa requirement analysis, and
relocation cost calculations for international job seekers.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)


class VisaType(Enum):
    """Types of work visas."""
    WORK_PERMIT = "work_permit"
    SKILLED_WORKER = "skilled_worker"
    TEMPORARY_WORKER = "temporary_worker"
    INVESTOR = "investor"
    INTRA_COMPANY_TRANSFER = "intra_company_transfer"
    FREELANCER = "freelancer"
    ENTREPRENEUR = "entrepreneur"
    STUDENT_TO_WORK = "student_to_work"


class ProcessingTime(Enum):
    """Visa processing time categories."""
    EXPEDITED = "expedited"  # 1-4 weeks
    STANDARD = "standard"    # 1-3 months
    EXTENDED = "extended"    # 3-6 months
    COMPLEX = "complex"      # 6+ months


@dataclass
class VisaRequirement:
    """Represents visa requirements for a specific country and role."""
    country: str
    country_code: str
    visa_type: VisaType
    required: bool
    processing_time: ProcessingTime
    estimated_cost_usd: float
    required_documents: List[str]
    qualification_requirements: List[str]
    sponsorship_required: bool
    salary_threshold_usd: Optional[float]
    language_requirements: List[str]
    success_rate: float
    additional_notes: List[str]


@dataclass
class ImmigrationLawyer:
    """Represents an immigration lawyer in the network."""
    name: str
    firm: str
    country: str
    city: str
    specializations: List[str]
    languages: List[str]
    rating: float
    years_experience: int
    hourly_rate_usd: float
    consultation_fee_usd: float
    contact_email: str
    contact_phone: str
    website: str
    success_rate: float
    client_reviews: int
    verified: bool


@dataclass
class RelocationCost:
    """Represents relocation cost breakdown."""
    from_country: str
    to_country: str
    from_city: str
    to_city: str
    visa_fees: float
    moving_costs: float
    temporary_accommodation: float
    permanent_housing_deposit: float
    cost_of_living_difference: float
    transportation: float
    insurance: float
    miscellaneous: float
    total_cost_usd: float
    monthly_living_cost_difference: float
    break_even_months: int


@dataclass
class ImmigrationTimeline:
    """Represents immigration process timeline."""
    phases: List[Dict[str, Any]]
    total_duration_months: int
    critical_milestones: List[str]
    potential_delays: List[str]
    recommended_start_date: datetime


class ImmigrationSupportService:
    """Comprehensive immigration and relocation support service."""
    
    def __init__(self):
        """Initialize the immigration support service."""
        self.lawyer_network = []
        self.visa_database = {}
        self.cost_database = {}
        self.timeline_cache = {}
        self.exchange_rates = {}
        
        # Initialize lawyer network
        self._initialize_lawyer_network()
        
        # Initialize visa requirements database
        self._initialize_visa_database()
        
        # Initialize cost of living data
        self._initialize_cost_database()
        
        # Supported countries for immigration services
        self.supported_countries = [
            'US', 'CA', 'GB', 'DE', 'FR', 'NL', 'CH', 'SE', 'NO', 'DK',
            'AU', 'NZ', 'SG', 'HK', 'JP', 'KR', 'AE', 'IE', 'ES', 'IT'
        ]
        
        # Visa processing complexity by country
        self.processing_complexity = {
            'US': 'complex',
            'GB': 'extended',
            'CA': 'standard',
            'AU': 'standard',
            'DE': 'standard',
            'SG': 'expedited',
            'NL': 'standard',
            'CH': 'extended',
            'NZ': 'standard',
            'SE': 'standard'
        }
    
    def get_visa_requirements(self, 
                            destination_country: str,
                            origin_country: str,
                            job_role: str,
                            salary_usd: float) -> VisaRequirement:
        """Get visa requirements for working in a destination country."""
        try:
            country_code = destination_country.upper()
            
            # Check if visa is required
            visa_required = self._check_visa_requirement(origin_country, destination_country)
            
            if not visa_required:
                return self._create_no_visa_requirement(destination_country)
            
            # Determine appropriate visa type
            visa_type = self._determine_visa_type(job_role, salary_usd, destination_country)
            
            # Get processing time
            processing_time = self._get_processing_time(destination_country, visa_type)
            
            # Calculate costs
            estimated_cost = self._calculate_visa_costs(destination_country, visa_type)
            
            # Get required documents
            required_docs = self._get_required_documents(destination_country, visa_type)
            
            # Get qualification requirements
            qualifications = self._get_qualification_requirements(destination_country, visa_type, job_role)
            
            # Check sponsorship requirement
            sponsorship_required = self._check_sponsorship_requirement(destination_country, visa_type)
            
            # Get salary threshold
            salary_threshold = self._get_salary_threshold(destination_country, visa_type)
            
            # Get language requirements
            language_reqs = self._get_language_requirements(destination_country)
            
            # Calculate success rate
            success_rate = self._calculate_success_rate(destination_country, visa_type, salary_usd)
            
            # Get additional notes
            additional_notes = self._get_additional_notes(destination_country, visa_type)
            
            return VisaRequirement(
                country=destination_country,
                country_code=country_code,
                visa_type=visa_type,
                required=True,
                processing_time=processing_time,
                estimated_cost_usd=estimated_cost,
                required_documents=required_docs,
                qualification_requirements=qualifications,
                sponsorship_required=sponsorship_required,
                salary_threshold_usd=salary_threshold,
                language_requirements=language_reqs,
                success_rate=success_rate,
                additional_notes=additional_notes
            )
            
        except Exception as e:
            logger.error(f"Failed to get visa requirements: {e}")
            return self._create_default_visa_requirement(destination_country)
    
    def find_immigration_lawyers(self,
                               country: str,
                               specialization: str = None,
                               budget_usd: float = None,
                               language: str = None) -> List[ImmigrationLawyer]:
        """Find immigration lawyers in the network based on criteria."""
        try:
            # Filter lawyers by country
            lawyers = [lawyer for lawyer in self.lawyer_network if lawyer.country.upper() == country.upper()]
            
            # Filter by specialization
            if specialization:
                lawyers = [
                    lawyer for lawyer in lawyers 
                    if any(spec.lower() in specialization.lower() for spec in lawyer.specializations)
                ]
            
            # Filter by budget
            if budget_usd:
                lawyers = [lawyer for lawyer in lawyers if lawyer.hourly_rate_usd <= budget_usd]
            
            # Filter by language
            if language:
                lawyers = [
                    lawyer for lawyer in lawyers 
                    if any(lang.lower() == language.lower() for lang in lawyer.languages)
                ]
            
            # Sort by rating and experience
            lawyers.sort(key=lambda x: (x.rating, x.years_experience), reverse=True)
            
            return lawyers[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Failed to find immigration lawyers: {e}")
            return []
    
    def calculate_relocation_costs(self,
                                 from_country: str,
                                 to_country: str,
                                 from_city: str,
                                 to_city: str,
                                 family_size: int = 1,
                                 shipping_volume: str = "standard") -> RelocationCost:
        """Calculate comprehensive relocation costs."""
        try:
            # Visa and legal fees
            visa_fees = self._calculate_visa_fees(to_country, family_size)
            
            # Moving costs (shipping, flights, etc.)
            moving_costs = self._calculate_moving_costs(from_country, to_country, shipping_volume, family_size)
            
            # Temporary accommodation (first month)
            temp_accommodation = self._calculate_temporary_accommodation(to_city, family_size)
            
            # Permanent housing deposit
            housing_deposit = self._calculate_housing_deposit(to_city, family_size)
            
            # Cost of living difference (annual)
            col_difference = self._calculate_cost_of_living_difference(from_city, to_city, family_size)
            
            # Transportation (flights, local transport setup)
            transportation = self._calculate_transportation_costs(from_country, to_country, family_size)
            
            # Insurance (health, travel, etc.)
            insurance = self._calculate_insurance_costs(to_country, family_size)
            
            # Miscellaneous (documentation, utilities setup, etc.)
            miscellaneous = self._calculate_miscellaneous_costs(to_country, family_size)
            
            # Calculate totals
            total_cost = (visa_fees + moving_costs + temp_accommodation + 
                         housing_deposit + transportation + insurance + miscellaneous)
            
            # Calculate monthly living cost difference
            monthly_col_diff = col_difference / 12
            
            # Calculate break-even point if moving for higher salary
            break_even_months = int(total_cost / max(abs(monthly_col_diff), 1000)) if monthly_col_diff != 0 else 12
            
            return RelocationCost(
                from_country=from_country,
                to_country=to_country,
                from_city=from_city,
                to_city=to_city,
                visa_fees=visa_fees,
                moving_costs=moving_costs,
                temporary_accommodation=temp_accommodation,
                permanent_housing_deposit=housing_deposit,
                cost_of_living_difference=col_difference,
                transportation=transportation,
                insurance=insurance,
                miscellaneous=miscellaneous,
                total_cost_usd=total_cost,
                monthly_living_cost_difference=monthly_col_diff,
                break_even_months=break_even_months
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate relocation costs: {e}")
            return self._create_default_relocation_cost(from_country, to_country, from_city, to_city)
    
    def create_immigration_timeline(self,
                                  destination_country: str,
                                  visa_type: VisaType,
                                  target_start_date: datetime) -> ImmigrationTimeline:
        """Create detailed immigration process timeline."""
        try:
            phases = []
            current_date = datetime.now()
            
            # Phase 1: Preparation (1-3 months before application)
            prep_duration = 2  # months
            phases.append({
                'phase': 'Preparation',
                'duration_months': prep_duration,
                'start_date': current_date,
                'end_date': current_date + timedelta(days=prep_duration * 30),
                'tasks': [
                    'Gather required documents',
                    'Obtain language certifications if needed',
                    'Secure job offer with sponsorship',
                    'Complete educational credential evaluations',
                    'Prepare financial documentation'
                ],
                'estimated_cost': 2000,
                'critical_items': ['Job offer', 'Document authentication']
            })
            
            # Phase 2: Application Submission (1 month)
            app_duration = 1
            app_start = phases[-1]['end_date']
            phases.append({
                'phase': 'Application Submission',
                'duration_months': app_duration,
                'start_date': app_start,
                'end_date': app_start + timedelta(days=app_duration * 30),
                'tasks': [
                    'Complete visa application forms',
                    'Submit application with supporting documents',
                    'Pay application fees',
                    'Schedule biometrics appointment',
                    'Attend visa interview if required'
                ],
                'estimated_cost': 1500,
                'critical_items': ['Application submission', 'Interview attendance']
            })
            
            # Phase 3: Processing (varies by country)
            processing_months = self._get_processing_duration(destination_country, visa_type)
            proc_start = phases[-1]['end_date']
            phases.append({
                'phase': 'Processing & Approval',
                'duration_months': processing_months,
                'start_date': proc_start,
                'end_date': proc_start + timedelta(days=processing_months * 30),
                'tasks': [
                    'Application review by immigration authorities',
                    'Background checks and verifications',
                    'Medical examinations if required',
                    'Additional document requests handling',
                    'Decision notification'
                ],
                'estimated_cost': 500,
                'critical_items': ['Medical exams', 'Background clearance']
            })
            
            # Phase 4: Pre-departure (1-2 months)
            predep_duration = 1.5
            predep_start = phases[-1]['end_date']
            phases.append({
                'phase': 'Pre-departure',
                'duration_months': predep_duration,
                'start_date': predep_start,
                'end_date': predep_start + timedelta(days=predep_duration * 30),
                'tasks': [
                    'Book flights and arrange shipping',
                    'Secure temporary accommodation',
                    'Arrange international banking',
                    'Obtain international health insurance',
                    'Plan first month logistics'
                ],
                'estimated_cost': 5000,
                'critical_items': ['Accommodation booking', 'Banking setup']
            })
            
            total_duration = sum(phase['duration_months'] for phase in phases)
            
            # Identify critical milestones
            critical_milestones = [
                'Job offer secured',
                'Application submitted',
                'Visa approved',
                'Departure scheduled'
            ]
            
            # Potential delays
            potential_delays = self._identify_potential_delays(destination_country, visa_type)
            
            # Recommended start date (working backwards from target)
            recommended_start = target_start_date - timedelta(days=total_duration * 30)
            
            return ImmigrationTimeline(
                phases=phases,
                total_duration_months=int(total_duration),
                critical_milestones=critical_milestones,
                potential_delays=potential_delays,
                recommended_start_date=recommended_start
            )
            
        except Exception as e:
            logger.error(f"Failed to create immigration timeline: {e}")
            return self._create_default_timeline(destination_country, target_start_date)
    
    def get_immigration_insights(self,
                               origin_country: str,
                               destination_country: str,
                               job_role: str,
                               salary_usd: float) -> Dict[str, Any]:
        """Get comprehensive immigration insights and recommendations."""
        try:
            # Get visa requirements
            visa_req = self.get_visa_requirements(destination_country, origin_country, job_role, salary_usd)
            
            # Find recommended lawyers
            lawyers = self.find_immigration_lawyers(destination_country, "work visa")
            
            # Calculate relocation costs (using capital cities as default)
            capital_cities = {
                'US': 'Washington DC', 'CA': 'Ottawa', 'GB': 'London',
                'DE': 'Berlin', 'AU': 'Canberra', 'SG': 'Singapore'
            }
            
            from_city = capital_cities.get(origin_country, 'Unknown')
            to_city = capital_cities.get(destination_country, 'Unknown')
            
            relocation_cost = self.calculate_relocation_costs(
                origin_country, destination_country, from_city, to_city
            )
            
            # Create timeline
            timeline = self.create_immigration_timeline(
                destination_country, visa_req.visa_type, datetime.now() + timedelta(days=180)
            )
            
            # Generate recommendations
            recommendations = self._generate_immigration_recommendations(
                visa_req, relocation_cost, timeline
            )
            
            # Assess feasibility
            feasibility = self._assess_immigration_feasibility(visa_req, salary_usd)
            
            return {
                'visa_requirements': visa_req,
                'recommended_lawyers': lawyers[:3],  # Top 3
                'relocation_costs': relocation_cost,
                'immigration_timeline': timeline,
                'recommendations': recommendations,
                'feasibility_assessment': feasibility,
                'key_challenges': self._identify_key_challenges(visa_req, relocation_cost),
                'success_probability': visa_req.success_rate,
                'estimated_total_investment': relocation_cost.total_cost_usd + visa_req.estimated_cost_usd
            }
            
        except Exception as e:
            logger.error(f"Failed to get immigration insights: {e}")
            return self._create_default_insights(origin_country, destination_country)
    
    # Helper methods for visa requirements
    def _check_visa_requirement(self, origin: str, destination: str) -> bool:
        """Check if visa is required between countries."""
        # EU citizens working in EU don't need work visas
        eu_countries = ['DE', 'FR', 'NL', 'ES', 'IT', 'SE', 'DK', 'NO']
        if origin.upper() in eu_countries and destination.upper() in eu_countries:
            return False
        
        # Other visa-free arrangements
        visa_free_arrangements = {
            ('US', 'CA'): False,  # NAFTA professionals
            ('AU', 'NZ'): False,  # Trans-Tasman arrangement
        }
        
        key = (origin.upper(), destination.upper())
        return visa_free_arrangements.get(key, True)
    
    def _determine_visa_type(self, job_role: str, salary_usd: float, country: str) -> VisaType:
        """Determine appropriate visa type based on role and salary."""
        # High-skilled roles typically qualify for skilled worker visas
        skilled_roles = ['engineer', 'manager', 'scientist', 'analyst', 'consultant', 'developer']
        
        if any(role in job_role.lower() for role in skilled_roles):
            if salary_usd > 100000:
                return VisaType.SKILLED_WORKER
            else:
                return VisaType.WORK_PERMIT
        
        # Investment thresholds for investor visas
        if salary_usd > 200000:
            return VisaType.INVESTOR
        
        return VisaType.WORK_PERMIT
    
    def _get_processing_time(self, country: str, visa_type: VisaType) -> ProcessingTime:
        """Get expected processing time for visa application."""
        country_processing = {
            'US': ProcessingTime.COMPLEX,
            'GB': ProcessingTime.EXTENDED,
            'CA': ProcessingTime.STANDARD,
            'AU': ProcessingTime.STANDARD,
            'DE': ProcessingTime.STANDARD,
            'SG': ProcessingTime.EXPEDITED,
            'NL': ProcessingTime.STANDARD
        }
        
        return country_processing.get(country.upper(), ProcessingTime.STANDARD)
    
    def _calculate_visa_costs(self, country: str, visa_type: VisaType) -> float:
        """Calculate visa application costs."""
        base_costs = {
            'US': 2500,  # H1B + legal fees
            'GB': 1800,  # Skilled Worker visa
            'CA': 1500,  # Express Entry
            'AU': 2000,  # Skilled visa
            'DE': 1200,  # EU Blue Card
            'SG': 800,   # Employment Pass
            'NL': 1400,  # Highly Skilled Migrant
        }
        
        base_cost = base_costs.get(country.upper(), 1500)
        
        # Adjust for visa type
        if visa_type == VisaType.INVESTOR:
            base_cost *= 2
        elif visa_type == VisaType.SKILLED_WORKER:
            base_cost *= 1.2
        
        return base_cost
    
    def _get_required_documents(self, country: str, visa_type: VisaType) -> List[str]:
        """Get required documents for visa application."""
        common_docs = [
            'Valid passport',
            'Job offer letter',
            'Educational certificates',
            'Professional experience letters',
            'Financial statements',
            'Medical examination results',
            'Police clearance certificates',
            'Passport-sized photographs'
        ]
        
        country_specific = {
            'US': ['Form I-129', 'LCA certification'],
            'GB': ['Certificate of Sponsorship', 'English language test'],
            'CA': ['Express Entry profile', 'Provincial nomination'],
            'AU': ['Skills assessment', 'Health insurance'],
            'DE': ['University degree recognition', 'German language proof']
        }
        
        specific_docs = country_specific.get(country.upper(), [])
        return common_docs + specific_docs
    
    def _get_qualification_requirements(self, country: str, visa_type: VisaType, job_role: str) -> List[str]:
        """Get qualification requirements for visa."""
        requirements = [
            'University degree or equivalent professional experience',
            'Relevant work experience (typically 2+ years)',
            'Clean criminal background'
        ]
        
        # Country-specific requirements
        if country.upper() == 'US':
            requirements.append('Bachelor\'s degree for H1B specialty occupation')
        elif country.upper() == 'CA':
            requirements.append('Canadian Language Benchmarks (CLB) level 7+')
        elif country.upper() == 'AU':
            requirements.append('Positive skills assessment from relevant authority')
        elif country.upper() == 'DE':
            requirements.append('German language proficiency (B1 level minimum)')
        
        return requirements
    
    def _check_sponsorship_requirement(self, country: str, visa_type: VisaType) -> bool:
        """Check if employer sponsorship is required."""
        sponsorship_required = {
            'US': True,   # H1B requires sponsorship
            'GB': True,   # Skilled Worker visa requires sponsorship
            'SG': True,   # Employment Pass requires sponsorship
            'CA': False,  # Express Entry is points-based
            'AU': False,  # Some skilled visas don't require sponsorship
            'DE': False   # EU Blue Card can be self-sponsored
        }
        
        return sponsorship_required.get(country.upper(), True)
    
    def _get_salary_threshold(self, country: str, visa_type: VisaType) -> Optional[float]:
        """Get minimum salary threshold for visa."""
        thresholds = {
            'US': 60000,   # H1B prevailing wage
            'GB': 38700,   # Skilled Worker visa threshold
            'SG': 45000,   # Employment Pass minimum
            'AU': 53900,   # Temporary Skill Shortage visa
            'DE': 56800,   # EU Blue Card threshold
            'NL': 37296    # Highly Skilled Migrant
        }
        
        return thresholds.get(country.upper())
    
    def _get_language_requirements(self, country: str) -> List[str]:
        """Get language requirements for visa."""
        requirements = {
            'US': ['English proficiency demonstrated through work/education'],
            'GB': ['English language test (IELTS, PTE, or equivalent)'],
            'CA': ['English or French language test'],
            'AU': ['English language test (IELTS, PTE, or equivalent)'],
            'DE': ['German language proficiency (A1-B1 depending on visa)'],
            'FR': ['French language proficiency'],
            'NL': ['Dutch language helpful but not always required']
        }
        
        return requirements.get(country.upper(), ['Local language proficiency may be required'])
    
    def _calculate_success_rate(self, country: str, visa_type: VisaType, salary_usd: float) -> float:
        """Calculate visa application success rate."""
        base_rates = {
            'US': 0.65,  # H1B lottery + approval
            'GB': 0.85,  # Generally high approval rate
            'CA': 0.75,  # Express Entry success
            'AU': 0.80,  # Skilled visa success
            'DE': 0.90,  # EU Blue Card high success
            'SG': 0.85   # Employment Pass high success
        }
        
        base_rate = base_rates.get(country.upper(), 0.75)
        
        # Adjust for salary (higher salary = higher success rate)
        salary_threshold = self._get_salary_threshold(country, visa_type) or 50000
        if salary_usd > salary_threshold * 1.5:
            base_rate = min(base_rate * 1.2, 0.95)
        elif salary_usd < salary_threshold:
            base_rate = base_rate * 0.8
        
        return round(base_rate, 2)
    
    def _get_additional_notes(self, country: str, visa_type: VisaType) -> List[str]:
        """Get additional notes and tips for visa application."""
        notes = {
            'US': [
                'H1B visa subject to annual lottery system',
                'Premium processing available for faster review',
                'Start application process early due to high demand'
            ],
            'GB': [
                'Health surcharge required for applications over 6 months',
                'Faster decision available with priority service',
                'Sponsor must have valid sponsor license'
            ],
            'CA': [
                'Provincial Nominee Programs can provide additional points',
                'French language skills provide bonus points',
                'Express Entry draws happen regularly'
            ],
            'AU': [
                'Points test system - higher points increase chances',
                'State/territory nomination available for some occupations',
                'Health insurance required from day one'
            ]
        }
        
        return notes.get(country.upper(), ['Consult with immigration lawyer for specific advice'])
    
    # Helper methods for lawyer network
    def _initialize_lawyer_network(self):
        """Initialize immigration lawyer network database."""
        # Sample lawyers (in real implementation, this would be a comprehensive database)
        self.lawyer_network = [
            ImmigrationLawyer(
                name="Sarah Johnson",
                firm="Global Immigration Partners",
                country="US",
                city="New York",
                specializations=["H1B", "EB-1", "EB-2", "Tech visas"],
                languages=["English", "Spanish"],
                rating=4.8,
                years_experience=12,
                hourly_rate_usd=450,
                consultation_fee_usd=200,
                contact_email="sarah.johnson@globalimmigration.com",
                contact_phone="+1-212-555-0123",
                website="www.globalimmigration.com",
                success_rate=0.91,
                client_reviews=156,
                verified=True
            ),
            ImmigrationLawyer(
                name="David Chen",
                firm="Silicon Valley Immigration Law",
                country="US",
                city="San Francisco",
                specializations=["H1B", "O-1", "L-1", "Startup visas"],
                languages=["English", "Mandarin"],
                rating=4.9,
                years_experience=15,
                hourly_rate_usd=520,
                consultation_fee_usd=250,
                contact_email="david.chen@svimmigration.com",
                contact_phone="+1-415-555-0456",
                website="www.svimmigration.com",
                success_rate=0.94,
                client_reviews=203,
                verified=True
            ),
            ImmigrationLawyer(
                name="Emma Thompson",
                firm="UK Immigration Experts",
                country="GB",
                city="London",
                specializations=["Skilled Worker", "Global Talent", "Innovator"],
                languages=["English", "French"],
                rating=4.7,
                years_experience=10,
                hourly_rate_usd=380,
                consultation_fee_usd=150,
                contact_email="emma.thompson@ukimmigration.co.uk",
                contact_phone="+44-20-7555-0789",
                website="www.ukimmigration.co.uk",
                success_rate=0.88,
                client_reviews=134,
                verified=True
            ),
            ImmigrationLawyer(
                name="Michael Weber",
                firm="German Work Visa Specialists",
                country="DE",
                city="Berlin",
                specializations=["EU Blue Card", "Work permits", "Family reunification"],
                languages=["German", "English"],
                rating=4.6,
                years_experience=8,
                hourly_rate_usd=320,
                consultation_fee_usd=120,
                contact_email="michael.weber@germanvisa.de",
                contact_phone="+49-30-555-0321",
                website="www.germanvisa.de",
                success_rate=0.85,
                client_reviews=98,
                verified=True
            ),
            ImmigrationLawyer(
                name="Lisa Tan",
                firm="Singapore Immigration Services",
                country="SG",
                city="Singapore",
                specializations=["Employment Pass", "Tech.Pass", "Entrepreneur Pass"],
                languages=["English", "Mandarin", "Malay"],
                rating=4.8,
                years_experience=9,
                hourly_rate_usd=280,
                consultation_fee_usd=100,
                contact_email="lisa.tan@sgimmigration.com.sg",
                contact_phone="+65-6555-0654",
                website="www.sgimmigration.com.sg",
                success_rate=0.92,
                client_reviews=87,
                verified=True
            )
        ]
    
    def _initialize_visa_database(self):
        """Initialize visa requirements database."""
        # This would contain comprehensive visa information
        self.visa_database = {
            'processing_times': {
                'US': {'H1B': 90, 'L1': 60, 'O1': 45},
                'GB': {'Skilled Worker': 60, 'Global Talent': 21},
                'CA': {'Express Entry': 180, 'Work Permit': 90},
                'AU': {'TSS': 75, 'Skilled': 120},
                'DE': {'EU Blue Card': 90, 'Work Permit': 60}
            }
        }
    
    def _initialize_cost_database(self):
        """Initialize cost of living and relocation cost database."""
        self.cost_database = {
            'living_costs_monthly': {
                'New York': 4500, 'San Francisco': 4800, 'London': 3800,
                'Berlin': 2200, 'Singapore': 3200, 'Toronto': 2800,
                'Sydney': 3400, 'Amsterdam': 2900, 'Zurich': 4200
            },
            'moving_costs_base': {
                'domestic': 2000, 'international': 8000, 'intercontinental': 15000
            }
        }
    
    # Helper methods for relocation costs
    def _calculate_visa_fees(self, country: str, family_size: int) -> float:
        """Calculate visa fees for family."""
        base_fees = {
            'US': 2500, 'GB': 1800, 'CA': 1500, 'AU': 2000, 'DE': 1200, 'SG': 800
        }
        
        base_fee = base_fees.get(country.upper(), 1500)
        
        # Family multiplier (spouse and children)
        if family_size > 1:
            base_fee += (family_size - 1) * base_fee * 0.7
        
        return base_fee
    
    def _calculate_moving_costs(self, from_country: str, to_country: str, 
                              shipping_volume: str, family_size: int) -> float:
        """Calculate physical moving costs."""
        # Base costs by distance
        if from_country == to_country:
            base_cost = 2000  # Domestic move
        elif self._same_continent(from_country, to_country):
            base_cost = 8000  # Regional move
        else:
            base_cost = 15000  # Intercontinental move
        
        # Adjust for shipping volume
        volume_multipliers = {'minimal': 0.5, 'standard': 1.0, 'extensive': 1.8}
        base_cost *= volume_multipliers.get(shipping_volume, 1.0)
        
        # Adjust for family size
        base_cost *= (1 + (family_size - 1) * 0.3)
        
        return base_cost
    
    def _calculate_temporary_accommodation(self, city: str, family_size: int) -> float:
        """Calculate temporary accommodation costs (first month)."""
        daily_rates = {
            'New York': 200, 'San Francisco': 220, 'London': 180,
            'Berlin': 100, 'Singapore': 150, 'Toronto': 120,
            'Sydney': 160, 'Amsterdam': 140, 'Zurich': 200
        }
        
        daily_rate = daily_rates.get(city, 120)
        
        # Family room premium
        if family_size > 2:
            daily_rate *= 1.5
        elif family_size > 1:
            daily_rate *= 1.3
        
        return daily_rate * 30  # 30 days
    
    def _calculate_housing_deposit(self, city: str, family_size: int) -> float:
        """Calculate housing deposit (typically 2-3 months rent)."""
        monthly_rents = {
            'New York': 3500, 'San Francisco': 4000, 'London': 2800,
            'Berlin': 1200, 'Singapore': 2500, 'Toronto': 1800,
            'Sydney': 2200, 'Amsterdam': 1600, 'Zurich': 2800
        }
        
        monthly_rent = monthly_rents.get(city, 1500)
        
        # Adjust for family size (bigger apartment)
        if family_size > 2:
            monthly_rent *= 1.6
        elif family_size > 1:
            monthly_rent *= 1.3
        
        return monthly_rent * 2.5  # 2.5 months deposit
    
    def _calculate_cost_of_living_difference(self, from_city: str, to_city: str, family_size: int) -> float:
        """Calculate annual cost of living difference."""
        monthly_costs = self.cost_database.get('living_costs_monthly', {})
        
        from_cost = monthly_costs.get(from_city, 2500)
        to_cost = monthly_costs.get(to_city, 2500)
        
        # Adjust for family size
        from_cost *= (1 + (family_size - 1) * 0.4)
        to_cost *= (1 + (family_size - 1) * 0.4)
        
        return (to_cost - from_cost) * 12  # Annual difference
    
    def _calculate_transportation_costs(self, from_country: str, to_country: str, family_size: int) -> float:
        """Calculate transportation costs (flights, shipping)."""
        # Flight costs
        if self._same_continent(from_country, to_country):
            flight_cost = 800
        else:
            flight_cost = 1500
        
        flight_cost *= family_size
        
        # Add local transportation setup
        local_transport = 500
        
        return flight_cost + local_transport
    
    def _calculate_insurance_costs(self, country: str, family_size: int) -> float:
        """Calculate insurance setup costs."""
        # Health insurance setup, travel insurance, etc.
        base_insurance = 1200
        
        # Adjust for family
        base_insurance *= (1 + (family_size - 1) * 0.6)
        
        return base_insurance
    
    def _calculate_miscellaneous_costs(self, country: str, family_size: int) -> float:
        """Calculate miscellaneous setup costs."""
        # Document fees, utility setup, phone, internet, etc.
        base_misc = 800
        
        # Adjust for family
        base_misc *= (1 + (family_size - 1) * 0.3)
        
        return base_misc
    
    def _same_continent(self, country1: str, country2: str) -> bool:
        """Check if two countries are on the same continent."""
        continents = {
            'north_america': ['US', 'CA', 'MX'],
            'europe': ['GB', 'DE', 'FR', 'NL', 'CH', 'SE', 'NO', 'DK', 'ES', 'IT'],
            'asia_pacific': ['SG', 'AU', 'NZ', 'JP', 'KR', 'HK', 'MY', 'TH'],
            'middle_east': ['AE', 'SA', 'QA', 'KW']
        }
        
        for continent, countries in continents.items():
            if country1.upper() in countries and country2.upper() in countries:
                return True
        
        return False
    
    # Helper methods for timeline creation
    def _get_processing_duration(self, country: str, visa_type: VisaType) -> int:
        """Get processing duration in months."""
        durations = {
            'US': 4,  # H1B with potential delays
            'GB': 2,  # Skilled Worker
            'CA': 6,  # Express Entry
            'AU': 3,  # Skilled visa
            'DE': 3,  # EU Blue Card
            'SG': 1   # Employment Pass
        }
        
        return durations.get(country.upper(), 3)
    
    def _identify_potential_delays(self, country: str, visa_type: VisaType) -> List[str]:
        """Identify potential delays in the process."""
        common_delays = [
            'Document authentication delays',
            'Medical examination scheduling',
            'Background check processing',
            'Embassy appointment availability'
        ]
        
        country_specific_delays = {
            'US': ['H1B lottery results', 'Premium processing backlog'],
            'GB': ['Sponsor license verification', 'Health surcharge processing'],
            'CA': ['Provincial nomination timing', 'Express Entry draw frequency'],
            'AU': ['Skills assessment delays', 'Health examination results']
        }
        
        specific_delays = country_specific_delays.get(country.upper(), [])
        return common_delays + specific_delays
    
    # Default/fallback methods
    def _create_no_visa_requirement(self, country: str) -> VisaRequirement:
        """Create visa requirement object for no visa needed."""
        return VisaRequirement(
            country=country,
            country_code=country.upper(),
            visa_type=VisaType.WORK_PERMIT,
            required=False,
            processing_time=ProcessingTime.EXPEDITED,
            estimated_cost_usd=0,
            required_documents=['Valid passport for travel'],
            qualification_requirements=['Right to work in destination country'],
            sponsorship_required=False,
            salary_threshold_usd=None,
            language_requirements=[],
            success_rate=1.0,
            additional_notes=['No work visa required due to existing work rights']
        )
    
    def _create_default_visa_requirement(self, country: str) -> VisaRequirement:
        """Create default visa requirement when data is unavailable."""
        return VisaRequirement(
            country=country,
            country_code=country.upper(),
            visa_type=VisaType.WORK_PERMIT,
            required=True,
            processing_time=ProcessingTime.STANDARD,
            estimated_cost_usd=1500,
            required_documents=['Standard visa application documents'],
            qualification_requirements=['Professional qualifications'],
            sponsorship_required=True,
            salary_threshold_usd=50000,
            language_requirements=['Local language proficiency'],
            success_rate=0.75,
            additional_notes=['Consult with immigration specialist for detailed requirements']
        )
    
    def _create_default_relocation_cost(self, from_country: str, to_country: str, 
                                      from_city: str, to_city: str) -> RelocationCost:
        """Create default relocation cost estimate."""
        return RelocationCost(
            from_country=from_country,
            to_country=to_country,
            from_city=from_city,
            to_city=to_city,
            visa_fees=1500,
            moving_costs=10000,
            temporary_accommodation=3000,
            permanent_housing_deposit=5000,
            cost_of_living_difference=12000,
            transportation=2000,
            insurance=1200,
            miscellaneous=800,
            total_cost_usd=23500,
            monthly_living_cost_difference=1000,
            break_even_months=24
        )
    
    def _create_default_timeline(self, country: str, target_date: datetime) -> ImmigrationTimeline:
        """Create default immigration timeline."""
        return ImmigrationTimeline(
            phases=[
                {
                    'phase': 'Preparation',
                    'duration_months': 2,
                    'tasks': ['Document preparation', 'Legal consultation']
                },
                {
                    'phase': 'Application',
                    'duration_months': 1,
                    'tasks': ['Application submission', 'Fee payment']
                },
                {
                    'phase': 'Processing',
                    'duration_months': 3,
                    'tasks': ['Government review', 'Decision']
                }
            ],
            total_duration_months=6,
            critical_milestones=['Application submitted', 'Approval received'],
            potential_delays=['Document verification', 'Processing backlog'],
            recommended_start_date=target_date - timedelta(days=180)
        )
    
    def _generate_immigration_recommendations(self, visa_req: VisaRequirement, 
                                            relocation_cost: RelocationCost,
                                            timeline: ImmigrationTimeline) -> List[str]:
        """Generate immigration recommendations."""
        recommendations = []
        
        # Visa-specific recommendations
        if visa_req.success_rate < 0.7:
            recommendations.append("Consider strengthening application with additional qualifications")
        
        if visa_req.sponsorship_required:
            recommendations.append("Secure job offer with sponsorship before applying")
        
        # Cost-related recommendations
        if relocation_cost.total_cost_usd > 30000:
            recommendations.append("Plan for significant relocation investment - consider phased approach")
        
        if relocation_cost.break_even_months > 18:
            recommendations.append("Ensure salary increase justifies relocation costs")
        
        # Timeline recommendations
        if timeline.total_duration_months > 6:
            recommendations.append("Start immigration process well in advance due to lengthy timeline")
        
        recommendations.append("Consult with immigration lawyer for personalized strategy")
        
        return recommendations
    
    def _assess_immigration_feasibility(self, visa_req: VisaRequirement, salary_usd: float) -> Dict[str, Any]:
        """Assess overall immigration feasibility."""
        feasibility_score = 0.0
        factors = []
        
        # Visa approval probability
        feasibility_score += visa_req.success_rate * 0.4
        factors.append(f"Visa approval probability: {visa_req.success_rate:.1%}")
        
        # Salary threshold
        if visa_req.salary_threshold_usd:
            if salary_usd >= visa_req.salary_threshold_usd:
                feasibility_score += 0.3
                factors.append("Salary meets minimum requirements")
            else:
                factors.append(f"Salary below threshold (${visa_req.salary_threshold_usd:,.0f})")
        else:
            feasibility_score += 0.3
        
        # Sponsorship requirement
        if not visa_req.sponsorship_required:
            feasibility_score += 0.2
            factors.append("No sponsorship required")
        else:
            feasibility_score += 0.1
            factors.append("Employer sponsorship required")
        
        # Processing complexity
        if visa_req.processing_time in [ProcessingTime.EXPEDITED, ProcessingTime.STANDARD]:
            feasibility_score += 0.1
            factors.append("Standard processing timeline")
        else:
            factors.append("Extended processing timeline")
        
        # Determine feasibility level
        if feasibility_score >= 0.8:
            level = "High"
        elif feasibility_score >= 0.6:
            level = "Moderate"
        elif feasibility_score >= 0.4:
            level = "Challenging"
        else:
            level = "Difficult"
        
        return {
            'feasibility_level': level,
            'feasibility_score': round(feasibility_score, 2),
            'key_factors': factors,
            'recommendation': self._get_feasibility_recommendation(level)
        }
    
    def _get_feasibility_recommendation(self, level: str) -> str:
        """Get recommendation based on feasibility level."""
        recommendations = {
            'High': 'Proceed with confidence - strong probability of success',
            'Moderate': 'Proceed with preparation - address any weak points',
            'Challenging': 'Consider strengthening profile before applying',
            'Difficult': 'Explore alternative pathways or improve qualifications'
        }
        
        return recommendations.get(level, 'Consult with immigration specialist')
    
    def _identify_key_challenges(self, visa_req: VisaRequirement, 
                               relocation_cost: RelocationCost) -> List[str]:
        """Identify key challenges in the immigration process."""
        challenges = []
        
        if visa_req.success_rate < 0.7:
            challenges.append("Low visa approval probability")
        
        if visa_req.sponsorship_required:
            challenges.append("Employer sponsorship requirement")
        
        if relocation_cost.total_cost_usd > 25000:
            challenges.append("High relocation costs")
        
        if visa_req.processing_time in [ProcessingTime.EXTENDED, ProcessingTime.COMPLEX]:
            challenges.append("Lengthy processing timeline")
        
        if visa_req.language_requirements:
            challenges.append("Language proficiency requirements")
        
        return challenges
    
    def _create_default_insights(self, origin: str, destination: str) -> Dict[str, Any]:
        """Create default insights when detailed analysis fails."""
        return {
            'visa_requirements': self._create_default_visa_requirement(destination),
            'recommended_lawyers': [],
            'relocation_costs': self._create_default_relocation_cost(origin, destination, 'Unknown', 'Unknown'),
            'immigration_timeline': self._create_default_timeline(destination, datetime.now() + timedelta(days=180)),
            'recommendations': ['Consult with immigration specialist', 'Research specific requirements'],
            'feasibility_assessment': {
                'feasibility_level': 'Unknown',
                'feasibility_score': 0.5,
                'key_factors': ['Limited data available'],
                'recommendation': 'Seek professional immigration advice'
            },
            'key_challenges': ['Insufficient data for detailed analysis'],
            'success_probability': 0.5,
            'estimated_total_investment': 25000
        }


# Global instance for use across the application
immigration_support_service = ImmigrationSupportService()
