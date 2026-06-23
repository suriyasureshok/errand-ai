from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.agents.test_agent import TestAgent


@pytest.fixture
def mock_session_manager() -> Mock:
    manager = Mock()

    manager.save_log.return_value = Path(".errand-ai/logs/retry-0.log")

    return manager


@pytest.fixture
def mock_telegram_client() -> Mock:
    client = Mock()

    client.notify_success = AsyncMock()
    client.notify_failure = AsyncMock()

    return client


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    script = tmp_path / "errand_ai.sh"

    script.write_text(
        "#!/bin/bash\necho 'hello world'\n",
        encoding="utf-8",
    )

    return tmp_path


def test_execute_success(
    workspace: Path,
    mock_session_manager: Mock,
    mock_telegram_client: Mock,
) -> None:
    agent = TestAgent(
        session_manager=mock_session_manager,
        telegram_client=mock_telegram_client,
    )

    context = {
        "workspace": str(workspace),
    }

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = "all tests passed"
        mock_run.return_value.stderr = ""
        mock_run.return_value.returncode = 0

        result = agent.execute(context)

    assert result["tests_passed"] is True

    assert result["test_exit_code"] == 0

    mock_session_manager.mark_success.assert_called_once()

    mock_session_manager.save_log.assert_called_once()


def test_execute_failure(
    workspace: Path,
    mock_session_manager: Mock,
    mock_telegram_client: Mock,
) -> None:
    agent = TestAgent(
        session_manager=mock_session_manager,
        telegram_client=mock_telegram_client,
    )

    context = {
        "workspace": str(workspace),
    }

    with patch("subprocess.run") as mock_run:
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "ImportError"
        mock_run.return_value.returncode = 1

        result = agent.execute(context)

    assert result["tests_passed"] is False

    assert result["test_exit_code"] == 1

    mock_session_manager.mark_success.assert_not_called()

    mock_session_manager.save_log.assert_called_once()


def test_missing_script_raises(
    tmp_path: Path,
    mock_session_manager: Mock,
    mock_telegram_client: Mock,
) -> None:
    agent = TestAgent(
        session_manager=mock_session_manager,
        telegram_client=mock_telegram_client,
    )

    context = {
        "workspace": str(tmp_path),
    }

    with pytest.raises(FileNotFoundError):
        agent.execute(context)
