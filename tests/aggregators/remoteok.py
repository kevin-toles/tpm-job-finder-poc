"""
RemoteOK connector
──────────────────
Fetches Technical Program Manager (TPM) postings from the RemoteOK public
JSON API.  Endpoint returns max ~100 posts; filtering is done client-side.

Why RemoteOK first?
    • Zero auth, ToS-friendly.
    • JSON already contains epoch, tags, url, salary.
"""
from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone
from typing import List

import requests

from .base import BaseConnector
from ..jobs.schema import JobPosting

log = logging.getLogger(__name__)


class RemoteOKConnector(BaseConnector):
    SOURCE = "remoteok"
    _API = "https://remoteok.com/api"

    def fetch_since(self, *, days: int = 7) -> List[JobPosting]:  # noqa: D401
        cutoff = self._cutoff(days)
        try:
            resp = requests.get(self._API, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"RemoteOK error: {exc}") from exc

        postings: list[JobPosting] = []
        for item in resp.json()[1:]:  # first element is metadata
            if (epoch := item.get("epoch")) is None:
                continue
            posted = datetime.fromtimestamp(epoch, tz=timezone.utc)
            if posted < cutoff:
                continue
            title = item["position"]
            if "program manager" not in title.lower():
                continue  # simple keyword filter

            data = JobPosting(
                id=hashlib.sha256(item["url"].encode()).hexdigest(),
                source=self.SOURCE,
                company=item["company"],
                title=title,
                location=item.get("location"),
                salary=item.get("salary"),
                url=item["url"],
                date_posted=posted,
                raw=item,
            )
            postings.append(data)

        log.info("remoteok fetched %s recent TPM jobs", len(postings))
        return postings
