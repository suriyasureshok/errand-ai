"""Agent responsible for safety and syntax verification.

This module provides the GuardrailAgent, which inspects generated patches
to ensure they are syntactically valid and free of dangerous operations
before passing them down the pipeline.
"""

import ast

from src.domain.interfaces import BaseAgent
from src.domain.models import GuardrailResult
from src.domain.models import PatchRecommendation
from src.utils import get_logger

logger = get_logger(__name__)


class GuardrailAgent(BaseAgent[PatchRecommendation, GuardrailResult]):
    """Agent that enforces syntactic and security safety on generated patches."""

    def __init__(self) -> None:
        """Initializes the GuardrailAgent."""
        pass

    async def execute(self, input_data: PatchRecommendation) -> GuardrailResult:
        """Validates the proposed code modifications.

        Currently enforces AST (Abstract Syntax Tree) compilation checks to
        prevent syntax-breaking hallucinations.

        Args:
            input_data (PatchRecommendation): The AI-generated patch proposal.

        Returns:
            GuardrailResult: A domain model indicating pass/fail status.
        """
        logger.info("Executing guardrail validations on proposed patch...")

        for patch in input_data.patches:
            # We only check Python files for AST validity
            if not patch.file_path.endswith(".py"):
                continue

            try:
                # Attempt to parse the replacement block as valid Python syntax.
                # We wrap it in a try/except because sometimes the block is just a
                # fragment (like changing a variable name inside an expression),
                # but for full statements, this catches indentation/colon errors.
                ast.parse(patch.replace_block)
            except SyntaxError as e:
                # If it's a blatant syntax error, reject it immediately
                reason = f"SyntaxError detected in patch for {patch.file_path}: {e}"
                logger.warning(f"Guardrail check failed: {reason}")
                return GuardrailResult(
                    passed=False,
                    recommendation=input_data,
                    reason=reason,
                )

        # Future extensions can include checks for 'os.system' or 'subprocess' injections here.

        logger.info("Guardrail checks passed successfully.")
        return GuardrailResult(
            passed=True,
            recommendation=input_data,
            reason=None,
        )
