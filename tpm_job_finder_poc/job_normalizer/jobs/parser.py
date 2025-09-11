from typing import Any, Dict
from .schema import JobPosting, ValidationError
from datetime import datetime, timezone
import logging

def parse_job(raw: Dict[str, Any], source: str) -> JobPosting:
	"""
	Parse raw job data from a connector into a JobPosting object.
	Logs and raises errors for malformed or missing data.
	"""
	try:
		job = JobPosting(
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
		return job
	except ValidationError as e:
		logging.error(f"Failed to parse job: {e}. Raw: {raw}")
		raise