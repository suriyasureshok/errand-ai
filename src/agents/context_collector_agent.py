from pathlib import Path
from typing import Any

from src.domain.interfaces.agent import BaseAgent
from src.domain.models.context_package import ContextFile, ContextPackage
from src.domain.models.failure_analysis import FailureAnalysis


class ContextCollectorAgent(BaseAgent):
    """
    Collects the smallest useful context set
    for patch generation.
    """

    MAX_FILE_SIZE = 20_000

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        workspace = Path(context["workspace"])

        collected_files: list[ContextFile] = []

        analysis: FailureAnalysis = context["failure_analysis"]

        files_to_collect: set[str] = set()

        files_to_collect.update(analysis.relevant_files)
        files_to_collect.update(analysis.relevant_tests)

        for file_path in files_to_collect:
            absolute_path = workspace / file_path

            if not absolute_path.exists():
                continue

            content = absolute_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

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

        context["context_package"] = package

        return context
