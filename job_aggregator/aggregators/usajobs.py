import requests
from datetime import datetime
from typing import List, Dict

class USAJobsConnector:
    source = "usajobs"

    def __init__(self, user_agent: str, api_key: str):
        self.user_agent = user_agent
        self.api_key = api_key
        self.base_url = "https://data.usajobs.gov/api/Search"

    def fetch_since(self, since: datetime) -> List[Dict]:
        headers = {
            "User-Agent": self.user_agent,
            "Authorization-Key": self.api_key
        }
        params = {
            "Keyword": "Technical Program Manager",
            "ResultsPerPage": 50,
            "WhoMayApply": "all"
        }
        resp = requests.get(self.base_url, headers=headers, params=params)
        resp.raise_for_status()
        jobs = []
        for item in resp.json().get("SearchResult", {}).get("SearchResultItems", []):
            desc = item.get("MatchedObjectDescriptor", {})
            jobs.append({
                "title": desc.get("PositionTitle"),
                "company": desc.get("OrganizationName"),
                "location": desc.get("PositionLocationDisplay"),
                "posted_date": desc.get("PositionStartDate"),
                "canonical_url": desc.get("ApplyURI", [None])[0],
                "source_site": self.source,
                "salary_min": None,
                "salary_max": None,
                "description": desc.get("UserArea", {}).get("Details", {}).get("JobSummary"),
            })
        return jobs
