"""Agent responsible for aggregating source code context.

This module provides the ContextCollectorAgent, which reads the files flagged
by the LogAnalyzerAgent and bundles them into a package for patch generation.
"""

from src.domain.interfaces import BaseAgent
from src.domain.models import ContextFile, ContextPackage
from src.domain.models import FailureAnalysis
from src.infrastructure.filesystem import ContextManager
from src.utils import get_logger

logger = get_logger(__name__)


class ContextCollectorAgent(BaseAgent[FailureAnalysis, ContextPackage]):
    """Agent that builds a context payload from local source files.

    Attributes:
        context_manager (ContextManager): Infrastructure manager for safe file reading.
    """

    def __init__(self, context_manager: ContextManager) -> None:
        """Initializes the ContextCollectorAgent.

        Args:
            context_manager (ContextManager): The filesystem context reader.
        """
        self.context_manager = context_manager

    async def execute(self, input_data: FailureAnalysis) -> ContextPackage:
        """Collects the content of all files relevant to the failure.

        Args:
            input_data (FailureAnalysis): The diagnostic data from the analyzer.

        Returns:
            ContextPackage: A bundled package of file contents and error summaries.
        """
        logger.info("Collecting source code context based on analysis...")

        collected_files: list[ContextFile] = []

        # Combine unique file paths from both source and test lists
        target_files = set(input_data.relevant_files + input_data.relevant_tests)

        for file_path in target_files:
            content = self.context_manager.read_source_file(file_path)
            if content is not None:
                collected_files.append(ContextFile(path=file_path, content=content))
                logger.debug(f"Included {file_path} in context package.")
            else:
                logger.warning(f"Could not read {file_path} for context.")

        return ContextPackage(
            error_type=input_data.error_type,
            error_summary=input_data.summary,
            collected_files=collected_files,
            relevant_tests=input_data.relevant_tests,
            related_modules=input_data.related_modules,
        )
