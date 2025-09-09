import requests
from job_normalizer.jobs.schema import JobPosting

class SmartRecruitersConnector:
    API_URL_PATTERN = "https://api.smartrecruiters.com/v1/companies/{company}/postings?limit=20&offset=0"
    JOB_DETAILS_URL = "https://api.smartrecruiters.com/v1/companies/{company}/postings/{postingId}"

    def __init__(self, company):
        self.company = company

    def fetch_jobs(self):
        url = self.API_URL_PATTERN.format(company=self.company)
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        jobs = []
        for item in data.get("content", []):
            posting_id = item.get("id")
            details_url = self.JOB_DETAILS_URL.format(company=self.company, postingId=posting_id)
            details_resp = requests.get(details_url)
            details_resp.raise_for_status()
            details = details_resp.json()
            job_ad = details.get("jobAd", {}).get("sections", {})
            description = job_ad.get("jobDescription", {}).get("text", "")
            # Parse createdOn to datetime
            from datetime import datetime, timezone
            created_on = item.get("createdOn")
            if created_on:
                try:
                    date_posted = datetime.fromisoformat(created_on.replace("Z", "+00:00"))
                except Exception:
                    date_posted = datetime.now(timezone.utc)
            else:
                date_posted = datetime.now(timezone.utc)
            jobs.append(JobPosting(
                id=posting_id,
                source="smartrecruiters",
                company=self.company,
                title=item.get("name"),
                location=item.get("location", {}).get("city"),
                salary=None,
                url=item.get("applyUrl"),
                date_posted=date_posted,
                raw=details,
                description=description
            ))
        return jobs
