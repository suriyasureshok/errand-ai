"""Agent responsible for generating code fixes.

This module provides the PatchGeneratorAgent, which feeds the aggregated
context into an LLM and outputs a structured PatchRecommendation.
"""

import json

from src.domain.interfaces import AIProvider, BaseAgent
from src.domain.models import ContextPackage, PatchRecommendation
from src.utils import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are an elite, autonomous software engineer.
You will be provided with a set of source code files and an error summary.
Your objective is to fix the error by proposing exact, byte-for-byte search and replace blocks.
CRITICAL RULES:
1. The `search_block` must match the existing code in the file EXACTLY, including all indentation and newlines.
2. The `replace_block` must contain the fixed code with identical relative indentation.
3. Keep the patches as minimal as possible to avoid unintended side effects."""


class PatchGeneratorAgent(BaseAgent[ContextPackage, PatchRecommendation]):
    """Agent that formulates actionable codebase modifications.

    Attributes:
        ai_provider (AIProvider): The configured LLM inference engine.
    """

    def __init__(self, ai_provider: AIProvider) -> None:
        """Initializes the PatchGeneratorAgent.

        Args:
            ai_provider (AIProvider): The infrastructure provider for AI inference.
        """
        self.ai_provider = ai_provider

    async def execute(self, input_data: ContextPackage) -> PatchRecommendation:
        """Generates a code modification proposal based on the context.

        Args:
            input_data (ContextPackage): The bundled source code and error data.

        Returns:
            PatchRecommendation: The structured, platform-agnostic patch proposal.

        Raises:
            ValueError: If the AI provider fails to return a valid schema.
        """
        logger.info("Generating patch recommendation via AI...")

        # Construct a highly detailed prompt containing all file context
        files_context = "\n\n".join(
            f"--- FILE: {f.path} ---\n```python\n{f.content}\n```"
            for f in input_data.collected_files
        )

        prompt = (
            f"ERROR TYPE: {input_data.error_type}\n"
            f"ERROR SUMMARY: {input_data.error_summary}\n\n"
            f"Below are the files relevant to the issue:\n\n{files_context}\n\n"
            f"Please generate the exact search-and-replace patches required to fix this issue."
        )

        recommendation = await self.ai_provider.run(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            response_schema=PatchRecommendation,
        )

        if not isinstance(recommendation, PatchRecommendation):
            raise ValueError("AI Provider returned an invalid response type.")

        logger.debug(
            f"Patch generated with {len(recommendation.patches)} modifications."
        )
        return recommendation
