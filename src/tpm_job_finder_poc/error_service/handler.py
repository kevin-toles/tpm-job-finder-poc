from src.logging_service.logger import CentralLogger

logger = CentralLogger(name='error_service')

def handle_error(exc, context=None, notify=False):
    error_info = {
        'type': type(exc).__name__,
        'message': str(exc),
        'context': context or {}
    }
    logger.error("Exception captured", error=error_info)
    if notify:
        # TODO: Integrate with notifier (email, Slack, etc.)
        pass
    return error_info

def error_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            handle_error(exc, context={'function': func.__name__})
            raise
    return wrapper
