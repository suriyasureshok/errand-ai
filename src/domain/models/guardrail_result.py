"""Domain models for security and safety validation.

This module defines the output of the GuardrailAgent, which ensures proposed
code modifications do not violate security policies or syntax rules.
"""

from dataclasses import dataclass
from typing import Optional

from src.domain.models.patch_recommendation import PatchRecommendation


@dataclass
class GuardrailResult:
    """Encapsulates the verdict of a guardrail safety check.

    Attributes:
        passed (bool): True if the patch is safe to apply, False otherwise.
        recommendation (PatchRecommendation): The original or safely modified patch.
        reason (Optional[str]): Explanation for why the patch failed validation, if applicable.
    """

    passed: bool
    recommendation: PatchRecommendation
    reason: Optional[str] = None
