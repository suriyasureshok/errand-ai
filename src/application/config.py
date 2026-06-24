import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
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
        return cls(
            workspace=Path(os.getenv("WORKSPACE", os.getcwd())),
            provider=os.getenv("MODEL_PROVIDER", "ollama"),
            model=os.getenv("MODEL", "qwen3-coder"),
            base_url=os.getenv("BASE_URL", "http://host.docker.internal:11434/v1"),
            api_key=os.getenv("API_KEY", ""),
            telegram_token=os.environ["TELEGRAM_TOKEN"],  # Throws KeyError if missing
            chat_id=os.environ["CHAT_ID"],  # Throws KeyError if missing
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            approval_timeout_min=int(os.getenv("APPROVAL_TIMEOUT_MIN", "15")),
        )
