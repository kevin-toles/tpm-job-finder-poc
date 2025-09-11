def handle_error(exc, context, notify=False):
    return {
        "type": exc.__class__.__name__,
        "message": str(exc),
        "context": context
    }

def error_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            handle_error(exc, {})
            raise  # Re-raise the exception after handling it
    return wrapper
