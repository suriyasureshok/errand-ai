from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional


class ApprovalStatus(Enum):
    APPROVED = auto()
    REJECTED = auto()
    REFACTOR_REQUESTED = auto()
    TIMEOUT = auto()
    ERROR = auto()


@dataclass
class ApprovalResult:
    status: ApprovalStatus
    reason: Optional[str] = None
