import asyncio
from pathlib import Path

from src.utils.logger import get_logger

logger = get_logger(__name__)


class GitClient:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    async def create_checkpoint(self, retry_number: int) -> None:
        logger.info(f"Creating Git checkpoint for retry #{retry_number}...")
        
        # Stage all changes
        add_process = await asyncio.create_subprocess_exec(
            "git", "add", ".",
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await add_process.communicate()

        # Commit the checkpoint
        commit_process = await asyncio.create_subprocess_exec(
            "git", "commit", "-m", f"Errand AI Retry #{retry_number}",
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await commit_process.communicate()
        
        logger.debug("Git checkpoint committed successfully.")

    async def get_diff(self) -> str:
        process = await asyncio.create_subprocess_exec(
            "git", "diff",
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await process.communicate()
        
        return stdout.decode("utf-8")