import requests
from datetime import datetime, timedelta
from typing import List, Dict

class AdzunaConnector:
    source = "adzuna"

    def __init__(self, app_id: str, app_key: str, country: str = "us"):
        self.app_id = app_id
        self.app_key = app_key
        self.country = country
        self.base_url = f"http://api.adzuna.com/v1/api/jobs/{country}/search/1"

    def fetch_since(self, since: datetime) -> List[Dict]:
        params = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": 50,
            "what": "technical program manager",
            "max_days_old": (datetime.now() - since).days,
            "sort_by": "date",
            "salary_include_unknown": 1,
            "content-type": "application/json"
        }
        resp = requests.get(self.base_url, params=params)
        resp.raise_for_status()
        jobs = []
        for result in resp.json().get("results", []):
            jobs.append({
                "title": result.get("title"),
                "company": result.get("company", {}).get("display_name"),
                "location": result.get("location", {}).get("display_name"),
                "posted_date": result.get("created"),
                "canonical_url": result.get("redirect_url"),
                "source_site": self.source,
                "salary_min": result.get("salary_min"),
                "salary_max": result.get("salary_max"),
                "description": result.get("description"),
            })
        return jobs
