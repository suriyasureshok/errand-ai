import asyncio
import subprocess
from pathlib import Path
from typing import Any

from src.application.session_manager import SessionManager
from src.domain.interfaces.agent import BaseAgent
from src.infrastructure.notifications.telegram import TelegramClient


class TestAgent(BaseAgent):
    SCRIPT_NAME = "errand_ai.sh"

    def __init__(
        self,
        session_manager: SessionManager,
        telegram_client: TelegramClient,
    ) -> None:
        self.session_manager = session_manager
        self.telegram_client = telegram_client

    def execute(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        workspace = Path(context["workspace"])

        script_path = workspace / self.SCRIPT_NAME

        if not script_path.exists():
            raise FileNotFoundError(f"{self.SCRIPT_NAME} not found in {workspace}")

        self.session_manager.append_event(
            "test_started",
            f"Executing {self.SCRIPT_NAME}",
        )

        result = subprocess.run(
            ["bash", str(script_path)],
            cwd=workspace,
            capture_output=True,
            text=True,
        )

        stdout = result.stdout
        stderr = result.stderr

        tests_passed = result.returncode == 0

        log_content = f"""
STDOUT
======

{stdout}

STDERR
======

{stderr}
"""

        log_file = self.session_manager.save_log(
            retry_number=0,
            content=log_content,
        )

        context["test_stdout"] = stdout
        context["test_stderr"] = stderr
        context["test_exit_code"] = result.returncode
        context["tests_passed"] = tests_passed
        context["log_file"] = str(log_file)

        if tests_passed:
            self.session_manager.mark_success()

            self.session_manager.append_event(
                "workflow_completed",
                "All tests passed",
            )

            asyncio.run(
                self.telegram_client.notify_success(
                    "✅ Test execution completed successfully."
                )
            )

            context["workflow_completed"] = True

            return context

        self.session_manager.append_event(
            "workflow_continues",
            "Starting remediation workflow",
        )

        asyncio.run(
            self.telegram_client.notify_failure(
                "❌ Tests failed. Starting remediation workflow."
            )
        )

        context["workflow_completed"] = False

        return context
