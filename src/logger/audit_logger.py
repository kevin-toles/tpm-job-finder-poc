"""
POC Audit Logger
Append-only JSONL logger for user/system actions.
Lightweight audit aids reproducibility and debugging without a DB.
"""
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

class AuditLogger:
    _lock = threading.Lock()
    _log_path = Path("audit_log.jsonl")

    @classmethod
    def log(cls, action: str, user: str = None, details: dict = None):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "action": action,
            "user": user,
            "details": details or {}
        }
        line = json.dumps(entry)
        with cls._lock:
            with cls._log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    @classmethod
    def set_log_path(cls, path: str):
        cls._log_path = Path(path)

# Example usage:
# AuditLogger.log("login", user="alice", details={"success": True})
# AuditLogger.log("job_apply", user="bob", details={"job_id": 123})
