"""Interface definition for pipeline agents.

This module provides the generic base contract that all isolated agents
in the Errand AI remediation pipeline must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


class BaseAgent(ABC, Generic[T_in, T_out]):
    """Base contract implemented by all Errand AI pipeline agents.

    Each agent represents a single, isolated step in the remediation workflow.
    It receives a strongly-typed input domain model, performs a specific
    responsibility, and returns a strongly-typed output domain model.
    """

    @abstractmethod
    async def execute(self, input_data: T_in) -> T_out:
        """Executes the asynchronous business logic of the agent.

        Args:
            input_data (T_in): The domain model outputted by the previous
                pipeline step or the workflow engine.

        Returns:
            T_out: The resulting domain model, representing the output state
                to be passed to the next agent.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
