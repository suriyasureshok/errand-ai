from typing import Any

from src.domain.interfaces.agent import BaseAgent
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.context_package import ContextPackage
from src.domain.models.patch_recommendation import PatchRecommendation


class PatchGeneratorAgent(BaseAgent):
    """
    Generates a proposed patch using the configured
    LLM provider.
    """

    def __init__(self, ai_provider: AIProvider) -> None:
        self.ai_provider = ai_provider

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        package: ContextPackage = context["context_package"]

        prompt: str = self._build_prompt(package)

        recommendation: PatchRecommendation = self.ai_provider.run(
            prompt=prompt,
            response_schema=PatchRecommendation,
        )

        context["patch_recommendation"] = recommendation

        # Placeholder for future approval workflow
        context["approval_required"] = True

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

        files_text: str = "\n\n".join(file_sections)

        return f"""
You are an expert software debugging assistant.

Analyze the failure.

ERROR TYPE:
{package.error_type}

ERROR SUMMARY:
{package.error_summary}

FILES:
{files_text}

Tasks:

1. Determine the root cause.
2. Propose the safest fix.
3. Generate a unified diff patch.
4. Modify only the necessary files.
5. Avoid unrelated changes.
"""
