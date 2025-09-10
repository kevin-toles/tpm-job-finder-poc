
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured

import unittest
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured

class TestHealthAuditIntegration(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setFormatter(JsonFormatter())
        self.logger = setup_logger()
        self.logger.handlers = []
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)
        self.handler.close()
        self.stream.close()

    def test_health_event_logging(self):
        log_structured(
            level=30,  # WARNING
            message="Health check failed",
            event_type="HEALTH_CHECK",
            service="job_aggregator",
            timestamp="2025-09-06T12:02:00Z",
            details={"status": "DOWN"}
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "HEALTH_CHECK"' in line for line in output))
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "HEALTH_CHECK":
                self.assertEqual(data["service"], "job_aggregator")
                self.assertEqual(data["details"]["status"], "DOWN")

if __name__ == '__main__':
    unittest.main()
