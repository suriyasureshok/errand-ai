"""Domain models for human-in-the-loop approval workflows.

This module defines the states and results associated with a human reviewer
evaluating a generated patch recommendation.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class ApprovalStatus(Enum):
    """Represents the possible outcomes of a human approval request."""

    APPROVED = auto()
    REJECTED = auto()
    REFACTOR_REQUESTED = auto()
    TIMEOUT = auto()
    ERROR = auto()


@dataclass
class ApprovalResult:
    """Encapsulates the result of an approval workflow.

    Attributes:
        status (ApprovalStatus): The final status decided by the human or system timeout.
        reason (Optional[str]): An optional explanation provided by the reviewer,
            particularly useful when the status is REJECTED or REFACTOR_REQUESTED.
    """

    status: ApprovalStatus
    reason: Optional[str] = None
