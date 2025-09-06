"""
Greenhouse Boards connector
────────────────────────────
Iterates over a list of company board tokens (e.g. `airbnb`, `stripe`) and
pulls each board’s JSON feed.

Notes
-----
* No official public API, but the JSON is served without auth +
  referenced by Greenhouse docs — considered ToS-safe for read-only.
* Pagination not required (single feed per company).
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import Iterable, List

import requests

from .base import BaseConnector
from ..jobs.schema import JobPosting

log = logging.getLogger(__name__)

# Add/remove tokens as desired
DEFAULT_COMPANIES = ["airbnb", "stripe", "openai"]


class GreenhouseConnector(BaseConnector):
    SOURCE = "greenhouse"

    def __init__(self, companies: Iterable[str] | None = None) -> None:
        self.companies = list(companies or DEFAULT_COMPANIES)

    def _url(self, token: str) -> str:
        return f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"

    def fetch_since(self, *, days: int = 7) -> List[JobPosting]:
        cutoff = self._cutoff(days)
        postings: list[JobPosting] = []

        for company in self.companies:
            try:
                resp = requests.get(self._url(company), timeout=10)
                resp.raise_for_status()
            except requests.RequestException as exc:
                log.warning("greenhouse %s error: %s", company, exc)
                continue

            for job in resp.json().get("jobs", []):
                posted = datetime.fromisoformat(job["updated_at"].rstrip("Z")).replace(
                    tzinfo=timezone.utc
                )
                if posted < cutoff:
                    continue
                title = job["title"]
                if "program manager" not in title.lower():
                    continue

                data = JobPosting(
                    id=hashlib.sha256(job["absolute_url"].encode()).hexdigest(),
                    source=self.SOURCE,
                    company=company.capitalize(),
                    title=title,
                    location=job.get("location", {}).get("name"),
                    salary=None,
                    url=job["absolute_url"],
                    date_posted=posted,
                    raw=job,
                )
                postings.append(data)

        log.info("greenhouse fetched %s recent TPM jobs", len(postings))
        return postings
