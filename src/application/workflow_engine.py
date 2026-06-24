"""Workflow orchestration engine for Errand AI.

This module provides the WorkflowEngine, which acts as the central
coordinator, executing agents in sequence, managing state transitions,
and handling the retry/refactor loops.
"""

from src.agents import (
    ApplyPatchAgent,
    ApprovalAgent,
    ContextCollectorAgent,
    GitAgent,
    GuardrailAgent,
    LogAnalyzerAgent,
    PatchGeneratorAgent,
    RefactorAgent,
    TestAgent,
)
from src.application import Config, SessionManager
from src.domain.models import ApprovalStatus, RefactorRequest
from src.utils import get_logger

logger = get_logger(__name__)


class WorkflowEngine:
    """Orchestrates the execution of the remediation pipeline.

    Attributes:
        config (Config): The application configuration.
        session_manager (SessionManager): Manager for state and events.
        # ... agent attributes ...
    """

    def __init__(
        self,
        config: Config,
        session_manager: SessionManager,
        test_agent: TestAgent,
        log_analyzer: LogAnalyzerAgent,
        context_collector: ContextCollectorAgent,
        patch_generator: PatchGeneratorAgent,
        guardrail_agent: GuardrailAgent,
        approval_agent: ApprovalAgent,
        refactor_agent: RefactorAgent,
        git_agent: GitAgent,
        apply_patch_agent: ApplyPatchAgent,
    ) -> None:
        """Initializes the WorkflowEngine with all required agents."""
        self.config = config
        self.session_manager = session_manager
        self.test_agent = test_agent
        self.log_analyzer = log_analyzer
        self.context_collector = context_collector
        self.patch_generator = patch_generator
        self.guardrail_agent = guardrail_agent
        self.approval_agent = approval_agent
        self.refactor_agent = refactor_agent
        self.git_agent = git_agent
        self.apply_patch_agent = apply_patch_agent

    async def run(self) -> None:
        """Executes the main autonomous remediation loop.

        This method runs tests, analyzes failures, generates patches, and loops
        through safety and human approvals until the issue is resolved or
        the maximum retry limit is reached.
        """
        logger.info("Initializing Errand AI Workflow Engine...")

        while True:
            session = self.session_manager.load_session()

            if session.current_retry >= session.max_retries:
                logger.error("Maximum retry limit reached. Aborting pipeline.")
                self.session_manager.mark_failed()
                break

            # Step 1: Run the Test Suite
            test_result = await self.test_agent.execute(session)
            if test_result.passed:
                logger.info("Target codebase tests passed! Pipeline successful.")
                self.session_manager.mark_success()
                break

            # Step 2 & 3: Analyze and Collect Context
            analysis = await self.log_analyzer.execute(test_result)
            context_package = await self.context_collector.execute(analysis)

            # Step 4: Generate Initial Patch
            recommendation = await self.patch_generator.execute(context_package)

            # Inner Loop: Guardrails, Approval, and Refactoring
            patch_approved = False
            while not patch_approved:

                # Guardrail Check
                guardrail_result = await self.guardrail_agent.execute(recommendation)
                if not guardrail_result.passed:
                    logger.warning("Patch failed guardrail check. Triggering refactor.")
                    refactor_req = RefactorRequest(
                        package=context_package,
                        previous_recommendation=recommendation,
                        rejection_reason=guardrail_result.reason
                        or "Failed automated safety guardrails.",
                    )
                    recommendation = await self.refactor_agent.execute(refactor_req)
                    continue  # Loop back to re-evaluate the new patch

                # Human Approval Check
                approval_result = await self.approval_agent.execute(recommendation)

                if approval_result.status == ApprovalStatus.APPROVED:
                    patch_approved = True

                elif approval_result.status == ApprovalStatus.REFACTOR_REQUESTED:
                    logger.info("Human requested a refactor. Triggering AI revision.")
                    refactor_req = RefactorRequest(
                        package=context_package,
                        previous_recommendation=recommendation,
                        rejection_reason=approval_result.reason
                        or "Human reviewer requested structural changes.",
                    )
                    recommendation = await self.refactor_agent.execute(refactor_req)
                    continue  # Loop back to re-evaluate the new patch

                else:
                    # Catch REJECTED, TIMEOUT, or ERROR
                    logger.error(
                        f"Pipeline halted due to approval status: {approval_result.status.name}"
                    )
                    self.session_manager.mark_failed()
                    return

            # Step 5 & 6: Safety Checkpoint and Patch Application
            await self.git_agent.execute(recommendation)
            await self.apply_patch_agent.execute(recommendation)

            # Increment loop counter and try testing again
            self.session_manager.increment_retry()
