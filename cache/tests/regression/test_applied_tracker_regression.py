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

def test_regression_missing_status_column():
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        job_ids = ["x", "y"]
        applied_ids = ["x"]
        # Create Excel without Status column
        df = pd.DataFrame({"JobID": job_ids})
        df.to_excel(tmp.name, index=False)
        tracker = AlreadyAppliedTracker(tmp.name)
        # Should not crash, should treat all as unapplied
        assert not tracker.is_applied("x")
        assert not tracker.is_applied("y")
        assert tracker.filter_unapplied(job_ids) == ["x", "y"]
    os.unlink(tmp.name)
