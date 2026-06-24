# System Architecture

Errand AI is engineered to adhere strictly to Clean Architecture and Dependency Inversion principles. The application is decoupled into four isolated layers, ensuring that core business logic remains entirely oblivious to external frameworks, file systems, or network APIs.

---

## Directory Structure

```
src/
├── domain/           # Immutable models and abstract interfaces
├── application/      # State management and workflow orchestration
├── agents/           # Isolated, single-responsibility business logic
├── infrastructure/   # Concrete API wrappers, databases, and filesystems
├── prompts/          # LLM prompt templates
└── utils/            # Stateless, pure-function helpers
```

---

## Architectural Layers

### Layer 1: Domain (`src/domain/`)

The absolute core of the application. It defines the language the entire system speaks and enforces a clear boundary that prevents circular dependencies.

**Contents:**

- `models/` — Strictly typed Pydantic models: `PatchRecommendation`, `ContextPackage`, `FailureAnalysis`, `GuardrailResult`, `RefactorRequest`, `Session`, `TestResult`, `Approval`.
- `interfaces/` — Abstract base classes: `BaseAgent`, `AIProvider`, `Notifier`, `Repository`, `Guardrail`.
- `error.py` — Domain-level exception definitions.

**Dependency rule:** This layer has zero dependencies on any other layer. Nothing inside `src/domain/` may import from `src/agents/`, `src/application/`, or `src/infrastructure/`.

---

### Layer 2: Application (`src/application/`)

Handles orchestration of the system. This layer consumes domain interfaces only and never touches concrete implementations.

- **`WorkflowEngine`** — A deterministic state machine that loops through testing, patching, and guardrails. It depends exclusively on `BaseAgent` interfaces, preventing circular dependencies with the infrastructure layer.
- **`SessionManager`** — A facade that exposes high-level persistence events (`increment_retry()`, `persist_patch()`) while delegating raw I/O to the infrastructure layer.
- **`StateMachine`** — Encodes legal state transitions (e.g., `TESTING -> ANALYZING -> PATCHING -> AWAITING_APPROVAL -> APPLYING`) and prevents the engine from entering invalid states.
- **`Config`** — Loads and validates all environment configuration at startup.

---

### Layer 3: Agents (`src/agents/`)

Contains single-responsibility classes that implement the business logic of each pipeline stage. Every agent accepts a domain model as input and returns a domain model as output. No agent reaches directly into the infrastructure layer.

| Agent | Input Model | Output Model |
|---|---|---|
| `TestAgent` | `Session` | `TestResult` |
| `LogAnalyzerAgent` | `TestResult` | `FailureAnalysis` |
| `ContextCollectorAgent` | `FailureAnalysis` | `ContextPackage` |
| `PatchGeneratorAgent` | `ContextPackage` | `PatchRecommendation` |
| `GuardrailAgent` | `PatchRecommendation` | `GuardrailResult` |
| `RefactorAgent` | `RefactorRequest` | `PatchRecommendation` |
| `ApprovalAgent` | `PatchRecommendation` | `Approval` |
| `GitAgent` | `Session` | `None` |
| `ApplyPatchAgent` | `PatchRecommendation` | `None` |

---

### Layer 4: Infrastructure (`src/infrastructure/`)

The concrete outside world. This layer implements the domain interfaces and handles all raw I/O. Nothing outside this layer is aware of specific technologies.

- **AI Providers** (`src/infrastructure/ai_providers/`) — Concrete implementations of `AIProvider` for Ollama and NVIDIA NIM. All network calls are wrapped in `@async_retry` decorators with exponential backoff to survive transient API failures.
- **Notifications** (`src/infrastructure/notifications/`) — Telegram bot implementation of the `Notifier` interface, handling asynchronous message delivery and response parsing.
- **Persistence** (`src/infrastructure/persistence/`) — `SessionStore` and `EventStore` manage JSON-backed state to the `.errand-ai/` directory.
- **Git** (`src/infrastructure/git/`) — `GitClient` executes OS-level subprocesses to create checkpoint commits before every patch application.
- **Filesystem** (`src/infrastructure/filesystem/`) — `PatchManager` and `ContextManager` handle all raw byte manipulation, encoding, and byte-perfect search-and-replace patching. `LogManager` captures and archives test output per retry.

---

## Data Flow

The following diagram traces the path of data from test failure to patch application. Each arrow represents a domain model crossing a layer boundary.

