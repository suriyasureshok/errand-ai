from typing import Any

from src.application.session_manager import SessionManager
from src.domain.interfaces.agent import BaseAgent
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.failure_analysis import FailureAnalysis


class LogAnalyzerAgent(BaseAgent):
    def __init__(
        self,
        ai_provider: AIProvider,
        session_manager: SessionManager,
    ) -> None:
        self.ai_provider = ai_provider
        self.session_manager = session_manager

    def execute(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        stdout = context["test_stdout"]
        stderr = context["test_stderr"]

        self.session_manager.append_event(
            "log_analysis_started",
            "Analyzing failed test output",
        )

        prompt = f"""
Analyze the following test failure.

Return:

1. Error type
2. Root cause summary
3. Relevant source files
4. Relevant test files
5. Related modules

STDOUT:
{stdout}

STDERR:
{stderr}
"""

        analysis: FailureAnalysis = self.ai_provider.run(
            prompt=prompt,
            system_prompt=("You are an expert software " "debugging assistant."),
            response_schema=FailureAnalysis,
        )

        self.session_manager.append_event(
            "log_analysis_completed",
            analysis.error_type,
        )

        context["failure_analysis"] = analysis

        return context
