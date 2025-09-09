
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured, set_correlation_id

import unittest
import logging
import io
import json
from audit_logger.logger import setup_logger, JsonFormatter, log_structured, set_correlation_id

class TestLLMProviderAuditIntegration(unittest.TestCase):
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

    def test_llm_event_logging(self):
        set_correlation_id('llm-corr-id-1')
        log_structured(
            level=20,
            message="LLM scoring request",
            event_type="LLM_SCORE_REQUEST",
            user_id=42,
            timestamp="2025-09-06T12:01:00Z",
            details={"model": "gpt-4", "input": "resume text"}
        )
        self.handler.flush()
        self.stream.seek(0)
        output = self.stream.getvalue().strip().splitlines()
        self.assertTrue(any('"event_type": "LLM_SCORE_REQUEST"' in line for line in output))
        for line in output:
            data = json.loads(line)
            if data.get("event_type") == "LLM_SCORE_REQUEST":
                self.assertEqual(data["user_id"], 42)
                self.assertEqual(data["details"]["model"], "gpt-4")
                self.assertEqual(data["details"]["input"], "resume text")

if __name__ == '__main__':
    unittest.main()
