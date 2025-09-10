import pandas as pd
import tempfile
import os
from cache.applied_tracker import AlreadyAppliedTracker

def create_excel(path, job_ids, applied_ids):
    df = pd.DataFrame({
        "JobID": job_ids,
        "Status": ["Application submitted" if jid in applied_ids else "Not applied" for jid in job_ids]
    })
    df.to_excel(path, index=False)

def test_is_applied_and_filter_unapplied():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        job_ids = ["1", "2", "3"]
        applied_ids = ["2"]
        create_excel(tmp.name, job_ids, applied_ids)
        tracker = AlreadyAppliedTracker(tmp.name)
        assert tracker.is_applied("2")
        assert not tracker.is_applied("1")
        assert tracker.filter_unapplied(job_ids) == ["1", "3"]
    os.unlink(tmp.name)
