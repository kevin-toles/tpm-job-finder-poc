import pandas as pd
import tempfile
import os
from src.cache.applied_tracker import AlreadyAppliedTracker

def create_excel(path, job_ids, applied_ids):
    df = pd.DataFrame({
        "JobID": job_ids,
        "Status": ["Application submitted" if jid in applied_ids else "Not applied" for jid in job_ids]
    })
    df.to_excel(path, index=False)

def test_e2e_applied_tracker_workflow():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        job_ids = ["101", "102", "103", "104"]
        applied_ids = ["101", "104"]
        create_excel(tmp.name, job_ids, applied_ids)
        tracker = AlreadyAppliedTracker(tmp.name)
        unapplied = tracker.filter_unapplied(job_ids)
        assert unapplied == ["102", "103"]
        # Simulate a new run with updated Excel
        create_excel(tmp.name, job_ids, ["101", "102", "104"])
        tracker._load_applied()
        unapplied = tracker.filter_unapplied(job_ids)
        assert unapplied == ["103"]
    os.unlink(tmp.name)
