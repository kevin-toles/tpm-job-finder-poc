import unittest
import os
import logging
from audit_logger.logger import logger, enable_json_logging, log_structured, JsonFormatter

class TestAuditLogger(unittest.TestCase):
    def test_log_filtering(self):
        from audit_logger.logger import AuditLogFilter, setup_logger, JsonFormatter, log_structured
        import io, json
        # Filter by user_id
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        log_filter = AuditLogFilter(user_id=42)
        logger = setup_logger(log_filter=log_filter)
        logger.handlers = []
        handler.addFilter(log_filter)
        logger.addHandler(handler)
        log_structured(logging.INFO, "Audit event", user_id=42, event_type="USER_LOGIN")
        log_structured(logging.INFO, "Audit event", user_id=99, event_type="USER_LOGIN")
        handler.flush()
        stream.seek(0)
        output = stream.getvalue().strip().splitlines()
        self.assertTrue(any('"user_id": 42' in line for line in output))
        self.assertFalse(any('"user_id": 99' in line for line in output))
        # Filter by event_type
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        log_filter = AuditLogFilter(event_type="USER_LOGIN")
        logger.handlers = []
        handler.addFilter(log_filter)
        logger.addHandler(handler)
        log_structured(logging.INFO, "Audit event", user_id=42, event_type="USER_LOGIN")
        log_structured(logging.INFO, "Audit event", user_id=42, event_type="JOB_APPLY")
        handler.flush()
        stream.seek(0)
        output = stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "USER_LOGIN"' in line for line in output))
        self.assertFalse(any('"event_type": "JOB_APPLY"' in line for line in output))
    def test_audit_event_schema_enforcement(self):
        from audit_logger.logger import logger, enable_json_logging, log_structured, JsonFormatter
        import io, json
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger.handlers = []
        logger.addHandler(handler)
        # Valid audit event
        log_structured(
            logging.INFO,
            "Audit event",
            event_type="USER_LOGIN",
            user_id=42,
            timestamp="2025-09-06T12:00:00Z",
            correlation_id="abc-123",
            details={"ip": "127.0.0.1"}
        )
        handler.flush()
        stream.seek(0)
        output = stream.getvalue().strip()
        data = json.loads(output)
        self.assertNotIn("audit_schema_error", data)
        # Invalid audit event (missing details)
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger.handlers = []
        logger.addHandler(handler)
        log_structured(
            logging.INFO,
            "Audit event",
            event_type="USER_LOGIN",
            user_id=42,
            timestamp="2025-09-06T12:00:00Z",
            correlation_id="abc-123"
            # details missing
        )
        handler.flush()
        stream.seek(0)
        output = stream.getvalue().strip()
        data = json.loads(output)
        self.assertIn("audit_schema_error", data)
    def test_async_logging(self):
        import os
        from audit_logger.logger import setup_logger
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["LOG_FORMAT"] = "%(levelname)s %(message)s"
        os.environ["LOG_FILE_PATH"] = "test_async_audit.log"
        os.environ["LOG_SINK"] = "file"
        logger = setup_logger(async_mode=True)
        logger.debug("Async logging test")
        # Wait briefly to ensure log is processed
        import time
        time.sleep(0.1)
        # Flush listener if present
        if hasattr(logger, "_async_listener"):
            logger._async_listener.stop()
        with open("test_async_audit.log", "r") as f:
            logs = f.read()
        self.assertIn("DEBUG Async logging test", logs)
        os.remove("test_async_audit.log")
    def test_syslog_sink(self):
        import logging
        from audit_logger.logger import setup_logger
        # Use UDP localhost for syslog (does not require a real syslog server for test)
        import socket
        syslog_address = ("localhost", 514)
        os.environ["LOG_SINK"] = "syslog"
        os.environ["SYSLOG_ADDRESS"] = f"{syslog_address[0]},{syslog_address[1]}"
        logger = setup_logger()
        # Patch SysLogHandler to use a dummy socket
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.SysLogHandler):
                handler.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Just ensure no exception is raised when logging
        try:
            logger.info("Syslog test message")
        except Exception as e:
            self.fail(f"Syslog handler raised exception: {e}")
    def test_config_manager_integration(self):
        import os
        # Set environment variables for config manager BEFORE import
        os.environ["LOG_LEVEL"] = "DEBUG"
        os.environ["LOG_FORMAT"] = "%(levelname)s %(message)s"
        os.environ["LOG_FILE_PATH"] = "test_config_audit.log"
        os.environ["LOG_SINK"] = "file"
        from audit_logger.logger import setup_logger
        logger = setup_logger()
        logger.debug("Config manager integration test")
        for handler in logger.handlers:
            handler.flush()
        with open("test_config_audit.log", "r") as f:
            logs = f.read()
        self.assertIn("DEBUG Config manager integration test", logs)
        os.remove("test_config_audit.log")
    def test_correlation_id_in_structured_log(self):
        from audit_logger.logger import logger, log_structured, JsonFormatter, set_correlation_id, get_correlation_id
        import io, json
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        corr_id = set_correlation_id('test-corr-id-123')
        log_structured(logging.INFO, "Correlation event", user_id=99)
        handler.flush()
        stream.seek(0)
        output = stream.getvalue().strip()
        self.assertTrue(output)
        data = json.loads(output)
        self.assertEqual(data["correlation_id"], 'test-corr-id-123')
        self.assertEqual(data["message"], "Correlation event")
        self.assertEqual(data["user_id"], 99)
    def setUp(self):
        self.log_file = 'test_audit.log'
        self.logger = logging.getLogger("tpm-job-finder-test")
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        handlers = self.logger.handlers[:]
        for handler in handlers:
            handler.close()
            self.logger.removeHandler(handler)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)

    def test_info_logging(self):
        self.logger.info('Test info message')
        with open(self.log_file, 'r') as f:
            logs = f.read()
        self.assertIn('Test info message', logs)
        self.assertIn('INFO', logs)

    def test_error_logging(self):
        self.logger.error('Test error message')
        with open(self.log_file, 'r') as f:
            logs = f.read()
        self.assertIn('Test error message', logs)
        self.assertIn('ERROR', logs)

    def test_debug_logging(self):
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug('Test debug message')
        with open(self.log_file, 'r') as f:
            logs = f.read()
        self.assertIn('Test debug message', logs)
        self.assertIn('DEBUG', logs)

    def test_log_format(self):
        self.logger.warning('Test warning')
        with open(self.log_file, 'r') as f:
            logs = f.read()
        self.assertRegex(logs, r'\d{4}-\d{2}-\d{2}')  # Timestamp
        self.assertIn('WARNING', logs)

    def test_log_rotation(self):
        # Simulate log rotation by creating a new handler
        handler = logging.FileHandler('test_audit_rotated.log')
        self.logger.addHandler(handler)
        self.logger.info('Rotated log message')
        with open('test_audit_rotated.log', 'r') as f:
            logs = f.read()
        self.assertIn('Rotated log message', logs)
        self.logger.removeHandler(handler)
        handler.close()
        os.remove('test_audit_rotated.log')

    def test_structured_json_logging(self):
        from audit_logger.logger import logger, log_structured, JsonFormatter
        import io, json
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        log_structured(logging.INFO, "Audit event", user_id=42, action="test")
        handler.flush()
        stream.seek(0)
        output = stream.getvalue().strip()
        self.assertTrue(output)
        data = json.loads(output)
        self.assertEqual(data["message"], "Audit event")
        self.assertEqual(data["user_id"], 42)
        self.assertEqual(data["action"], "test")

if __name__ == '__main__':
    unittest.main()
