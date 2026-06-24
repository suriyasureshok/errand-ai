# Errand AI

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Architecture: Clean](https://img.shields.io/badge/Architecture-Clean-success.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An autonomous, multi-agent codebase remediation pipeline with human-in-the-loop safety constraints.**

Errand AI is a resilient, containerized AI agent designed to act as a junior developer. It autonomously executes your test suite, diagnoses failures, collects relevant file context, formulates precise Python-based string replacements, and requests human approval via Telegram before committing safety checkpoints and patching your local disk.

---

## The Problem

Modern development is iterative. A typical debugging loop looks like this:

1. Run tests.
2. Tests fail.
3. Inspect logs and identify affected files.
4. Formulate and apply a fix.
5. Rerun tests.
6. Repeat until the build is green.

The problem is that this workflow stops entirely when the developer steps away from the workstation. A failed test can sit untouched for hours despite the machine having everything required to continue the investigation.

Errand AI automates the repetitive parts of this cycle while preserving human control over every code modification.

---

## Core Features

- **Multi-Agent Architecture:** Isolated, single-responsibility agents orchestrate the full remediation lifecycle.
- **Provider Agnostic:** Hot-swappable AI infrastructure supporting local Ollama models, LM Studio, and remote API endpoints including NVIDIA NIM, OpenAI, and Gemini.
- **Human-in-the-Loop (HITL):** Asynchronous Telegram bot integration for patch approval, refactoring feedback, and telemetry.
- **Deterministic Operations:** Pure-Python search-and-replace modification ensuring absolute immunity to Git line-ending clashes or markdown formatting hallucinations.
- **Self-Healing Infrastructure:** Automated Git checkpointing and container volume permission management.
- **Fault-Tolerant Loops:** Exponential backoff retries for network calls and automated refactor loops for failed guardrail checks.

---

## Pipeline Overview

```
Trigger Pipeline
       |
       v
[TestAgent] -- Run ./errand_ai.sh
       |
       |-- Tests Pass --> SESSION COMPLETE
       |
       v
[LogAnalyzerAgent] -- Extract failures, stack traces, source locations
       |
       v
[ContextCollectorAgent] -- Identify and collect relevant files only
       |
       v
[PatchGeneratorAgent] -- Formulate root-cause explanation and fix
       |
       v
[GuardrailAgent] -- AST syntax check, dangerous API scan, protected file check
       |
       |-- Rejected --> [RefactorAgent] -- Rewrite patch --> [GuardrailAgent]
       |
       v (Passed)
[ApprovalAgent] -- Send patch to developer via Telegram
       |
       |-- Timeout / Rejected --> PIPELINE FAILED
       |-- Refactor Requested --> [RefactorAgent]
       |
       v (Approved)
[GitAgent] -- Create checkpoint commit
       |
       v
[ApplyPatchAgent] -- Mutate filesystem with validated diff
       |
       v
Increment retry counter --> [TestAgent]
```

---

## Quick Start (Docker)

Errand AI is fully containerized and designed to be dropped into any failing repository.

**Step 1: Create your environment file**

In the root of your target repository, create a `.env` file:

```env
# AI Configuration
MODEL_PROVIDER=nvidia
MODEL=meta/llama-3.1-70b-instruct
BASE_URL=https://integrate.api.nvidia.com/v1
API_KEY=your_nvidia_api_key

# Out-of-band Telemetry
TELEGRAM_TOKEN=your_telegram_bot_token
CHAT_ID=your_telegram_chat_id

# Safety Configuration
MAX_RETRIES=3
APPROVAL_TIMEOUT_MIN=15
```

**Step 2: Add the `docker-compose.yml`**

```yaml
version: '3.8'
services:
  errand-ai:
    image: suriyasureshkumar1312/errand-ai:latest
    container_name: errand-ai-agent
    volumes:
      - .:/workspace
    environment:
      - WORKSPACE=/workspace
    env_file:
      - .env
```

**Step 3: Launch**

```bash
docker compose up
```

Alternatively, run directly:

```bash
docker pull suriyasureshkumar1312/errand-ai:latest

docker run \
  -v $(pwd):/workspace \
  --env-file .env \
  suriyasureshkumar1312/errand-ai:latest
```

The container discovers `/workspace/errand_ai.sh` automatically and begins the remediation workflow.

---

## Test Script

Errand AI does not impose a testing framework. The `errand_ai.sh` script in your repository root defines how your project should be tested:

```bash
#!/bin/bash
# Python project
pytest

# Rust project
cargo test

# Node project
npm test

# Makefile target
make test
```

Anything executable from a shell script is supported. This makes Errand AI language-agnostic and framework-agnostic.

---

## Supported Model Providers

| Provider | Type | Notes | Implementation Status |
|---|---|---|---|
| Ollama | Local | No API key required | Done |
| NVIDIA NIM | Local / Cloud | Requires API key | Done |
| LM Studio | Local | OpenAI-compatible endpoint | Pending |
| OpenAI | Remote | Requires API key | Pending |
| Gemini | Remote | Requires API key | Pending |
| OpenRouter | Remote | Any OpenAI-compatible API | Pending |

Provider switching requires configuration changes only. No code changes are necessary.

---

## Safety Guarantees

**Mandatory Approval:** Every code modification requires explicit human approval via Telegram before the filesystem is touched.

**Protected Files:** The following files cannot be modified under any circumstance:

```
.env
.git/*
Cargo.lock
package-lock.json
```

**Dangerous API Blocklist:** Patches referencing the following are rejected at the guardrail stage:

```python
os.system()
subprocess.run()
eval()
exec()
os.remove()
shutil.rmtree()
```

**Retry Limits:** Configurable via `MAX_RETRIES` to prevent unbounded remediation loops.

**Git Recovery:** Every applied patch is preceded by a Git checkpoint commit. Any modification can be reverted immediately.

---

## Session State Layout

```
.errand-ai/
├── session.json
├── logs/
│   ├── retry-1.log
│   └── retry-n.log
├── patches/
│   ├── retry-1.diff
│   └── retry-n.diff
├── context/
│   ├── retry-1-context.txt
│   └── retry-n-context.txt
└── history/
    └── events.json
```

---

## Non-Goals

Errand AI is not an autonomous software engineer, a cloud service, a CI/CD replacement, or a repository-wide code generation tool. It does one thing: continue the local testing and remediation loop while the developer is away.

---

## Documentation

- [System Architecture and Design Philosophy](docs/ARCHITECTURE.md)
- [Contributing Guidelines](docs/CONTRIBUTING.md)

---

## License

This project is licensed under the MIT License.
