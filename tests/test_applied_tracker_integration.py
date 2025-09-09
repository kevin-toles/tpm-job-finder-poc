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

def test_integration_multiple_flags():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        job_ids = ["a", "b", "c", "d"]
        applied_ids = ["a", "d"]
        create_excel(tmp.name, job_ids, applied_ids)
        tracker = AlreadyAppliedTracker(tmp.name)
        assert tracker.is_applied("a")
        assert tracker.is_applied("d")
        assert not tracker.is_applied("b")
        assert not tracker.is_applied("c")
        assert tracker.filter_unapplied(job_ids) == ["b", "c"]
    os.unlink(tmp.name)
