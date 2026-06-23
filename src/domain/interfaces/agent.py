from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """
    Base contract implemented by all Errand AI agents.

    Each agent receives the current workflow context,
    performs a single responsibility,
    and returns the updated context.
    """

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the agent's logic.

        Args:
            context: Shared workflow state passed between agents.

        Returns:
            Updated workflow context.
        """
        raise NotImplementedError
