"""LinkedIn job scraper implementation."""

from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..models.job import Job

class LinkedInScraper(BaseScraper):
    """Scraper for LinkedIn jobs."""

    BASE_URL = "https://www.linkedin.com/jobs/search"

    def _build_search_params(
        self, 
        search_terms: List[str], 
        location: Optional[str] = None
    ) -> Dict[str, str]:
        """Build search parameters for LinkedIn API."""
        params = {
            "keywords": " ".join(search_terms),
            "f_TPR": "r86400",  # Last 24 hours
            "position": "1",
            "pageNum": "0"
        }
        if location:
            params["location"] = location
        return params

    def _parse_job(self, raw_job: Dict[str, Any]) -> Job:
        """Parse raw LinkedIn job data into Job model."""
        return Job(
            title=raw_job["title"],
            company=raw_job["company"],
            location=raw_job["location"],
            description=raw_job.get("description", ""),
            url=raw_job.get("url", ""),
            source="linkedin",
            posted_date=raw_job.get("postedDate"),
            salary_range=raw_job.get("salaryRange"),
            employment_type=raw_job.get("employmentType")
        )

    async def fetch_jobs(
        self,
        search_terms: List[str],
        location: Optional[str] = None,
        max_results: int = 10
    ) -> List[Job]:
        """Fetch jobs from LinkedIn."""
        params = self._build_search_params(search_terms, location)
        jobs = []
        page = 0

        while len(jobs) < max_results:
            params["pageNum"] = str(page)
            response = await self.make_request(self.BASE_URL, params=params)
            
            if not response.get("jobs"):
                break

            for raw_job in response["jobs"]:
                if len(jobs) >= max_results:
                    break
                jobs.append(self._parse_job(raw_job))

            page += 1

        return jobs
