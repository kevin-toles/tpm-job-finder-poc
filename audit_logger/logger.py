import logging

class AuditLogFilter(logging.Filter):
	def __init__(self, user_id=None, job_id=None, event_type=None):
		super().__init__()
		self.user_id = user_id
		self.job_id = job_id
		self.event_type = event_type

	def filter(self, record):
		# record.extra may not exist, so use getattr
		extra = getattr(record, 'extra', {})
		if self.user_id is not None and extra.get('user_id') != self.user_id:
			return False
		if self.job_id is not None and extra.get('job_id') != self.job_id:
			return False
		if self.event_type is not None and extra.get('event_type') != self.event_type:
			return False
		return True
from typing import Optional, Dict, Any
# Audit event schema definition
AUDIT_EVENT_SCHEMA = {
	"event_type": str,
	"user_id": (str, int, type(None)),
	"timestamp": str,
	"correlation_id": (str, type(None)),
	"details": dict,
}

def validate_audit_event(event: Dict[str, Any]) -> Optional[str]:
	"""Validate event against the audit schema. Returns error string or None."""
	for key, typ in AUDIT_EVENT_SCHEMA.items():
		if key not in event:
			return f"Missing required audit field: {key}"
		if not isinstance(event[key], typ):
			return f"Field '{key}' must be of type {typ}, got {type(event[key])}"
	return None
import queue
import logging
import sys
import json

import logging.handlers

# Centralized config manager
try:
	from src.config_manager import Config
except ImportError:
	Config = None

import uuid
import contextvars

# Context variable for correlation ID
correlation_id_ctx = contextvars.ContextVar('correlation_id', default=None)

def set_correlation_id(corr_id=None):
	"""Set a correlation ID for the current context."""
	if corr_id is None:
		corr_id = str(uuid.uuid4())
	correlation_id_ctx.set(corr_id)
	return corr_id

def get_correlation_id():
	"""Get the correlation ID for the current context."""
	return correlation_id_ctx.get()

class JsonFormatter(logging.Formatter):
	def format(self, record):
		log_record = {
			"timestamp": self.formatTime(record, self.datefmt),
			"level": record.levelname,
			"name": record.name,
			"message": record.getMessage(),
			"correlation_id": get_correlation_id(),
		}
		# Optionally add extra fields
		if hasattr(record, 'extra') and isinstance(record.extra, dict):
			log_record.update(record.extra)
		# Audit event schema enforcement
		if log_record.get("event_type"):
			error = validate_audit_event(log_record)
			if error:
				log_record["audit_schema_error"] = error
		return json.dumps(log_record)




def setup_logger(async_mode=False, log_filter: AuditLogFilter = None):
	LOG_FORMAT = Config.get("LOG_FORMAT", "%(asctime)s %(levelname)s %(name)s: %(message)s") if Config else "%(asctime)s %(levelname)s %(name)s: %(message)s"
	LOG_LEVEL = Config.get("LOG_LEVEL", "INFO") if Config else "INFO"
	LOG_FILE = Config.get("LOG_FILE_PATH") if Config else None
	LOG_SINK = Config.get("LOG_SINK", "console") if Config else "console"
	logger = logging.getLogger("tpm-job-finder")
	logger.handlers = []
	if LOG_SINK == "file" and LOG_FILE:
		handler = logging.FileHandler(LOG_FILE)
	elif LOG_SINK == "syslog":
		syslog_address = Config.get("SYSLOG_ADDRESS", "/dev/log")
		handler = logging.handlers.SysLogHandler(address=syslog_address)
	else:
		handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(logging.Formatter(LOG_FORMAT))
	if log_filter:
		handler.addFilter(log_filter)
	if async_mode:
		log_queue = queue.Queue(-1)
		queue_handler = logging.handlers.QueueHandler(log_queue)
		logger.addHandler(queue_handler)
		listener = logging.handlers.QueueListener(log_queue, handler)
		listener.start()
		logger._async_listener = listener
	else:
		logger.addHandler(handler)
	logger.setLevel(LOG_LEVEL)
	return logger

def add_external_handler(handler):
	logger = logging.getLogger("tpm-job-finder")
	logger.addHandler(handler)
	return logger

logger = setup_logger()

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
# set_correlation_id() # Optionally set a correlation ID for the current request/job