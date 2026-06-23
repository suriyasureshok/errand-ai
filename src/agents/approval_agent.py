import asyncio
from typing import Any

from src.application.session_manager import (
    SessionManager,
)
from src.domain.interfaces.agent import (
    BaseAgent,
)
from src.domain.models.patch_recommendation import (
    PatchRecommendation,
)
from src.infrastructure.notifications.telegram import (
    TelegramClient,
)


class ApprovalAgent(BaseAgent):
    def __init__(
        self,
        telegram_client: TelegramClient,
        session_manager: SessionManager,
    ) -> None:
        self.telegram_client = telegram_client
        self.session_manager = session_manager

    def execute(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        recommendation: PatchRecommendation = context["patch_recommendation"]

        approval_message = f"""
Tests Failed

Root Cause:
{recommendation.root_cause}

Suggested Fix:
{recommendation.proposed_solution}

Diff:
{recommendation.unified_diff}

Approve?
"""

        asyncio.run(self.telegram_client.request_approval(approval_message))

        self.session_manager.append_event(
            "approval_requested",
            "Telegram approval sent",
        )

        context["approval_status"] = "pending"

        return context
