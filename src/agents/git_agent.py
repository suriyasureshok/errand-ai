from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.models import PatchRecommendation
from src.infrastructure.git import GitClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GitAgent(BaseAgent[PatchRecommendation, PatchRecommendation]):
    def __init__(
        self,
        session_manager: SessionManager,
        git_client: GitClient,
    ) -> None:
        self.session_manager = session_manager
        self.git_client = git_client

    async def execute(self, recommendation: PatchRecommendation) -> PatchRecommendation:
        session = self.session_manager.load_session()
        retry_number = session.current_retry

        logger.info("GitAgent: Establishing recovery checkpoint before code modification.")
        
        await self.git_client.create_checkpoint(retry_number=retry_number)

        self.session_manager.append_event(
            "git_checkpoint_created",
            f"Retry #{retry_number}"
        )

        # Pass the recommendation unmodified down the pipeline
        return recommendation