"""Utility module for asynchronous network resilience.

This module provides decorators to automatically retry asynchronous functions
that are prone to transient network failures, utilizing exponential backoff
and randomized jitter to prevent thundering herd problems.
"""

import asyncio
import functools
import random
from typing import Any, Awaitable, Callable, TypeVar

from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """Decorator to retry an asynchronous function upon specified exceptions.

    Implements an exponential backoff strategy with "Full Jitter". The delay
    before each retry is calculated as a random value between 0 and
    min(max_delay, base_delay * 2 ** attempt).

    Args:
        max_retries (int): The maximum number of times to retry the execution
            before letting the exception bubble up. Defaults to 3.
        base_delay (float): The initial base delay in seconds. Defaults to 1.0.
        max_delay (float): The absolute maximum delay in seconds between retries.
            Defaults to 10.0.
        exceptions (tuple[type[Exception], ...]): A tuple of exception classes
            that should trigger a retry. Defaults to catching all Exceptions.

    Returns:
        Callable: A wrapped asynchronous function that includes retry logic.

    Raises:
        Exception: Re-raises the last caught exception if `max_retries` are exhausted.
    """

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            attempts = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    if attempts > max_retries:
                        logger.error(
                            f"Function '{func.__name__}' failed after {max_retries} retries. "
                            f"Final exception: {e}"
                        )
                        raise

                    # Calculate exponential backoff with jitter
                    exponential_delay = min(
                        max_delay, base_delay * (2 ** (attempts - 1))
                    )
                    jittered_delay = random.uniform(0, exponential_delay)

                    logger.warning(
                        f"Attempt {attempts}/{max_retries} for '{func.__name__}' "
                        f"failed: {e}. Retrying in {jittered_delay:.2f} seconds..."
                    )

                    await asyncio.sleep(jittered_delay)

        return wrapper

    return decorator
