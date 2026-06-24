"""Persistence layer for application state management.

This module provides the SessionStore class, responsible for the safe,
atomic reading and writing of the pipeline's mutable state to disk.
"""

import json
from pathlib import Path
from typing import Any, Dict

from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionStore:
    """Manages the atomic reading and writing of session state.

    Attributes:
        file_path (Path): The absolute path to the session JSON file.
    """

    def __init__(self, file_path: Path) -> None:
        """Initializes the SessionStore.

        Args:
            file_path (Path): The target path for the session state file.
        """
        self.file_path = file_path

    def load(self) -> Dict[str, Any]:
        """Loads the current session state from disk.

        If the file does not exist, it safely returns an empty dictionary,
        allowing the application layer to initialize default values.

        Returns:
            Dict[str, Any]: The parsed JSON state, or an empty dict if the
                file does not exist.

        Raises:
            json.JSONDecodeError: If the file exists but contains invalid JSON.
        """
        if not self.file_path.exists():
            logger.debug(
                f"Session file not found at {self.file_path}. Returning empty state."
            )
            return {}

        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, state: Dict[str, Any]) -> None:
        """Saves the session state to disk atomically.

        Writes the state to a temporary file first, then atomically replaces
        the target file. This prevents state corruption if the process is
        interrupted during the write operation.

        Args:
            state (Dict[str, Any]): The current application state to serialize.

        Raises:
            IOError: If the file cannot be written to disk.
        """
        # Ensure the parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        temp_file = self.file_path.with_suffix(".tmp")

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=4)

            # Atomic replacement (POSIX compliant, heavily reduces corruption risk)
            temp_file.replace(self.file_path)
            logger.debug(f"Session state atomically saved to {self.file_path}")

        except Exception as e:
            logger.error(f"Failed to save session state: {e}")
            # Clean up the orphaned temp file if the write failed
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise
