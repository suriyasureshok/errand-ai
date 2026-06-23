from pathlib import Path
from unittest.mock import Mock

from src.agents.context_collector_agent import ContextCollectorAgent
from src.domain.models.failure_analysis import FailureAnalysis


def test_collect_context_files(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "src" / "cache.py"

    source_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    source_file.write_text(
        "import redis",
        encoding="utf-8",
    )

    test_file = tmp_path / "tests" / "test_cache.py"

    test_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    test_file.write_text(
        "def test_cache(): pass",
        encoding="utf-8",
    )

    mock_session_manager = Mock()

    analysis = FailureAnalysis(
        error_type="ImportError",
        summary="Redis import failed",
        relevant_files=["src/cache.py"],
        relevant_tests=["tests/test_cache.py"],
        related_modules=["redis"],
    )

    agent = ContextCollectorAgent(
        session_manager=mock_session_manager,
    )

    context = {
        "workspace": str(tmp_path),
        "failure_analysis": analysis,
        "retry_number": 1,
    }

    result = agent.execute(context)

    package = result["context_package"]

    assert package.error_type == "ImportError"

    assert len(package.collected_files) == 2

    mock_session_manager.save_context.assert_called_once()

    mock_session_manager.append_event.assert_called_once()


def test_missing_files_are_ignored(
    tmp_path: Path,
) -> None:
    mock_session_manager = Mock()

    analysis = FailureAnalysis(
        error_type="ImportError",
        summary="Redis import failed",
        relevant_files=["src/missing.py"],
        relevant_tests=[],
        related_modules=[],
    )

    agent = ContextCollectorAgent(
        session_manager=mock_session_manager,
    )

    context = {
        "workspace": str(tmp_path),
        "failure_analysis": analysis,
        "retry_number": 1,
    }

    result = agent.execute(context)

    package = result["context_package"]

    assert len(package.collected_files) == 0
