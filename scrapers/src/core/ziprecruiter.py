"""ZipRecruiter job scraper implementation."""

from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from .base import BaseScraper
from ..models.job import Job

class ZipRecruiterScraper(BaseScraper):
    """Scraper for ZipRecruiter jobs."""

    BASE_URL = "https://api.ziprecruiter.com/jobs/v1/search"

    def _build_search_params(
        self,
        search_terms: List[str],
        location: Optional[str] = None
    ) -> Dict[str, str]:
        """Build search parameters for ZipRecruiter API."""
        params = {
            "search": " ".join(search_terms),
            "days_ago": "1",  # Last 24 hours
            "page": "1",
            "jobs_per_page": "10"
        }
        if location:
            params["location"] = location
        return params

    def _parse_job(self, raw_job: Dict[str, Any]) -> Job:
        """Parse raw ZipRecruiter job data into Job model."""
        return Job(
            title=raw_job["name"],
            company=raw_job["hiring_company"]["name"],
            location=raw_job["location"],
            description=raw_job.get("snippet", ""),
            url=raw_job["url"],
            source="ziprecruiter",
            posted_date=raw_job.get("posted_time"),
            salary_range=raw_job.get("salary_interval"),
            employment_type=raw_job.get("employment_type")
        )

    async def fetch_jobs(
        self,
        search_terms: List[str],
        location: Optional[str] = None,
        max_results: int = 10
    ) -> List[Job]:
        """Fetch jobs from ZipRecruiter."""
        params = self._build_search_params(search_terms, location)
        jobs = []
        page = 1

        while len(jobs) < max_results:
            params["page"] = str(page)
            response = await self.make_request(self.BASE_URL, params=params)
            
            if not response.get("jobs"):
                break

            for raw_job in response["jobs"]:
                if len(jobs) >= max_results:
                    break
                jobs.append(self._parse_job(raw_job))

            page += 1

        return jobs
