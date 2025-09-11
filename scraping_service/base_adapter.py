class AdapterError(Exception):
    pass

class AuthenticationError(AdapterError):
    pass

class RateLimitError(AdapterError):
    pass

class ScrapingError(AdapterError):
    pass

class JobData:
    def __init__(self, job_id=None, title=None, company=None, location=None, 
                 description=None, url=None, salary_range=None, posted_date=None,
                 source=None, raw_data=None, *args, **kwargs):
        self.job_id = job_id
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.url = url
        self.salary_range = salary_range
        self.posted_date = posted_date
        self.source = source
        self.raw_data = raw_data

class ScrapingConfig:
    def __init__(self, backend=None, proxy_enabled=False, proxy_config=None,
                 rate_limit=60, timeout=30, retries=3):
        self.backend = backend
        self.proxy_enabled = proxy_enabled
        self.proxy_config = proxy_config
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.retries = retries

class BaseAdapter:
    def __init__(self, config):
        self.config = config
    
    async def fetch_jobs(self, params):
        """Fetch jobs based on parameters. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement fetch_jobs")
    
    async def validate_credentials(self):
        """Validate API credentials. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement validate_credentials")
    
    async def health_check(self):
        """Check adapter health. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement health_check")
