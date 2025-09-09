def notify_error(error_info, method='log'):
    # method: 'log', 'email', 'slack', 'sentry', etc.
    from src.logging_service.logger import CentralLogger
    logger = CentralLogger(name='error_notifier')
    if method == 'log':
        logger.error(f"[ERROR NOTIFY] {error_info}")
    elif method == 'email':
        # TODO: Integrate with email service
        pass
    elif method == 'slack':
        # TODO: Integrate with Slack webhook
        pass
    elif method == 'sentry':
        # TODO: Integrate with Sentry SDK
        pass
    else:
        logger.error(f"[ERROR NOTIFY] Unknown method: {method}")
