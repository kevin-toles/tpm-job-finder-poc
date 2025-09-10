"""Indeed job scraper implementation."""

from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..models.job import Job

class IndeedScraper(BaseScraper):
    """Scraper for Indeed jobs."""

    BASE_URL = "https://www.indeed.com/jobs"

    def _build_search_params(
        self,
        search_terms: List[str],
        location: Optional[str] = None
    ) -> Dict[str, str]:
        """Build search parameters for Indeed API."""
        params = {
            "q": " ".join(search_terms),
            "sort": "date",  # Most recent first
            "fromage": "1",  # Last 24 hours
            "start": "0"
        }
        if location:
            params["l"] = location
        return params

    def _parse_job(self, raw_job: Dict[str, Any]) -> Job:
        """Parse raw Indeed job data into Job model."""
        return Job(
            title=raw_job["jobtitle"],
            company=raw_job["company"],
            location=raw_job["formattedLocation"],
            description=raw_job.get("snippet", ""),
            url=f"https://www.indeed.com/viewjob?jk={raw_job['jobkey']}",
            source="indeed",
            posted_date=raw_job.get("formattedRelativeTime"),
            salary_range=raw_job.get("formattedPayScale"),
            employment_type=raw_job.get("jobType")
        )

    async def fetch_jobs(
        self,
        search_terms: List[str],
        location: Optional[str] = None,
        max_results: int = 10
    ) -> List[Job]:
        """Fetch jobs from Indeed."""
        params = self._build_search_params(search_terms, location)
        jobs = []
        start = 0

        while len(jobs) < max_results:
            params["start"] = str(start)
            response = await self.make_request(self.BASE_URL, params=params)
            
            if not response.get("results"):
                break

            for raw_job in response["results"]:
                if len(jobs) >= max_results:
                    break
                jobs.append(self._parse_job(raw_job))

            start += 10

        return jobs
