import json
from src.logger.audit_logger import AuditLogger
from pathlib import Path

def test_e2e_audit_logger_workflow(tmp_path):
    log_path = tmp_path / "e2e_audit_log.jsonl"
    AuditLogger.set_log_path(str(log_path))
    # Simulate a user workflow
    AuditLogger.log("user_login", user="alice", details={"success": True})
    AuditLogger.log("job_apply", user="alice", details={"job_id": 42})
    AuditLogger.log("logout", user="alice")
    lines = log_path.read_text().splitlines()
    assert len(lines) == 3
    actions = [json.loads(line)["action"] for line in lines]
    assert actions == ["user_login", "job_apply", "logout"]
    users = set(json.loads(line)["user"] for line in lines)
    assert users == {"alice"}
