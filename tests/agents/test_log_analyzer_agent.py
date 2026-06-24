from unittest.mock import AsyncMock

import pytest

from src.agents.log_analyzer_agent import LogAnalyzerAgent
from src.application.config import Config
from src.application.session_manager import SessionManager
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.failure_analysis import FailureAnalysis
from src.domain.models.test_result import TestResult


@pytest.mark.asyncio
async def test_log_analyzer_execute(mock_config: Config):
    """Tests that logs are sent to the AI and a FailureAnalysis is returned."""
    session_manager = SessionManager(config=mock_config)

    # Mock the AI Provider to return a known FailureAnalysis object
    mock_ai = AsyncMock(spec=AIProvider)
    expected_analysis = FailureAnalysis(
        error_type="AssertionError",
        summary="Test math failed",
        relevant_files=["tests/test_math.py"],
        relevant_tests=[],
        related_modules=[],
    )
    mock_ai.run.return_value = expected_analysis

    agent = LogAnalyzerAgent(ai_provider=mock_ai, session_manager=session_manager)

    # Create a dummy test result
    test_result = TestResult(
        passed=False,
        stdout="",
        stderr="Traceback...",
        exit_code=1,
        log_file_path="/fake/path.log",
    )

    result = await agent.execute(test_result)

    assert result == expected_analysis
    mock_ai.run.assert_called_once()
    assert "Traceback..." in mock_ai.run.call_args.kwargs["prompt"]
