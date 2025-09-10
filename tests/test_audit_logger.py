import os
import json
from audit_logger.logger import AuditLogger
from pathlib import Path

def test_log_creates_jsonl_entry(tmp_path):
    log_path = tmp_path / "test_audit_log.jsonl"
    AuditLogger.set_log_path(str(log_path))
    AuditLogger.log("test_action", user="test_user", details={"foo": "bar"})
    lines = log_path.read_text().splitlines()
    assert len(lines) == 1
    entry = json.loads(lines[0])
    assert entry["action"] == "test_action"
    assert entry["user"] == "test_user"
    assert entry["details"] == {"foo": "bar"}
    assert "timestamp" in entry

def test_log_appends_multiple_entries(tmp_path):
    log_path = tmp_path / "test_audit_log.jsonl"
    AuditLogger.set_log_path(str(log_path))
    AuditLogger.log("action1")
    AuditLogger.log("action2", user="user2")
    AuditLogger.log("action3", details={"x": 1})
    lines = log_path.read_text().splitlines()
    assert len(lines) == 3
    actions = [json.loads(line)["action"] for line in lines]
    assert actions == ["action1", "action2", "action3"]
