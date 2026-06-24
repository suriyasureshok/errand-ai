"""Session orchestration and persistence management.

This module provides the SessionManager, which acts as a facade over the
persistence and filesystem layers. It exposes high-level domain operations
while delegating raw disk I/O to dedicated infrastructure managers.
"""

from datetime import datetime, timezone
from pathlib import Path

from src.application.config import Config
from src.domain.models.session import Session, SessionStatus
from src.infrastructure.filesystem import ContextManager, LogManager, PatchManager
from src.infrastructure.persistence import EventStore, SessionStore
from src.utils import get_current_utc_iso, get_logger

logger = get_logger(__name__)


class SessionManager:
    """Orchestrates pipeline state, history, and workspace modifications.

    Attributes:
        workspace (Path): The root directory of the target codebase.
        max_retries (int): The maximum allowed pipeline loops.
    """

    def __init__(self, config: Config) -> None:
        """Initializes the SessionManager and its underlying infrastructure stores.

        Args:
            config (Config): The application configuration object.
        """
        self.workspace = config.workspace
        self.max_retries = config.max_retries

        self.base_dir = self.workspace / ".errand-ai"

        # Legacy context directory for raw text dumps
        self.context_dir = self.base_dir / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)

        # Initialize dedicated infrastructure layers
        self._session_store = SessionStore(self.base_dir / "session.json")
        self._event_store = EventStore(self.base_dir / "history" / "events.jsonl")

        self.log_manager = LogManager(self.base_dir / "logs")
        self.patch_manager = PatchManager(self.workspace, self.base_dir / "patches")
        self.context_manager = ContextManager(self.workspace)

        self._initialize()

    def _initialize(self) -> None:
        """Ensures a session exists, creating one if this is a fresh run."""
        if not self._session_store.file_path.exists():
            self._create_session()

    def _create_session(self) -> None:
        """Initializes a new session domain model and writes it to disk."""
        now_iso = get_current_utc_iso()
        # Parse it back to a datetime object for the Domain Model initialization
        now_dt = datetime.fromisoformat(now_iso.replace("Z", "+00:00"))

        session = Session(
            session_id=f"sess_{int(now_dt.timestamp())}",
            status=SessionStatus.RUNNING,
            current_retry=0,
            max_retries=self.max_retries,
            started_at=now_dt,
            updated_at=now_dt,
        )

        self.save_session(session)

    def load_session(self) -> Session:
        """Reads the session from disk and returns a hydrated Domain Model.

        Returns:
            Session: The current pipeline session state.
        """
        data = self._session_store.load()
        return Session.from_dict(data)

    def save_session(self, session: Session) -> None:
        """Updates the session timestamp and atomically writes it to disk.

        Args:
            session (Session): The modified session state to persist.
        """
        session.updated_at = datetime.now(timezone.utc)
        self._session_store.save(session.to_dict())

    def increment_retry(self) -> int:
        """Increments the retry counter and saves the session.

        Returns:
            int: The new retry count.
        """
        session = self.load_session()
        session.current_retry += 1
        self.save_session(session)
        self.append_event(
            "retry_incremented", f"Beginning retry loop {session.current_retry}"
        )
        return session.current_retry

    def mark_success(self) -> None:
        """Marks the session as completed successfully."""
        session = self.load_session()
        session.status = SessionStatus.SUCCESS
        self.save_session(session)
        self.append_event("session_success", "Pipeline resolved the issue.")

    def mark_failed(self) -> None:
        """Marks the session as failed (e.g., out of retries)."""
        session = self.load_session()
        session.status = SessionStatus.FAILED
        self.save_session(session)
        self.append_event("session_failed", "Pipeline failed to resolve the issue.")

    def append_event(self, event_type: str, details: str) -> None:
        """Appends an event to the JSON Lines history ledger.

        Args:
            event_type (str): Categorical identifier for the event.
            details (str): Contextual information about the event.
        """
        self._event_store.append(event_name=event_type, details=details)

    def save_log(self, retry_number: int, content: str) -> Path:
        """Saves raw output logs via the LogManager.

        Args:
            retry_number (int): The current retry loop iteration.
            content (str): Raw stdout/stderr to persist.

        Returns:
            Path: The path to the saved log file.
        """
        return self.log_manager.save_test_output(retry_number, content)

    def save_patch(self, retry_number: int, diff_content: str) -> Path:
        """Saves a visual diff patch via the PatchManager.

        Args:
            retry_number (int): The current retry loop iteration.
            diff_content (str): The unified diff string to persist.

        Returns:
            Path: The path to the saved diff file.
        """
        self.patch_manager.save_unified_diff(retry_number, diff_content)
        return self.patch_manager.patches_dir / f"retry-{retry_number}.diff"

    def save_context(self, retry_number: int, context_content: str) -> Path:
        """Saves the aggregated LLM prompt context to disk for debugging.

        Args:
            retry_number (int): The current retry loop iteration.
            context_content (str): The full text prompt sent to the LLM.

        Returns:
            Path: The path to the saved context file.
        """
        context_file = self.context_dir / f"retry-{retry_number}-context.txt"
        context_file.write_text(context_content, encoding="utf-8")
        return context_file
