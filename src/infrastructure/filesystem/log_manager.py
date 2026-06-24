"""Filesystem layer for test log management.

This module provides the LogManager class, responsible for persisting raw
terminal outputs (stdout/stderr) from test runners to disk for historical
auditing and AI analysis.
"""

from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class LogManager:
    """Manages the persistence of raw test execution logs.

    Attributes:
        logs_dir (Path): The absolute path to the directory where logs are saved.
    """

    def __init__(self, logs_dir: Path) -> None:
        """Initializes the LogManager and ensures the target directory exists.

        Args:
            logs_dir (Path): The directory to store test run logs.
        """
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)

    def save_test_output(self, retry_number: int, output: str) -> Path:
        """Saves the raw output of a test run to a text file.

        Args:
            retry_number (int): The current retry loop iteration (used for naming).
            output (str): The raw stdout/stderr output from the test execution.

        Returns:
            Path: The absolute path to the newly created log file.

        Raises:
            IOError: If the log file cannot be written to disk.
        """
        log_file = self.logs_dir / f"retry-{retry_number}.log"

        try:
            log_file.write_text(output, encoding="utf-8")
            logger.debug(f"Test output saved to {log_file}")
            return log_file
        except Exception as e:
            logger.error(f"Failed to save log file {log_file}: {e}")
            raise
