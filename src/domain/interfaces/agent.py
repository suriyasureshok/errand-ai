from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T_in = TypeVar("T_in")
T_out = TypeVar("T_out")


class BaseAgent(ABC, Generic[T_in, T_out]):
    """
    Base contract implemented by all Errand AI agents.

    Each agent represents a single step in the remediation pipeline,
    receiving a strongly-typed input domain model, performing a specific
    responsibility, and returning a strongly-typed output domain model.
    """

    @abstractmethod
    async def execute(self, input_data: T_in) -> T_out:
        """
        Execute the agent's asynchronous logic.

        Args:
            input_data: The domain model outputted by the previous pipeline step.

        Returns:
            The resulting domain model to be passed to the next agent.
        """
        raise NotImplementedError
