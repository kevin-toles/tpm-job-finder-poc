"""
Real-time Salary Benchmarking Service for Global Job Intelligence.

This module provides comprehensive salary benchmarking and analysis
capabilities across different regions, roles, and market conditions.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict
import statistics
import json
from forex_python.converter import CurrencyRates

logger = logging.getLogger(__name__)


@dataclass
class SalaryBenchmark:
    """Represents a comprehensive salary benchmark."""
    role_category: str
    region: str
    country_code: str
    experience_level: str  # 'junior', 'mid', 'senior', 'principal'
    median_salary_usd: float
    mean_salary_usd: float
    percentile_10: float
    percentile_25: float
    percentile_75: float
    percentile_90: float
    local_currency: str
    local_median: float
    cost_of_living_adjusted: float
    sample_size: int
    confidence_level: str
    last_updated: datetime


@dataclass
class CompensationPackage:
    """Represents a complete compensation analysis."""
    base_salary: float
    equity_value: float
    bonus_potential: float
    total_compensation: float
    benefits_value: float
    remote_premium: float
    currency: str
    purchasing_power: float


@dataclass
class MarketPosition:
    """Represents salary position relative to market."""
    current_salary: float
    market_percentile: float
    gap_to_median: float
    gap_to_75th: float
    competitiveness: str  # 'below_market', 'competitive', 'above_market'
    negotiation_potential: float
    market_direction: str  # 'increasing', 'stable', 'decreasing'


@dataclass
class SalaryAnalysis:
    """Represents comprehensive salary analysis results."""
    market_position: MarketPosition
    regional_comparison: Dict[str, Any]
    confidence_score: float
    salary_range: str
    currency_info: Dict[str, str]


class SalaryBenchmarkingService:
    """Advanced salary benchmarking and analysis service."""
    
    def __init__(self):
        """Initialize the salary benchmarking service."""
        self.salary_data = []
        self.regional_adjustments = {}
        self.industry_multipliers = {}
        self.company_data = {}
        self.currency_converter = CurrencyRates()
        self.benchmark_cache = {}
        self.cache_expiry = timedelta(hours=4)
        
        # Supported regions for salary benchmarking
        self.supported_regions = [
            'North America', 'Western Europe', 'Eastern Europe', 'East Asia',
            'Southeast Asia', 'South Asia', 'South America', 'Africa',
            'Australia/Oceania', 'Central America'
        ]
        
        # Initialize regional cost of living data
        self.cost_of_living_index = {
            'North America': {
                'US': 1.0,  # Base index
                'CA': 0.85
            },
            'Western Europe': {
                'GB': 0.95,
                'DE': 0.80,
                'FR': 0.85,
                'NL': 0.88,
                'CH': 1.25,
                'SE': 0.90,
                'NO': 1.10
            },
            'East Asia': {
                'JP': 0.85,
                'SG': 0.90,
                'HK': 1.05,
                'CN': 0.40,
                'KR': 0.65
            },
            'Southeast Asia': {
                'TH': 0.35,
                'MY': 0.40,
                'ID': 0.30,
                'PH': 0.35,
                'VN': 0.25
            },
            'Australia/Oceania': {
                'AU': 0.95,
                'NZ': 0.85
            }
        }
        
        # Experience level multipliers
        self.experience_multipliers = {
            'junior': 0.7,
            'mid': 1.0,
            'senior': 1.4,
            'principal': 1.8,
            'director': 2.2
        }
        
        # Industry compensation multipliers
        self.industry_multipliers = {
            'big_tech': 1.3,
            'unicorn_startup': 1.2,
            'financial_services': 1.25,
            'consulting': 1.15,
            'traditional_enterprise': 1.0,
            'startup': 0.85,
            'non_profit': 0.7,
            'government': 0.8
        }
        
        # Benefits values by region (annual USD equivalent)
        self.benefits_values = {
            'North America': {
                'healthcare': 8000,
                'retirement': 6000,
                'vacation': 4000,
                'other': 3000
            },
            'Western Europe': {
                'healthcare': 2000,  # Often government provided
                'retirement': 8000,
                'vacation': 6000,
                'other': 4000
            },
            'East Asia': {
                'healthcare': 3000,
                'retirement': 4000,
                'vacation': 2000,
                'other': 2000
            },
            'Southeast Asia': {
                'healthcare': 1500,
                'retirement': 2000,
                'vacation': 1500,
                'other': 1000
            }
        }
    
    def add_salary_data_point(self, job_data: Dict[str, Any]) -> None:
        """Add a salary data point for benchmarking analysis."""
        try:
            if not job_data.get('salary_usd_equivalent'):
                return  # Skip jobs without salary data
                
            data_point = {
                'title': job_data.get('title', ''),
                'company': job_data.get('company', ''),
                'region': job_data.get('region', 'unknown'),
                'country_code': job_data.get('country_code', ''),
                'salary_usd': float(job_data.get('salary_usd_equivalent', 0)),
                'local_salary': job_data.get('salary_original'),
                'local_currency': job_data.get('currency', 'USD'),
                'experience_level': self._infer_experience_level(job_data.get('title', '')),
                'company_size': job_data.get('company_size', 'unknown'),
                'industry': job_data.get('industry', 'technology'),
                'remote_option': job_data.get('remote_option', False),
                'posted_date': job_data.get('date_posted', datetime.now()),
                'source': job_data.get('source_site', 'unknown')
            }
            
            self.salary_data.append(data_point)
            
            # Keep only recent data for accuracy
            cutoff_date = datetime.now() - timedelta(days=180)
            self.salary_data = [
                data for data in self.salary_data 
                if isinstance(data['posted_date'], datetime) and data['posted_date'] > cutoff_date
            ]
            
        except Exception as e:
            logger.warning(f"Failed to add salary data point: {e}")
    
    def benchmark_salary(self, role: str, region: str, country: str, 
                        experience_level: str, salary_range: str = None) -> 'SalaryAnalysis':
        """Benchmark a salary against market data.
        
        Args:
            role: Job role/title
            region: Geographic region
            country: Country name
            experience_level: Experience level (junior, mid, senior, etc.)
            salary_range: Optional salary range string (e.g., "120000-150000 SGD")
            
        Returns:
            SalaryAnalysis object with benchmarking results
        """
        try:
            # Map country to country code
            country_code_map = {
                'singapore': 'SG',
                'germany': 'DE', 
                'japan': 'JP',
                'united kingdom': 'GB',
                'united states': 'US',
                'canada': 'CA',
                'australia': 'AU',
                'france': 'FR',
                'netherlands': 'NL',
                'switzerland': 'CH',
                'india': 'IN'
            }
            
            country_code = country_code_map.get(country.lower(), 'US')
            role_category = self._categorize_role(role)
            
            # Get salary benchmark
            benchmark = self.get_salary_benchmark(
                role_category=role_category,
                region=region,
                country_code=country_code,
                experience_level=experience_level
            )
            
            # Parse salary range
            salary_value = self._parse_salary_range(salary_range)
            
            # Calculate market position
            market_position = self.get_market_position(
                current_salary=salary_value,
                role_category=role_category,
                region=region,
                country_code=country_code,
                experience_level=experience_level
            )
            
            # Create analysis result
            return SalaryAnalysis(
                market_position=market_position,
                regional_comparison=self._get_regional_comparison(benchmark, salary_value),
                confidence_score=self._calculate_confidence_score(benchmark.sample_size),
                salary_range=salary_range,
                currency_info=self._get_currency_info(country_code)
            )
            
        except Exception as e:
            logger.error(f"Failed to benchmark salary: {e}")
            return self._create_default_salary_analysis(role, region, salary_range)
    
    def get_salary_benchmark(self, 
                           role_category: str, 
                           region: str,
                           country_code: str,
                           experience_level: str = 'mid') -> SalaryBenchmark:
        """Get comprehensive salary benchmark for a role and location."""
        cache_key = f"{role_category}_{region}_{country_code}_{experience_level}"
        
        # Check cache
        if cache_key in self.benchmark_cache:
            cached_result, cache_time = self.benchmark_cache[cache_key]
            if datetime.now() - cache_time < self.cache_expiry:
                return cached_result
        
        try:
            # Filter relevant salary data
            relevant_data = [
                data for data in self.salary_data
                if (self._categorize_role(data['title']) == role_category and
                    data['region'] == region and
                    (not country_code or data['country_code'] == country_code) and
                    data['experience_level'] == experience_level and
                    data['salary_usd'] > 0)
            ]
            
            if len(relevant_data) < 3:
                # Insufficient data - use estimated benchmark
                return self._create_estimated_benchmark(role_category, region, country_code, experience_level)
            
            # Calculate salary statistics
            salaries = [data['salary_usd'] for data in relevant_data]
            salaries.sort()
            
            median_salary = statistics.median(salaries)
            mean_salary = statistics.mean(salaries)
            
            # Calculate percentiles
            n = len(salaries)
            percentile_10 = salaries[max(0, int(n * 0.1) - 1)]
            percentile_25 = salaries[max(0, int(n * 0.25) - 1)]
            percentile_75 = salaries[min(n - 1, int(n * 0.75))]
            percentile_90 = salaries[min(n - 1, int(n * 0.9))]
            
            # Get local currency info
            local_currency = self._get_primary_currency(country_code)
            local_median = self._convert_to_local_currency(median_salary, local_currency)
            
            # Calculate cost of living adjustment
            col_factor = self._get_cost_of_living_factor(region, country_code)
            cost_of_living_adjusted = median_salary * col_factor
            
            # Determine confidence level
            confidence_level = self._calculate_confidence_level(len(relevant_data))
            
            result = SalaryBenchmark(
                role_category=role_category,
                region=region,
                country_code=country_code,
                experience_level=experience_level,
                median_salary_usd=median_salary,
                mean_salary_usd=mean_salary,
                percentile_10=percentile_10,
                percentile_25=percentile_25,
                percentile_75=percentile_75,
                percentile_90=percentile_90,
                local_currency=local_currency,
                local_median=local_median,
                cost_of_living_adjusted=cost_of_living_adjusted,
                sample_size=len(relevant_data),
                confidence_level=confidence_level,
                last_updated=datetime.now()
            )
            
            # Cache result
            self.benchmark_cache[cache_key] = (result, datetime.now())
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate salary benchmark: {e}")
            return self._create_estimated_benchmark(role_category, region, country_code, experience_level)
    
    def analyze_compensation_package(self, 
                                   base_salary: float,
                                   equity_percentage: float,
                                   company_valuation: float,
                                   bonus_percentage: float,
                                   region: str,
                                   country_code: str) -> CompensationPackage:
        """Analyze complete compensation package."""
        try:
            # Calculate equity value (simplified)
            equity_value = (equity_percentage / 100) * company_valuation if company_valuation > 0 else 0
            
            # Calculate bonus potential
            bonus_potential = base_salary * (bonus_percentage / 100)
            
            # Calculate total compensation
            total_compensation = base_salary + equity_value + bonus_potential
            
            # Calculate benefits value
            regional_benefits = self.benefits_values.get(region, self.benefits_values['North America'])
            benefits_value = sum(regional_benefits.values())
            
            # Calculate remote premium (if applicable)
            remote_premium = base_salary * 0.05  # 5% premium for remote roles
            
            # Get local currency
            local_currency = self._get_primary_currency(country_code)
            
            # Calculate purchasing power
            col_factor = self._get_cost_of_living_factor(region, country_code)
            purchasing_power = total_compensation * col_factor
            
            return CompensationPackage(
                base_salary=base_salary,
                equity_value=equity_value,
                bonus_potential=bonus_potential,
                total_compensation=total_compensation,
                benefits_value=benefits_value,
                remote_premium=remote_premium,
                currency=local_currency,
                purchasing_power=purchasing_power
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze compensation package: {e}")
            return CompensationPackage(
                base_salary=base_salary,
                equity_value=0,
                bonus_potential=0,
                total_compensation=base_salary,
                benefits_value=15000,  # Default
                remote_premium=0,
                currency='USD',
                purchasing_power=base_salary
            )
    
    def get_market_position(self, 
                          current_salary: float,
                          role_category: str,
                          region: str,
                          country_code: str,
                          experience_level: str = 'mid') -> MarketPosition:
        """Analyze current salary position relative to market."""
        try:
            # Get market benchmark
            benchmark = self.get_salary_benchmark(role_category, region, country_code, experience_level)
            
            # Calculate percentile position
            market_percentile = self._calculate_percentile_position(current_salary, benchmark)
            
            # Calculate gaps
            gap_to_median = benchmark.median_salary_usd - current_salary
            gap_to_75th = benchmark.percentile_75 - current_salary
            
            # Determine competitiveness
            competitiveness = self._assess_competitiveness(market_percentile)
            
            # Calculate negotiation potential
            negotiation_potential = self._calculate_negotiation_potential(current_salary, benchmark)
            
            # Determine market direction
            market_direction = self._assess_market_direction(role_category, region)
            
            return MarketPosition(
                current_salary=current_salary,
                market_percentile=market_percentile,
                gap_to_median=gap_to_median,
                gap_to_75th=gap_to_75th,
                competitiveness=competitiveness,
                negotiation_potential=negotiation_potential,
                market_direction=market_direction
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze market position: {e}")
            return MarketPosition(
                current_salary=current_salary,
                market_percentile=50.0,
                gap_to_median=0,
                gap_to_75th=0,
                competitiveness='competitive',
                negotiation_potential=0.1,
                market_direction='stable'
            )
    
    def get_regional_salary_comparison(self, 
                                     role_category: str,
                                     experience_level: str = 'mid') -> Dict[str, SalaryBenchmark]:
        """Compare salaries across different regions for the same role."""
        regions = ['North America', 'Western Europe', 'East Asia', 'Southeast Asia']
        comparison = {}
        
        for region in regions:
            # Get primary country for each region
            country_map = {
                'North America': 'US',
                'Western Europe': 'GB',
                'East Asia': 'SG',
                'Southeast Asia': 'SG'
            }
            
            country_code = country_map[region]
            benchmark = self.get_salary_benchmark(role_category, region, country_code, experience_level)
            comparison[region] = benchmark
            
        return comparison
    
    def generate_salary_insights(self, 
                               role_category: str,
                               region: str,
                               experience_level: str = 'mid') -> List[str]:
        """Generate insights about salary trends and market conditions."""
        insights = []
        
        try:
            # Get regional comparison
            regional_comparison = self.get_regional_salary_comparison(role_category, experience_level)
            
            # Find highest and lowest paying regions
            sorted_regions = sorted(
                regional_comparison.items(),
                key=lambda x: x[1].median_salary_usd,
                reverse=True
            )
            
            if len(sorted_regions) >= 2:
                highest_region = sorted_regions[0]
                lowest_region = sorted_regions[-1]
                
                insights.append(
                    f"Highest paying region: {highest_region[0]} "
                    f"(${highest_region[1].median_salary_usd:,.0f} median)"
                )
                
                salary_difference = highest_region[1].median_salary_usd - lowest_region[1].median_salary_usd
                percentage_diff = (salary_difference / lowest_region[1].median_salary_usd) * 100
                
                insights.append(
                    f"Pay gap between regions: {percentage_diff:.1f}% "
                    f"(${salary_difference:,.0f} difference)"
                )
            
            # Current region insights
            current_benchmark = regional_comparison.get(region)
            if current_benchmark:
                confidence_msg = {
                    'high': 'Based on strong data',
                    'medium': 'Based on moderate data',
                    'low': 'Based on limited data'
                }.get(current_benchmark.confidence_level, '')
                
                insights.append(
                    f"{region} median: ${current_benchmark.median_salary_usd:,.0f} "
                    f"({confidence_msg})"
                )
                
                # Sample size insight
                if current_benchmark.sample_size < 10:
                    insights.append(
                        f"Limited salary data available ({current_benchmark.sample_size} samples) - "
                        f"estimates may vary"
                    )
            
            # Experience level comparison
            if experience_level == 'mid':
                senior_benchmark = self.get_salary_benchmark(role_category, region, 'US', 'senior')
                if senior_benchmark.median_salary_usd > 0:
                    progression = senior_benchmark.median_salary_usd - current_benchmark.median_salary_usd
                    insights.append(
                        f"Senior level premium: ${progression:,.0f} "
                        f"({(progression/current_benchmark.median_salary_usd)*100:.1f}% increase)"
                    )
            
            # Market timing insight
            market_direction = self._assess_market_direction(role_category, region)
            direction_messages = {
                'increasing': 'Salaries trending upward - good time to negotiate',
                'stable': 'Stable salary market - standard negotiation applies',
                'decreasing': 'Market softening - consider total compensation package'
            }
            insights.append(direction_messages.get(market_direction, 'Market conditions unclear'))
            
        except Exception as e:
            logger.error(f"Failed to generate salary insights: {e}")
            insights.append("Unable to generate detailed salary insights at this time")
            
        return insights[:6]  # Limit to top 6 insights
    
    # Helper methods
    def _categorize_role(self, title: str) -> str:
        """Categorize a job title for salary analysis."""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['technical program manager', 'tpm', 'program manager']):
            return 'technical_program_manager'
        elif any(keyword in title_lower for keyword in ['product manager', 'product lead', 'product owner']):
            return 'product_manager'
        elif any(keyword in title_lower for keyword in ['engineering manager', 'engineering lead', 'tech lead']):
            return 'engineering_manager'
        elif any(keyword in title_lower for keyword in ['data scientist', 'machine learning', 'data engineer']):
            return 'data_science'
        elif any(keyword in title_lower for keyword in ['consultant', 'strategy']):
            return 'consultant'
        else:
            return 'other'
    
    def _infer_experience_level(self, title: str) -> str:
        """Infer experience level from job title."""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['senior', 'sr.', 'lead']):
            return 'senior'
        elif any(keyword in title_lower for keyword in ['principal', 'staff', 'architect']):
            return 'principal'
        elif any(keyword in title_lower for keyword in ['director', 'vp', 'head of']):
            return 'director'
        elif any(keyword in title_lower for keyword in ['junior', 'jr.', 'associate', 'entry']):
            return 'junior'
        else:
            return 'mid'
    
    def _get_primary_currency(self, country_code: str) -> str:
        """Get primary currency for a country."""
        currency_map = {
            'US': 'USD', 'CA': 'CAD', 'GB': 'GBP', 'DE': 'EUR',
            'FR': 'EUR', 'NL': 'EUR', 'CH': 'CHF', 'SE': 'SEK',
            'NO': 'NOK', 'JP': 'JPY', 'SG': 'SGD', 'HK': 'HKD',
            'CN': 'CNY', 'KR': 'KRW', 'AU': 'AUD', 'NZ': 'NZD'
        }
        return currency_map.get(country_code, 'USD')
    
    def _convert_to_local_currency(self, usd_amount: float, target_currency: str) -> float:
        """Convert USD amount to local currency."""
        if target_currency == 'USD':
            return usd_amount
            
        try:
            return self.currency_converter.convert('USD', target_currency, usd_amount)
        except Exception:
            # Fallback to approximate rates
            approximate_rates = {
                'EUR': 0.85, 'GBP': 0.75, 'CAD': 1.35, 'CHF': 0.90,
                'SEK': 10.5, 'NOK': 10.8, 'JPY': 150, 'SGD': 1.35,
                'HKD': 7.8, 'CNY': 7.2, 'KRW': 1300, 'AUD': 1.55, 'NZD': 1.65
            }
            rate = approximate_rates.get(target_currency, 1.0)
            return usd_amount * rate
    
    def _get_cost_of_living_factor(self, region: str, country_code: str) -> float:
        """Get cost of living adjustment factor."""
        regional_data = self.cost_of_living_index.get(region, {})
        return regional_data.get(country_code, 0.8)
    
    def _calculate_confidence_level(self, sample_size: int) -> str:
        """Calculate confidence level based on sample size."""
        if sample_size >= 20:
            return 'high'
        elif sample_size >= 8:
            return 'medium'
        else:
            return 'low'
    
    def _create_estimated_benchmark(self, role_category: str, region: str, 
                                  country_code: str, experience_level: str) -> SalaryBenchmark:
        """Create estimated benchmark when insufficient data is available."""
        # Base salary estimates by role and region
        base_estimates = {
            'North America': {
                'technical_program_manager': 140000,
                'product_manager': 135000,
                'engineering_manager': 155000,
                'data_science': 125000,
                'consultant': 120000
            },
            'Western Europe': {
                'technical_program_manager': 90000,
                'product_manager': 85000,
                'engineering_manager': 95000,
                'data_science': 80000,
                'consultant': 75000
            },
            'East Asia': {
                'technical_program_manager': 85000,
                'product_manager': 80000,
                'engineering_manager': 90000,
                'data_science': 75000,
                'consultant': 70000
            },
            'Southeast Asia': {
                'technical_program_manager': 55000,
                'product_manager': 50000,
                'engineering_manager': 60000,
                'data_science': 45000,
                'consultant': 40000
            }
        }
        
        base_salary = base_estimates.get(region, {}).get(role_category, 100000)
        
        # Apply experience multiplier
        exp_multiplier = self.experience_multipliers.get(experience_level, 1.0)
        adjusted_salary = base_salary * exp_multiplier
        
        # Calculate percentiles (approximate distribution)
        percentile_10 = adjusted_salary * 0.7
        percentile_25 = adjusted_salary * 0.85
        percentile_75 = adjusted_salary * 1.25
        percentile_90 = adjusted_salary * 1.5
        
        local_currency = self._get_primary_currency(country_code)
        local_median = self._convert_to_local_currency(adjusted_salary, local_currency)
        col_factor = self._get_cost_of_living_factor(region, country_code)
        
        return SalaryBenchmark(
            role_category=role_category,
            region=region,
            country_code=country_code,
            experience_level=experience_level,
            median_salary_usd=adjusted_salary,
            mean_salary_usd=adjusted_salary * 1.05,
            percentile_10=percentile_10,
            percentile_25=percentile_25,
            percentile_75=percentile_75,
            percentile_90=percentile_90,
            local_currency=local_currency,
            local_median=local_median,
            cost_of_living_adjusted=adjusted_salary * col_factor,
            sample_size=0,
            confidence_level='estimated',
            last_updated=datetime.now()
        )
    
    def _calculate_percentile_position(self, salary: float, benchmark: SalaryBenchmark) -> float:
        """Calculate what percentile a salary represents."""
        if salary <= benchmark.percentile_10:
            return 10.0
        elif salary <= benchmark.percentile_25:
            return 25.0
        elif salary <= benchmark.median_salary_usd:
            return 50.0
        elif salary <= benchmark.percentile_75:
            return 75.0
        elif salary <= benchmark.percentile_90:
            return 90.0
        else:
            return 95.0
    
    def _assess_competitiveness(self, percentile: float) -> str:
        """Assess salary competitiveness based on percentile."""
        if percentile >= 75:
            return 'above_market'
        elif percentile >= 40:
            return 'competitive'
        else:
            return 'below_market'
    
    def _calculate_negotiation_potential(self, current_salary: float, benchmark: SalaryBenchmark) -> float:
        """Calculate potential salary increase through negotiation."""
        if current_salary < benchmark.percentile_25:
            return 0.15  # 15% potential increase
        elif current_salary < benchmark.median_salary_usd:
            return 0.10  # 10% potential increase
        elif current_salary < benchmark.percentile_75:
            return 0.05  # 5% potential increase
        else:
            return 0.02  # 2% potential increase
    
    def _assess_market_direction(self, role_category: str, region: str) -> str:
        """Assess salary market direction based on recent trends."""
        # This would integrate with the market trend analyzer
        # For now, return estimated direction based on region/role
        growth_regions = ['Southeast Asia', 'East Asia']
        if region in growth_regions:
            return 'increasing'
        else:
            return 'stable'
    
    def _parse_salary_range(self, salary_range: str = None) -> float:
        """Parse salary range string to get numeric value."""
        try:
            if salary_range is None:
                return 100000.0  # Default when no salary provided
                
            import re
            # Extract numbers from salary string
            numbers = re.findall(r'\d+', salary_range.replace(',', ''))
            if numbers:
                # Take average if range, otherwise single value
                values = [int(num) for num in numbers if len(num) >= 4]  # Ignore small numbers
                if len(values) >= 2:
                    return (values[0] + values[1]) / 2
                elif len(values) == 1:
                    return float(values[0])
            return 100000.0  # Default fallback
        except Exception:
            return 100000.0
    
    def _get_regional_comparison(self, benchmark: SalaryBenchmark, salary: float) -> Dict[str, Any]:
        """Get regional comparison data."""
        return {
            'market_median': benchmark.median_salary_usd,
            'your_salary': salary,
            'difference_pct': ((salary - benchmark.median_salary_usd) / benchmark.median_salary_usd * 100) if benchmark.median_salary_usd > 0 else 0,
            'region': benchmark.region,
            'sample_size': benchmark.sample_size
        }
    
    def _calculate_confidence_score(self, sample_size: int) -> float:
        """Calculate confidence score based on sample size."""
        if sample_size >= 50:
            return 0.9
        elif sample_size >= 20:
            return 0.7
        elif sample_size >= 10:
            return 0.5
        else:
            return 0.3
    
    def _get_currency_info(self, country_code: str) -> Dict[str, str]:
        """Get currency information for country."""
        currency_map = {
            'SG': {'code': 'SGD', 'name': 'Singapore Dollar'},
            'DE': {'code': 'EUR', 'name': 'Euro'},
            'JP': {'code': 'JPY', 'name': 'Japanese Yen'},
            'GB': {'code': 'GBP', 'name': 'British Pound'},
            'US': {'code': 'USD', 'name': 'US Dollar'},
            'CA': {'code': 'CAD', 'name': 'Canadian Dollar'},
            'AU': {'code': 'AUD', 'name': 'Australian Dollar'}
        }
        return currency_map.get(country_code, {'code': 'USD', 'name': 'US Dollar'})
    
    def _create_default_salary_analysis(self, role: str, region: str, salary_range: str) -> SalaryAnalysis:
        """Create default salary analysis when data is insufficient."""
        salary_value = self._parse_salary_range(salary_range)
        
        default_market_position = MarketPosition(
            current_salary=salary_value,
            market_percentile=50.0,
            gap_to_median=0.0,
            gap_to_75th=salary_value * 0.15,
            competitiveness='competitive',
            negotiation_potential=0.1,
            market_direction='stable'
        )
        
        return SalaryAnalysis(
            market_position=default_market_position,
            regional_comparison={'region': region, 'market_median': salary_value, 'sample_size': 0},
            confidence_score=0.3,
            salary_range=salary_range,
            currency_info={'code': 'USD', 'name': 'US Dollar'}
        )


# Global instance for use across the application
salary_benchmarking_service = SalaryBenchmarkingService()
