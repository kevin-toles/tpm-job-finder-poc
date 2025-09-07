from typing import List, Dict
from .schema import JobPosting

def normalize_title(title: str) -> str:
	"""Basic normalization for job titles."""
	return title.strip().title()

def normalize_salary(salary: str | None) -> str | None:
	"""Basic normalization for salary field."""
	if not salary:
		return None
	return salary.replace('$', '').replace(',', '').strip()

def normalize_location(location: str | None) -> str | None:
	"""Basic normalization for location field."""
	if not location:
		return None
	return location.strip().title()

def normalize_job(job: JobPosting) -> JobPosting:
	"""Return a new JobPosting with normalized fields."""
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

def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
	"""Remove duplicate jobs by URL, company, and title."""
	seen: Dict[str, JobPosting] = {}
	for job in jobs:
		key = f"{str(job.url)}|{job.company}|{job.title}"
		if key not in seen:
			seen[key] = job
	return list(seen.values())