import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.agents.test_agent import TestAgent
from src.application.config import Config
from src.application.session_manager import SessionManager
from src.infrastructure.notifications.telegram import TelegramNotifier


@pytest.fixture
def test_agent(mock_config: Config):
    session_manager = SessionManager(config=mock_config)
    notifier = AsyncMock(spec=TelegramNotifier)
    return TestAgent(session_manager=session_manager, notifier=notifier)


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_execute_tests_pass(mock_exec: AsyncMock, test_agent: TestAgent):
    """Tests behavior when the test suite returns exit code 0."""
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (b"All tests passed", b"")
    mock_exec.return_value = mock_process

    script_path = test_agent.session_manager.workspace / "errand_ai.sh"
    script_path.touch()

    result = await test_agent.execute()

    assert result.passed is True
    assert result.stdout == "All tests passed"
    test_agent.notifier.notify_failure.assert_not_called()


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_execute_tests_fail(mock_exec: AsyncMock, test_agent: TestAgent):
    """Tests behavior when the test suite returns a non-zero exit code."""
    mock_process = AsyncMock()
    mock_process.returncode = 1
    mock_process.communicate.return_value = (b"AssertionError", b"")
    mock_exec.return_value = mock_process
    script_path = test_agent.session_manager.workspace / "errand_ai.sh"
    script_path.touch()

    result = await test_agent.execute()

    assert result.passed is False
    assert result.stdout == "AssertionError"
    test_agent.notifier.notify_failure.assert_called_once()
