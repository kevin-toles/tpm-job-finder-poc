

from typing import List, Dict
from .schema import JobPosting
import logging

def normalize_title(title: str) -> str:
	"""Enhanced normalization for job titles."""
	if not isinstance(title, str):
		logging.warning(f"normalize_title: expected str, got {type(title)}")
		return ""
	
	# Normalize the title
	normalized = title.strip()
	
	# Common abbreviation expansions
	abbreviations = {
		'sr.': 'Senior',
		'sr': 'Senior',
		'jr.': 'Junior',
		'jr': 'Junior',
		'mgr': 'Manager',
		'eng': 'Engineer',
		'dev': 'Developer',
		'sw': 'Software',
		'hw': 'Hardware'
	}
	
	# Split into words and expand abbreviations
	words = normalized.lower().split()
	for i, word in enumerate(words):
		if word in abbreviations:
			words[i] = abbreviations[word]
	
	# Rejoin and title case
	return ' '.join(words).title()

def normalize_salary(salary: str | None) -> str | None:
	"""Enhanced normalization for salary field."""
	if not salary:
		return None
	if not isinstance(salary, str):
		logging.warning(f"normalize_salary: expected str or None, got {type(salary)}")
		return None
	
	# Handle common salary formats
	import re
	
	# Replace k/K with appropriate zeros
	salary_normalized = salary.replace('k', '000').replace('K', '000')
	
	# Find all numbers in the salary
	numbers = re.findall(r'\$?(\d+(?:,\d{3})*)', salary_normalized)
	
	if len(numbers) >= 2:
		# Range format like $100,000 - $150,000
		return f"${int(numbers[0]):,} - ${int(numbers[1]):,}"
	elif len(numbers) == 1:
		# Single value
		return f"${int(numbers[0]):,}"
	
	# If we can't parse it, return cleaned version
	return salary.replace('$', '').replace(',', '').strip()

def normalize_location(location: str | None) -> str | None:
	"""Enhanced normalization for location field."""
	if not location:
		return None
	if not isinstance(location, str):
		logging.warning(f"normalize_location: expected str or None, got {type(location)}")
		return None
	
	# Location abbreviation expansions
	location_mappings = {
		'sf': 'San Francisco',
		'nyc': 'New York City',
		'la': 'Los Angeles',
		'chi': 'Chicago',
		'dc': 'Washington DC'
	}
	
	# Clean and normalize
	normalized = location.strip()
	
	# Handle comma-separated format like "SF, CA"
	parts = [part.strip() for part in normalized.split(',')]
	
	# Expand the first part (city) if it's an abbreviation
	if parts and parts[0].lower() in location_mappings:
		parts[0] = location_mappings[parts[0].lower()]
	
	# Rejoin and title case
	return ', '.join(parts).title()

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
			description=job.description,  # Preserve description
			raw=job.raw
		)
	except Exception as e:
		logging.error(f"Failed to normalize job: {e}. Job: {job}")
		raise

def dedupe_jobs(jobs: List[JobPosting]) -> List[JobPosting]:
	"""Remove duplicate jobs by URL or by company + title combination."""
	seen_urls: Dict[str, JobPosting] = {}
	seen_company_title: Dict[str, JobPosting] = {}
	unique_jobs: List[JobPosting] = []
	
	for job in jobs:
		url_key = str(job.url)
		company_title_key = f"{job.company}|{job.title}"
		
		# Skip if we've seen this URL before
		if url_key in seen_urls:
			continue
			
		# Skip if we've seen this company + title combination before
		if company_title_key in seen_company_title:
			continue
		
		# This is a unique job
		seen_urls[url_key] = job
		seen_company_title[company_title_key] = job
		unique_jobs.append(job)
	
	logging.info(f"dedupe_jobs: {len(jobs)} input, {len(unique_jobs)} output")
	return unique_jobs