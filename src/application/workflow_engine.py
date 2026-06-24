from src.agents import ApprovalAgent
from src.agents import ContextCollectorAgent
from src.agents import GitAgent
from src.agents import GuardrailAgent
from src.agents import LogAnalyzerAgent
from src.agents import PatchGeneratorAgent
from src.agents import RefactorAgent
from src.agents import TestAgent
from src.agents import ApplyPatchAgent
from src.application.session_manager import SessionManager
from src.application.state_machine import WorkflowState
from src.domain.models import ApprovalStatus
from src.domain.models import RefactorRequest
from src.utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowEngine:
    def __init__(
        self,
        session_manager: SessionManager,
        test_agent: TestAgent,
        log_analyzer_agent: LogAnalyzerAgent,
        context_collector_agent: ContextCollectorAgent,
        patch_generator_agent: PatchGeneratorAgent,
        guardrail_agent: GuardrailAgent,
        approval_agent: ApprovalAgent,
        refactor_agent: RefactorAgent,
        git_agent: GitAgent,
        apply_patch_agent: ApplyPatchAgent
    ) -> None:
        self.session_manager = session_manager
        self.test_agent = test_agent
        self.log_analyzer_agent = log_analyzer_agent
        self.context_collector_agent = context_collector_agent
        self.patch_generator_agent = patch_generator_agent
        self.guardrail_agent = guardrail_agent
        self.approval_agent = approval_agent
        self.refactor_agent = refactor_agent
        self.git_agent = git_agent
        self.apply_patch_agent = apply_patch_agent
        
        self.current_state = WorkflowState.INIT

        # Pipeline state storage (Domain Models)
        self.test_result = None
        self.failure_analysis = None
        self.context_package = None
        self.patch_recommendation = None
        self.rejection_reason = None

    async def run(self) -> None:
        logger.info("Initializing Errand AI Remediation Session...")
        self.current_state = WorkflowState.RUNNING_TESTS

        while self.current_state not in [WorkflowState.SUCCESS, WorkflowState.FAILED]:
            session = self.session_manager.load_session()
            
            if session.current_retry >= session.max_retries and self.current_state != WorkflowState.RUNNING_TESTS:
                logger.warning("Maximum retries reached. Aborting session.")
                self.current_state = WorkflowState.FAILED
                break

            if self.current_state == WorkflowState.RUNNING_TESTS:
                self.test_result = await self.test_agent.execute(None)
                
                if self.test_result.passed:
                    self.current_state = WorkflowState.SUCCESS
                else:
                    self.current_state = WorkflowState.ANALYZING_LOGS

            elif self.current_state == WorkflowState.ANALYZING_LOGS:
                self.failure_analysis = await self.log_analyzer_agent.execute(self.test_result)
                self.current_state = WorkflowState.COLLECTING_CONTEXT

            elif self.current_state == WorkflowState.COLLECTING_CONTEXT:
                self.context_package = await self.context_collector_agent.execute(self.failure_analysis)
                self.current_state = WorkflowState.GENERATING_PATCH

            elif self.current_state == WorkflowState.GENERATING_PATCH:
                self.patch_recommendation = await self.patch_generator_agent.execute(self.context_package)
                self.current_state = WorkflowState.VALIDATING_GUARDRAILS

            elif self.current_state == WorkflowState.VALIDATING_GUARDRAILS:
                guardrail_result = await self.guardrail_agent.execute(self.patch_recommendation)
                
                if guardrail_result.passed:
                    self.current_state = WorkflowState.AWAITING_APPROVAL
                else:
                    self.rejection_reason = guardrail_result.reason
                    self.current_state = WorkflowState.REFACTORING_PATCH

            elif self.current_state == WorkflowState.AWAITING_APPROVAL:
                approval_result = await self.approval_agent.execute(self.patch_recommendation)
                
                if approval_result.status == ApprovalStatus.APPROVED:
                    # Pass through the Git Agent to create a checkpoint before applying
                    self.patch_recommendation = await self.git_agent.execute(self.patch_recommendation)
                    self.current_state = WorkflowState.APPLYING_PATCH
                
                elif approval_result.status == ApprovalStatus.REFACTOR_REQUESTED:
                    self.rejection_reason = "Human requested a manual refactor of the proposed solution."
                    self.current_state = WorkflowState.REFACTORING_PATCH
                
                else:
                    logger.warning("Patch was rejected or timed out by human.")
                    self.current_state = WorkflowState.FAILED

            elif self.current_state == WorkflowState.REFACTORING_PATCH:
                request = RefactorRequest(
                    package=self.context_package,
                    previous_recommendation=self.patch_recommendation,
                    rejection_reason=self.rejection_reason
                )
                self.patch_recommendation = await self.refactor_agent.execute(request)
                self.current_state = WorkflowState.VALIDATING_GUARDRAILS

            elif self.current_state == WorkflowState.APPLYING_PATCH:
                logger.info("Applying approved patch to workspace...")
                
                await self.apply_patch_agent.execute(self.patch_recommendation)
                
                # Increment retry counter before running tests again
                self.session_manager.increment_retry()
                self.current_state = WorkflowState.RUNNING_TESTS

        if self.current_state == WorkflowState.SUCCESS:
            logger.info("Session concluded successfully. Codebase is green.")
            self.session_manager.mark_success()
        else:
            logger.error("Session failed to resolve the issue.")
            self.session_manager.mark_failed()