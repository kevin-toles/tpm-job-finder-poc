import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
logging.basicConfig(stream=sys.stdout, level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("tpm-job-finder")

# Usage: from audit_logger.logger import logger
# logger.info("message")