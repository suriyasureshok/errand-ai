"""Agent responsible for human-in-the-loop workflows.

This module provides the ApprovalAgent, which halts the asynchronous
pipeline execution until a human reviewer interacts with the configured
notification infrastructure (e.g., Telegram).
"""

from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.interfaces import Notifier
from src.domain.models import ApprovalResult
from src.domain.models import PatchRecommendation
from src.utils import get_logger

logger = get_logger(__name__)


class ApprovalAgent(BaseAgent[PatchRecommendation, ApprovalResult]):
    """Agent that coordinates mandatory human review of code patches.

    Attributes:
        notifier (Notifier): The outbound messaging infrastructure.
        session_manager (SessionManager): Manager for session events.
    """

    def __init__(
        self,
        notifier: Notifier,
        session_manager: SessionManager,
    ) -> None:
        """Initializes the ApprovalAgent.

        Args:
            notifier (Notifier): The configured notification client.
            session_manager (SessionManager): The session state manager.
        """
        self.notifier = notifier
        self.session_manager = session_manager

    async def execute(self, input_data: PatchRecommendation) -> ApprovalResult:
        """Dispatches an interactive approval request and awaits a response.

        Args:
            input_data (PatchRecommendation): The proposed fix to be reviewed.

        Returns:
            ApprovalResult: The decision yielded by the human or system timeout.
        """
        logger.info("Requesting human approval via notification channels...")

        summary = (
            f"Root Cause Analysis:\n{input_data.root_cause}\n\n"
            f"Proposed Solution:\n{input_data.proposed_solution}"
        )

        self.session_manager.append_event(
            event_type="approval_requested",
            details="Notification dispatched to human reviewer.",
        )

        # Pipeline halts asynchronously here until the notifier unblocks it
        result = await self.notifier.request_approval(
            summary=summary,
            diff=input_data.unified_diff,
        )

        logger.info(f"Approval process concluded with status: {result.status.name}")
        
        self.session_manager.append_event(
            event_type="approval_concluded",
            details=f"Status: {result.status.name} | Reason: {result.reason or 'None'}",
        )

        return result