from datetime import datetime
from typing import List, Dict, Any
import aiohttp

class Job:
    def __init__(self, title, company, location, description, source, posted_date, job_id=None, raw_data=None):
        self.title = title
        self.company = company  
        self.location = location
        self.description = description
        self.source = source
        self.posted_date = posted_date
        self.job_id = job_id
        self.raw_data = raw_data

class GreenhouseAdapter:
    def __init__(self, config, test_client=None):
        self.config = config
        self.test_client = test_client

    async def fetch_jobs(self, params):
        """Fetch jobs from Greenhouse API"""
        from scraping_service.base_adapter import RateLimitError, AuthenticationError
        
        company_ids = params.get('company_ids', [])
        jobs = []
        
        # Use test client if provided (for testing)
        if self.test_client:
            for company_id in company_ids:
                url = f"/v1/boards/{company_id}/jobs"
                async with self.test_client.get(url) as response:
                    if response.status == 429:
                        raise RateLimitError("Rate limit exceeded")
                    elif response.status == 401:
                        raise AuthenticationError("Authentication failed")
                    elif response.status == 200:
                        data = await response.json()
                        parsed_jobs = self._parse_jobs(data.get('jobs', []), company_id)
                        jobs.extend(parsed_jobs)
        else:
            # Real implementation would go here
            async with aiohttp.ClientSession() as session:
                for company_id in company_ids:
                    url = f"https://boards-api.greenhouse.io/v1/boards/{company_id}/jobs"
                    async with session.get(url) as response:
                        if response.status == 429:
                            raise RateLimitError("Rate limit exceeded")
                        elif response.status == 401:
                            raise AuthenticationError("Authentication failed")
                        elif response.status == 200:
                            data = await response.json()
                            parsed_jobs = self._parse_jobs(data.get('jobs', []), company_id)
                            jobs.extend(parsed_jobs)
        
        return jobs
    
    def _parse_jobs(self, jobs_data, company):
        """Parse jobs from Greenhouse API format"""
        parsed_jobs = []
        for job_data in jobs_data:
            job_id = f"greenhouse_{company}_{job_data.get('id', '')}"
            job = Job(
                title=job_data.get('title', ''),
                company=job_data.get('company_name', company),
                location=job_data.get('location', {}).get('name', ''),
                description=job_data.get('content', ''),
                source='greenhouse',
                posted_date=datetime.now(),
                job_id=job_id,
                raw_data=job_data
            )
            parsed_jobs.append(job)
        return parsed_jobs
    
    async def health_check(self):
        """Mock health check"""
        return {'status': 'ok'}
