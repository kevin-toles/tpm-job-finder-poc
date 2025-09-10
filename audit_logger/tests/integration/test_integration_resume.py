
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter

import unittest
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured

class TestResumeAuditIntegration(unittest.TestCase):
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

    def test_resume_event_logging(self):
        self.logger.handlers = []
        self.logger.addHandler(self.handler)
        log_structured(
            level=20,
            message="Resume uploaded",
            event_type="RESUME_UPLOAD",
            user_id=42,
            job_id=101,
            timestamp="2025-09-06T12:03:00Z",
            details={"filename": "resume.pdf"}
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "RESUME_UPLOAD"' in line for line in output))
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "RESUME_UPLOAD":
                self.assertEqual(data["user_id"], 42)
                self.assertEqual(data["job_id"], 101)
                self.assertEqual(data["details"]["filename"], "resume.pdf")

if __name__ == '__main__':
    unittest.main()
