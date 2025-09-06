"""
RemoteOK aggregator
──────────────────
Fetches Technical Program Manager (TPM) postings from the RemoteOK public API.

Why RemoteOK first?
    • No auth / scraper needed (ToS-safe JSON endpoint).
    • Returns date-posted, tags, URL, salary range—perfect for POC.
"""

from datetime import datetime, timezone
from typing import List, Dict
import requests

API_URL = "https://remoteok.com/api"

def fetch(days: int = 7) -> List[Dict]:
    """Return job dicts newer than <days>."""
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86_400
    resp = requests.get(API_URL, headers={"User-Agent": "tpm-poc/0.1"})
    resp.raise_for_status()

    results = []
    for job in resp.json()[1:]:  # first element is metadata
        if job.get("position") and "program manager" in job["position"].lower():
            if job["epoch"] and job["epoch"] > cutoff:
                results.append(
                    {
                        "id": job["id"],
                        "title": job["position"],
                        "company": job["company"],
                        "url": f"https://remoteok.com/remote-jobs/{job['id']}",
                        "location": job.get("location", "Remote"),
                        "tags": job.get("tags", []),
                        "date_posted": datetime.utcfromtimestamp(job["epoch"]),
                        "salary": job.get("salary"),
                    }
                )
    return results
