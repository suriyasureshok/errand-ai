"""Domain models for iterative AI prompting.

This module defines the data required to ask the AI to try generating
a fix again, usually after a guardrail failure or human rejection.
"""

from dataclasses import dataclass

from src.domain.models.context_package import ContextPackage
from src.domain.models.patch_recommendation import PatchRecommendation


@dataclass
class RefactorRequest:
    """Bundles data required for a subsequent refactor attempt.

    Attributes:
        package (ContextPackage): The original codebase context and error data.
        previous_recommendation (PatchRecommendation): The patch that was rejected.
        rejection_reason (str): The specific reason the patch was rejected, guiding the AI.
    """

    package: ContextPackage
    previous_recommendation: PatchRecommendation
    rejection_reason: str
