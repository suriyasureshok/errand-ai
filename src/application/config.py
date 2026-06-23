import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    provider: str
    model: str
    base_url: str
    api_key: str
    telegram_token: str
    telegram_chat_id: str
    max_retries: int
    approval_timeout_min: int

    @classmethod
    def load(cls) -> "Config":
        return cls(
            provider=os.environ["MODEL_PROVIDER"],
            model=os.environ["MODEL"],
            base_url=os.environ["BASE_URL"],
            api_key=os.environ.get("API_KEY", ""),
            telegram_token=os.environ["TELEGRAM_TOKEN"],
            telegram_chat_id=os.environ["TELEGRAM_CHAT_ID"],
            max_retries=int(os.environ.get("MAX_RETRIES", "3")),
            approval_timeout_min=int(os.environ.get("APPROVAL_TIMEOUT_MIN", "15")),
        )
