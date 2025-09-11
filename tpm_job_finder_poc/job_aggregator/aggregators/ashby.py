import requests
from tpm_job_finder_poc.job_normalizer.jobs.schema import JobPosting

class AshbyConnector:
    API_URL_PATTERN = "https://api.ashbyhq.com/posting-api/job-board/{board_name}?includeCompensation=true"

    def __init__(self, board_name):
        self.board_name = board_name

    def fetch_jobs(self):
        url = self.API_URL_PATTERN.format(board_name=self.board_name)
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        jobs = []
        for item in data.get("jobs", []):
                # Parse publishedAt to datetime
                from datetime import datetime, timezone
                published_at = item.get("publishedAt")
                if published_at:
                    try:
                        date_posted = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    except Exception:
                        date_posted = datetime.now(timezone.utc)
                else:
                    date_posted = datetime.now(timezone.utc)
                jobs.append(JobPosting(
                    id=item.get("jobUrl"),
                    source="ashby",
                    company=item.get("department", ""),
                    title=item.get("title"),
                    location=item.get("location"),
                    salary=None,
                    url=item.get("jobUrl"),
                    date_posted=date_posted,
                    raw=item,
                    description=item.get("descriptionPlain") or item.get("descriptionHtml")
                ))
        return jobs
