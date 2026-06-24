"""Interface definition for code safety and validation rules.

This module defines the contract for guardrails—components that inspect
generated patches to ensure they do not introduce syntax errors, security
vulnerabilities, or destructive commands.
"""

from abc import ABC, abstractmethod

from src.domain.models import GuardrailResult, PatchRecommendation


class Guardrail(ABC):
    """Abstract interface for code verification and security scanning."""

    @abstractmethod
    async def validate(self, recommendation: PatchRecommendation) -> GuardrailResult:
        """Inspects a patch recommendation for safety and validity.

        Args:
            recommendation (PatchRecommendation): The proposed patch generated
                by the AI.

        Returns:
            GuardrailResult: A domain object indicating whether the patch passed
                validation, and optionally providing a reason for rejection.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
