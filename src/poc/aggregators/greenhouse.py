import requests
from datetime import datetime, timezone
from poc.jobs.schema import JobPosting

class GreenhouseConnector:
	def _normalize_jobs(self, data):
		jobs = []
		company = data.get("company_name", "")
		from datetime import datetime, timezone
		for item in data.get("jobs", []):
			location = item.get("location")
			if isinstance(location, dict):
				location = location.get("name")
			posted = item.get("updated_at") or item.get("posted_at")
			try:
				date_posted = datetime.fromisoformat(posted.replace("Z", "+00:00")) if posted else datetime.now(timezone.utc)
			except Exception:
				date_posted = datetime.now(timezone.utc)
			jobs.append(JobPosting(
				id=str(item.get("id")),
				source="greenhouse",
				company=item.get("company", company),
				title=item.get("title"),
				location=location,
				salary=None,
				url=item.get("absolute_url"),
				date_posted=date_posted,
				raw=item
			))
		return jobs
	def normalize_jobs_from_data(self, data):
		return self._normalize_jobs(data)
	API_URL_PATTERN = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs?content=true"

	def __init__(self, companies=None):
		self.companies = companies or []

	def fetch_since(self, days=7):
		jobs = []
		cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
		for company in self.companies:
			url = self.API_URL_PATTERN.format(board_token=company)
			resp = requests.get(url)
			if resp.status_code != 200:
				continue
			data = resp.json()
			for item in data.get("jobs", []):
				# Parse date_posted
				posted = item.get("updated_at") or item.get("posted_at")
				try:
					date_posted = datetime.fromisoformat(posted.replace("Z", "+00:00")) if posted else None
				except Exception:
					date_posted = None
				if not date_posted or date_posted.timestamp() < cutoff:
					continue
				location = item.get("location")
				if isinstance(location, dict):
					location = location.get("name")
				jobs.append(JobPosting(
					id=str(item.get("id")),
					source="greenhouse",
					company=item.get("company", company),
					title=item.get("title"),
					location=location,
					salary=None,
					url=item.get("absolute_url"),
					date_posted=date_posted,
					raw=item
				))
		return jobs