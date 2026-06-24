"""Domain models for pipeline state tracking.

This module defines the core Session state object, which tracks the overall
progress, retries, and timestamps of the current remediation attempt.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SessionStatus(str, Enum):
    """Represents the high-level state of the remediation pipeline."""

    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Session:
    """Tracks the state and metadata of a single pipeline execution.

    Attributes:
        session_id (str): Unique identifier for this run.
        status (SessionStatus): Current overall status of the pipeline.
        current_retry (int): How many times the pipeline has looped.
        max_retries (int): The hard limit for pipeline loops.
        started_at (datetime): UTC timestamp of when the session began.
        updated_at (datetime): UTC timestamp of the last state change.
    """

    session_id: str
    status: SessionStatus
    current_retry: int
    max_retries: int
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        """Serializes the session state to a dictionary for storage.

        Returns:
            dict: The dictionary representation, natively handling ISO formats
                if used with standard JSON serializers mapping datetimes.
        """
        data = asdict(self)
        # Ensure datetimes are strictly ISO strings for the JSON persistence layer
        data["started_at"] = self.started_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        """Deserializes a dictionary back into a Session object.

        Args:
            data (dict): The dictionary loaded from persistent storage.

        Returns:
            Session: A hydrated session instance.
        """
        return cls(
            session_id=data["session_id"],
            status=SessionStatus(data["status"]),
            current_retry=data["current_retry"],
            max_retries=data["max_retries"],
            started_at=datetime.fromisoformat(data["started_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
