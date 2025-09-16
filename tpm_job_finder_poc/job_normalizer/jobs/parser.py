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
		# Parse date_posted if it's a string
		date_posted = raw.get('date_posted', datetime.now(timezone.utc))
		if isinstance(date_posted, str):
			try:
				# Try parsing ISO format datetime string
				date_posted = datetime.fromisoformat(date_posted.replace('Z', '+00:00'))
			except ValueError:
				# Fallback to current time if parsing fails
				logging.warning(f"Could not parse date_posted '{date_posted}', using current time")
				date_posted = datetime.now(timezone.utc)
		
		job = JobPosting(
			id=raw.get('id', ''),
			source=source,
			company=raw.get('company', ''),
			title=raw.get('title', ''),
			location=raw.get('location'),
			salary=raw.get('salary'),
			url=raw.get('url', ''),
			date_posted=date_posted,
			raw=raw
		)
		return job
	except ValidationError as e:
		logging.error(f"Failed to parse job: {e}. Raw: {raw}")
		raise