from abc import ABC, abstractmethod

from src.domain.models import ApprovalResult


class Notifier(ABC):
    """Abstract interface for human-in-the-loop notifications."""

    @abstractmethod
    async def notify_success(self, message: str) -> None:
        """Send a non-blocking success notification."""
        pass

    @abstractmethod
    async def notify_failure(self, message: str) -> None:
        """Send a non-blocking failure notification."""
        pass

    @abstractmethod
    async def request_approval(self, summary: str, diff: str) -> ApprovalResult:
        """
        Send an approval request and block until a human responds or it times out.
        """
        pass
