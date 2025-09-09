from src.logging_service.logger import CentralLogger

def test_logger_cloud_hook(tmp_path):
    cloud_logs = []
    def cloud_hook(level, msg, kwargs):
        cloud_logs.append({"level": level, "msg": msg, **kwargs})
    log_file = tmp_path / "integration_app.log"
    logger = CentralLogger(name="integration_logger", log_file=str(log_file), cloud_hook=cloud_hook)
    logger.info("Integration test info log", integration_key="integration")
    logger.error("Integration test error log", integration_key="integration")
    assert any(log["level"] == "info" and log["msg"] == "Integration test info log" for log in cloud_logs)
    assert any(log["level"] == "error" and log["msg"] == "Integration test error log" for log in cloud_logs)
