from src.application import SessionManager
from src.domain.interfaces import AIProvider, BaseAgent
from src.domain.models import FailureAnalysis, TestResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class LogAnalyzerAgent(BaseAgent):
    def __init__(
        self,
        ai_provider: AIProvider,
        session_manager: SessionManager,
    ) -> None:
        self.ai_provider = ai_provider
        self.session_manager = session_manager

    async def execute(self, test_result: TestResult) -> FailureAnalysis:
        logger.info("Starting log analysis...")
        self.session_manager.append_event(
            "log_analysis_started", "Analyzing failed test output"
        )

        prompt = f"""
Analyze the following test failure and extract the required structured data.

STDOUT:
{test_result.stdout}

STDERR:
{test_result.stderr}
"""

        # Assuming AIProvider.run is an async method that enforces the Pydantic schema
        analysis: FailureAnalysis = await self.ai_provider.run(
            prompt=prompt,
            system_prompt="You are an expert software debugging assistant. Provide structured root cause analysis.",
            response_schema=FailureAnalysis,
        )

        logger.info(f"Analysis complete. Detected error: {analysis.error_type}")
        self.session_manager.append_event(
            "log_analysis_completed", f"Detected: {analysis.error_type}"
        )

        return analysis
