"""Indeed job board scraper."""

import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.base import BaseJobScraper, logger

class IndeedScraper(BaseJobScraper):
    """Scraper for Indeed jobs."""
    
    BASE_SEARCH_URL = "https://www.indeed.com/jobs?"
    
    def __init__(self, search_terms: List[str], location: Optional[str] = None):
        """Initialize Indeed scraper."""
        super().__init__(search_terms, location)
        
    async def search(self, search_term: str) -> List[JobPosting]:
        """Search Indeed jobs."""
        params = {
            "q": search_term,
            "l": self.location or "United States",
            "fromage": 7,  # Last 7 days
            "sort": "date"
        }
        
        url = self.BASE_SEARCH_URL + urlencode(params)
        soup = await self._get_page(url)
        if not soup:
            return []
            
        jobs = []
        job_cards = soup.find_all("div", class_="job_seen_beacon")
        if not job_cards:
            logger.warning("No job cards found - selectors might need updating")
            return []

        for job_card in job_cards:
            try:
                # Extract basic job info with selector maintenance
                title_text, title_ok = await self._extract_field(job_card, 'indeed', 'job_card_title')
                company_text, company_ok = await self._extract_field(job_card, 'indeed', 'job_card_company')
                location_text, location_ok = await self._extract_field(job_card, 'indeed', 'job_card_location')
                
                if not (title_ok and company_ok and location_ok):
                    logger.warning("Failed to extract required fields from job card")
                    continue
                    
                # Get job link and ID with selector maintenance
                link_elem = job_card.find("a", class_="jcs-JobTitle")
                if not link_elem or not link_elem.get("data-jk"):
                    logger.warning("No job ID found in card")
                    continue
                    
                job_id = link_elem["data-jk"]
                job_link = f"https://www.indeed.com/viewjob?jk={job_id}"
                
                # Parse relative date to datetime
                date_text = job_card.find("span", class_="date").get_text(strip=True)
                date_posted = self._parse_relative_date(date_text)
                
                # Get salary if available with selector maintenance
                salary_text, _ = await self._extract_field(job_card, 'indeed', 'job_card_salary')
                salary = salary_text if salary_text else None
                
                # Get full description
                description = await self.get_job_details(job_link)
                
                job = JobPosting(
                    id=job_id,
                    source="indeed",
                    company=company_text,
                    title=title_text,
                    location=location_text,
                    salary=salary,
                    url=job_link,
                    date_posted=date_posted,
                    description=description,
                    raw={
                        "title": title_text,
                        "company": company_text,
                        "location": location_text,
                        "salary": salary,
                        "url": job_link,
                        "posted_date": date_posted.isoformat(),
                        "description": description
                    }
                )
                jobs.append(job)
                
            except Exception as e:
                logger.error(f"Error parsing Indeed job card: {str(e)}")
                continue
                
        return jobs
        
    async def get_job_details(self, url: str) -> Optional[str]:
        """Get full job description from Indeed job page."""
        soup = await self._get_page(url)
        if not soup:
            return None
            
        try:
            # Extract job description with selector maintenance
            description_text, description_ok = await self._extract_field(
                soup,
                'indeed',
                'job_description'
            )
            
            if description_ok:
                return description_text
                
            # If selector maintenance failed, try legacy selector as last resort
            description_div = soup.find("div", id="jobDescriptionText")
            if description_div:
                text = self._clean_text(description_div.get_text())
                # Use this as sample for future selector repair
                await self._extract_field(
                    soup,
                    'indeed',
                    'job_description',
                    sample_content=text
                )
                return text
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting Indeed job description: {str(e)}")
            return None
            
    def _parse_relative_date(self, date_text: str) -> datetime:
        """Convert Indeed's relative date text to datetime.
        
        Args:
            date_text: Text like "3 days ago", "Just posted", etc.
            
        Returns:
            Datetime object
        """
        now = datetime.now(timezone.utc)
        
        if "just posted" in date_text.lower():
            return now
            
        if "today" in date_text.lower():
            return now
            
        if "yesterday" in date_text.lower():
            return now - timedelta(days=1)
            
        # Parse "X days ago"
        match = re.search(r"(\d+)\s+days?\s+ago", date_text.lower())
        if match:
            days = int(match.group(1))
            return now - timedelta(days=days)
            
        # Parse "X hours ago"
        match = re.search(r"(\d+)\s+hours?\s+ago", date_text.lower())
        if match:
            hours = int(match.group(1))
            return now - timedelta(hours=hours)
            
        # If we can't parse it, just use current time
        return now
