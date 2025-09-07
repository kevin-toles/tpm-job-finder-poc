"""
BaseConnector
──────────────
Defines the contract every ATS connector must implement.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Protocol, Sequence

from ..jobs.schema import JobPosting


class BaseConnector(Protocol):
    """All concrete connectors must satisfy this Protocol."""

    SOURCE: str  # lowercase slug, e.g. "remoteok"

    def fetch_since(self, *, days: int = 7) -> Sequence[JobPosting]:
        """
        Return all postings newer than **today-days** (inclusive).

        Implementations should:
            • Handle HTTP/backoff errors gracefully (raise RuntimeError).
            • Populate JobPosting.raw with the full upstream dict.
            • Deduplicate inside the connector if pagination overlaps occur.
        """
        ...

    # Helper -------------------------------------------------------------
    @staticmethod
    def _cutoff(days: int) -> datetime:
        return datetime.now(timezone.utc) - timedelta(days=days)
