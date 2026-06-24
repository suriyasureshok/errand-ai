"""Infrastructure layer for the Errand AI pipeline.

This package encapsulates all interactions with the external world. It provides
concrete implementations of the domain interfaces, handling tasks such as API 
communication with LLMs, filesystem I/O, Git subprocess execution, and Telegram 
webhooks. 
"""

from .ai_providers import NvidiaNIMProvider, OllamaProvider
from .filesystem import ContextManager, LogManager, PatchManager
from .git import GitClient
from .notifications import TelegramNotifier
from .persistence import EventStore, SessionStore

# Export all the major infrastructure components for the orchestration layer
__all__ = [
    "ContextManager",
    "EventStore",
    "GitClient",
    "LogManager",
    "NvidiaNIMProvider",
    "OllamaProvider",
    "PatchManager",
    "SessionStore",
    "TelegramNotifier",
]
