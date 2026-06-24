from unittest.mock import AsyncMock

import pytest

from src.agents.approval_agent import ApprovalAgent
from src.application.session_manager import SessionManager
from src.domain.interfaces.notifier import Notifier
from src.domain.models.approval import ApprovalResult, ApprovalStatus
from src.domain.models.patch_recommendation import PatchRecommendation
from src.application.config import Config


@pytest.mark.asyncio
async def test_approval_agent_execute(mock_config: Config):
    session_manager = SessionManager(config=mock_config)
    mock_notifier = AsyncMock(spec=Notifier)
    
    expected_result = ApprovalResult(status=ApprovalStatus.APPROVED)
    mock_notifier.request_approval.return_value = expected_result
    
    agent = ApprovalAgent(notifier=mock_notifier, session_manager=session_manager)
    
    recommendation = PatchRecommendation(
        root_cause="Bug",
        proposed_solution="Fix",
        patches=[],
        unified_diff="--- a\n+++ b"
    )
    
    result = await agent.execute(recommendation)
    
    assert result == expected_result
    mock_notifier.request_approval.assert_called_once()