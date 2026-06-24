from unittest.mock import AsyncMock

import pytest

from src.agents.patch_generator_agent import PatchGeneratorAgent
from src.application.session_manager import SessionManager
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.context_package import ContextPackage, ContextFile
from src.domain.models.patch_recommendation import PatchRecommendation, SearchReplacePatch
from src.application.config import Config


@pytest.mark.asyncio
async def test_patch_generator_execute(mock_config: Config):
    session_manager = SessionManager(config=mock_config)
    
    mock_ai = AsyncMock(spec=AIProvider)
    expected_recommendation = PatchRecommendation(
        root_cause="Bug in math logic",
        proposed_solution="Change - to +",
        patches=[SearchReplacePatch(file_path="app.py", search_block="a - b", replace_block="a + b")],
        unified_diff="--- a/app.py\n+++ b/app.py\n-a - b\n+a + b"
    )
    mock_ai.run.return_value = expected_recommendation

    agent = PatchGeneratorAgent(ai_provider=mock_ai, session_manager=session_manager)
    
    package = ContextPackage(
        error_type="AssertionError",
        error_summary="Math failed",
        collected_files=[ContextFile(path="app.py", content="def add(a,b): return a - b")],
        relevant_tests=["test_addition"],
        related_modules=["math_utils"]
    )
    
    result = await agent.execute(package)

    assert result == expected_recommendation
    mock_ai.run.assert_called_once()
    
    # Verify the patch was saved to disk
    patch_file = session_manager.patches_dir / "retry-0.diff"
    assert patch_file.exists()
    assert patch_file.read_text(encoding="utf-8") == expected_recommendation.unified_diff