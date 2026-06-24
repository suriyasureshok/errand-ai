"""Centralized logging configuration for the Errand AI pipeline.

This module provides a unified logging factory to ensure all agents and
infrastructure components emit logs with a consistent format, severity
level, and output destination.
"""

import logging
import sys

# Define the standard log format used across the entire application
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_root_logger(level: str = "INFO") -> None:
    """Configures the root logger for the application.

    This function should be called exactly once at the entry point of the
    application (e.g., in `main.py`). It sets up the stdout handler and
    establishes the global formatting rules.

    Args:
        level (str, optional): The minimal logging severity level to record.
            Valid values are 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'.
            Defaults to "INFO".

    Raises:
        ValueError: If the provided log level string is invalid.
    """
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Clear any existing handlers to prevent duplicate log entries
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Configure the stdout handler for container/terminal friendly output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Apply the standard pipeline formatter
    formatter = logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT)
    console_handler.setFormatter(formatter)

    # Attach to root and set global level
    root_logger.addHandler(console_handler)
    root_logger.setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    """Retrieves a configured logger instance for a specific module.

    This acts as the standardized factory for all logging within the system.
    It automatically inherits the formatting and handlers from the root
    logger configured by `setup_root_logger`.

    Args:
        name (str): The name of the module requesting the logger. This should
            almost always be passed as `__name__` from the calling file.

    Returns:
        logging.Logger: A logger instance bound to the given module name.
    """
    return logging.getLogger(name)
