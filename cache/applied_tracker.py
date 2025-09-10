"""
Already-Applied Tracker
Tracks jobs the user has already applied to by reading a user-supplied Excel sheet.
Honors "Application submitted" flags across runs. No extra UI; Excel is source-of-truth.
"""
import pandas as pd
from typing import List, Optional
from pathlib import Path

class AlreadyAppliedTracker:
    def __init__(self, excel_path: str, job_id_column: str = "JobID", status_column: str = "Status", applied_flag: str = "Application submitted"):
        self.excel_path = Path(excel_path)
        self.job_id_column = job_id_column
        self.status_column = status_column
        self.applied_flag = applied_flag
        self._applied_ids = set()
        self._load_applied()

    def _load_applied(self):
        from error_handler.handler import handle_error
        if not self.excel_path.exists():
            self._applied_ids = set()
            return
        try:
            df = pd.read_excel(self.excel_path)
            if self.status_column not in df.columns or self.job_id_column not in df.columns:
                # If required columns are missing, treat all as unapplied
                self._applied_ids = set()
                return
            applied = df[df[self.status_column] == self.applied_flag][self.job_id_column]
            self._applied_ids = set(str(jid) for jid in applied.dropna())
        except Exception as e:
            handle_error(e, context={'component': 'applied_tracker', 'method': '_load_applied', 'excel_path': str(self.excel_path)})
            self._applied_ids = set()

    def is_applied(self, job_id: str) -> bool:
        return str(job_id) in self._applied_ids

    def filter_unapplied(self, job_ids: List[str]) -> List[str]:
        return [jid for jid in job_ids if not self.is_applied(jid)]

# Example usage:
# tracker = AlreadyAppliedTracker("applied_jobs.xlsx")
# if not tracker.is_applied(job_id):
#     ...process job...
# unapplied_jobs = tracker.filter_unapplied(all_job_ids)
