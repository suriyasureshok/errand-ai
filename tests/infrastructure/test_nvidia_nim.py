from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from src.application.config import Config
from src.infrastructure.ai_providers.nvidia_nim import NvidiaNIMProvider


class MockSchema(BaseModel):
    reasoning: str
    result: int


@pytest.fixture
def nim_provider(mock_config: Config):
    with patch("src.infrastructure.ai_providers.nvidia_nim.AsyncOpenAI") as mock_openai:
        provider = NvidiaNIMProvider(config=mock_config)
        provider._client = mock_openai.return_value
        yield provider


@pytest.mark.asyncio
async def test_run_without_schema(nim_provider: NvidiaNIMProvider):
    """Tests raw text generation without a Pydantic schema."""
    # Mock the nested OpenAI chat.completions.create response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a mock response."
    nim_provider._client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await nim_provider.run(prompt="Hello", system_prompt="Be polite.")
    
    assert result == "This is a mock response."
    nim_provider._client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_run_with_schema(nim_provider: NvidiaNIMProvider):
    """Tests JSON mode generation and Pydantic validation."""
    mock_response = MagicMock()
    # Provide a valid JSON string that matches MockSchema
    mock_response.choices[0].message.content = '{"reasoning": "math", "result": 42}'
    nim_provider._client.chat.completions.create = AsyncMock(return_value=mock_response)

    result = await nim_provider.run(prompt="Calculate", response_schema=MockSchema)
    
    assert isinstance(result, MockSchema)
    assert result.reasoning == "math"
    assert result.result == 42