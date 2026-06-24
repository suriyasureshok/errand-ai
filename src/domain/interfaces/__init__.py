"""Domain interfaces package for the Errand AI pipeline.

This package houses the abstract base classes (ABCs) that define the strict
contracts between the orchestration layer, the agents, and external
infrastructure integrations.
"""

from .agent import BaseAgent
from .ai_provider import AIProvider
from .guardrail import Guardrail
from .notifier import Notifier
from .repository import Repository

__all__ = [
    "AIProvider",
    "BaseAgent",
    "Guardrail",
    "Notifier",
    "Repository",
]
