"""
Lever Boards connector
──────────────────────
Very similar to Greenhouse: each company exposes `https://jobs.lever.co/<slug>?mode=json`.
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

DEFAULT_COMPANIES = ["databricks", "robinhood", "figma"]


class LeverConnector(BaseConnector):
    SOURCE = "lever"

    def __init__(self, companies: Iterable[str] | None = None) -> None:
        self.companies = list(companies or DEFAULT_COMPANIES)

    def _url(self, token: str) -> str:
        return f"https://jobs.lever.co/{token}?mode=json"

    def fetch_since(self, *, days: int = 7) -> List[JobPosting]:
        cutoff = self._cutoff(days)
        postings: list[JobPosting] = []

        for company in self.companies:
            try:
                resp = requests.get(self._url(company), timeout=10)
                resp.raise_for_status()
            except requests.RequestException as exc:
                log.warning("lever %s error: %s", company, exc)
                continue

            for job in resp.json():
                posted = datetime.fromisoformat(job["createdAt"]).astimezone(
                    timezone.utc
                )
                if posted < cutoff:
                    continue
                title = job["text"]
                if "program manager" not in title.lower():
                    continue

                data = JobPosting(
                    id=hashlib.sha256(job["hostedUrl"].encode()).hexdigest(),
                    source=self.SOURCE,
                    company=company.capitalize(),
                    title=title,
                    location=job.get("categories", {}).get("location"),
                    salary=None,
                    url=job["hostedUrl"],
                    date_posted=posted,
                    raw=job,
                )
                postings.append(data)

        log.info("lever fetched %s recent TPM jobs", len(postings))
        return postings
