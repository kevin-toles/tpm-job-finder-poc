import json
from src.logging_service.logger import CentralLogger

def test_logger_info_creates_log_file(tmp_path):
    log_file = tmp_path / "test_app.log"
    logger = CentralLogger(name="test_logger", log_file=str(log_file))
    logger.info("Unit test info log", test_key="unit")
    assert log_file.exists()
    with open(log_file) as f:
        lines = f.readlines()
        assert any("Unit test info log" in line for line in lines)
        for line in lines:
            log_record = json.loads(line)
            assert log_record["level"] == "INFO"
            assert log_record["message"] == "Unit test info log"
            assert log_record["test_key"] == "unit"

def test_logger_error_creates_log_file(tmp_path):
    log_file = tmp_path / "test_app.log"
    logger = CentralLogger(name="test_logger", log_file=str(log_file))
    logger.error("Unit test error log", test_key="unit")
    with open(log_file) as f:
        lines = f.readlines()
        assert any("Unit test error log" in line for line in lines)
        for line in lines:
            log_record = json.loads(line)
            assert log_record["level"] == "ERROR"
            assert log_record["message"] == "Unit test error log"
            assert log_record["test_key"] == "unit"
