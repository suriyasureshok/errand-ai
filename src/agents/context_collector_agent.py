from pathlib import Path

from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.models import ContextFile, ContextPackage
from src.domain.models import FailureAnalysis
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ContextCollectorAgent(BaseAgent):
    MAX_FILE_SIZE = 20_000

    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager

    async def execute(self, analysis: FailureAnalysis) -> ContextPackage:
        logger.info("Collecting context files based on analysis...")

        workspace = self.session_manager.workspace
        session = self.session_manager.load_session()
        current_retry = session.current_retry

        collected_files: list[ContextFile] = []

        # Use a set to prevent duplicating files if they appear in multiple lists
        files_to_collect: set[str] = set()
        files_to_collect.update(analysis.relevant_files)
        files_to_collect.update(analysis.relevant_tests)

        for file_path in files_to_collect:
            # Prevent directory traversal attacks or escaping the workspace
            absolute_path = (workspace / file_path).resolve()
            if not str(absolute_path).startswith(str(workspace.resolve())):
                logger.warning(f"Skipping out-of-bounds file path: {file_path}")
                continue

            if not absolute_path.exists() or not absolute_path.is_file():
                logger.warning(f"File not found or is a directory: {file_path}")
                continue

            content = absolute_path.read_text(encoding="utf-8", errors="ignore")

            collected_files.append(
                ContextFile(
                    path=file_path,
                    content=content[: self.MAX_FILE_SIZE],
                )
            )

        package = ContextPackage(
            error_type=analysis.error_type,
            error_summary=analysis.summary,
            collected_files=collected_files,
            relevant_tests=analysis.relevant_tests,
            related_modules=analysis.related_modules,
        )

        # Persist the collected context to the .errand-ai/context directory
        context_dump = package.model_dump_json(indent=2)
        self.session_manager.save_context(
            retry_number=current_retry,
            context_content=context_dump,
        )

        logger.info(
            f"Context collection complete. Gathered {len(collected_files)} files."
        )
        self.session_manager.append_event(
            "context_collected", f"Collected {len(collected_files)} files"
        )

        return package
