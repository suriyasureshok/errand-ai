"""Git version control infrastructure.

This module provides the GitClient, responsible for executing OS-level git
commands to create safety checkpoints and extract uncommitted changes.
"""

import asyncio
from pathlib import Path

from src.domain.interfaces import Repository
from src.utils import get_logger

logger = get_logger(__name__)


class GitClient(Repository):
    """Implementation of the Repository interface using the local Git CLI.

    Attributes:
        workspace (Path): The root directory of the target Git repository.
    """

    def __init__(self, workspace: Path) -> None:
        """Initializes the GitClient.

        Args:
            workspace (Path): The absolute path to the codebase workspace.
        """
        self.workspace = workspace

    async def create_checkpoint(self, retry_number: int) -> None:
        """Stages and commits all current changes as a safety checkpoint.

        Args:
            retry_number (int): The current pipeline execution loop index.

        Raises:
            RuntimeError: If the Git subprocess fails to execute properly.
        """
        logger.info(f"Creating Git checkpoint for retry #{retry_number}...")

        # Stage all changes
        add_process = await asyncio.create_subprocess_exec(
            "git",
            "add",
            ".",
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await add_process.communicate()

        if add_process.returncode != 0:
            logger.warning(
                "Git add command returned a non-zero exit code. Working directory might be empty or unchanged."
            )

        # Commit the checkpoint
        commit_process = await asyncio.create_subprocess_exec(
            "git",
            "commit",
            "-m",
            f"Errand AI Retry #{retry_number}",
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await commit_process.communicate()

        # Git commit returns 1 if there is nothing to commit. We can safely ignore that.
        if commit_process.returncode not in (0, 1):
            error_msg = stderr.decode("utf-8").strip()
            raise RuntimeError(f"Git commit failed: {error_msg}")

        logger.debug("Git checkpoint processed successfully.")

    async def get_diff(self) -> str:
        """Retrieves the current uncommitted changes.

        Returns:
            str: The raw unified diff representing pending changes.

        Raises:
            RuntimeError: If the Git diff subprocess fails.
        """
        process = await asyncio.create_subprocess_exec(
            "git",
            "diff",
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode("utf-8").strip()
            raise RuntimeError(f"Git diff failed: {error_msg}")

        return stdout.decode("utf-8")
