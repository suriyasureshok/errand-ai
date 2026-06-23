import json
from datetime import datetime
from pathlib import Path


class SessionManager:
    def __init__(
        self,
        workspace: Path,
        max_retries: int,
    ) -> None:
        self.workspace = workspace

        self.base_dir = workspace / ".errand-ai"

        self.logs_dir = self.base_dir / "logs"

        self.patches_dir = self.base_dir / "patches"

        self.context_dir = self.base_dir / "context"

        self.history_dir = self.base_dir / "history"

        self.session_file = self.base_dir / "session.json"

        self.events_file = self.history_dir / "events.jsonl"

        self.max_retries = max_retries

        self._initialize()

    def _initialize(self) -> None:
        self.logs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.patches_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.context_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.history_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.session_file.exists():
            self._create_session()

    def _create_session(self) -> None:
        session = {
            "session_id": (f"sess_{int(datetime.utcnow().timestamp())}"),
            "status": "running",
            "current_retry": 0,
            "max_retries": self.max_retries,
            "started_at": (datetime.utcnow().isoformat()),
            "updated_at": (datetime.utcnow().isoformat()),
        }

        self.session_file.write_text(
            json.dumps(
                session,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_session(self) -> dict:
        return json.loads(self.session_file.read_text(encoding="utf-8"))

    def save_session(
        self,
        session: dict,
    ) -> None:
        session["updated_at"] = datetime.utcnow().isoformat()

        self.session_file.write_text(
            json.dumps(
                session,
                indent=2,
            ),
            encoding="utf-8",
        )

    def increment_retry(self) -> int:
        session = self.load_session()

        session["current_retry"] += 1

        self.save_session(session)

        return session["current_retry"]

    def mark_success(self) -> None:
        session = self.load_session()

        session["status"] = "success"

        self.save_session(session)

    def mark_failed(self) -> None:
        session = self.load_session()

        session["status"] = "failed"

        self.save_session(session)

    def append_event(
        self,
        event_type: str,
        details: str,
    ) -> None:
        event = {
            "timestamp": (datetime.utcnow().isoformat()),
            "event": event_type,
            "details": details,
        }

        with self.events_file.open(
            "a",
            encoding="utf-8",
        ) as file:
            file.write(json.dumps(event))
            file.write("\n")

    def save_log(
        self,
        retry_number: int,
        content: str,
    ) -> Path:
        log_file = self.logs_dir / f"retry-{retry_number}.log"

        log_file.write_text(
            content,
            encoding="utf-8",
        )

        return log_file

    def save_patch(
        self,
        retry_number: int,
        diff_content: str,
    ) -> Path:
        patch_file = self.patches_dir / f"retry-{retry_number}.diff"

        patch_file.write_text(
            diff_content,
            encoding="utf-8",
        )

        return patch_file

    def save_context(
        self,
        retry_number: int,
        context_content: str,
    ) -> Path:
        context_file = self.context_dir / f"retry-{retry_number}-context.txt"

        context_file.write_text(
            context_content,
            encoding="utf-8",
        )

        return context_file
