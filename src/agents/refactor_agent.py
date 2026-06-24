from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.interfaces import AIProvider
from src.domain.models import PatchRecommendation
from src.domain.models import RefactorRequest
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RefactorAgent(BaseAgent[RefactorRequest, PatchRecommendation]):
    def __init__(
        self,
        ai_provider: AIProvider,
        session_manager: SessionManager,
    ) -> None:
        self.ai_provider = ai_provider
        self.session_manager = session_manager

    async def execute(self, request: RefactorRequest) -> PatchRecommendation:
        logger.info("Initiating refactor for rejected patch...")
        
        prompt = self._build_refactor_prompt(request)

        # Re-generate the patch using the strict Pydantic schema
        recommendation: PatchRecommendation = await self.ai_provider.run(
            prompt=prompt,
            system_prompt="You are an expert software engineer. Correct your previous code based on the provided feedback.",
            response_schema=PatchRecommendation,
        )

        session = self.session_manager.load_session()

        # Overwrite or save the new refactored patch
        self.session_manager.save_patch(
            retry_number=session.current_retry,
            diff_content=recommendation.unified_diff,
        )

        self.session_manager.append_event(
            "patch_refactored",
            f"Addressed rejection: {request.rejection_reason}"
        )

        logger.info("Refactor complete.")

        return recommendation

    def _build_refactor_prompt(self, request: RefactorRequest) -> str:
        # Extract files from the original context package
        file_sections: list[str] = []
        for context_file in request.package.collected_files:
            file_sections.append(
                f"FILE: {context_file.path}\n\n{context_file.content}"
            )
        files_text = "\n\n".join(file_sections)

        return f"""
Your previous attempt to fix the codebase was rejected.

ERROR SUMMARY (Original):
{request.package.error_summary}

REJECTION REASON:
{request.rejection_reason}

PREVIOUS (REJECTED) DIFF:
{request.previous_recommendation.unified_diff}

CODE CONTEXT:
{files_text}

Requirements:
1. Analyze the rejection reason carefully.
2. Formulate a new root cause analysis if necessary.
3. Propose an updated, compliant solution.
4. Output a new, strictly valid unified diff that resolves the issue without violating constraints.
"""