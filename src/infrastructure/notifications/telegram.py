"""Telegram notification infrastructure.

This module provides the TelegramNotifier, responsible for dispatching
asynchronous alerts and managing interactive human-in-the-loop approval workflows.
"""

import asyncio

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from src.application import Config
from src.domain.interfaces import Notifier
from src.domain.models import ApprovalResult, ApprovalStatus
from src.utils import async_retry, get_logger

logger = get_logger(__name__)


class TelegramNotifier(Notifier):
    """Implementation of the Notifier interface using the Telegram API.

    Handles outbound messaging and long-polling for inline keyboard callbacks
    to facilitate human approval of generated patches.
    """

    def __init__(self, config: Config) -> None:
        """Initializes the Telegram Notifier.

        Args:
            config (Config): The application configuration containing the token and chat ID.
        """
        self._config = config
        self._bot = Bot(token=config.telegram_token)
        self._chat_id = config.chat_id
        self._timeout_seconds = config.approval_timeout_min * 60

    @async_retry(max_retries=3, base_delay=2.0)
    async def notify_success(self, message: str) -> None:
        """Sends a formatted success notification to the configured chat.

        Args:
            message (str): The details of the successful operation.
        """
        await self._bot.send_message(
            chat_id=self._chat_id,
            text=f"**Success:**\n{message}",
            parse_mode="Markdown",
        )

    @async_retry(max_retries=3, base_delay=2.0)
    async def notify_failure(self, message: str) -> None:
        """Sends a formatted failure notification to the configured chat.

        Args:
            message (str): The details of the failure or error.
        """
        await self._bot.send_message(
            chat_id=self._chat_id,
            text=f"**Failure:**\n{message}",
            parse_mode="Markdown",
        )

    @async_retry(max_retries=3, base_delay=2.0)
    async def request_approval(self, summary: str, diff: str) -> ApprovalResult:
        """Requests human approval for a proposed code patch.

        Sends an interactive message with inline buttons and waits for a callback
        response. The diff is truncated if it exceeds Telegram's size limits.

        Args:
            summary (str): The root cause analysis summary.
            diff (str): The unified diff representing the proposed patch.

        Returns:
            ApprovalResult: The domain model containing the human's decision.
        """
        keyboard = [
            [
                InlineKeyboardButton(text="Approve", callback_data="approve"),
                InlineKeyboardButton(text="Refactor", callback_data="refactor"),
                InlineKeyboardButton(text="Reject", callback_data="reject"),
            ]
        ]
        markup = InlineKeyboardMarkup(keyboard)

        # Telegram has a strict 4096 char limit. Truncate diff if necessary.
        safe_diff = diff[:3000] + "\n...[diff truncated]" if len(diff) > 3000 else diff
        full_text = f"**Action Required**\n\n{summary}\n\n**Proposed Patch:**\n```diff\n{safe_diff}\n```"

        message = await self._bot.send_message(
            chat_id=self._chat_id,
            text=full_text,
            reply_markup=markup,
            parse_mode="Markdown",
        )

        return await self._wait_for_user_response(message.message_id)

    async def _wait_for_user_response(self, message_id: int) -> ApprovalResult:
        """Polls the Telegram API until a button is clicked or the timeout is reached.

        This method is not decorated with @async_retry because it handles its own
        time-bound looping logic via long-polling.

        Args:
            message_id (int): The specific Telegram message ID to listen for callbacks on.

        Returns:
            ApprovalResult: The user's decision, or a TIMEOUT result.
        """
        start_time = asyncio.get_event_loop().time()
        offset = None

        logger.info(
            f"Waiting for human approval for {self._timeout_seconds} seconds..."
        )

        while (asyncio.get_event_loop().time() - start_time) < self._timeout_seconds:
            try:
                # Long polling: timeout=10 means Telegram holds the connection open for 10s
                updates = await self._bot.get_updates(offset=offset, timeout=10)

                for update in updates:
                    offset = update.update_id + 1

                    if update.callback_query:
                        query = update.callback_query

                        if query.message and query.message.message_id == message_id:
                            await query.answer()

                            # Remove the buttons so the user can't click them again
                            await self._bot.edit_message_reply_markup(
                                chat_id=self._chat_id,
                                message_id=message_id,
                                reply_markup=None,
                            )

                            if query.data == "approve":
                                return ApprovalResult(status=ApprovalStatus.APPROVED)
                            elif query.data == "refactor":
                                return ApprovalResult(
                                    status=ApprovalStatus.REFACTOR_REQUESTED
                                )
                            elif query.data == "reject":
                                return ApprovalResult(status=ApprovalStatus.REJECTED)

            except Exception as e:
                # Catch transient polling errors (like ReadTimeout) and continue looping
                logger.warning(
                    f"Transient error while polling for Telegram updates: {e}"
                )
                await asyncio.sleep(2)

        logger.warning("Approval request timed out.")

        try:
            await self._bot.edit_message_reply_markup(
                chat_id=self._chat_id, message_id=message_id, reply_markup=None
            )
        except Exception as e:
            logger.debug(f"Could not remove reply markup on timeout: {e}")

        return ApprovalResult(
            status=ApprovalStatus.TIMEOUT, reason="Human did not respond in time."
        )
