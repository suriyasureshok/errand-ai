from typing import Any

from src.domain.interfaces import AIProvider, BaseAgent
from src.domain.models import FailureAnalysis


class LogAnalyzerAgent(BaseAgent):
    """
    Analyzes failed test output and extracts
    structured debugging information.
    """

    def __init__(self, ai_provider: AIProvider):
        self.ai_provider = ai_provider

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        stdout = context.get("test_stdout", "")
        stderr = context.get("test_stderr", "")

        prompt = f"""
Analyze the following test failure.

Return:

1. Error type
2. Root cause summary
3. Relevant source files
4. Relevant test files
5. Relevant modules

STDOUT:
{stdout}

STDERR:
{stderr}
"""

        response = self.ai_provider.run(
            prompt=prompt,
            system_prompt="You are an expert software debugging assistant.",
            response_schema=FailureAnalysis,
        )

        context["failure_analysis"] = response

        return context
