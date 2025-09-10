"""Job scraper service client."""

import httpx
from typing import List, Optional
from ..models.job import Job

class ScraperServiceClient:
    """Client for interacting with the job scraper microservice."""

    def __init__(self, base_url: str = "http://scraper-service:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def search_jobs(
        self,
        source: str,
        search_terms: List[str],
        location: Optional[str] = None,
        max_results: int = 10
    ) -> List[Job]:
        """Search for jobs using the scraper service."""
        response = await self.client.post(
            "/jobs/search",
            json={
                "source": source,
                "search_terms": search_terms,
                "location": location,
                "max_results": max_results
            }
        )
        response.raise_for_status()
        data = response.json()
        return [Job(**job) for job in data["jobs"]]

    async def check_health(self) -> bool:
        """Check if the scraper service is healthy."""
        try:
            response = await self.client.get("/health")
            response.raise_for_status()
            return response.json()["status"] == "healthy"
        except (httpx.HTTPError, KeyError):
            return False
