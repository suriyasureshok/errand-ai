from unittest.mock import AsyncMock, patch

import pytest

from src.application.config import Config
from src.infrastructure.notifications.telegram import TelegramClient


@pytest.fixture
def config() -> Config:
    return Config(
        provider="ollama",
        model="qwen3",
        base_url="http://localhost:11434/v1",
        api_key="dummy",
        telegram_token="test-token",
        telegram_chat_id="123456",
        max_retries=3,
        approval_timeout_min=15,
    )


@pytest.fixture
def telegram_client(
    config: Config,
) -> TelegramClient:
    return TelegramClient(config)


@pytest.mark.asyncio
@patch(
    "src.infrastructure.notifications.telegram.Bot.send_message",
    new_callable=AsyncMock,
)
async def test_notify_success(
    mock_send_message: AsyncMock,
    telegram_client: TelegramClient,
) -> None:
    await telegram_client.notify_success("Tests passed")

    mock_send_message.assert_awaited_once_with(
        chat_id="123456",
        text="Tests passed",
    )


@pytest.mark.asyncio
@patch(
    "src.infrastructure.notifications.telegram.Bot.send_message",
    new_callable=AsyncMock,
)
async def test_notify_failure(
    mock_send_message: AsyncMock,
    telegram_client: TelegramClient,
) -> None:
    await telegram_client.notify_failure("Tests failed")

    mock_send_message.assert_awaited_once_with(
        chat_id="123456",
        text="Tests failed",
    )


@pytest.mark.asyncio
@patch(
    "src.infrastructure.notifications.telegram.Bot.send_message",
    new_callable=AsyncMock,
)
async def test_request_approval(
    mock_send_message: AsyncMock,
    telegram_client: TelegramClient,
) -> None:
    await telegram_client.request_approval("Patch Proposal")

    mock_send_message.assert_awaited_once()

    kwargs = mock_send_message.await_args.kwargs

    assert kwargs["chat_id"] == "123456"

    assert kwargs["text"] == "Patch Proposal"

    assert kwargs["reply_markup"] is not None
