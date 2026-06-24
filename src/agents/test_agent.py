import asyncio
from pathlib import Path
from typing import Any

from src.application import SessionManager
from src.domain.interfaces import BaseAgent, Notifier
from src.domain.models import TestResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TestAgent(BaseAgent[Any, TestResult]):
    SCRIPT_NAME = "errand_ai.sh"

    def __init__(
        self,
        session_manager: SessionManager,
        notifier: Notifier,
    ) -> None:
        self.session_manager = session_manager
        self.notifier = notifier

    async def execute(self, input_data: Any = None) -> TestResult:
        workspace = self.session_manager.workspace
        script_path = workspace / self.SCRIPT_NAME

        if not script_path.exists():
            logger.error(f"{self.SCRIPT_NAME} not found in {workspace}")
            raise FileNotFoundError(f"{self.SCRIPT_NAME} not found in {workspace}")

        # Fetch the current state from the session manager dynamically
        session = self.session_manager.load_session()
        current_retry = session.current_retry

        self.session_manager.append_event(
            "test_started", f"Executing {self.SCRIPT_NAME} (Retry {current_retry})"
        )
        logger.info(f"Running test script: {self.SCRIPT_NAME}...")

        # Non-blocking subprocess execution
        process = await asyncio.create_subprocess_exec(
            "bash",
            str(script_path),
            cwd=workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes, stderr_bytes = await process.communicate()

        stdout = stdout_bytes.decode("utf-8")
        stderr = stderr_bytes.decode("utf-8")
        exit_code = process.returncode
        tests_passed = exit_code == 0

        log_content = f"STDOUT\n======\n\n{stdout}\n\nSTDERR\n======\n\n{stderr}\n"

        log_file = self.session_manager.save_log(
            retry_number=current_retry,
            content=log_content,
        )

        if tests_passed:
            logger.info("Tests passed successfully.")
            self.session_manager.mark_success()
            self.session_manager.append_event("workflow_completed", "All tests passed")
            await self.notifier.notify_success("Test execution completed successfully.")
        else:
            logger.warning(
                f"Tests failed with exit code {exit_code}. Initiating remediation."
            )
            self.session_manager.append_event(
                "workflow_continues", "Starting remediation workflow"
            )
            await self.notifier.notify_failure(
                "Tests failed. Starting remediation workflow."
            )

        return TestResult(
            passed=tests_passed,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            log_file_path=str(log_file),
        )
