
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured, set_correlation_id

import unittest
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured, set_correlation_id

class TestJobAggregatorAuditIntegration(unittest.TestCase):
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

    def test_job_event_logging(self):
        set_correlation_id('job-corr-id-1')
        log_structured(
            level=20,  # INFO
            message="Job created",
            event_type="JOB_CREATED",
            job_id=101,
            user_id=42,
            timestamp="2025-09-06T12:00:00Z",
            details={"title": "TPM"}
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "JOB_CREATED"' in line for line in output))
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "JOB_CREATED":
                self.assertEqual(data["job_id"], 101)
                self.assertEqual(data["user_id"], 42)
                self.assertEqual(data["details"]["title"], "TPM")

if __name__ == '__main__':
    unittest.main()
