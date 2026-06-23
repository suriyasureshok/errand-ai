from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

from src.application.config import Config


class TelegramClient:
    def __init__(
        self,
        config: Config,
    ) -> None:
        self._config = config

        self._bot = Bot(
            token=config.telegram_token,
        )

    async def notify_success(
        self,
        message: str,
    ) -> None:
        await self._bot.send_message(
            chat_id=self._config.telegram_chat_id,
            text=message,
        )

    async def notify_failure(
        self,
        message: str,
    ) -> None:
        await self._bot.send_message(
            chat_id=self._config.telegram_chat_id,
            text=message,
        )

    async def request_approval(
        self,
        summary: str,
    ) -> None:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data="approve",
                ),
                InlineKeyboardButton(
                    text="🔄 Refactor",
                    callback_data="refactor",
                ),
            ]
        ]

        markup = InlineKeyboardMarkup(
            keyboard,
        )

        await self._bot.send_message(
            chat_id=self._config.telegram_chat_id,
            text=summary,
            reply_markup=markup,
        )
