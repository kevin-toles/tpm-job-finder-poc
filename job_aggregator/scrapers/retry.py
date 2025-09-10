"""Retry utilities for job scrapers."""

import asyncio
from typing import TypeVar, Callable, Any, Optional
import logging
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

def with_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    logger: Optional[logging.Logger] = None
) -> Callable:
    """Decorator for retrying async functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        logger: Optional logger for retry attempts
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        if logger:
                            logger.error(
                                f"Final retry attempt failed for {func.__name__}: {str(e)}"
                            )
                        raise last_exception
                        
                    if logger:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}"
                            f"\nRetrying in {delay} seconds..."
                        )
                        
                    await asyncio.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
                    
            return None  # Should never reach here
            
        return wrapper
    return decorator
