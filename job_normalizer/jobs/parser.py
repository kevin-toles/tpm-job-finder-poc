from typing import Any, Dict
from .schema import JobPosting
from datetime import datetime, timezone

def parse_job(raw: Dict[str, Any], source: str) -> JobPosting:
	"""
	Parse raw job data from a connector into a JobPosting object.
	This should be customized per connector/source.
	"""
	return JobPosting(
		id=raw.get('id', ''),
		source=source,
		company=raw.get('company', ''),
		title=raw.get('title', ''),
		location=raw.get('location'),
		salary=raw.get('salary'),
		url=raw.get('url', ''),
		date_posted=raw.get('date_posted', datetime.now(timezone.utc)),
		raw=raw
	)