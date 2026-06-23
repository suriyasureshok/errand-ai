from unittest.mock import AsyncMock, Mock, patch

from src.agents.patch_generator_agent import PatchGeneratorAgent
from src.domain.models.context_package import ContextFile, ContextPackage
from src.domain.models.patch_recommendation import PatchRecommendation


def test_generate_patch() -> None:
    mock_ai_provider = Mock()

    mock_session_manager = Mock()

    mock_telegram_client = Mock()

    mock_telegram_client.request_approval = AsyncMock()

    recommendation = PatchRecommendation(
        root_cause=("Incorrect redis import"),
        proposed_solution=("Use redis.asyncio"),
        unified_diff="""
--- a/cache.py
+++ b/cache.py
@@
-import redis
+import redis.asyncio as redis
""",
    )

    mock_ai_provider.run.return_value = recommendation

    agent = PatchGeneratorAgent(
        ai_provider=mock_ai_provider,
        telegram_client=mock_telegram_client,
        session_manager=mock_session_manager,
    )

    package = ContextPackage(
        error_type="ImportError",
        error_summary=("Redis import failed"),
        collected_files=[
            ContextFile(
                path="src/cache.py",
                content="import redis",
            )
        ],
        relevant_tests=["tests/test_cache.py"],
        related_modules=["redis"],
    )

    context = {
        "context_package": package,
        "retry_number": 1,
    }

    with patch("asyncio.run") as mock_asyncio:
        result = agent.execute(context)

    assert result["patch_recommendation"] == recommendation

    assert result["awaiting_approval"] is True

    mock_ai_provider.run.assert_called_once()

    mock_session_manager.save_patch.assert_called_once()

    mock_asyncio.assert_called_once()


def test_prompt_contains_context() -> None:
    agent = PatchGeneratorAgent(
        ai_provider=Mock(),
        telegram_client=Mock(),
        session_manager=Mock(),
    )

    package = ContextPackage(
        error_type="ImportError",
        error_summary="Redis failure",
        collected_files=[
            ContextFile(
                path="src/cache.py",
                content="import redis",
            )
        ],
        relevant_tests=[],
        related_modules=[],
    )

    prompt = agent._build_prompt(package)

    assert "ImportError" in prompt

    assert "Redis failure" in prompt

    assert "src/cache.py" in prompt

    assert "import redis" in prompt
