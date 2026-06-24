import pytest

from src.agents.apply_patch_agent import ApplyPatchAgent
from src.application.config import Config
from src.application.session_manager import SessionManager
from src.domain.models.patch_recommendation import (
    PatchRecommendation,
    SearchReplacePatch,
)


@pytest.mark.asyncio
async def test_apply_patch_success(mock_config: Config):
    # Setup the dummy file in our mocked workspace
    target_file = mock_config.workspace / "math.py"
    target_file.write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")

    agent = ApplyPatchAgent(session_manager=SessionManager(config=mock_config))

    recommendation = PatchRecommendation(
        root_cause="Bug",
        proposed_solution="Fix",
        patches=[
            SearchReplacePatch(
                file_path="math.py",
                search_block="return a - b",
                replace_block="return a + b",
            )
        ],
        unified_diff="visual diff",
    )

    await agent.execute(recommendation)

    # Verify the file was correctly modified
    updated_content = target_file.read_text(encoding="utf-8")
    assert "return a + b" in updated_content
    assert "return a - b" not in updated_content


@pytest.mark.asyncio
async def test_apply_patch_hallucinated_code(mock_config: Config):
    target_file = mock_config.workspace / "math.py"
    target_file.write_text("def add(a, b):\n    return a - b\n", encoding="utf-8")

    agent = ApplyPatchAgent(session_manager=SessionManager(config=mock_config))

    # LLM hallucinated a search block that doesn't exist
    recommendation = PatchRecommendation(
        root_cause="Bug",
        proposed_solution="Fix",
        patches=[
            SearchReplacePatch(
                file_path="math.py",
                search_block="return a * b",  # DOES NOT EXIST
                replace_block="return a + b",
            )
        ],
        unified_diff="visual diff",
    )

    # Assert that our safety check catches it and raises a RuntimeError
    with pytest.raises(RuntimeError, match="Could not find the target code block"):
        await agent.execute(recommendation)
