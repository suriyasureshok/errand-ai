import json
from pathlib import Path

from src.application.config import Config
from src.application.session_manager import SessionManager
from src.domain.models.session import Session, SessionStatus


def test_session_manager_initialization(mock_config: Config):
    """Tests that the SessionManager creates the necessary directories."""
    manager = SessionManager(config=mock_config)

    assert manager.logs_dir.exists()
    assert manager.patches_dir.exists()


def test_load_and_increment_retry(mock_config: Config):
    """Tests state transitions within the session."""
    manager = SessionManager(config=mock_config)

    # Load initial
    session = manager.load_session()
    assert session.current_retry == 0

    # Increment
    manager.increment_retry()

    # Reload and verify
    updated_session = manager.load_session()
    assert updated_session.current_retry == 1


def test_save_patch(mock_config: Config):
    """Tests that unified diffs are correctly written to disk."""
    manager = SessionManager(config=mock_config)
    diff_content = "--- a/test\n+++ b/test\n@@ -1 +1 @@\n- old\n+ new\n"

    manager.save_patch(retry_number=1, diff_content=diff_content)

    patch_file = manager.patches_dir / "retry-1.diff"
    assert patch_file.exists()
    assert patch_file.read_text(encoding="utf-8") == diff_content


def test_append_event(mock_config: Config):
    """Tests that events are appended as JSON Lines."""
    manager = SessionManager(config=mock_config)

    manager.append_event("test_event", "Something happened")
    manager.append_event("test_event_2", "Another thing happened")

    lines = manager.events_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2

    first_event = json.loads(lines[0])
    assert first_event["event"] == "test_event"
    assert first_event["details"] == "Something happened"
