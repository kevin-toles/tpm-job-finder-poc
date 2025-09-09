import logging
import json
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'funcName': record.funcName,
            'lineNo': record.lineno,
        }
        # Include all custom attributes (extra fields)
        for key, value in record.__dict__.items():
            if key not in log_record and not key.startswith('_') and key not in ('args', 'msg', 'exc_info', 'exc_text', 'stack_info', 'levelno', 'pathname', 'filename', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'lineno', 'funcName', 'module', 'name', 'levelname', 'levelno', 'getMessage', 'message', 'asctime'):
                log_record[key] = value
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

class CentralLogger:
    def __init__(self, name='tpm_job_finder', log_file='app.log', cloud_hook=None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        self.cloud_hook = cloud_hook
        # File handler (rotating)
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(file_handler)
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(console_handler)
        # Timed rotating handler (optional)
        timed_handler = TimedRotatingFileHandler(log_file, when='midnight', backupCount=7)
        timed_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(timed_handler)

    def info(self, msg, **kwargs):
        self.logger.info(msg, extra=kwargs)
        self._cloud_log('info', msg, kwargs)

    def warning(self, msg, **kwargs):
        self.logger.warning(msg, extra=kwargs)
        self._cloud_log('warning', msg, kwargs)

    def error(self, msg, **kwargs):
        self.logger.error(msg, extra=kwargs)
        self._cloud_log('error', msg, kwargs)

    def debug(self, msg, **kwargs):
        self.logger.debug(msg, extra=kwargs)
        self._cloud_log('debug', msg, kwargs)

    def exception(self, msg, **kwargs):
        self.logger.exception(msg, extra=kwargs)
        self._cloud_log('exception', msg, kwargs)

    def _cloud_log(self, level, msg, kwargs):
        if self.cloud_hook:
            try:
                self.cloud_hook(level, msg, kwargs)
            except Exception as e:
                self.logger.error(f"Cloud log failed: {e}")

# Example cloud integration hook

def example_cloud_hook(level, msg, kwargs):
    # Integrate with cloud logging provider (e.g., AWS CloudWatch, GCP Logging, Datadog)
    print(f"[CLOUD LOG] {level.upper()}: {msg} | {kwargs}")

# Usage:
# logger = CentralLogger(cloud_hook=example_cloud_hook)
# logger.info('Service started', service='webhook')
