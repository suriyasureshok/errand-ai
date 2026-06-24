"""Entry point for the Errand AI pipeline.

This script initializes the environment, wires up the infrastructure and
domain agents via dependency injection, and starts the WorkflowEngine.
"""

import asyncio
import sys

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
from src.application import Config, SessionManager, WorkflowEngine
from src.infrastructure.ai_providers import NvidiaNIMProvider, OllamaProvider
from src.infrastructure.git import GitClient
from src.infrastructure.notifications import TelegramNotifier
from src.utils import get_logger, setup_root_logger

# Configure standard logging immediately
setup_root_logger(level="INFO")
logger = get_logger(__name__)


async def main() -> None:
    """Initializes and runs the core asynchronous pipeline."""
    logger.info("Booting Errand AI...")

    try:
        config = Config.load()
    except KeyError as e:
        logger.error(f"Missing required environment variable: {e}")
        sys.exit(1)

    # 1. Initialize Infrastructure
    if config.provider.lower() == "ollama":
        ai_provider = OllamaProvider(config)
    else:
        ai_provider = NvidiaNIMProvider(config)

    git_client = GitClient(config.workspace)
    notifier = TelegramNotifier(config)

    # 2. Initialize Session and File Managers
    session_manager = SessionManager(config)

    # 3. Initialize Agents (Dependency Injection)
    test_agent = TestAgent(config.workspace, session_manager.log_manager)
    log_analyzer = LogAnalyzerAgent(ai_provider)
    context_collector = ContextCollectorAgent(session_manager.context_manager)
    patch_generator = PatchGeneratorAgent(ai_provider)
    guardrail_agent = GuardrailAgent()
    approval_agent = ApprovalAgent(notifier, session_manager)
    refactor_agent = RefactorAgent(ai_provider, session_manager)
    git_agent = GitAgent(session_manager, git_client)
    apply_patch_agent = ApplyPatchAgent(session_manager)

    # 4. Initialize and Run Orchestrator
    engine = WorkflowEngine(
        config=config,
        session_manager=session_manager,
        test_agent=test_agent,
        log_analyzer=log_analyzer,
        context_collector=context_collector,
        patch_generator=patch_generator,
        guardrail_agent=guardrail_agent,
        approval_agent=approval_agent,
        refactor_agent=refactor_agent,
        git_agent=git_agent,
        apply_patch_agent=apply_patch_agent,
    )

    try:
        await engine.run()
    except Exception as e:
        logger.critical(f"Fatal pipeline crash: {e}", exc_info=True)
        session_manager.mark_failed()
        sys.exit(1)


if __name__ == "__main__":
    # Ensure Windows compatibility for asyncio subprocesses
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    asyncio.run(main())
