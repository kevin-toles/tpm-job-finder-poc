"""
RemoteOK aggregator
───────────────────
Fetches Technical Program Manager (TPM) postings from the RemoteOK public API.

Why RemoteOK first?
    • No auth / scraping required – ToS-safe JSON endpoint.
    • Provides date-posted, tags, URL, salary range – perfect for the POC.

Returns
    List[Dict] with keys:
        id, title, company, url, location, tags, date_posted (UTC tz-aware),
        salary
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Dict

import requests

API_URL = "https://remoteok.com/api"


def fetch(days: int = 7) -> List[Dict]:
    """
    Return TPM job postings newer than <days> days.

    Filtering rules
        1. Title contains "program manager" (case-insensitive).
        2. Job `epoch` >= <cutoff>.
    """
    cutoff_ts = datetime.now(timezone.utc).timestamp() - days * 86_400

    resp = requests.get(API_URL, headers={"User-Agent": "tpm-poc/0.1"})
    resp.raise_for_status()
    raw = resp.json()

    results: List[Dict] = []
    for job in raw[1:]:  # first element is API metadata
        title = (job.get("position") or "").lower()
        epoch = job.get("epoch")

        if "program manager" not in title:
            continue
        if not epoch or epoch < cutoff_ts:
            continue

        results.append(
            {
                "id": job["id"],
                "title": job["position"],
                "company": job["company"],
                "url": f"https://remoteok.com/remote-jobs/{job['id']}",
                "location": job.get("location", "Remote"),
                "tags": job.get("tags", []),
                # tz-aware datetime (UTC)  ↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
                "date_posted": datetime.fromtimestamp(epoch, tz=timezone.utc),
                "salary": job.get("salary"),
            }
        )

    return results
