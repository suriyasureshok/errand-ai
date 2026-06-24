from src.application import SessionManager
from src.domain.interfaces import BaseAgent
from src.domain.models import GuardrailResult
from src.domain.models import PatchRecommendation
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GuardrailAgent(BaseAgent[PatchRecommendation, GuardrailResult]):
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

    def __init__(self, session_manager: SessionManager) -> None:
        self.session_manager = session_manager

    async def execute(self, recommendation: PatchRecommendation) -> GuardrailResult:
        logger.info("Evaluating patch against safety guardrails...")
        diff = recommendation.unified_diff

        for pattern in self.BLOCKED_PATTERNS:
            if pattern in diff:
                reason = f"Blocked execution pattern detected: {pattern}"
                logger.warning(f"Guardrail failed: {reason}")
                self.session_manager.append_event("guardrail_rejected", reason)
                return GuardrailResult(passed=False, recommendation=recommendation, reason=reason)

        for file_name in self.BLOCKED_FILES:
            if file_name in diff:
                reason = f"Protected file modification detected: {file_name}"
                logger.warning(f"Guardrail failed: {reason}")
                self.session_manager.append_event("guardrail_rejected", reason)
                return GuardrailResult(passed=False, recommendation=recommendation, reason=reason)

        logger.info("Patch passed all safety guardrails.")
        self.session_manager.append_event("guardrail_passed", "Patch approved by static analysis")
        
        return GuardrailResult(passed=True, recommendation=recommendation)