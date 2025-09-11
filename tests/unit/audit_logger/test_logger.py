import unittest
import os
import logging
from tpm_job_finder_poc.audit_logger.logger import enable_json_logging, log_structured, JsonFormatter, logger


class TestAuditLogger(unittest.TestCase):
    def setUp(self):
        self.log_file = 'test_audit.log'
        self.logger = logging.getLogger("tpm-job-finder-test")
        self.logger.handlers = []
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
        enable_json_logging()
        import io, json
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(JsonFormatter())
        logger.handlers = []
        logger.addHandler(handler)
        log_structured(logging.INFO, "Audit event", user_id=42, action="test")
        stream.seek(0)
        output = stream.getvalue()
        self.assertIn('Audit event', output)
        data = json.loads(output)
        self.assertEqual(data["user_id"], 42)
        self.assertEqual(data["action"], "test")

if __name__ == '__main__':
    unittest.main()