```
EXTERNAL: ./errand_ai.sh
       |
       | stdout / stderr / exit code
       v
[TestAgent]
       |
       | TestResult { exit_code, stdout, stderr, duration }
       v
[LogAnalyzerAgent]
       |
       | FailureAnalysis { failing_tests[], stack_traces[], source_locations[], error_summary }
       v
[ContextCollectorAgent]         <-- reads Local Filesystem (via ContextManager)
       |
       | ContextPackage { file_contents{}, relevant_imports[], test_bodies[] }
       v
[PatchGeneratorAgent]           <-- calls AIProvider (Ollama / NVIDIA NIM)
       |
       | PatchRecommendation { root_cause, proposed_diff, target_file, search_str, replace_str }
       v
[GuardrailAgent]
       |
       |-- FAIL --> RefactorRequest { original_patch, rejection_reason }
       |                 |
       |                 v
       |            [RefactorAgent]  <-- calls AIProvider
       |                 |
       |                 | PatchRecommendation (revised)
       |                 v
       |           [GuardrailAgent]  (re-evaluated)
       |
       |-- PASS -->
       v
[ApprovalAgent]                 <-- Telegram bot sends patch summary to developer
       |
       |-- TIMEOUT / REJECTED --> pipeline terminates
       |-- REFACTOR_REQUESTED --> RefactorRequest --> [RefactorAgent]
       |
       |-- APPROVED -->
       v
[GitAgent]                      <-- git add . && git commit -m "Errand AI Retry #N"
       |
       v
[ApplyPatchAgent]               <-- PatchManager performs byte-perfect search-and-replace
       |
       v
Increment retry counter
       |
       v
[TestAgent]  (next iteration)
```

---

## The Refactor Loop

A critical architectural feature is the self-correction loop. If the `PatchGeneratorAgent` produces code that fails the `GuardrailAgent` (syntax error, dangerous API usage, protected file modification) or is explicitly rejected by the developer via Telegram, the pipeline does not crash.

```
[PatchGeneratorAgent]
        |
        v
[GuardrailAgent]
        |
        |-- PASS --> [ApprovalAgent]
        |
        |-- FAIL -->
        v
[RefactorAgent]
   - Receives: RefactorRequest { patch, rejection_reason }
   - Prompts the LLM with the original patch and the specific rejection reason
   - Returns: PatchRecommendation (revised)
        |
        v
[GuardrailAgent]  (re-evaluated)
        |
        |-- Continues looping until pass or retry limit is exhausted
```

The failure reason is bundled into a `RefactorRequest` domain model and passed to the `RefactorAgent`, which prompts the LLM to correct its specific mistake before re-entering the guardrail queue.

---

## State Machine

The `WorkflowEngine` progresses through the following states. No agent is invoked outside of the correct state.

```
IDLE
  |
  v
TESTING
  |-- pass --> COMPLETE
  |-- fail --> ANALYZING
                  |
                  v
              COLLECTING_CONTEXT
                  |
                  v
              GENERATING_PATCH
                  |
                  v
              VALIDATING
                  |-- fail --> REFACTORING --> VALIDATING
                  |
                  v (pass)
              AWAITING_APPROVAL
                  |-- timeout / reject --> FAILED
                  |-- refactor         --> REFACTORING --> VALIDATING
                  |
                  v (approved)
              CHECKPOINTING
                  |
                  v
              APPLYING_PATCH
                  |
                  v
              TESTING  (retry N+1)
                  |
                  |-- MAX_RETRIES exceeded --> FAILED
```

---

## Dependency Map

```
src/domain/          <-- no imports from any other src/ layer
     ^
     |
src/agents/          <-- imports domain models and domain interfaces only
     ^
     |
src/application/     <-- imports agents (via BaseAgent interface), imports domain
     ^
     |
src/infrastructure/  <-- implements domain interfaces; imports domain models only
```

The infrastructure layer is never imported by agents or the domain layer. All wiring is performed by the application layer, which injects concrete implementations through constructor arguments conforming to the domain interfaces.

---

## AI Provider Abstraction

```
AIProvider (domain/interfaces/ai_provider.py)
   |
   |-- OllamaProvider     (infrastructure/ai_providers/ollama.py)
   |-- NvidiaNimProvider  (infrastructure/ai_providers/nvidia_nim.py)
   |-- [Future] OpenAIProvider
   |-- [Future] GeminiProvider
   |-- [Future] LMStudioProvider
```

Switching providers requires only a change to the `MODEL_PROVIDER` environment variable. The `Config` layer resolves the correct concrete implementation and injects it into the agents at startup. No agent code changes are required.

---

## Session State

All session state is persisted to `.errand-ai/` in the repository root, allowing inspection and manual recovery at any stage.

```
.errand-ai/
├── session.json              # Current session metadata and retry counter
├── logs/
│   ├── retry-1.log           # stdout + stderr from test run
│   └── retry-n.log
├── patches/
│   ├── retry-1.diff          # Proposed diff before application
│   └── retry-n.diff
├── context/
│   ├── retry-1-context.txt   # Files injected into LLM context
│   └── retry-n-context.txt
└── history/
    └── events.json           # Full event log across all retries
```

---

## Git Checkpoint Strategy

Before any patch is applied to the filesystem, the `GitAgent` creates a traceable commit:

```
git add .
git commit -m "Errand AI Retry #N – pre-patch checkpoint"
```

If a patch produces a broken state, the developer can recover the workspace immediately:

```bash
git log --oneline
git revert HEAD
# or
git reset --hard HEAD~1
```

Every modification is traceable and reversible. There is no silent state mutation.
