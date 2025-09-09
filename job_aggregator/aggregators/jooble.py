import http.client
import json
from datetime import datetime
from typing import List, Dict

class JoobleConnector:
    source = "jooble"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.host = "jooble.org"

    def fetch_since(self, since: datetime) -> List[Dict]:
        connection = http.client.HTTPSConnection(self.host)
        headers = {"Content-type": "application/json"}
        body = json.dumps({
            "keywords": "technical program manager",
            "location": "United States",
            "page": 1
        })
        connection.request("POST", f"/api/{self.api_key}", body, headers)
        response = connection.getresponse()
        jobs = []
        if response.status == 200:
            data = json.loads(response.read().decode())
            for job in data.get("jobs", []):
                jobs.append({
                    "title": job.get("title"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                    "posted_date": job.get("updated"),
                    "canonical_url": job.get("link"),
                    "source_site": self.source,
                    "salary_min": None,
                    "salary_max": None,
                    "description": job.get("snippet"),
                })
        return jobs
