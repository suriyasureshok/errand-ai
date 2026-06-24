from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.interfaces import Notifier
from src.domain.models import ApprovalResult
from src.domain.models import PatchRecommendation
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApprovalAgent(BaseAgent[PatchRecommendation, ApprovalResult]):
    def __init__(
        self,
        notifier: Notifier,
        session_manager: SessionManager,
    ) -> None:
        self.notifier = notifier
        self.session_manager = session_manager

    async def execute(self, recommendation: PatchRecommendation) -> ApprovalResult:
        logger.info("Requesting human approval...")
        
        summary = (
            f"Root Cause Analysis:\n{recommendation.root_cause}\n\n"
            f"Proposed Solution:\n{recommendation.proposed_solution}"
        )

        self.session_manager.append_event(
            "approval_requested",
            "Notification dispatched to human reviewer"
        )

        # Execution halts here until the notifier returns a result
        result = await self.notifier.request_approval(
            summary=summary,
            diff=recommendation.unified_diff,
        )

        logger.info(f"Approval process concluded with status: {result.status.name}")
        self.session_manager.append_event(
            "approval_concluded",
            f"Status: {result.status.name}"
        )

        return result