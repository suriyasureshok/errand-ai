from pathlib import Path
from typing import Any

from src.application.session_manager import (
    SessionManager,
)
from src.domain.interfaces.agent import (
    BaseAgent,
)
from src.infrastructure.git.git_client import (
    GitClient,
)


class GitAgent(BaseAgent):
    def __init__(
        self,
        session_manager: SessionManager,
    ) -> None:
        self.session_manager = session_manager

    def execute(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        workspace = Path(context["workspace"])

        retry_number = context["retry_number"]

        git_client = GitClient(workspace=workspace)

        git_client.create_checkpoint(retry_number=retry_number)

        self.session_manager.append_event(
            "git_checkpoint_created",
            (f"Retry #{retry_number}"),
        )

        return context
