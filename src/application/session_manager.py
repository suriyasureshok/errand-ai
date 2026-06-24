import json
from datetime import datetime, timezone
from pathlib import Path

from src.application import Config
from src.domain.models import Session, SessionStatus


class SessionManager:
    def __init__(self, config: Config) -> None:
        self.workspace = Path(config.workspace)
        self.max_retries = config.max_retries

        self.base_dir = self.workspace / ".errand-ai"
        self.logs_dir = self.base_dir / "logs"
        self.patches_dir = self.base_dir / "patches"
        self.context_dir = self.base_dir / "context"
        self.history_dir = self.base_dir / "history"

        self.session_file = self.base_dir / "session.json"
        self.events_file = self.history_dir / "events.jsonl"

        self._initialize()

    def _initialize(self) -> None:
        """Creates the necessary directory structure if it doesn't exist."""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.patches_dir.mkdir(parents=True, exist_ok=True)
        self.context_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        if not self.session_file.exists():
            self._create_session()

    def _create_session(self) -> None:
        """Initializes a new session and writes it to disk."""
        now = datetime.now(timezone.utc)

        session = Session(
            session_id=f"sess_{int(now.timestamp())}",
            status=SessionStatus.RUNNING,
            current_retry=0,
            max_retries=self.max_retries,
            started_at=now.isoformat(),
            updated_at=now.isoformat(),
        )

        self.save_session(session)

    def load_session(self) -> Session:
        """Reads the session from disk and returns a Domain Model."""
        data = json.loads(self.session_file.read_text(encoding="utf-8"))
        return Session.from_dict(data)

    def save_session(self, session: Session) -> None:
        """Updates the timestamp and writes the Session model back to disk."""
        session.updated_at = datetime.now(timezone.utc).isoformat()

        self.session_file.write_text(
            json.dumps(
                session.to_dict(), 
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )

    def increment_retry(self) -> int:
        """Increments the current retry counter and saves the session."""
        session = self.load_session()
        session.current_retry += 1
        self.save_session(session)
        return session.current_retry

    def mark_success(self) -> None:
        """Marks the session as completed successfully."""
        session = self.load_session()
        session.status = SessionStatus.SUCCESS
        self.save_session(session)

    def mark_failed(self) -> None:
        """Marks the session as failed (e.g., out of retries)."""
        session = self.load_session()
        session.status = SessionStatus.FAILED
        self.save_session(session)

    def append_event(self, event_type: str, details: str) -> None:
        """Appends a timestamped event to the JSON Lines history file."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            "details": details,
        }

        with self.events_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(event, default=str) + "\n")

    def save_log(self, retry_number: int, content: str) -> Path:
        """Saves raw output logs for a specific retry attempt."""
        log_file = self.logs_dir / f"retry-{retry_number}.log"
        log_file.write_text(content, encoding="utf-8")
        return log_file

    def save_patch(self, retry_number: int, diff_content: str) -> Path:
        """Saves the generated diff patch for a specific retry attempt."""
        patch_file = self.patches_dir / f"retry-{retry_number}.diff"
        patch_file.write_text(diff_content, encoding="utf-8")
        return patch_file

    def save_context(self, retry_number: int, context_content: str) -> Path:
        """Saves the collected context window for a specific retry attempt."""
        context_file = self.context_dir / f"retry-{retry_number}-context.txt"
        context_file.write_text(context_content, encoding="utf-8")
        return context_file
