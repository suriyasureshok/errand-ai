import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.git.git_client import GitClient


@pytest.fixture
def git_client(tmp_path: Path) -> GitClient:
    return GitClient(workspace=tmp_path)


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_create_checkpoint(mock_exec: AsyncMock, git_client: GitClient):
    """Tests that Git checkpoints correctly stage and commit."""
    # Mock the process object returned by create_subprocess_exec
    mock_process = AsyncMock()
    mock_process.communicate.return_value = (b"", b"")
    mock_exec.return_value = mock_process

    await git_client.create_checkpoint(retry_number=2)

    # Verify 'git add .' was called
    mock_exec.assert_any_call(
        "git",
        "add",
        ".",
        cwd=git_client.workspace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Verify 'git commit' was called with the correct message
    mock_exec.assert_any_call(
        "git",
        "commit",
        "-m",
        "Errand AI Retry #2",
        cwd=git_client.workspace,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )


@pytest.mark.asyncio
@patch("asyncio.create_subprocess_exec")
async def test_get_diff(mock_exec: AsyncMock, git_client: GitClient):
    """Tests that get_diff captures and decodes stdout."""
    mock_process = AsyncMock()
    # Simulate a git diff output
    mock_process.communicate.return_value = (b"--- a/test\n+++ b/test", b"")
    mock_exec.return_value = mock_process

    diff = await git_client.get_diff()

    assert diff == "--- a/test\n+++ b/test"
