from pathlib import Path
import subprocess


class GitClient:
    def __init__(
        self,
        workspace: Path,
    ) -> None:
        self.workspace = workspace

    def create_checkpoint(
        self,
        retry_number: int,
    ) -> None:
        subprocess.run(
            ["git", "add", "."],
            cwd=self.workspace,
            check=True,
        )

        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                f"Errand AI Retry #{retry_number}",
            ],
            cwd=self.workspace,
            check=True,
        )

    def get_diff(self) -> str:
        result = subprocess.run(
            ["git", "diff"],
            cwd=self.workspace,
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout
