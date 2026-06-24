"""Agent responsible for iteratively correcting rejected patches.

This module provides the RefactorAgent, which utilizes negative feedback
from human reviewers or guardrails to prompt the LLM for a revised fix.
"""

from src.application.session_manager import SessionManager
from src.domain.interfaces import AIProvider, BaseAgent
from src.domain.models import PatchRecommendation, RefactorRequest
from src.utils import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are an expert software engineer. 
Your previous code patch was rejected by a human reviewer or security guardrail.
Correct your previous code based purely on the provided feedback and output a new, strict patch."""


class RefactorAgent(BaseAgent[RefactorRequest, PatchRecommendation]):
    """Agent that regenerates code patches based on rejection feedback.

    Attributes:
        ai_provider (AIProvider): The configured LLM inference engine.
        session_manager (SessionManager): Manager for session state and events.
    """

    def __init__(
        self,
        ai_provider: AIProvider,
        session_manager: SessionManager,
    ) -> None:
        """Initializes the RefactorAgent.

        Args:
            ai_provider (AIProvider): The AI inference provider.
            session_manager (SessionManager): The session state manager.
        """
        self.ai_provider = ai_provider
        self.session_manager = session_manager

    async def execute(self, input_data: RefactorRequest) -> PatchRecommendation:
        """Generates a revised patch proposal.

        Args:
            input_data (RefactorRequest): The bundle containing original context,
                the rejected patch, and the explicit rejection reason.

        Returns:
            PatchRecommendation: A newly generated, theoretically compliant patch.

        Raises:
            ValueError: If the AI provider fails to return the required schema.
        """
        logger.info("Initiating refactor for rejected patch...")

        prompt = self._build_refactor_prompt(input_data)

        # Re-generate the patch using the strict Pydantic schema
        recommendation = await self.ai_provider.run(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            response_schema=PatchRecommendation,
        )

        if not isinstance(recommendation, PatchRecommendation):
            raise ValueError("AI Provider returned an invalid response type.")

        session = self.session_manager.load_session()

        # Save the new diff purely for visual logging
        self.session_manager.save_patch(
            retry_number=session.current_retry,
            diff_content=recommendation.unified_diff,
        )

        self.session_manager.append_event(
            event_type="patch_refactored",
            details=f"Addressed rejection constraint.",
        )

        logger.info("Patch refactoring complete.")
        return recommendation

    def _build_refactor_prompt(self, request: RefactorRequest) -> str:
        """Constructs the heavily contextualized refactor prompt.

        Args:
            request (RefactorRequest): The domain model containing all prior context.

        Returns:
            str: The raw prompt string to send to the LLM.
        """
        file_sections = [
            f"FILE: {f.path}\n\n```python\n{f.content}\n```"
            for f in request.package.collected_files
        ]
        files_text = "\n\n".join(file_sections)

        return (
            f"Your previous attempt to fix the codebase was rejected.\n\n"
            f"ERROR SUMMARY (Original):\n{request.package.error_summary}\n\n"
            f"REJECTION REASON:\n{request.rejection_reason}\n\n"
            f"PREVIOUS (REJECTED) PATCH OVERVIEW:\n{request.previous_recommendation.proposed_solution}\n\n"
            f"CODE CONTEXT:\n{files_text}\n\n"
            f"Requirements:\n"
            f"1. Analyze the rejection reason carefully.\n"
            f"2. Formulate a new root cause analysis if necessary.\n"
            f"3. Propose an updated, compliant solution.\n"
            f"4. Output new, exact search-and-replace blocks that resolve the issue."
        )
