import json
from src.logging_service.logger import CentralLogger

def test_logger_e2e(tmp_path):
    log_file = tmp_path / "e2e_app.log"
    logger = CentralLogger(name="e2e_logger", log_file=str(log_file))
    logger.info("E2E test info log", e2e_key="e2e")
    logger.error("E2E test error log", e2e_key="e2e")
    # Simulate reading logs as an external system would
    with open(log_file) as f:
        lines = f.readlines()
        info_found = any("E2E test info log" in line for line in lines)
        error_found = any("E2E test error log" in line for line in lines)
        assert info_found and error_found
        for line in lines:
            log_record = json.loads(line)
            assert log_record["name"] == "e2e_logger"
            assert log_record["level"] in ["INFO", "ERROR"]
