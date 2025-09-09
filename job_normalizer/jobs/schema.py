"""Shared JobPosting model used by all ATS connectors.

Every connector should return data shaped exactly like this so
down-stream components can rely on a single schema.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


from pydantic import BaseModel, Field, HttpUrl, field_validator, ValidationError, model_validator
import logging



class JobPosting(BaseModel):
    """Normalized representation of a single job ad."""

    id: str = Field(..., description="SHA-256 hash or source-specific ID", min_length=1)
    source: str = Field(..., description="remoteok | greenhouse | lever | ...", min_length=1)
    company: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    location: str | None = None
    salary: str | None = None
    url: HttpUrl
    date_posted: datetime
    raw: dict[str, Any] = Field(
        default_factory=dict,
        description="Un-modified payload returned from the upstream API",
    )

    @field_validator("date_posted", mode="before")
    def _enforce_utc(cls, v: datetime) -> datetime:
        """Force all datetimes to UTC & timezone-aware."""
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)

    @model_validator(mode="after")
    def check_required_fields(self):
        missing = [f for f in ["id", "source", "company", "title", "url", "date_posted"] if not getattr(self, f, None)]
        if missing:
            logging.error(f"JobPosting missing required fields: {missing}")
            raise ValidationError(f"Missing required fields: {missing}")
        return self

    model_config = {
        "frozen": True,
        "populate_by_name": True,
        "str_max_length": 1_024,
    }
