"""Configuration management for the Errand AI pipeline.

This module defines the immutable Configuration object that loads and validates
environment variables required for the pipeline's execution.
"""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    """Immutable configuration object for the application.

    Attributes:
        workspace (Path): The absolute path to the target codebase.
        provider (str): The AI model provider (e.g., 'ollama', 'nvidia').
        model (str): The specific model identifier to use.
        base_url (str): The base URL for the AI provider's API.
        api_key (str): The authentication key for the AI provider.
        telegram_token (str): The bot token for the Telegram notification webhook.
        chat_id (str): The Telegram chat ID where approval requests are sent.
        max_retries (int): The maximum number of fix-and-test loops allowed.
        approval_timeout_min (int): Minutes to wait for human approval before aborting.
    """

    workspace: Path
    provider: str
    model: str
    base_url: str
    api_key: str
    telegram_token: str
    chat_id: str
    max_retries: int
    approval_timeout_min: int

    @classmethod
    def load(cls) -> "Config":
        """Loads and parses configuration from environment variables.

        Returns:
            Config: A fully populated and validated configuration instance.

        Raises:
            KeyError: If required environment variables (e.g., TELEGRAM_TOKEN) are missing.
            ValueError: If numeric environment variables cannot be parsed as integers.
        """
        return cls(
            workspace=Path(os.getenv("WORKSPACE", os.getcwd())),
            provider=os.getenv("MODEL_PROVIDER", "ollama"),
            model=os.getenv("MODEL", "phi4-mini"),
            base_url=os.getenv("BASE_URL", "http://host.docker.internal:11434/v1"),
            api_key=os.getenv("API_KEY", ""),
            telegram_token=os.environ["TELEGRAM_TOKEN"],
            chat_id=os.environ["CHAT_ID"],
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            approval_timeout_min=int(os.getenv("APPROVAL_TIMEOUT_MIN", "15")),
        )
