from pathlib import Path

import pytest

from src.agents.context_collector_agent import ContextCollectorAgent
from src.application.session_manager import SessionManager
from src.domain.models.failure_analysis import FailureAnalysis
from src.application.config import Config


@pytest.mark.asyncio
async def test_context_collector_execute(mock_config: Config, tmp_path: Path):
    """Tests that the agent reads suspected files and bundles them into a ContextPackage."""
    # Create a real dummy file in our mocked workspace
    mock_config.workspace = tmp_path
    target_file = tmp_path / "app" / "main.py"
    target_file.parent.mkdir()
    target_file.write_text("def run(): pass", encoding="utf-8")

    session_manager = SessionManager(config=mock_config)
    agent = ContextCollectorAgent(session_manager=session_manager)

    analysis = FailureAnalysis(
        error_type="SyntaxError",
        summary="Missing colon",
        relevant_files=["app/main.py", "does_not_exist.py"],
        relevant_tests=[],
        related_modules=[]
    )

    package = await agent.execute(analysis)

    assert package.error_type == "SyntaxError"
    assert len(package.collected_files) == 1
    assert package.collected_files[0].path == "app/main.py"
    assert package.collected_files[0].content == "def run(): pass"