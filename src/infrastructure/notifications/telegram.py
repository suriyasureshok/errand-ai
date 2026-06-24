import asyncio

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from src.application import Config
from src.domain.interfaces import Notifier
from src.domain.models import ApprovalResult, ApprovalStatus
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TelegramNotifier(Notifier):
    def __init__(self, config: Config) -> None:
        self._config = config
        self._bot = Bot(token=config.telegram_token)
        self._chat_id = config.chat_id
        self._timeout_seconds = config.approval_timeout_min * 60

    async def notify_success(self, message: str) -> None:
        await self._bot.send_message(
            chat_id=self._chat_id,
            text=f"**Success:**\n{message}",
            parse_mode="Markdown",
        )

    async def notify_failure(self, message: str) -> None:
        await self._bot.send_message(
            chat_id=self._chat_id,
            text=f"**Failure:**\n{message}",
            parse_mode="Markdown",
        )

    async def request_approval(self, summary: str, diff: str) -> ApprovalResult:
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
        """
        Polls the Telegram API via get_updates until the user clicks a button
        on the specific message_id, or the timeout is reached.
        """
        start_time = asyncio.get_event_loop().time()
        offset = None

        logger.info(
            f"Waiting for human approval for {self._timeout_seconds} seconds..."
        )

        while (asyncio.get_event_loop().time() - start_time) < self._timeout_seconds:
            # Long polling: timeout=10 means Telegram holds the connection open for 10s
            # before returning an empty list, saving API calls.
            updates = await self._bot.get_updates(offset=offset, timeout=10)

            for update in updates:
                offset = update.update_id + 1

                if update.callback_query:
                    query = update.callback_query

                    # Only process clicks that belong to the message we just sent
                    if query.message and query.message.message_id == message_id:
                        # Answer the query immediately to stop the loading spinner on the user's app
                        await query.answer()

                        # Remove the buttons so the user can't click them again later
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

        # If the while loop exits natively, we hit the timeout
        logger.warning("Approval request timed out.")

        # Clean up the buttons on timeout
        await self._bot.edit_message_reply_markup(
            chat_id=self._chat_id, message_id=message_id, reply_markup=None
        )

        return ApprovalResult(
            status=ApprovalStatus.TIMEOUT, reason="Human did not respond in time."
        )
