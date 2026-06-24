"""Persistence layer for append-only event logging.

This module provides the EventStore class, which acts as an immutable
ledger for the pipeline, recording discrete events in JSON Lines format
for observability and debugging.
"""

import json
from pathlib import Path
from typing import Any, Dict

from src.utils.logger import get_logger
from src.utils.timestamps import get_current_utc_iso

logger = get_logger(__name__)


class EventStore:
    """Manages the append-only JSON Lines event ledger.

    Attributes:
        file_path (Path): The absolute path to the .jsonl events file.
    """

    def __init__(self, file_path: Path) -> None:
        """Initializes the EventStore.

        Args:
            file_path (Path): The target path for the events ledger.
        """
        self.file_path = file_path
        # Ensure the parent directory exists immediately
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event_name: str, details: Any) -> None:
        """Appends a new event to the ledger with a standardized UTC timestamp.

        Because this uses JSON Lines format, it opens the file in append mode
        ('a') and writes a single line. This is highly memory efficient and
        safe for concurrent observation.

        Args:
            event_name (str): A distinct identifier for the event (e.g.,
                'patch_applied', 'tests_failed').
            details (Any): The contextual data associated with the event.
                Must be JSON serializable.

        Raises:
            TypeError: If the details object cannot be serialized to JSON.
            IOError: If the ledger file cannot be written to.
        """
        event_record: Dict[str, Any] = {
            "timestamp": get_current_utc_iso(),
            "event": event_name,
            "details": details,
        }

        try:
            # json.dumps ensures everything is on a single line
            line = json.dumps(event_record)

            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

            logger.debug(f"Event '{event_name}' appended to ledger.")

        except Exception as e:
            logger.error(f"Failed to append event '{event_name}' to ledger: {e}")
            raise
