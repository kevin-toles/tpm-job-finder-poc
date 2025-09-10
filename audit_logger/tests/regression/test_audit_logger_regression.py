import json
from audit_logger.logger import AuditLogger
from pathlib import Path

def test_regression_log_format(tmp_path):
    log_path = tmp_path / "regression_audit_log.jsonl"
    AuditLogger.set_log_path(str(log_path))
    AuditLogger.log("regression_action", user="regression_user", details={"regression": True})
    line = log_path.read_text().strip()
    entry = json.loads(line)
    # Regression: ensure timestamp is ISO8601 and ends with Z
    assert entry["timestamp"].endswith("Z")
    assert "T" in entry["timestamp"]
    assert entry["action"] == "regression_action"
    assert entry["user"] == "regression_user"
    assert entry["details"] == {"regression": True}
