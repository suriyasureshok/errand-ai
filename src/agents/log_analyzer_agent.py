"""Agent responsible for analyzing test failure logs.

This module provides the LogAnalyzerAgent, which uses an AIProvider to
parse raw stdout/stderr dumps and extract a structured root-cause analysis.
"""

from src.domain.interfaces import BaseAgent
from src.domain.interfaces import AIProvider
from src.domain.models import FailureAnalysis
from src.domain.models import TestResult
from src.utils import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are an expert software engineer and diagnostic system.
Your task is to analyze test suite failure logs and extract the root cause.
Identify the exact error type, summarize the failure succinctly, and list the 
exact file paths (relative to the workspace root) of the source code and tests involved."""


class LogAnalyzerAgent(BaseAgent[TestResult, FailureAnalysis]):
    """Agent that translates raw test output into structured failure data.

    Attributes:
        ai_provider (AIProvider): The configured LLM inference engine.
    """

    def __init__(self, ai_provider: AIProvider) -> None:
        """Initializes the LogAnalyzerAgent.

        Args:
            ai_provider (AIProvider): The infrastructure provider for AI inference.
        """
        self.ai_provider = ai_provider

    async def execute(self, input_data: TestResult) -> FailureAnalysis:
        """Analyzes the test result to determine the root cause of failure.

        Args:
            input_data (TestResult): The raw output from the TestAgent.

        Returns:
            FailureAnalysis: The structured diagnostic schema.

        Raises:
            ValueError: If the AI provider fails to return a valid schema.
        """
        logger.info("Analyzing test failure logs via AI...")

        prompt = (
            f"Please analyze the following test execution output.\n\n"
            f"EXIT CODE: {input_data.exit_code}\n\n"
            f"STDOUT:\n{input_data.stdout}\n\n"
            f"STDERR:\n{input_data.stderr}\n"
        )

        analysis = await self.ai_provider.run(
            prompt=prompt,
            system_prompt=_SYSTEM_PROMPT,
            response_schema=FailureAnalysis,
        )

        # Type narrowing to satisfy static type checkers
        if not isinstance(analysis, FailureAnalysis):
            raise ValueError("AI Provider returned an invalid response type.")

        logger.debug(f"Identified error type: {analysis.error_type}")
        return analysis
