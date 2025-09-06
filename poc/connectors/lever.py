"""
Lever board scraper
───────────────────
Queries the Lever public postings API.

Why Lever?
    • Free unauthenticated JSON (`https://api.lever.co/v0/postings/{org}`).
    • Most fields already match our schema.

Known quirks
    • `categories.commitment` sometimes holds "Full-time".
    • No salary in public feed – we leave it None.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import List

API = "https://api.lever.co/v0/postings/{org}?mode=json"


def _load(org: str) -> list[dict]:
    with urllib.request.urlopen(API.format(org=org), timeout=10) as resp:
        return json.loads(resp.read().decode())


def _is_tpm(title: str) -> bool:
    t = title.lower()
    return "program manager" in t or "tpm" in t


def fetch(org: str, max_days: int = 7) -> List[dict]:
    rows = _load(org)
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    out: list[dict] = []

    for row in rows:
        if not _is_tpm(row["text"]):
            continue
        posted = datetime.fromtimestamp(row["created"], tz=timezone.utc)
        if posted < cutoff:
            continue

        out.append(
            {
                "source": "lever",
                "id": f'{row["id"]}-lever',
                "title": row["text"],
                "company": org.title(),
                "location": row["categories"].get("location") or "Remote",
                "url": row["hostedUrl"],
                "date_posted": posted,
                "tags": [row["categories"].get("team")],
                "salary": None,
            }
        )
    return out
