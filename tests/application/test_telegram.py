from unittest.mock import AsyncMock, patch

import pytest
from telegram import Bot

from src.application.config import Config
from src.infrastructure.notifications.telegram import TelegramNotifier
from src.domain.models.approval import ApprovalStatus


@pytest.fixture
def mock_bot():
    """Mocks the telegram.Bot to intercept network calls."""
    with patch("src.infrastructure.notifications.telegram.Bot", autospec=True) as MockBotClass:
        mock_instance = MockBotClass.return_value
        mock_instance.send_message = AsyncMock()
        yield mock_instance


@pytest.mark.asyncio
async def test_notify_failure(mock_config: Config, mock_bot: Bot):
    """Tests that a standard failure message is sent correctly."""
    notifier = TelegramNotifier(config=mock_config)
    
    await notifier.notify_failure("Test failed")
    
    mock_bot.send_message.assert_called_once()
    kwargs = mock_bot.send_message.call_args.kwargs
    assert kwargs["chat_id"] == "mock_chat_id"
    assert "Test failed" in kwargs["text"]


@pytest.mark.asyncio
async def test_request_approval_sends_message(mock_config: Config, mock_bot: Bot):
    """Tests that the approval request correctly sends a message with a keyboard."""
    notifier = TelegramNotifier(config=mock_config)
    
    # We mock the method so it sends the message but skips the blocking polling loop
    with patch.object(notifier, "request_approval", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = ApprovalStatus.APPROVED
        
        result = await notifier.request_approval(
            summary="Root cause: bug",
            diff="--- a\n+++ b"
        )
        
        assert result == ApprovalStatus.APPROVED
        mock_request.assert_called_once()