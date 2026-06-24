import asyncio
import sys
from pathlib import Path

from src.application import Config
from src.application import SessionManager
from src.application import WorkflowEngine

from src.infrastructure.notifications import TelegramNotifier
from src.infrastructure.git import GitClient
from src.infrastructure.ai_providers import NvidiaNIMProvider
# If you implemented Ollama exactly like NIM:
# from src.infrastructure.ai_providers.ollama import OllamaProvider

from src.agents import TestAgent
from src.agents import LogAnalyzerAgent
from src.agents import ContextCollectorAgent
from src.agents import PatchGeneratorAgent
from src.agents import GuardrailAgent
from src.agents import ApprovalAgent
from src.agents import RefactorAgent
from src.agents import GitAgent
from src.agents import ApplyPatchAgent

from src.utils.logger import setup_logger, get_logger


def get_ai_provider(config: Config):
    """Factory function to instantiate the correct AI provider based on config."""
    provider_name = config.provider.lower()
    if provider_name == "nvidia_nim":
        return NvidiaNIMProvider(config)
    # elif provider_name == "ollama":
    #     return OllamaProvider(config)
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")


async def main() -> None:
    # 1. Load Configuration
    try:
        config = Config.load()
    except KeyError as e:
        print(f"FATAL: Missing environment variable: {e}")
        sys.exit(1)

    # 2. Setup Core Managers
    session_manager = SessionManager(config=config)
    
    # Setup the root logger, routing logs to both console and the specific retry file
    current_retry = session_manager.load_session().current_retry
    log_file = session_manager.logs_dir / f"retry-{current_retry}-system.log"
    setup_logger(log_file=log_file)
    logger = get_logger(__name__)
    
    logger.info("Starting Errand AI Boot Sequence...")

    # 3. Setup Infrastructure Clients
    notifier = TelegramNotifier(config=config)
    git_client = GitClient(workspace=config.workspace)
    ai_provider = get_ai_provider(config=config)

    # 4. Instantiate Pipeline Agents (Dependency Injection)
    test_agent = TestAgent(
        session_manager=session_manager,
        notifier=notifier,
    )
    log_analyzer_agent = LogAnalyzerAgent(
        ai_provider=ai_provider,
        session_manager=session_manager,
    )
    context_collector_agent = ContextCollectorAgent(
        session_manager=session_manager,
    )
    patch_generator_agent = PatchGeneratorAgent(
        ai_provider=ai_provider,
        session_manager=session_manager,
    )
    guardrail_agent = GuardrailAgent(
        session_manager=session_manager,
    )
    approval_agent = ApprovalAgent(
        notifier=notifier,
        session_manager=session_manager,
    )
    refactor_agent = RefactorAgent(
        ai_provider=ai_provider,
        session_manager=session_manager,
    )
    git_agent = GitAgent(
        session_manager=session_manager,
        git_client=git_client,
    )
    apply_patch_agent = ApplyPatchAgent(
        session_manager=session_manager,
    )

    # 5. Assemble and Start the Workflow Engine
    engine = WorkflowEngine(
        session_manager=session_manager,
        test_agent=test_agent,
        log_analyzer_agent=log_analyzer_agent,
        context_collector_agent=context_collector_agent,
        patch_generator_agent=patch_generator_agent,
        guardrail_agent=guardrail_agent,
        approval_agent=approval_agent,
        refactor_agent=refactor_agent,
        git_agent=git_agent,
        apply_patch_agent=apply_patch_agent,
    )

    try:
        await engine.run()
    except Exception as e:
        logger.exception(f"Fatal error during execution: {e}")
        session_manager.mark_failed()
        sys.exit(1)


if __name__ == "__main__":
    # Ensure graceful exit on KeyboardInterrupt (Ctrl+C)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutdown signal received. Exiting Errand AI.")
        sys.exit(0)