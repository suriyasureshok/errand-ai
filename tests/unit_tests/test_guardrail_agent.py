from unittest.mock import Mock

from src.agents.guardrail_agent import GuardrailAgent
from src.domain.models.patch_recommendation import PatchRecommendation


def create_patch(diff: str) -> PatchRecommendation:
    return PatchRecommendation(
        root_cause="test",
        proposed_solution="test",
        unified_diff=diff,
    )


def test_guardrail_passes_safe_patch() -> None:
    session_manager = Mock()

    agent = GuardrailAgent(
        session_manager=session_manager,
    )

    context = {
        "patch_recommendation": create_patch(
            """
--- a/cache.py
+++ b/cache.py
@@
-import redis
+import redis.asyncio as redis
"""
        )
    }

    result = agent.execute(context)

    assert result["guardrail_passed"] is True

    session_manager.append_event.assert_called_once()


def test_guardrail_blocks_dangerous_api() -> None:
    session_manager = Mock()

    agent = GuardrailAgent(
        session_manager=session_manager,
    )

    context = {
        "patch_recommendation": create_patch(
            """
+os.system("rm -rf /")
"""
        )
    }

    result = agent.execute(context)

    assert result["guardrail_passed"] is False

    assert "Blocked pattern" in result["guardrail_reason"]


def test_guardrail_blocks_protected_file() -> None:
    session_manager = Mock()

    agent = GuardrailAgent(
        session_manager=session_manager,
    )

    context = {
        "patch_recommendation": create_patch(
            """
--- a/.env
+++ b/.env
"""
        )
    }

    result = agent.execute(context)

    assert result["guardrail_passed"] is False

    assert "Protected file" in result["guardrail_reason"]
