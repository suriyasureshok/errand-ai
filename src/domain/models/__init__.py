"""Domain models package for the Errand AI pipeline.

This package defines the strictly typed data structures used to pass
information between agents, infrastructure, and the workflow engine.
These classes represent the immutable source of truth for application state.
"""

from .approval import ApprovalResult, ApprovalStatus
from .context_package import ContextFile, ContextPackage
from .failure_analysis import FailureAnalysis
from .guardrail_result import GuardrailResult
from .patch_recommendation import PatchRecommendation, SearchReplacePatch
from .refactor_request import RefactorRequest
from .session import Session, SessionStatus
from .test_result import TestResult

__all__ = [
    "ApprovalResult",
    "ApprovalStatus",
    "ContextFile",
    "ContextPackage",
    "FailureAnalysis",
    "GuardrailResult",
    "PatchRecommendation",
    "RefactorRequest",
    "SearchReplacePatch",
    "Session",
    "SessionStatus",
    "TestResult",
]
