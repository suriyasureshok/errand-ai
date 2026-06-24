"""Interface definition for version control management.

This module defines the contract for interacting with the target codebase's
underlying version control system (e.g., Git).
"""

from abc import ABC, abstractmethod


class Repository(ABC):
    """Abstract interface for codebase version control operations.

    This ensures the pipeline can create safety nets before modifying files,
    allowing it to safely rollback changes if a generated patch is faulty.
    """

    @abstractmethod
    async def create_checkpoint(self, retry_number: int) -> None:
        """Creates a snapshot of the current workspace state.

        Args:
            retry_number (int): The current execution loop index, used for
                labeling or tagging the checkpoint.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_diff(self) -> str:
        """Retrieves the current uncommitted changes in the workspace.

        Returns:
            str: The raw unified diff representing pending changes.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
