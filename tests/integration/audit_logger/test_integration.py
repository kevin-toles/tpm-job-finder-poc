import unittest
import logging
import io
import json
from tpm_job_finder_poc.audit_logger.logger import setup_logger, JsonFormatter, log_structured, AuditLogFilter, set_correlation_id

class TestAuditLoggerIntegration(unittest.TestCase):
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

	def test_structured_logging_with_correlation_and_filter(self):
		# Set correlation ID
		corr_id = set_correlation_id('integration-corr-id')
		# Add filter for user_id
		log_filter = AuditLogFilter(user_id=123)
		self.handler.addFilter(log_filter)
		# Log matching and non-matching events
		log_structured(logging.INFO, "Audit event", event_type="USER_LOGIN", user_id=123, timestamp="2025-09-06T12:00:00Z", correlation_id=corr_id, details={"ip": "127.0.0.1"})
		log_structured(logging.INFO, "Audit event", event_type="USER_LOGIN", user_id=999, timestamp="2025-09-06T12:00:00Z", correlation_id=corr_id, details={"ip": "127.0.0.1"})
		self.handler.flush()
		self.stream.seek(0)
		output = self.stream.getvalue().strip().splitlines()
		self.assertTrue(any('"user_id": 123' in line for line in output))
		self.assertFalse(any('"user_id": 999' in line for line in output))
		# Check correlation ID present
		for line in output:
			data = json.loads(line)
			self.assertEqual(data["correlation_id"], 'integration-corr-id')

	def test_schema_and_async_integration(self):
		# Setup async logger with schema enforcement
		async_logger = setup_logger(async_mode=True)
		stream = io.StringIO()
		handler = logging.StreamHandler(stream)
		handler.setFormatter(JsonFormatter())
		async_logger.handlers = []
		async_logger.addHandler(handler)
		# Valid event
		log_structured(logging.INFO, "Audit event", event_type="USER_LOGIN", user_id=42, timestamp="2025-09-06T12:00:00Z", correlation_id="abc-123", details={"ip": "127.0.0.1"})
		# Invalid event (missing details)
		log_structured(logging.INFO, "Audit event", event_type="USER_LOGIN", user_id=42, timestamp="2025-09-06T12:00:00Z", correlation_id="abc-123")
		import time
		time.sleep(0.1)
		if hasattr(async_logger, "_async_listener"):
			async_logger._async_listener.stop()
		stream.seek(0)
		output = stream.getvalue().strip().splitlines()
		found_valid = False
		found_invalid = False
		for line in output:
			data = json.loads(line)
			if "audit_schema_error" in data:
				found_invalid = True
			else:
				found_valid = True
		self.assertTrue(found_valid)
		self.assertTrue(found_invalid)

if __name__ == '__main__':
	unittest.main()
