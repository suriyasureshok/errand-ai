from unittest.mock import AsyncMock, Mock, patch

from src.agents.approval_agent import ApprovalAgent
from src.domain.models.patch_recommendation import PatchRecommendation


def test_approval_request_sent() -> None:
    telegram_client = Mock()

    telegram_client.request_approval = AsyncMock()

    session_manager = Mock()

    agent = ApprovalAgent(
        telegram_client=telegram_client,
        session_manager=session_manager,
    )

    context = {
        "patch_recommendation": (
            PatchRecommendation(
                root_cause="ImportError",
                proposed_solution=("Use redis.asyncio"),
                unified_diff="""
--- a/cache.py
+++ b/cache.py
@@
-import redis
+import redis.asyncio as redis
""",
            )
        )
    }

    with patch("asyncio.run") as mock_asyncio:
        result = agent.execute(context)

    assert result["approval_status"] == "pending"

    mock_asyncio.assert_called_once()

    session_manager.append_event.assert_called_once()
