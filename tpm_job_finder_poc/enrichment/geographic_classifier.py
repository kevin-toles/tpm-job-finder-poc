"""Geographic classification and regional intelligence system."""

import logging
from typing import Dict, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class GeographicClassifier:
    """Classifier for organizing jobs by geographic regions with intelligence."""
    
    def __init__(self):
        """Initialize geographic classifier with regional mappings."""
        # Complete regional mapping based on Careerjet plan
        self.regional_mapping = {
            'North America': [
                'US', 'CA', 'MX'
            ],
            'Western Europe': [
                'GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'CH', 'AT',
                'PT', 'IE', 'DK', 'SE', 'NO', 'FI', 'IS', 'LU'
            ],
            'Eastern Europe': [
                'PL', 'CZ', 'HU', 'SK', 'SI', 'HR', 'BG', 'RO', 'EE',
                'LV', 'LT', 'RU', 'UA', 'BY', 'MD', 'RS', 'BA', 'MK',
                'AL', 'ME', 'XK'
            ],
            'East Asia': [
                'JP', 'KR', 'CN', 'HK', 'MO', 'TW', 'MN'
            ],
            'Southeast Asia': [
                'SG', 'MY', 'TH', 'ID', 'PH', 'VN', 'KH', 'LA', 'MM',
                'BN', 'TL'
            ],
            'South Asia': [
                'IN', 'PK', 'BD', 'LK', 'NP', 'BT', 'MV', 'AF'
            ],
            'South America': [
                'BR', 'AR', 'CL', 'PE', 'CO', 'VE', 'EC', 'BO', 'PY',
                'UY', 'GY', 'SR', 'FK'
            ],
            'Africa': [
                'ZA', 'EG', 'NG', 'KE', 'GH', 'ET', 'UG', 'TZ', 'ZW',
                'ZM', 'MW', 'MZ', 'BW', 'NA', 'SZ', 'LS', 'MG', 'MU',
                'SC', 'KM', 'DJ', 'SO', 'ER', 'SS', 'SD', 'TD', 'CF',
                'CM', 'GQ', 'GA', 'CG', 'CD', 'ST', 'AO', 'CV', 'GW',
                'GN', 'SL', 'LR', 'CI', 'BF', 'ML', 'NE', 'SN', 'GM',
                'MR', 'MA', 'DZ', 'TN', 'LY'
            ],
            'Australia/Oceania': [
                'AU', 'NZ', 'FJ', 'PG', 'WS', 'TO', 'VU', 'SB', 'FM', 
                'KI', 'MH', 'PW', 'TV', 'NR'
            ],
            'Central America': [
                'BZ', 'CR', 'SV', 'GT', 'HN', 'NI', 'PA'
            ],
            'Other': ['AQ']  # Antarctica and special territories
        }
        
        # Reverse mapping for fast lookup
        self.country_to_region = {}
        for region, countries in self.regional_mapping.items():
            for country in countries:
                self.country_to_region[country] = region
                
        # Regional metadata for intelligence
        self.regional_metadata = {
            'North America': {
                'timezone_range': [-8, -5],  # PST to EST
                'primary_languages': ['English', 'Spanish'],
                'business_culture': 'Direct, fast-paced',
                'work_visa_complexity': 'Low (for US citizens)',
                'avg_cost_of_living': 1.0,  # Baseline
                'major_tech_hubs': ['San Francisco', 'Seattle', 'New York', 'Austin', 'Toronto'],
                'currency_stability': 'High',
                'remote_work_acceptance': 'Very High',
            },
            'Western Europe': {
                'timezone_range': [0, 2],   # GMT to CEST
                'primary_languages': ['English', 'German', 'French'],
                'business_culture': 'Formal, process-oriented',
                'work_visa_complexity': 'Medium',
                'avg_cost_of_living': 1.15,
                'major_tech_hubs': ['London', 'Berlin', 'Amsterdam', 'Zurich', 'Stockholm'],
                'currency_stability': 'High',
                'remote_work_acceptance': 'High',
            },
            'Eastern Europe': {
                'timezone_range': [1, 3],   # CET to MSK
                'primary_languages': ['Polish', 'Czech', 'Hungarian', 'Russian'],
                'business_culture': 'Hierarchical, relationship-focused',
                'work_visa_complexity': 'Medium-High',
                'avg_cost_of_living': 0.6,
                'major_tech_hubs': ['Warsaw', 'Prague', 'Budapest', 'Krakow', 'Moscow'],
                'currency_stability': 'Medium',
                'remote_work_acceptance': 'Medium',
            },
            'East Asia': {
                'timezone_range': [8, 9],   # CST to JST
                'primary_languages': ['Chinese', 'Japanese', 'Korean'],
                'business_culture': 'Hierarchical, consensus-driven',
                'work_visa_complexity': 'High',
                'avg_cost_of_living': 1.3,
                'major_tech_hubs': ['Tokyo', 'Seoul', 'Shanghai', 'Beijing', 'Hong Kong'],
                'currency_stability': 'High',
                'remote_work_acceptance': 'Medium',
            },
            'Southeast Asia': {
                'timezone_range': [7, 8],   # ICT to SGT
                'primary_languages': ['English', 'Malay', 'Thai', 'Indonesian'],
                'business_culture': 'Relationship-based, flexible',
                'work_visa_complexity': 'Medium',
                'avg_cost_of_living': 0.4,
                'major_tech_hubs': ['Singapore', 'Kuala Lumpur', 'Bangkok', 'Jakarta', 'Manila'],
                'currency_stability': 'Medium',
                'remote_work_acceptance': 'High',
            },
            'South Asia': {
                'timezone_range': [5, 6],   # IST to BST
                'primary_languages': ['Hindi', 'English', 'Bengali', 'Urdu'],
                'business_culture': 'Hierarchical, relationship-focused',
                'work_visa_complexity': 'High',
                'avg_cost_of_living': 0.25,
                'major_tech_hubs': ['Bangalore', 'Mumbai', 'Hyderabad', 'Pune', 'Delhi'],
                'currency_stability': 'Medium',
                'remote_work_acceptance': 'Very High',
            },
            'South America': {
                'timezone_range': [-5, -3], # COT to BRT
                'primary_languages': ['Spanish', 'Portuguese'],
                'business_culture': 'Relationship-based, flexible',
                'work_visa_complexity': 'Medium',
                'avg_cost_of_living': 0.5,
                'major_tech_hubs': ['São Paulo', 'Buenos Aires', 'Santiago', 'Bogotá', 'Lima'],
                'currency_stability': 'Medium',
                'remote_work_acceptance': 'High',
            },
            'Africa': {
                'timezone_range': [0, 3],   # GMT to EAT
                'primary_languages': ['English', 'French', 'Arabic', 'Swahili'],
                'business_culture': 'Relationship-based, community-oriented',
                'work_visa_complexity': 'High',
                'avg_cost_of_living': 0.35,
                'major_tech_hubs': ['Cape Town', 'Lagos', 'Nairobi', 'Cairo', 'Casablanca'],
                'currency_stability': 'Low-Medium',
                'remote_work_acceptance': 'High',
            },
            'Australia/Oceania': {
                'timezone_range': [10, 12], # AEST to NZDT
                'primary_languages': ['English'],
                'business_culture': 'Direct, egalitarian',
                'work_visa_complexity': 'Medium',
                'avg_cost_of_living': 1.2,
                'major_tech_hubs': ['Sydney', 'Melbourne', 'Auckland', 'Brisbane', 'Perth'],
                'currency_stability': 'High',
                'remote_work_acceptance': 'High',
            },
            'Central America': {
                'timezone_range': [-6, -5], # CST to EST
                'primary_languages': ['Spanish', 'English'],
                'business_culture': 'Relationship-based, flexible',
                'work_visa_complexity': 'Medium',
                'avg_cost_of_living': 0.4,
                'major_tech_hubs': ['San José', 'Guatemala City', 'Panama City'],
                'currency_stability': 'Medium',
                'remote_work_acceptance': 'High',
            }
        }
    
    def classify_job_region(self, country_code: str) -> str:
        """Classify job's geographic region.
        
        Args:
            country_code: ISO 2-letter country code
            
        Returns:
            Region name
        """
        return self.country_to_region.get(country_code.upper(), 'Other')
    
    def classify_location(self, location_string: str) -> Dict[str, str]:
        """Classify location string to region and country.
        
        Args:
            location_string: Location string like 'Singapore', 'Berlin, Germany', 'Tokyo, Japan'
            
        Returns:
            Dictionary with 'region' and 'country' keys
        """
        # Location mapping for common formats
        location_mappings = {
            # Direct city to country mappings
            'singapore': {'country': 'Singapore', 'country_code': 'SG'},
            'tokyo': {'country': 'Japan', 'country_code': 'JP'},
            'tokyo, japan': {'country': 'Japan', 'country_code': 'JP'},
            'berlin': {'country': 'Germany', 'country_code': 'DE'},
            'berlin, germany': {'country': 'Germany', 'country_code': 'DE'},
            'london': {'country': 'United Kingdom', 'country_code': 'GB'},
            'london, uk': {'country': 'United Kingdom', 'country_code': 'GB'},
            'new york': {'country': 'United States', 'country_code': 'US'},
            'new york, usa': {'country': 'United States', 'country_code': 'US'},
            'toronto': {'country': 'Canada', 'country_code': 'CA'},
            'toronto, canada': {'country': 'Canada', 'country_code': 'CA'},
            'sydney': {'country': 'Australia', 'country_code': 'AU'},
            'sydney, australia': {'country': 'Australia', 'country_code': 'AU'},
            'paris': {'country': 'France', 'country_code': 'FR'},
            'paris, france': {'country': 'France', 'country_code': 'FR'},
            'amsterdam': {'country': 'Netherlands', 'country_code': 'NL'},
            'amsterdam, netherlands': {'country': 'Netherlands', 'country_code': 'NL'},
            'zurich': {'country': 'Switzerland', 'country_code': 'CH'},
            'zurich, switzerland': {'country': 'Switzerland', 'country_code': 'CH'},
            'hong kong': {'country': 'Hong Kong', 'country_code': 'HK'},
            'mumbai': {'country': 'India', 'country_code': 'IN'},
            'mumbai, india': {'country': 'India', 'country_code': 'IN'},
            'bangalore': {'country': 'India', 'country_code': 'IN'},
            'bangalore, india': {'country': 'India', 'country_code': 'IN'},
        }
        
        # Normalize location string
        location_norm = location_string.lower().strip()
        
        # Try direct mapping first
        if location_norm in location_mappings:
            mapping = location_mappings[location_norm]
            country_code = mapping['country_code']
            region = self.classify_job_region(country_code)
            return {
                'region': region,
                'country': mapping['country']
            }
        
        # Try to extract country from comma-separated format
        if ',' in location_string:
            parts = [part.strip().lower() for part in location_string.split(',')]
            # Check if last part is a known country
            country_keywords = {
                'germany': {'country': 'Germany', 'country_code': 'DE'},
                'japan': {'country': 'Japan', 'country_code': 'JP'},
                'singapore': {'country': 'Singapore', 'country_code': 'SG'},
                'uk': {'country': 'United Kingdom', 'country_code': 'GB'},
                'united kingdom': {'country': 'United Kingdom', 'country_code': 'GB'},
                'usa': {'country': 'United States', 'country_code': 'US'},
                'united states': {'country': 'United States', 'country_code': 'US'},
                'canada': {'country': 'Canada', 'country_code': 'CA'},
                'australia': {'country': 'Australia', 'country_code': 'AU'},
                'france': {'country': 'France', 'country_code': 'FR'},
                'netherlands': {'country': 'Netherlands', 'country_code': 'NL'},
                'switzerland': {'country': 'Switzerland', 'country_code': 'CH'},
                'india': {'country': 'India', 'country_code': 'IN'},
            }
            
            for part in reversed(parts):
                if part in country_keywords:
                    mapping = country_keywords[part]
                    country_code = mapping['country_code']
                    region = self.classify_job_region(country_code)
                    return {
                        'region': region,
                        'country': mapping['country']
                    }
        
        # Default fallback
        return {
            'region': 'Other',
            'country': 'Unknown'
        }
    
    def get_regional_metadata(self, region: str) -> Dict:
        """Get regional context and metadata.
        
        Args:
            region: Region name
            
        Returns:
            Dictionary of regional metadata
        """
        metadata = self.regional_metadata.get(region, {}).copy()
        
        # Add avg_visa_complexity as alias for work_visa_complexity
        if 'work_visa_complexity' in metadata:
            complexity_map = {
                'Low (for US citizens)': 'low',
                'Medium': 'medium',
                'Medium-High': 'high',
                'High': 'high'
            }
            metadata['avg_visa_complexity'] = complexity_map.get(
                metadata['work_visa_complexity'], 'medium'
            )
        
        # Format timezone range as string
        if 'timezone_range' in metadata:
            tz_range = metadata['timezone_range']
            if isinstance(tz_range, list) and len(tz_range) == 2:
                metadata['timezone_range'] = f"UTC{tz_range[0]:+d} to UTC{tz_range[1]:+d}"
        
        return metadata
    
    def calculate_timezone_overlap(self, job_timezone: int, base_timezone: int = -8) -> str:
        """Calculate timezone overlap with base location (default: PST).
        
        Args:
            job_timezone: Job location timezone offset from UTC
            base_timezone: Base location timezone offset from UTC
            
        Returns:
            Overlap assessment string
        """
        overlap_hours = abs(job_timezone - base_timezone)
        
        if overlap_hours <= 3:
            return "Excellent (3+ hours overlap)"
        elif overlap_hours <= 6:
            return "Good (2-3 hours overlap)"
        elif overlap_hours <= 9:
            return "Fair (1-2 hours overlap)"
        else:
            return "Challenging (<1 hour overlap)"
    
    def assess_visa_requirements(self, country_code: str) -> Dict[str, str]:
        """Assess visa requirements for US citizens.
        
        Args:
            country_code: ISO 2-letter country code
            
        Returns:
            Dictionary with visa assessment
        """
        # Simplified visa requirements for US citizens
        visa_free_work = {
            'CA': 'NAFTA/USMCA allows easier work authorization'
        }
        
        visa_required_work = {
            'GB': 'Skilled Worker visa required',
            'DE': 'EU Blue Card or work permit required',
            'FR': 'Work permit required',
            'AU': 'Skilled visa (189/190) or employer sponsorship',
            'NZ': 'Work visa or Essential Skills visa',
            'SG': 'Employment Pass required',
            'JP': 'Work visa required',
            'HK': 'Work visa required'
        }
        
        if country_code in visa_free_work:
            return {
                'required': False,
                'details': visa_free_work[country_code],
                'complexity': 'Low'
            }
        elif country_code in visa_required_work:
            return {
                'required': True,
                'details': visa_required_work[country_code],
                'complexity': 'Medium-High'
            }
        elif country_code == 'US':
            return {
                'required': False,
                'details': 'Domestic position',
                'complexity': 'none'
            }
        else:
            return {
                'required': True,
                'details': 'Work authorization likely required',
                'complexity': 'High'
            }
    
    def get_cost_of_living_adjustment(self, region: str, salary: Optional[float]) -> Optional[float]:
        """Calculate cost of living adjusted salary.
        
        Args:
            region: Region name
            salary: Salary amount in USD
            
        Returns:
            Cost of living adjusted salary or None
        """
        if not salary:
            return None
            
        metadata = self.get_regional_metadata(region)
        cost_multiplier = metadata.get('avg_cost_of_living', 1.0)
        
        # Adjust salary to equivalent purchasing power
        adjusted_salary = salary / cost_multiplier
        return round(adjusted_salary, 2)
    
    def organize_jobs_by_region(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """Organize jobs by geographic region.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Dictionary with region names as keys and job lists as values
        """
        regional_jobs = {}
        
        for job in jobs:
            # Get region from job data
            region = job.get('region')
            if not region and job.get('country_code'):
                region = self.classify_job_region(job['country_code'])
                job['region'] = region
            
            region = region or 'Other'
            
            if region not in regional_jobs:
                regional_jobs[region] = []
            regional_jobs[region].append(job)
        
        # Sort jobs within each region by match score (desc) then salary (desc)
        for region in regional_jobs:
            regional_jobs[region].sort(
                key=lambda x: (
                    -(x.get('match_score') or 0),
                    -(x.get('usd_equivalent') or 0)
                )
            )
        
        return regional_jobs
    
    def get_region_priority_order(self) -> List[str]:
        """Get recommended region priority order for job browsing.
        
        Returns:
            List of region names in priority order
        """
        return [
            'North America',      # Primary focus for US-based job seekers
            'Western Europe',     # High opportunity, good visa options
            'Australia/Oceania',  # English-speaking, good opportunities
            'East Asia',          # Major tech hubs, high compensation
            'Southeast Asia',     # Growing markets, cost-effective
            'Eastern Europe',     # Emerging tech scenes
            'South America',      # Remote-friendly, timezone overlap
            'South Asia',         # Large tech industry
            'Africa',             # Emerging markets
            'Central America',    # Timezone overlap
            'Other'              # Catch-all
        ]
