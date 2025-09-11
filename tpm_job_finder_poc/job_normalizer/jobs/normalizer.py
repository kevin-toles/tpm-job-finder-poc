

from typing import List, Dict
from .schema import JobPosting
import logging

def normalize_title(title: str) -> str:
	"""Basic normalization for job titles."""
	if not isinstance(title, str):
		logging.warning(f"normalize_title: expected str, got {type(title)}")
		return ""
	return title.strip().title()

def normalize_salary(salary: str | None) -> str | None:
	"""Basic normalization for salary field."""
	if not salary:
		return None
	if not isinstance(salary, str):
		logging.warning(f"normalize_salary: expected str or None, got {type(salary)}")
		return None
	return salary.replace('$', '').replace(',', '').strip()

def normalize_location(location: str | None) -> str | None:
	"""Basic normalization for location field."""
	if not location:
		return None
	if not isinstance(location, str):
		logging.warning(f"normalize_location: expected str or None, got {type(location)}")
		return None
	return location.strip().title()

def normalize_job(job: JobPosting) -> JobPosting:
	"""Return a new JobPosting with normalized fields."""
	try:
		return JobPosting(
			id=job.id,
			source=job.source,
			company=job.company,
			title=normalize_title(job.title),
			location=normalize_location(job.location),
			salary=normalize_salary(job.salary),
			url=job.url,
			date_posted=job.date_posted,
			raw=job.raw
		)
	except Exception as e:
		logging.error(f"Failed to normalize job: {e}. Job: {job}")
		raise

def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
	"""Remove duplicate jobs by URL, company, and title."""
	seen: Dict[str, JobPosting] = {}
	for job in jobs:
		key = f"{str(job.url)}|{job.company}|{job.title}"
		if key not in seen:
			seen[key] = job
	deduped = list(seen.values())
	logging.info(f"dedupe_jobs: {len(jobs)} input, {len(deduped)} output")
	return deduped