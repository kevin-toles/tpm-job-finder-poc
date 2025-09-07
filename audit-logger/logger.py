import logging
import sys
import json

class JsonFormatter(logging.Formatter):
	def format(self, record):
		log_record = {
			"timestamp": self.formatTime(record, self.datefmt),
			"level": record.levelname,
			"name": record.name,
			"message": record.getMessage(),
		}
		# Optionally add extra fields
		if hasattr(record, 'extra') and isinstance(record.extra, dict):
			log_record.update(record.extra)
		return json.dumps(log_record)

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("tpm-job-finder")

def enable_json_logging():
	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(JsonFormatter())
	logger.handlers = []
	logger.addHandler(handler)

def log_structured(level, message, **kwargs):
	extra = {"extra": kwargs} if kwargs else {}
	logger.log(level, message, extra=extra)

# Usage:
# from audit_logger.logger import logger, enable_json_logging, log_structured
# enable_json_logging()
# log_structured(logging.INFO, "User login", user_id=123, action="login")