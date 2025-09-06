import requests
from datetime import datetime, timezone
from poc.jobs.schema import JobPosting

class RemoteOKConnector:
	def _normalize_jobs(self, data):
		jobs = []
		from datetime import datetime, timezone
		for item in data:
			if not isinstance(item, dict):
				continue
			epoch = item.get("epoch")
			if epoch:
				date_posted = datetime.fromtimestamp(epoch, tz=timezone.utc)
			else:
				date_posted = datetime.now(timezone.utc)
			jobs.append(JobPosting(
				id=str(item.get("id")),
				source=item.get("source", "remoteok"),
				company=item.get("company"),
				title=item.get("position"),
				location=item.get("location"),
				salary=item.get("salary", ""),
				url=item.get("url"),
				date_posted=date_posted,
				raw=item
			))
		return jobs
	def normalize_jobs_from_data(self, data):
		return self._normalize_jobs(data)
	API_URL = "https://remoteok.com/api"

	def fetch_since(self, days=7):
		resp = requests.get(self.API_URL)
		if resp.status_code != 200:
			return []
		data = resp.json()
		jobs = []
		cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
		for item in data:
			if not isinstance(item, dict):
				continue
			if item.get("epoch", 0) < cutoff:
				continue
			jobs.append(JobPosting(
				id=str(item.get("id")),
				source=item.get("source", "remoteok"),
				company=item.get("company"),
				title=item.get("position"),
				location=item.get("location"),
				salary=item.get("salary", ""),
				url=item.get("url"),
				date_posted=datetime.fromtimestamp(item.get("epoch", 0), tz=timezone.utc),
				raw=item
			))
		return jobs