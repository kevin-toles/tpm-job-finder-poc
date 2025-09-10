"""LinkedIn job board scraper."""

import re
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from job_normalizer.jobs.schema import JobPosting
from job_aggregator.scrapers.base import BaseJobScraper, logger

class LinkedInScraper(BaseJobScraper):
    """Scraper for LinkedIn jobs."""
    
    BASE_SEARCH_URL = "https://www.linkedin.com/jobs/search?"
    
    def __init__(self, search_terms: List[str], location: Optional[str] = None):
        """Initialize LinkedIn scraper."""
        super().__init__(search_terms, location)
        
    async def search(self, search_term: str) -> List[JobPosting]:
        """Search LinkedIn jobs."""
        params = {
            "keywords": search_term,
            "location": self.location or "United States",
            "f_TPR": "r604800",  # Last 7 days
            "position": 1,
            "pageNum": 0
        }
        
        url = self.BASE_SEARCH_URL + urlencode(params)
        soup = await self._get_page(url)
        if not soup:
            return []
            
        jobs = []
        job_cards = soup.find_all("div", class_="job-search-card")
        if not job_cards:
            logger.warning("No job cards found - selectors might need updating")
            return []

        for job_card in job_cards:
            try:
                # Extract basic job info with selector maintenance
                title_text, title_ok = await self._extract_field(job_card, 'linkedin', 'job_card_title')
                company_text, company_ok = await self._extract_field(job_card, 'linkedin', 'job_card_company')
                location_text, location_ok = await self._extract_field(job_card, 'linkedin', 'job_card_location')
                
                if not (title_ok and company_ok and location_ok):
                    logger.warning("Failed to extract required fields from job card")
                    continue

                # Get job link
                link_elem = job_card.find("a", class_="base-card__full-link")
                if not link_elem or not link_elem.get("href"):
                    logger.warning("No job link found in card")
                    continue
                job_link = link_elem["href"]
                
                # Get post date
                date_elem = job_card.find("time", class_="job-search-card__listdate")
                if date_elem:
                    date_str = date_elem["datetime"]
                    try:
                        date_posted = datetime.fromisoformat(date_str)
                    except ValueError:
                        date_posted = datetime.now(timezone.utc)
                else:
                    date_posted = datetime.now(timezone.utc)
                
                # Get full description
                description = await self.get_job_details(job_link)
                
                job = JobPosting(
                    id=job_link.split("?")[0].split("-")[-1],  # Extract LinkedIn job ID
                    source="linkedin",
                    company=company_text,
                    title=title_text,
                    location=location_text,
                    salary=None,  # LinkedIn doesn't consistently show salary
                    url=job_link,
                    date_posted=date_posted,
                    description=description,
                    raw={
                        "title": title_text,
                        "company": company_text,
                        "location": location_text,
                        "url": job_link,
                        "posted_date": date_posted.isoformat(),
                        "description": description
                    }
                )
                jobs.append(job)
                
            except Exception as e:
                logger.error(f"Error parsing LinkedIn job card: {str(e)}")
                continue
                
        return jobs
        
    async def get_job_details(self, url: str) -> Optional[str]:
        """Get full job description from LinkedIn job page."""
        soup = await self._get_page(url)
        if not soup:
            return None
            
        try:
            # Extract job description with selector maintenance
            description_text, description_ok = await self._extract_field(
                soup,
                'linkedin',
                'job_description'
            )
            
            if description_ok:
                return description_text

            # If selector maintenance failed, try legacy selector as last resort
            description_div = soup.find("div", class_="show-more-less-html__markup")
            if description_div:
                text = self._clean_text(description_div.get_text())
                # Use this as sample for future selector repair
                await self._extract_field(
                    soup,
                    'linkedin',
                    'job_description',
                    sample_content=text
                )
                return text
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn job description: {str(e)}")
            return None
