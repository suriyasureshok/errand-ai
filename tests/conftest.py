from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.application.config import Config


@pytest.fixture
def mock_config(tmp_path: Path) -> Config:
    """Provides a mocked Config with a safe, temporary workspace."""
    config = MagicMock(spec=Config)
    config.workspace = tmp_path / "test_workspace"
    config.workspace.mkdir()
    config.base_url = "https://mock.api"
    config.api_key = "mock_key"
    config.model = "mock-model"
    config.telegram_token = "mock_token"
    config.chat_id = "mock_chat_id"
    config.max_retries = 3
    config.approval_timeout_min = 10

    return config
