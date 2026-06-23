import asyncio
from typing import Any

from src.application.session_manager import SessionManager
from src.domain.interfaces.agent import BaseAgent
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.context_package import ContextPackage
from src.domain.models.patch_recommendation import PatchRecommendation
from src.infrastructure.notifications.telegram import TelegramClient


class PatchGeneratorAgent(BaseAgent):
    def __init__(
        self,
        ai_provider: AIProvider,
        telegram_client: TelegramClient,
        session_manager: SessionManager,
    ) -> None:
        self.ai_provider = ai_provider
        self.telegram_client = telegram_client
        self.session_manager = session_manager

    def execute(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        package: ContextPackage = context["context_package"]

        prompt = self._build_prompt(package)

        recommendation: PatchRecommendation = self.ai_provider.run(
            prompt=prompt,
            response_schema=PatchRecommendation,
        )

        context["patch_recommendation"] = recommendation

        self.session_manager.save_patch(
            retry_number=context["retry_number"],
            diff_content=recommendation.unified_diff,
        )

        self.session_manager.append_event(
            "patch_generated",
            recommendation.root_cause,
        )

        approval_message = f"""
Root Cause:
{recommendation.root_cause}

Proposed Solution:
{recommendation.proposed_solution}

Diff:

{recommendation.unified_diff}
"""

        asyncio.run(self.telegram_client.request_approval(approval_message))

        context["awaiting_approval"] = True

        return context

    def _build_prompt(
        self,
        package: ContextPackage,
    ) -> str:
        file_sections: list[str] = []

        for context_file in package.collected_files:
            file_sections.append(
                f"""
FILE: {context_file.path}

{context_file.content}
"""
            )

        files_text = "\n\n".join(file_sections)

        return f"""
You are an expert software debugging assistant.

ERROR TYPE:
{package.error_type}

ERROR SUMMARY:
{package.error_summary}

FILES:
{files_text}

Requirements:

1. Determine the exact root cause.
2. Propose the safest fix.
3. Generate a valid unified diff.
4. Modify only necessary files.
5. Do not introduce unrelated changes.
"""
