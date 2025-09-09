"""
RemoteOK connector
──────────────────
Fetches Technical Program Manager (TPM) postings from the RemoteOK
public JSON endpoint.  Used by tests/aggregators/test_remoteok.py.

Implementation notes
    • Zero-auth, ToS-friendly.
    • Endpoint returns an array where element 0 is metadata → skip it.
    • Filters purely on "program manager" / "tpm" keyword for the POC.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import List

import requests

from .base import BaseConnector
from ..jobs.schema import JobPosting

log = logging.getLogger(__name__)


class RemoteOKConnector(BaseConnector):
    """Concrete implementation of the RemoteOK ATS connector."""

    SOURCE = "remoteok"
    _API = "https://remoteok.com/api"

    # --------------------------------------------------------------------- #
    # public API
    # --------------------------------------------------------------------- #
    def fetch_since(self, *, days: int = 7) -> List[JobPosting]:  # noqa: D401
        """Return TPM postings not older than *days* (default = 7)."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        try:
            resp = requests.get(self._API, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as exc:  # network / 4xx / 5xx
            raise RuntimeError(f"RemoteOK request failed: {exc}") from exc

        records = resp.json()[1:]  # first element is API metadata
        postings: list[JobPosting] = []

        for row in records:
            # Skip job titles that don't look like TPM roles
            title = row.get("position") or ""
            if "program manager" not in title.lower() and "tpm" not in title.lower():
                continue

            epoch = row.get("epoch")
            if not epoch:
                continue  # row missing date – ignore

            posted = datetime.fromtimestamp(epoch, tz=timezone.utc)
            if posted < cutoff:
                continue  # too old

            postings.append(
                JobPosting(
                    id=hashlib.sha256(row["url"].encode()).hexdigest(),
                    source=self.SOURCE,
                    company=row.get("company", ""),
                    title=title,
                    location=row.get("location", "Remote"),
                    salary=row.get("salary"),
                    url=row["url"],
                    date_posted=posted,
                    raw=row,
                )
            )

        log.info("RemoteOK returned %s TPM jobs", len(postings))
        return postings
