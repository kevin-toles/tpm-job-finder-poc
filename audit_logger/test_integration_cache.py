
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured

import unittest
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured

class TestCacheAuditIntegration(unittest.TestCase):
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

    def test_cache_event_logging(self):
        log_structured(
            level=20,
            message="Cache hit",
            event_type="CACHE_HIT",
            key="job_101",
            timestamp="2025-09-06T12:05:00Z",
            details={"source": "dedupe"}
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "CACHE_HIT"' in line for line in output))
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "CACHE_HIT":
                self.assertEqual(data["key"], "job_101")
                self.assertEqual(data["details"]["source"], "dedupe")

if __name__ == '__main__':
    unittest.main()
