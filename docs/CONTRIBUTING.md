# Contributing to Errand AI

Thank you for your interest in improving Errand AI. This project operates a professional, heavily structured repository. Please review the following guidelines in full before opening a pull request.

---

## Local Development Setup

**1. Clone the repository:**

```bash
git clone https://github.com/suriyasureshkumar1312/errand-ai.git
cd errand-ai
```

**2. Set up a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Configure your environment:**

```bash
cp .env.example .env
# Edit .env with your preferred LLM provider and Telegram credentials
```

**5. Run the test suite:**

```bash
pytest tests/
```

---

## Repository Structure

Before contributing, familiarise yourself with the layer boundaries described in [ARCHITECTURE.md](ARCHITECTURE.md). Violations of these boundaries will cause a PR to be rejected during review.

```
src/
├── domain/           # Core models and interfaces. Zero external dependencies.
├── application/      # Orchestration only. Depends on domain interfaces.
├── agents/           # Business logic. Depends on domain models and interfaces.
├── infrastructure/   # Concrete I/O implementations. Implements domain interfaces.
├── prompts/          # LLM prompt templates in Markdown format.
└── utils/            # Stateless helper functions.
```

---

## Code Quality Standards

All contributions must meet the following standards. PRs that do not comply will not be merged.

### Type Hinting

All functions and class methods must have complete Python type hints, compliant with `mypy` in strict mode.

```python
# Correct
def analyze(self, result: TestResult) -> FailureAnalysis:
    ...

# Incorrect
def analyze(self, result):
    ...
```

### Google Docstrings

Every public module, class, and method must be documented using the standard Google Docstring format. Include `Args:`, `Returns:`, and `Raises:` sections wherever applicable.

```python
def analyze(self, result: TestResult) -> FailureAnalysis:
    """Extracts structured failure data from raw test output.

    Args:
        result: The raw output captured from the test runner.

    Returns:
        A structured FailureAnalysis containing failing test names,
        stack traces, exception types, and source file locations.

    Raises:
        DomainError: If the test output cannot be parsed.
    """
```

### Black Formatting

All code must be formatted using `black` before committing. Run:

```bash
black src/
```

### Clean Architecture Compliance

The following import rules are strictly enforced:

- `src/domain/` must not import from any other `src/` layer.
- `src/agents/` must not import from `src/infrastructure/`.
- `src/agents/` must communicate exclusively via `src/domain/models`.
- `src/application/` must not import concrete infrastructure classes directly. All dependencies are injected via domain interfaces.

A linting check enforces these boundaries in CI. Any violation will fail the pipeline.

---

## Branch Strategy

```
main          <-- stable releases only; protected
develop       <-- integration branch; all PRs target here
feat/*        <-- new features
fix/*         <-- bug fixes
refactor/*    <-- internal refactoring
docs/*        <-- documentation changes
```

Always branch from `develop`:

```bash
git checkout develop
git pull origin develop
git checkout -b feat/your-feature-name
```

---

## Commit Message Format

This repository uses Semantic Commit messaging. Changelogs and release notes are generated from commit history, so consistent formatting is required.

```
<type>(<scope>): <subject>
```

Permitted types:

| Type | Use case |
|---|---|
| `feat` | A new feature |
| `fix` | A bug fix |
| `refactor` | Code changes that neither fix a bug nor add a feature |
| `docs` | Documentation changes only |
| `test` | Adding or correcting tests |
| `chore` | Dependency updates, CI changes, tooling |

Examples:

```bash
feat(agents): add LM Studio provider implementation
fix(guardrail): correctly reject patches targeting .git subdirectories
refactor(workflow): extract retry logic into dedicated RetryPolicy class
docs(architecture): add state machine transition diagram
```

---

## Pull Request Process

**1. Ensure all tests pass locally:**

```bash
pytest tests/
mypy src/
black --check src/
```

**2. Push your branch:**

```bash
git push origin feat/your-feature-name
```

**3. Open a PR against the `develop` branch.**

**4. Use the following PR description format:**

```markdown
**Description:**
- [Component]: Brief explanation of the change and why it is needed.
- [Component]: Brief explanation of another change.

**Data Flow Impact:**
Describe any changes to how domain models flow between agents,
or any new interface contracts introduced.

**Testing:**
- [ ] Tested locally via Docker container.
- [ ] All new functions include Google Docstrings.
- [ ] `mypy` passes with no new errors.
- [ ] `black` formatting applied.
- [ ] Clean Architecture boundaries respected.
```

---

## Adding a New AI Provider

Adding a new LLM provider requires changes in one location only.

**1. Create the implementation file:**

```
src/infrastructure/ai_providers/your_provider.py
```

**2. Implement the `AIProvider` domain interface:**

```python
from src.domain.interfaces.ai_provider import AIProvider
from src.domain.models.context_package import ContextPackage

class YourProvider(AIProvider):
    async def complete(self, prompt: str) -> str:
        ...
```

**3. Register the provider in `src/application/config.py`:**

```python
PROVIDER_MAP = {
    "ollama": OllamaProvider,
    "nvidia": NvidiaNimProvider,
    "your_provider": YourProvider,  # Add here
}
```

**4. Document the required environment variables in `.env.example`.**

No changes to agents, the workflow engine, or the domain layer are required.

---

## Adding a New Guardrail

Guardrail checks are evaluated by `GuardrailAgent` before any patch reaches the approval stage.

**1. Implement a new check method in `src/agents/guardrail_agent.py`:**

```python
def _check_your_rule(self, patch: PatchRecommendation) -> GuardrailResult | None:
    """Returns a rejection result if the rule is violated, else None."""
    ...
```

**2. Register it in the agent's `evaluate()` method:**

```python
checks = [
    self._check_dangerous_apis,
    self._check_protected_files,
    self._check_ast_syntax,
    self._check_your_rule,  # Add here
]
```

**3. Write a corresponding test in `tests/test_guardrails.py`.**

---

## Running the Full Pipeline Locally

To test the end-to-end pipeline against a real repository:

```bash
cd /path/to/your/failing/repo

docker run \
  -v $(pwd):/workspace \
  --env-file .env \
  suriyasureshkumar1312/errand-ai:latest
```

Session state is written to `.errand-ai/` in the mounted workspace. Inspect `session.json` and `history/events.json` to trace execution.

---

## Questions

Open a GitHub Discussion before raising a PR for large or architectural changes. This avoids wasted effort if the direction does not align with the project's goals.
