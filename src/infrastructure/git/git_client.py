"""Git version control infrastructure.

This module provides the GitClient, responsible for executing OS-level git
commands to create safety checkpoints and extract uncommitted changes.
"""

import asyncio
from pathlib import Path

from src.domain.interfaces.repository import Repository
from src.utils.logger import get_logger

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

    async def _ensure_safe_directory(self) -> None:
        """Configures Git to trust the mounted workspace.

        This prevents 'dubious ownership' errors when running inside Docker
        containers with mounted host volumes.
        """
        process = await asyncio.create_subprocess_exec(
            "git",
            "config",
            "--global",
            "--add",
            "safe.directory",
            str(self.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await process.communicate()

    async def create_checkpoint(self, retry_number: int) -> None:
        """Stages and commits all current changes as a safety checkpoint."""
        logger.info(f"Creating Git checkpoint for retry #{retry_number}...")

        # Ensure Git trusts the container path before executing commands
        await self._ensure_safe_directory()

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
            logger.warning("Git add command returned a non-zero exit code.")

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

        if commit_process.returncode not in (0, 1):
            error_msg = stderr.decode("utf-8").strip()
            raise RuntimeError(f"Git commit failed: {error_msg}")

        logger.debug("Git checkpoint processed successfully.")

    async def get_diff(self) -> str:
        """Retrieves the current uncommitted changes."""
        await self._ensure_safe_directory()

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
