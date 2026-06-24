"""State machine definitions for the workflow orchestrator.

This module defines the discrete operational states of the Errand AI
pipeline, enabling robust transitions and clear logging within the Workflow Engine.
"""

from enum import Enum, auto


class WorkflowState(Enum):
    """Represents the discrete states of the remediation pipeline.

    States:
        INIT: Pipeline initialization and environment validation.
        RUNNING_TESTS: Executing the target codebase's test suite.
        ANALYZING_LOGS: LLM is interpreting test stdout/stderr.
        COLLECTING_CONTEXT: Gathering relevant source code into a package.
        GENERATING_PATCH: LLM is formulating a fix.
        VALIDATING_GUARDRAILS: Security and syntax checks are running on the patch.
        AWAITING_APPROVAL: Polling for human confirmation via Telegram.
        REFACTORING_PATCH: LLM is rewriting the patch based on rejection feedback.
        APPLYING_PATCH: Mutating the filesystem using search-and-replace.
        SUCCESS: Pipeline resolved the issue and tests pass.
        FAILED: Pipeline exhausted retries or encountered a fatal error.
    """

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
