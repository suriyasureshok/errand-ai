"""Agent responsible for executing the target codebase's test suite.

This module provides the TestAgent, which runs the configured test command
(defaulting to pytest) in the target workspace, captures the raw output,
and persists it via the LogManager.
"""

import asyncio
from pathlib import Path

from src.domain.interfaces import BaseAgent
from src.domain.models import Session
from src.domain.models import TestResult
from src.infrastructure.filesystem import LogManager
from src.utils import get_logger

logger = get_logger(__name__)


class TestAgent(BaseAgent[Session, TestResult]):
    """Agent that runs the test suite and captures the execution state.

    Attributes:
        workspace (Path): The root directory of the target codebase.
        log_manager (LogManager): Infrastructure manager for saving test logs.
        test_command (str): The command used to run the tests. Defaults to 'pytest'.
    """

    def __init__(self, workspace: Path, log_manager: LogManager, test_command: str = "pytest") -> None:
        """Initializes the TestAgent.

        Args:
            workspace (Path): The target codebase root.
            log_manager (LogManager): The infrastructure component for saving logs.
            test_command (str, optional): The shell command to trigger tests. Defaults to "pytest".
        """
        self.workspace = workspace
        self.log_manager = log_manager
        self.test_command = test_command

    async def execute(self, input_data: Session) -> TestResult:
        """Executes the test suite asynchronously.

        Args:
            input_data (Session): The current pipeline session state.

        Returns:
            TestResult: The domain model containing the test execution outcome.
        """
        logger.info(f"Running tests for retry loop {input_data.current_retry}...")

        process = await asyncio.create_subprocess_shell(
            self.test_command,
            cwd=self.workspace,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_bytes, stderr_bytes = await process.communicate()
        
        stdout = stdout_bytes.decode("utf-8")
        stderr = stderr_bytes.decode("utf-8")
        exit_code = process.returncode or 0

        # Pytest typically returns 0 for success, 1 for test failures, and 2+ for errors
        passed = exit_code == 0
        
        full_output = f"--- STDOUT ---\n{stdout}\n--- STDERR ---\n{stderr}"
        log_path = self.log_manager.save_test_output(input_data.current_retry, full_output)

        if passed:
            logger.info("Test suite passed successfully.")
        else:
            logger.warning(f"Test suite failed with exit code {exit_code}.")

        return TestResult(
            passed=passed,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            log_file_path=str(log_path),
        )