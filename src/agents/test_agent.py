from pathlib import Path
from subprocess import run
from typing import Any

from src.domain.interfaces.agent import BaseAgent


class TestAgent(BaseAgent):
    """
    Executes the user-provided test script and captures results.
    """

    SCRIPT_NAME = "errand_ai.sh"

    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        workspace = Path(context["workspace"])

        script_path = workspace / self.SCRIPT_NAME

        if not script_path.exists():
            raise FileNotFoundError(f"{self.SCRIPT_NAME} not found in {workspace}")

        result = run(
            ["bash", str(script_path)],
            cwd=workspace,
            capture_output=True,
            text=True,
        )

        context["test_stdout"] = result.stdout
        context["test_stderr"] = result.stderr
        context["test_exit_code"] = result.returncode
        context["tests_passed"] = result.returncode == 0

        # TODO:
        # notify user if tests passed

        return context
