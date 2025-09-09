import unittest
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured, set_correlation_id

class TestAuditLoggerE2E(unittest.TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setFormatter(JsonFormatter())
        self.logger = setup_logger()
        self.logger.handlers = []
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.handler.close()
        self.stream.close()
        self.logger.handlers = []

    def test_full_job_lifecycle_logging(self):
        # Simulate a full job lifecycle with audit events
        corr_id = set_correlation_id('e2e-corr-id')
        # Job created
        log_structured(logging.INFO, "Job created", event_type="JOB_CREATED", job_id=101, user_id=42, timestamp="2025-09-06T12:00:00Z", correlation_id=corr_id, details={"title": "TPM"})
        # Resume uploaded
        log_structured(logging.INFO, "Resume uploaded", event_type="RESUME_UPLOAD", job_id=101, user_id=42, timestamp="2025-09-06T12:01:00Z", correlation_id=corr_id, details={"filename": "resume.pdf"})
        # LLM scoring request
        log_structured(logging.INFO, "LLM scoring request", event_type="LLM_SCORE_REQUEST", user_id=42, timestamp="2025-09-06T12:02:00Z", correlation_id=corr_id, details={"model": "gpt-4", "input": "resume text"})
        # Health check
        log_structured(logging.WARNING, "Health check failed", event_type="HEALTH_CHECK", service="job_aggregator", timestamp="2025-09-06T12:03:00Z", correlation_id=corr_id, details={"status": "DOWN"})
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        # Validate all events are present and correlation_id is consistent
        event_types = set()
        for line in output:
            data = json.loads(line)
            self.assertEqual(data["correlation_id"], 'e2e-corr-id')
            event_types.add(data["event_type"])
        self.assertIn("JOB_CREATED", event_types)
        self.assertIn("RESUME_UPLOAD", event_types)
        self.assertIn("LLM_SCORE_REQUEST", event_types)
        self.assertIn("HEALTH_CHECK", event_types)

if __name__ == '__main__':
    unittest.main()
