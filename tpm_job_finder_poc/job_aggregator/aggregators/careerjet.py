"""Careerjet API connector for international job aggregation."""

import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pycountry
from forex_python.converter import CurrencyRates


logger = logging.getLogger(__name__)


class CareerjetConnector:
    """Careerjet API connector for international job search."""
    
    source = "careerjet"
    
    # Supported Careerjet locales mapped to regions
    LOCALE_REGIONS = {
        # North America
        "en_US": {"region": "North America", "country": "US", "currency": "USD"},
        "en_CA": {"region": "North America", "country": "CA", "currency": "CAD"},
        "fr_CA": {"region": "North America", "country": "CA", "currency": "CAD"},
        
        # Western Europe
        "en_GB": {"region": "Western Europe", "country": "GB", "currency": "GBP"},
        "de_DE": {"region": "Western Europe", "country": "DE", "currency": "EUR"},
        "fr_FR": {"region": "Western Europe", "country": "FR", "currency": "EUR"},
        "it_IT": {"region": "Western Europe", "country": "IT", "currency": "EUR"},
        "es_ES": {"region": "Western Europe", "country": "ES", "currency": "EUR"},
        "nl_NL": {"region": "Western Europe", "country": "NL", "currency": "EUR"},
        "pt_PT": {"region": "Western Europe", "country": "PT", "currency": "EUR"},
        "da_DK": {"region": "Western Europe", "country": "DK", "currency": "DKK"},
        "sv_SE": {"region": "Western Europe", "country": "SE", "currency": "SEK"},
        "no_NO": {"region": "Western Europe", "country": "NO", "currency": "NOK"},
        "fi_FI": {"region": "Western Europe", "country": "FI", "currency": "EUR"},
        
        # Eastern Europe
        "pl_PL": {"region": "Eastern Europe", "country": "PL", "currency": "PLN"},
        "cs_CZ": {"region": "Eastern Europe", "country": "CZ", "currency": "CZK"},
        "hu_HU": {"region": "Eastern Europe", "country": "HU", "currency": "HUF"},
        "ru_RU": {"region": "Eastern Europe", "country": "RU", "currency": "RUB"},
        "uk_UA": {"region": "Eastern Europe", "country": "UA", "currency": "UAH"},
        
        # East Asia
        "ja_JP": {"region": "East Asia", "country": "JP", "currency": "JPY"},
        "ko_KR": {"region": "East Asia", "country": "KR", "currency": "KRW"},
        "zh_CN": {"region": "East Asia", "country": "CN", "currency": "CNY"},
        "zh_HK": {"region": "East Asia", "country": "HK", "currency": "HKD"},
        "zh_TW": {"region": "East Asia", "country": "TW", "currency": "TWD"},
        
        # Southeast Asia
        "en_SG": {"region": "Southeast Asia", "country": "SG", "currency": "SGD"},
        "en_MY": {"region": "Southeast Asia", "country": "MY", "currency": "MYR"},
        "th_TH": {"region": "Southeast Asia", "country": "TH", "currency": "THB"},
        "id_ID": {"region": "Southeast Asia", "country": "ID", "currency": "IDR"},
        "vi_VN": {"region": "Southeast Asia", "country": "VN", "currency": "VND"},
        "en_PH": {"region": "Southeast Asia", "country": "PH", "currency": "PHP"},
        
        # South Asia
        "en_IN": {"region": "South Asia", "country": "IN", "currency": "INR"},
        "en_PK": {"region": "South Asia", "country": "PK", "currency": "PKR"},
        "en_BD": {"region": "South Asia", "country": "BD", "currency": "BDT"},
        
        # Australia/Oceania
        "en_AU": {"region": "Australia/Oceania", "country": "AU", "currency": "AUD"},
        "en_NZ": {"region": "Australia/Oceania", "country": "NZ", "currency": "NZD"},
        
        # South America
        "pt_BR": {"region": "South America", "country": "BR", "currency": "BRL"},
        "es_AR": {"region": "South America", "country": "AR", "currency": "ARS"},
        "es_CL": {"region": "South America", "country": "CL", "currency": "CLP"},
        "es_CO": {"region": "South America", "country": "CO", "currency": "COP"},
        "es_MX": {"region": "Central America", "country": "MX", "currency": "MXN"},
        
        # Africa
        "en_ZA": {"region": "Africa", "country": "ZA", "currency": "ZAR"},
        "ar_EG": {"region": "Africa", "country": "EG", "currency": "EGP"},
        "fr_MA": {"region": "Africa", "country": "MA", "currency": "MAD"},
    }
    
    def __init__(self, affiliate_id: str, locales: Optional[List[str]] = None):
        """Initialize Careerjet connector.
        
        Args:
            affiliate_id: Careerjet affiliate ID for API access
            locales: List of locales to search (defaults to major English-speaking markets)
        """
        self.affiliate_id = affiliate_id
        self.locales = locales or ["en_US", "en_GB", "en_CA", "en_AU", "en_SG"]
        self.currency_converter = CurrencyRates()
        
        # Base URLs for different locales
        self.locale_urls = {
            locale: f"http://public-api.careerjet.com/search?locale_code={locale}"
            for locale in self.locales if locale in self.LOCALE_REGIONS
        }
        
        logger.info(f"Initialized Careerjet connector for locales: {list(self.locale_urls.keys())}")
    
    def fetch_since(self, since: datetime) -> List[Dict]:
        """Fetch jobs posted since the given datetime.
        
        Args:
            since: Fetch jobs posted after this datetime
            
        Returns:
            List of job dictionaries with standardized format
        """
        all_jobs = []
        
        for locale in self.locale_urls.keys():
            try:
                jobs = self._fetch_jobs_for_locale(locale, since)
                all_jobs.extend(jobs)
                logger.info(f"Fetched {len(jobs)} jobs from Careerjet locale: {locale}")
            except Exception as e:
                logger.error(f"Error fetching jobs from Careerjet locale {locale}: {e}")
                
        logger.info(f"Total Careerjet jobs fetched: {len(all_jobs)}")
        return all_jobs
    
    def _fetch_jobs_for_locale(self, locale: str, since: datetime) -> List[Dict]:
        """Fetch jobs for a specific locale.
        
        Args:
            locale: Locale identifier (e.g., 'en_US')
            since: Fetch jobs posted after this datetime
            
        Returns:
            List of job dictionaries for this locale
        """
        jobs = []
        region_info = self.LOCALE_REGIONS[locale]
        
        # Search terms relevant to TPM roles
        search_terms = [
            "technical program manager",
            "senior technical program manager", 
            "principal technical program manager",
            "TPM",
            "program manager",
            "technical project manager"
        ]
        
        for search_term in search_terms:
            try:
                # Calculate days since for API parameter
                days_old = max(1, (datetime.now() - since).days)
                
                # Make HTTP request to Careerjet API
                params = {
                    'keywords': search_term,
                    'location': '',  # Global search within locale
                    'affid': self.affiliate_id,
                    'user_ip': '11.22.33.44',  # Required by API
                    'user_agent': 'Mozilla/5.0 (TPM Job Finder)',
                    'pagesize': 50,  # Maximum results per page
                    'page': 1,
                    'sort': 'date',  # Sort by posting date
                    'locale_code': locale
                }
                
                response = requests.get(
                    'http://public-api.careerjet.com/search',
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get('type') == 'JOBS':
                    for job_data in result.get('jobs', []):
                        job = self._normalize_job(job_data, locale, region_info, search_term)
                        if job and self._is_recent_job(job, since):
                            jobs.append(job)
                            
            except Exception as e:
                logger.error(f"Error searching Careerjet for '{search_term}' in {locale}: {e}")
                
        return jobs
    
    def _normalize_job(self, job_data: Dict, locale: str, region_info: Dict, search_term: str) -> Optional[Dict]:
        """Normalize job data to standard format.
        
        Args:
            job_data: Raw job data from Careerjet API
            locale: Locale identifier
            region_info: Region metadata
            search_term: Search term that found this job
            
        Returns:
            Normalized job dictionary or None if invalid
        """
        try:
            # Extract salary information
            salary_min, salary_max, local_salary = self._extract_salary(job_data)
            usd_equivalent = self._convert_to_usd(salary_max or salary_min, region_info['currency'])
            
            # Determine location details
            location = job_data.get('locations', '')
            country_name = self._get_country_name(region_info['country'])
            
            # Check visa requirements for US citizens
            visa_required = self._requires_visa(region_info['country'])
            
            return {
                "title": job_data.get('title', ''),
                "company": job_data.get('company', ''),
                "location": f"{location}, {country_name}" if location else country_name,
                "posted_date": job_data.get('date', ''),
                "canonical_url": job_data.get('url', ''),
                "source_site": self.source,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "local_salary": local_salary,
                "usd_equivalent": usd_equivalent,
                "description": job_data.get('description', ''),
                "locale": locale,
                "region": region_info['region'],
                "country_code": region_info['country'],
                "currency": region_info['currency'],
                "visa_required": visa_required,
                "search_term": search_term,
                "raw_data": job_data
            }
            
        except Exception as e:
            logger.error(f"Error normalizing job data: {e}")
            return None
    
    def _extract_salary(self, job_data: Dict) -> tuple:
        """Extract salary information from job data.
        
        Args:
            job_data: Raw job data
            
        Returns:
            Tuple of (salary_min, salary_max, local_salary_string)
        """
        salary_text = job_data.get('salary', '')
        if not salary_text or salary_text.lower() in ['', 'unknown', 'not specified']:
            return None, None, salary_text
        
        # Try to extract numeric values
        import re
        numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
        
        if len(numbers) >= 2:
            try:
                salary_min = int(numbers[0].replace(',', ''))
                salary_max = int(numbers[1].replace(',', ''))
                return salary_min, salary_max, salary_text
            except ValueError:
                pass
        elif len(numbers) == 1:
            try:
                salary = int(numbers[0].replace(',', ''))
                return salary, salary, salary_text
            except ValueError:
                pass
                
        return None, None, salary_text
    
    def _convert_to_usd(self, amount: Optional[float], currency: str) -> Optional[float]:
        """Convert salary amount to USD equivalent.
        
        Args:
            amount: Salary amount in local currency
            currency: Local currency code
            
        Returns:
            USD equivalent amount or None if conversion fails
        """
        if not amount or currency == 'USD':
            return amount
            
        try:
            # Use forex-python for currency conversion
            usd_amount = self.currency_converter.convert(currency, 'USD', amount)
            return round(usd_amount, 2) if usd_amount else None
        except Exception as e:
            logger.warning(f"Currency conversion failed for {amount} {currency}: {e}")
            return None
    
    def _get_country_name(self, country_code: str) -> str:
        """Get full country name from country code.
        
        Args:
            country_code: ISO 2-letter country code
            
        Returns:
            Full country name
        """
        try:
            country = pycountry.countries.get(alpha_2=country_code)
            return country.name if country else country_code
        except Exception:
            return country_code
    
    def _requires_visa(self, country_code: str) -> bool:
        """Check if country requires work visa for US citizens.
        
        Args:
            country_code: ISO 2-letter country code
            
        Returns:
            True if visa required, False otherwise
        """
        # Simplified visa requirements for US citizens
        visa_free_work = {'CA'}  # NAFTA/USMCA
        return country_code not in visa_free_work and country_code != 'US'
    
    def _is_recent_job(self, job: Dict, since: datetime) -> bool:
        """Check if job was posted since the given datetime.
        
        Args:
            job: Job dictionary
            since: Cutoff datetime
            
        Returns:
            True if job is recent enough
        """
        posted_date = job.get('posted_date', '')
        if not posted_date:
            return True  # Include jobs without date
            
        try:
            # Parse various date formats that Careerjet might return
            from dateutil.parser import parse
            job_date = parse(posted_date)
            return job_date >= since
        except Exception:
            return True  # Include jobs with unparseable dates
