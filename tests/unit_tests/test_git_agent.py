from pathlib import Path
from unittest.mock import Mock, patch

from src.agents.git_agent import GitAgent


@patch("src.agents.git_agent.GitClient")
def test_git_checkpoint_created(
    mock_git_client,
    tmp_path: Path,
) -> None:
    session_manager = Mock()

    agent = GitAgent(
        session_manager=session_manager,
    )

    context = {
        "workspace": str(tmp_path),
        "retry_number": 2,
    }

    agent.execute(context)

    mock_git_client.return_value.create_checkpoint.assert_called_once_with(
        retry_number=2
    )

    session_manager.append_event.assert_called_once()
