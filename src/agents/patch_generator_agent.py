from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.interfaces import AIProvider
from src.domain.models import ContextPackage
from src.domain.models import PatchRecommendation
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PatchGeneratorAgent(BaseAgent[ContextPackage, PatchRecommendation]):
    def __init__(
        self,
        ai_provider: AIProvider,
        session_manager: SessionManager,
    ) -> None:
        self.ai_provider = ai_provider
        self.session_manager = session_manager

    async def execute(self, package: ContextPackage) -> PatchRecommendation:
        logger.info("Generating patch recommendation based on collected context...")
        
        prompt = self._build_prompt(package)

        recommendation: PatchRecommendation = await self.ai_provider.run(
            prompt=prompt,
            system_prompt="You are an expert software engineer. Always output strictly valid unified diffs.",
            response_schema=PatchRecommendation,
        )

        session = self.session_manager.load_session()

        # Persist the proposed diff to the .errand-ai/patches directory
        self.session_manager.save_patch(
            retry_number=session.current_retry,
            diff_content=recommendation.unified_diff,
        )

        self.session_manager.append_event(
            "patch_generated",
            f"Root Cause: {recommendation.root_cause[:50]}..."
        )

        logger.info("Patch generation complete.")

        return recommendation

    def _build_prompt(self, package: ContextPackage) -> str:
        file_sections: list[str] = []
        for context_file in package.collected_files:
            file_sections.append(f"FILE: {context_file.path}\n\n{context_file.content}")
        files_text = "\n\n".join(file_sections)

        return f"""
Analyze the following code context to resolve the test failure.

ERROR TYPE:
{package.error_type}

ERROR SUMMARY:
{package.error_summary}

FILES:
{files_text}

Requirements:
1. Determine the exact root cause of the error.
2. Propose the safest logical fix.
3. Generate the `patches` array using exact Search and Replace blocks. 
   - The `search_block` MUST match the existing code exactly, including all indentation.
   - Keep the blocks concise (only include the lines being changed and 1-2 context lines).
4. Generate a `unified_diff` string purely for the human reviewer to read.
"""