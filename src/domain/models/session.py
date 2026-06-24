from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SessionStatus(str, Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Session:
    session_id: str
    status: SessionStatus
    current_retry: int
    max_retries: int
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(
            session_id=data["session_id"],
            status=SessionStatus(data["status"]),
            current_retry=data["current_retry"],
            max_retries=data["max_retries"],
            started_at=datetime.fromisoformat(data["started_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
