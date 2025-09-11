class GlassdoorScraper:
    def __init__(self, *args, **kwargs):
        pass
    def search_jobs(self, *args, **kwargs):
        return []
    def get_job_details(self, *args, **kwargs):
        raise NotImplementedError
    def verify_access(self, *args, **kwargs):
        return False
    def health_check(self, *args, **kwargs):
        raise NotImplementedError
