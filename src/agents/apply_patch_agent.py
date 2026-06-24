"""Agent responsible for applying codebase modifications.

This module provides the ApplyPatchAgent, which takes an approved
PatchRecommendation and executes the exact search-and-replace string
replacements against the local filesystem via the PatchManager.
"""

from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.models import PatchRecommendation
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplyPatchAgent(BaseAgent[PatchRecommendation, PatchRecommendation]):
    """Agent that safely mutates the filesystem with approved fixes.

    Attributes:
        session_manager (SessionManager): The facade for persistence and 
            filesystem operations.
    """

    def __init__(self, session_manager: SessionManager) -> None:
        """Initializes the ApplyPatchAgent.

        Args:
            session_manager (SessionManager): The system state and file manager.
        """
        self.session_manager = session_manager

    async def execute(self, input_data: PatchRecommendation) -> PatchRecommendation:
        """Applies the approved patches to the target codebase.

        Args:
            input_data (PatchRecommendation): The validated and approved patch proposal.

        Returns:
            PatchRecommendation: The identical recommendation, passed down 
                the pipeline for final logging or verification.

        Raises:
            RuntimeError: If a file is missing or a search block cannot be found.
        """
        logger.info("Applying approved patch via Pure Python Search/Replace...")

        session = self.session_manager.load_session()
        retry_number = session.current_retry

        # Delegate the actual file mutation to the highly-tested PatchManager
        for patch in input_data.patches:
            try:
                self.session_manager.patch_manager.apply_search_replace(
                    relative_path=patch.file_path,
                    search_block=patch.search_block,
                    replace_block=patch.replace_block,
                )
            except Exception as e:
                self.session_manager.append_event(
                    event_type="patch_application_failed",
                    details=f"Failed on {patch.file_path}: {e}",
                )
                raise RuntimeError(f"Patch application failed: {e}")

        # Save the unified diff strictly for historical human review
        self.session_manager.save_patch(
            retry_number=retry_number,
            diff_content=input_data.unified_diff,
        )

        logger.info("All files patched successfully.")
        self.session_manager.append_event(
            event_type="patch_applied",
            details=f"Successfully applied Python string replacement for retry #{retry_number}",
        )

        return input_data