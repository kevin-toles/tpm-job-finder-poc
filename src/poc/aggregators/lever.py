from src.error_service.handler import handle_error
import requests
from datetime import datetime, timezone
from poc.jobs.schema import JobPosting

class LeverConnector:
	def _normalize_jobs(self, data):
		jobs = []
		from datetime import datetime, timezone
		for item in data:
			created_at = item.get("createdAt")
			if created_at:
				if isinstance(created_at, int):
					date_posted = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
				elif isinstance(created_at, str):
					try:
						date_posted = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
					except Exception as e:
						handle_error(e, context={'component': 'lever', 'method': '_normalize_jobs', 'created_at': created_at})
						date_posted = datetime.now(timezone.utc)
				else:
					date_posted = datetime.now(timezone.utc)
			else:
				date_posted = datetime.now(timezone.utc)
			company = item.get("categories", {}).get("company")
			if not company:
				# Try to get company from top-level or fallback
				company = item.get("company") or "Unknown"
			jobs.append(JobPosting(
				id=str(item.get("id")),
				source="lever",
				company=company,
				title=item.get("text"),
				location=item.get("categories", {}).get("location"),
				salary=None,
				url=item.get("hostedUrl"),
				date_posted=date_posted,
				raw=item
			))
		return jobs
	def normalize_jobs_from_data(self, data):
		return self._normalize_jobs(data)
	API_URL_PATTERN = "https://api.lever.co/v0/postings/{company}?mode=json"

	def __init__(self, companies=None):
		self.companies = companies or []

	def fetch_since(self, days=7):
		jobs = []
		cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
		for company in self.companies:
			url = self.API_URL_PATTERN.format(company=company)
			resp = requests.get(url, timeout=10)
			if resp.status_code != 200:
				continue
			data = resp.json()
			for item in data:
				# Parse date_posted
				created_at = item.get("createdAt")
				if not created_at:
					continue
				date_posted = datetime.fromtimestamp(created_at / 1000, tz=timezone.utc)
				if date_posted.timestamp() < cutoff:
					continue
				jobs.append(JobPosting(
					id=str(item.get("id")),
					source="lever",
					company=item.get("categories", {}).get("company", company),
					title=item.get("text"),
					location=item.get("categories", {}).get("location"),
					salary=None,
					url=item.get("hostedUrl"),
					date_posted=date_posted,
					raw=item
				))
		return jobs