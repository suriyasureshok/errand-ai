from typing import Any

from src.application.session_manager import (
    SessionManager,
)
from src.domain.interfaces.agent import (
    BaseAgent,
)
from src.domain.models.patch_recommendation import (
    PatchRecommendation,
)


class GuardrailAgent(BaseAgent):
    BLOCKED_PATTERNS = [
        "os.system(",
        "subprocess.run(",
        "eval(",
        "exec(",
        "os.remove(",
        "shutil.rmtree(",
    ]

    BLOCKED_FILES = [
        ".env",
        ".git/",
        "Cargo.lock",
        "package-lock.json",
    ]

    def __init__(
        self,
        session_manager: SessionManager,
    ) -> None:
        self.session_manager = session_manager

    def execute(
        self,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        recommendation: PatchRecommendation = context["patch_recommendation"]

        diff = recommendation.unified_diff

        for pattern in self.BLOCKED_PATTERNS:
            if pattern in diff:
                context["guardrail_passed"] = False

                context["guardrail_reason"] = f"Blocked pattern: " f"{pattern}"

                return context

        for file_name in self.BLOCKED_FILES:
            if file_name in diff:
                context["guardrail_passed"] = False

                context["guardrail_reason"] = f"Protected file: " f"{file_name}"

                return context

        self.session_manager.append_event(
            "guardrail_passed",
            "Patch approved",
        )

        context["guardrail_passed"] = True

        return context
