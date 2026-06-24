from enum import Enum, auto

class WorkflowState(Enum):
    INIT = auto()
    RUNNING_TESTS = auto()
    ANALYZING_LOGS = auto()
    COLLECTING_CONTEXT = auto()
    GENERATING_PATCH = auto()
    VALIDATING_GUARDRAILS = auto()
    AWAITING_APPROVAL = auto()
    REFACTORING_PATCH = auto()
    APPLYING_PATCH = auto()
    SUCCESS = auto()
    FAILED = auto()