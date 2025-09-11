import requests
from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting

class RecruiteeConnector:
    API_URL_PATTERN = "https://{subdomain}.recruitee.com/api/offers/"

    def __init__(self, subdomain):
        self.subdomain = subdomain

    def fetch_jobs(self):
        url = self.API_URL_PATTERN.format(subdomain=self.subdomain)
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        jobs = []
        from datetime import datetime, timezone
        for item in data.get("offers", []):
            # Use current UTC time if no date is provided
            date_posted = datetime.now(timezone.utc)
            jobs.append(JobPosting(
                id=str(item.get("id")),
                source="recruitee",
                company=self.subdomain,
                title=item.get("title"),
                location=item.get("location", {}).get("city"),
                salary=None,
                url=item.get("url"),
                date_posted=date_posted,
                raw=item,
                description=item.get("description", "")
            ))
        return jobs
