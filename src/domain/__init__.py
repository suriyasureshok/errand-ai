"""Domain layer for the Errand AI pipeline.

This package encapsulates the core business logic, enterprise rules, and
immutable data structures of the application. It acts as the innermost 
layer of the architecture, containing strictly zero dependencies on external 
frameworks, databases, or UI components.

Sub-packages:
    models: Strictly typed Pydantic and dataclass definitions representing
        the state and data passed through the pipeline.
    interfaces: Abstract Base Classes (ABCs) defining the strict contracts for
        agents, infrastructure providers, and external integrations.
"""

from .interfaces import AIProvider, BaseAgent, Guardrail, Notifier, Repository
from .models import (
    ApprovalResult,
    ApprovalStatus,
    ContextFile,
    ContextPackage,
    FailureAnalysis,
    GuardrailResult,
    PatchRecommendation,
    RefactorRequest,
    SearchReplacePatch,
    Session,
    SessionStatus,
    TestResult,
)

# Explicitly define the public API of the entire domain layer.
__all__ = [
    # Interfaces
    "AIProvider",
    "BaseAgent",
    "Guardrail",
    "Notifier",
    "Repository",
    # Models
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
