"""Shared JobPosting model used by all ATS connectors.

Every connector should return data shaped exactly like this so
down-stream components can rely on a single schema.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class JobPosting(BaseModel):
    """Normalized representation of a single job ad."""

    id: str = Field(..., description="SHA-256 hash or source-specific ID")
    source: str = Field(..., description="remoteok | greenhouse | lever | ...")
    company: str
    title: str
    location: str | None = None
    salary: str | None = None
    url: HttpUrl
    date_posted: datetime
    raw: dict[str, Any] = Field(
        default_factory=dict,
        description="Un-modified payload returned from the upstream API",
    )

    # --- validators ---------------------------------------------------------

    @field_validator("date_posted", mode="before")
    def _enforce_utc(cls, v: datetime) -> datetime:  # noqa: N805  (class method)
        """Force all datetimes to UTC & timezone-aware."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    # --- model settings -----------------------------------------------------

    model_config = {
        "frozen": True,  # makes the model hashable / immutable
        "populate_by_name": True,
        "str_max_length": 1_024,
    }
