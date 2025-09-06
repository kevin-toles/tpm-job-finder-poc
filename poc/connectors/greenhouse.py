"""
Greenhouse board scraper
────────────────────────
Fetches openings from the public JSON feed of any Greenhouse-hosted job
board.

Why Greenhouse?
    • Widely used by tech companies (easy coverage bump).
    • JSON feed (``/boards/{slug}?format=json``) – no page scraping.
    • No auth needed.

Usage
-----
>>> fetch("stripe", role="program manager", max_days=14)
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import List

API = "https://boards.greenhouse.io/boards/{slug}?format=json"


def _load(slug: str) -> dict:
    with urllib.request.urlopen(API.format(slug=slug), timeout=10) as resp:
        return json.loads(resp.read().decode())


def _is_tpm(text: str) -> bool:
    t = text.lower()
    return ("program manager" in t) or ("tpm" in t)


def fetch(slug: str, role: str = "program manager", max_days: int = 7) -> List[dict]:
    data = _load(slug)
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_days)
    out: list[dict] = []

    for post in data.get("jobs", []):
        if not _is_tpm(post["title"]):
            continue
        posted = datetime.fromisoformat(post["updated_at"].rstrip("Z")).replace(
            tzinfo=timezone.utc
        )
        if posted < cutoff:
            continue

        out.append(
            {
                "source": "greenhouse",
                "id": f'{post["id"]}-gh',
                "title": post["title"],
                "company": data.get("company_name", ""),
                "location": post.get("location", "Remote"),
                "url": post["absolute_url"],
                "date_posted": posted,
                "tags": [d["name"] for d in post.get("departments", [])],
                "salary": None,
            }
        )
    return out
