"""Agent responsible for workspace checkpointing.

This module provides the GitAgent, which establishes a version control
safety net before any destructive filesystem modifications occur.
"""

from src.application.session_manager import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.interfaces import Repository
from src.domain.models import PatchRecommendation
from src.utils import get_logger

logger = get_logger(__name__)


class GitAgent(BaseAgent[PatchRecommendation, PatchRecommendation]):
    """Agent that creates recovery checkpoints via version control.

    Attributes:
        session_manager (SessionManager): Manager for session state and events.
        repository (Repository): The infrastructure provider for version control.
    """

    def __init__(
        self,
        session_manager: SessionManager,
        repository: Repository,
    ) -> None:
        """Initializes the GitAgent.

        Args:
            session_manager (SessionManager): The session state manager.
            repository (Repository): The configured version control client.
        """
        self.session_manager = session_manager
        self.repository = repository

    async def execute(self, input_data: PatchRecommendation) -> PatchRecommendation:
        """Creates a version control checkpoint for safe recovery.

        Args:
            input_data (PatchRecommendation): The pending patch proposal.

        Returns:
            PatchRecommendation: The unmodified proposal, passed forward.
        """
        session = self.session_manager.load_session()
        retry_number = session.current_retry

        logger.info("Establishing recovery checkpoint before code modification...")

        await self.repository.create_checkpoint(retry_number=retry_number)

        self.session_manager.append_event(
            event_type="vcs_checkpoint_created",
            details=f"Retry #{retry_number}",
        )

        return input_data
