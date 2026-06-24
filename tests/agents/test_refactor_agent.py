from unittest.mock import AsyncMock

import pytest

from src.agents.refactor_agent import RefactorAgent
from src.application.config import Config
from src.application.session_manager import SessionManager
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.context_package import ContextPackage
from src.domain.models.patch_recommendation import PatchRecommendation
from src.domain.models.refactor_request import RefactorRequest


@pytest.mark.asyncio
async def test_refactor_agent_execute(mock_config: Config):
    session_manager = SessionManager(config=mock_config)
    mock_ai = AsyncMock(spec=AIProvider)

    new_recommendation = PatchRecommendation(
        root_cause="Updated cause",
        proposed_solution="Updated fix",
        patches=[],
        unified_diff="new diff",
    )
    mock_ai.run.return_value = new_recommendation

    agent = RefactorAgent(ai_provider=mock_ai, session_manager=session_manager)

    request = RefactorRequest(
        package=ContextPackage(
            error_type="Err",
            error_summary="Sum",
            collected_files=[],
            relevant_tests=[],
            related_modules=[],
        ),
        previous_recommendation=PatchRecommendation(
            root_cause="old",
            proposed_solution="old",
            patches=[],
            unified_diff="old diff",
        ),
        rejection_reason="Failed guardrails",
    )

    result = await agent.execute(request)

    assert result == new_recommendation
    mock_ai.run.assert_called_once()
    assert "Failed guardrails" in mock_ai.run.call_args.kwargs["prompt"]
