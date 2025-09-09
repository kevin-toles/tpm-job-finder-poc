from src.logging_service.logger import CentralLogger

def test_logger_rotating_file(tmp_path):
    log_file = tmp_path / "regression_app.log"
    logger = CentralLogger(name="regression_logger", log_file=str(log_file))
    # Write many logs to trigger rotation
    for i in range(1000):
        logger.info(f"Regression log {i}", regression_key="regression")
    assert log_file.exists()
    with open(log_file) as f:
        lines = f.readlines()
        assert any("Regression log" in line for line in lines)
