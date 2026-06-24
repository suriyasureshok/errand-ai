from pathlib import Path

from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.models import PatchRecommendation
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ApplyPatchAgent(BaseAgent[PatchRecommendation, PatchRecommendation]):
    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager

    async def execute(self, recommendation: PatchRecommendation) -> PatchRecommendation:
        logger.info("Applying approved patch via Pure Python Search/Replace...")

        workspace = self.session_manager.workspace
        session = self.session_manager.load_session()
        retry_number = session.current_retry

        for patch in recommendation.patches:
            abs_path = workspace / patch.file_path
            
            if not abs_path.exists():
                raise RuntimeError(f"Target file does not exist: {abs_path}")

            # Read the raw file content
            content = abs_path.read_text(encoding="utf-8")

            # NORMALIZE EVERYTHING: This instantly neutralizes the Windows \r\n vs WSL \n clash.
            content_normalized = content.replace("\r\n", "\n")
            search_normalized = patch.search_block.replace("\r\n", "\n")
            replace_normalized = patch.replace_block.replace("\r\n", "\n")

            # Check if the LLM's search block actually exists in the file
            if search_normalized not in content_normalized:
                logger.error(f"Failed to find search block in {patch.file_path}")
                logger.debug(f"SEARCH BLOCK:\n{search_normalized}")
                self.session_manager.append_event("patch_application_failed", f"Search block not found in {patch.file_path}")
                raise RuntimeError(f"Could not find the target code block in {patch.file_path}. The LLM hallucinated the existing code.")

            # Apply the patch via strict string replacement
            new_content = content_normalized.replace(search_normalized, replace_normalized)

            # Write it back to disk safely
            with open(abs_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new_content)
                
            logger.debug(f"Successfully patched {patch.file_path}")

        # Save the unified diff purely for history/logging purposes
        patch_path = self.session_manager.patches_dir / f"retry-{retry_number}.diff"
        patch_path.write_text(recommendation.unified_diff, encoding="utf-8")

        logger.info("All files patched successfully using Search/Replace.")
        self.session_manager.append_event(
            "patch_applied", 
            f"Successfully applied Python string replacement for retry #{retry_number}"
        )

        return recommendation