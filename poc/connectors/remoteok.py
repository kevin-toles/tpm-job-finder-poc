"""
RemoteOK aggregator
───────────────────
Fetches Technical Program Manager (TPM) postings from the RemoteOK public
API.

Why RemoteOK first?
    • No auth / scraper needed (ToS-safe JSON endpoint).
    • Returns date-posted, tags, URL, salary range — perfect for POC.
    • One call per page; pagination handled via `?limit=` + `?offset=` (≤ 500).

Normalized job schema returned by ``fetch``
    {
        "source":        "remoteok",
        "id":            "12345-remoteok",
        "title":         "Technical Program Manager",
        "company":       "ACME Corp",
        "location":      "Remote",
        "url":           "https://remoteok.com/remote-jobs/12345",
        "date_posted":   datetime(..., tzinfo=timezone.utc),
        "tags":          ["tpm", "program-management"],
        "salary":        "USD 150-180k",
    }
"""
from __future__ import annotations

import http.client
import json
import time
from datetime import datetime, timezone
from typing import Iterable, List

REMOTEOK_HOST = "remoteok.com"
REMOTEOK_PATH = "/remote-jobs.json"
PAGE_SIZE = 50  # RemoteOK returns up to 500, but smaller pages = safer


def _get_page(offset: int = 0, limit: int = PAGE_SIZE) -> list[dict]:
    """Low-level GET wrapper (no external deps)."""
    conn = http.client.HTTPSConnection(REMOTEOK_HOST, timeout=10)
    path = f"{REMOTEOK_PATH}?limit={limit}&offset={offset}"
    conn.request("GET", path, headers={"User-Agent": "poc-tpm-finder"})
    resp = conn.getresponse()
    if resp.status >= 400:
        raise RuntimeError(f"RemoteOK HTTP {resp.status}")
    data = resp.read()
    conn.close()
    return json.loads(data.decode())


def _is_tpm(job: dict) -> bool:
    title = job.get("position") or job.get("title", "")
    return "program manager" in title.lower() or "tpm" in title.lower()


def fetch(max_days: int = 7, max_pages: int = 3) -> List[dict]:
    """
    Return TPM jobs posted in the last ``max_days``.

    Pagination: stops when either
        • collected ``max_pages`` pages, or
        • encounters a job older than the cutoff.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    out: list[dict] = []

    for page in range(max_pages):
        rows = _get_page(offset=page * PAGE_SIZE)
        if not rows:
            break

        for row in rows:
            if not _is_tpm(row):
                continue

            epoch = row.get("epoch")
            if not epoch:
                continue
            posted = datetime.fromtimestamp(epoch, tz=timezone.utc)
            if posted < cutoff:
                return out  # finished – remaining rows are older

            out.append(
                {
                    "source": "remoteok",
                    "id": f'{row["id"]}-remoteok',
                    "title": row.get("position") or row.get("title", ""),
                    "company": row.get("company", ""),
                    "location": row.get("location", "Remote"),
                    "url": row.get("url"),
                    "date_posted": posted,
                    "tags": row.get("tags", []),
                    "salary": row.get("salary"),
                }
            )

        time.sleep(1)  # gentle rate-limit

    return out
