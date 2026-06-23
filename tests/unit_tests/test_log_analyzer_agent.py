from unittest.mock import Mock

from src.agents.log_analyzer_agent import LogAnalyzerAgent
from src.domain.models.failure_analysis import FailureAnalysis


def test_log_analysis_success() -> None:
    mock_ai_provider = Mock()

    mock_session_manager = Mock()

    mock_ai_provider.run.return_value = FailureAnalysis(
        error_type="ImportError",
        summary="Redis import failed",
        relevant_files=["src/cache.py"],
        relevant_tests=["tests/test_cache.py"],
        related_modules=["redis"],
    )

    agent = LogAnalyzerAgent(
        ai_provider=mock_ai_provider,
        session_manager=mock_session_manager,
    )

    context = {
        "test_stdout": "",
        "test_stderr": ("ImportError: RedisClient"),
    }

    result = agent.execute(context)

    assert result["failure_analysis"].error_type == "ImportError"

    assert result["failure_analysis"].relevant_files == ["src/cache.py"]

    mock_ai_provider.run.assert_called_once()

    assert mock_session_manager.append_event.call_count == 2
