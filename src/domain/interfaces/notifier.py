"""Interface definition for human-in-the-loop notification systems.

This module defines the contract for messaging and alert systems used to
keep human overseers informed and to request explicit execution approvals.
"""

from abc import ABC, abstractmethod

from src.domain.models import ApprovalResult


class Notifier(ABC):
    """Abstract interface for outbound messaging and interactive alerts."""

    @abstractmethod
    async def notify_success(self, message: str) -> None:
        """Sends a non-blocking notification of pipeline success.

        Args:
            message (str): The success details to transmit to the human reviewer.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    async def notify_failure(self, message: str) -> None:
        """Sends a non-blocking notification of pipeline failure.

        Args:
            message (str): The error or failure details to transmit to the
                human reviewer.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    async def request_approval(self, summary: str, diff: str) -> ApprovalResult:
        """Requests human approval for a proposed codebase modification.

        This method must block execution (e.g., via long-polling or webhooks)
        until a human responds, or until a predefined timeout is reached.

        Args:
            summary (str): A brief explanation of the proposed patch.
            diff (str): The visual unified diff of the code changes.

        Returns:
            ApprovalResult: The domain model containing the human's decision
                (APPROVED, REJECTED, REFACTOR_REQUESTED) or a TIMEOUT status.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
