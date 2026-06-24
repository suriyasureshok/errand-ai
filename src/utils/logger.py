import logging
import sys
from pathlib import Path
from typing import Optional

# Standardize the output format across the entire application
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    level: int = logging.INFO, log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Bootstraps the root logger for the Errand AI application.
    This should be called exactly once by the Session Manager on startup.
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers to prevent duplicate log entries
    # if setup_logger is accidentally called multiple times.
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # 1. Console Handler (Streams to Docker logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 2. File Handler (Routes to .errand-ai/logs/retry-n.log)
    if log_file:
        # Ensure the .errand-ai/logs directory exists before writing
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        # We often want DEBUG level in the file even if console is INFO
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def get_logger(module_name: str) -> logging.Logger:
    """
    Utility function to retrieve a standardized logger for a specific module.

    Usage:
        from src.utils.logger import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(module_name)
