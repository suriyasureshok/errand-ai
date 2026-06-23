from pathlib import Path
from unittest.mock import patch

from src.infrastructure.git.git_client import GitClient


@patch("subprocess.run")
def test_create_checkpoint(
    mock_run,
    tmp_path: Path,
) -> None:
    client = GitClient(workspace=tmp_path)

    client.create_checkpoint(retry_number=2)

    assert mock_run.call_count == 2


@patch("subprocess.run")
def test_get_diff(
    mock_run,
    tmp_path: Path,
) -> None:
    mock_run.return_value.stdout = "fake diff"

    client = GitClient(workspace=tmp_path)

    diff = client.get_diff()

    assert diff == "fake diff"
