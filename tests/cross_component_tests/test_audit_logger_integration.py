import json
from tpm_job_finder_poc.audit_logger.logger import AuditLogger
from pathlib import Path

def test_integration_thread_safety(tmp_path):
    log_path = tmp_path / "integration_audit_log.jsonl"
    AuditLogger.set_log_path(str(log_path))
    import threading
    def log_action(i):
        AuditLogger.log(f"action_{i}", user=f"user_{i}")
    threads = [threading.Thread(target=log_action, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lines = log_path.read_text().splitlines()
    assert len(lines) == 10
    actions = set(json.loads(line)["action"] for line in lines)
    assert actions == {f"action_{i}" for i in range(10)}
