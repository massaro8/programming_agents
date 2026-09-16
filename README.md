# AgentReady

> Bootstrap once. Own the repository forever.

AgentReady is a vendor-neutral, detachable repository engineering layer for coding agents.
Its goal is not to replace Codex, Claude Code, Copilot, Cursor, or other coding agents.
It makes a repository easier for those agents and humans to understand, modify, verify,
and maintain without introducing a runtime dependency on AgentReady.

## Status

This repository is the public-ready engineering scaffold for the V0.1 implementation.
The first product milestone is intentionally narrow:

1. `agentready init` - bootstrap a new agent-ready repository.
2. `agentready doctor` - inspect repository readiness and instruction drift.
3. `agentready detach` - remove AgentReady maintenance metadata while keeping the project usable.

Only after those three commands are stable should the project add `adopt`, `sync`, `audit`,
and safe opt-in updates.

## Core promises

- **No runtime lock-in**: generated applications never import AgentReady.
- **No account or backend required**.
- **Vendor-neutral**: `AGENTS.md` is the public repository instruction entry point.
- **Progressive disclosure**: short always-loaded instructions; workflows and standards on demand.
- **Evidence over claims**: checks, exit codes, changed files, and residual risks are explicit.
- **Project ownership**: the generator never silently retakes ownership of user code.
- **Detachable by design**: deleting maintenance metadata must not break build, test, or agent usage.

## Engineering model

```text
Task
  -> classify complexity/risk
  -> retrieve minimum sufficient context
  -> strong planning only when justified
  -> focused implementation
  -> deterministic verification
  -> strong review only when risk/uncertainty justifies it
```

Recommended coding-agent routing for this repository:

```text
GPT-5.6 Sol   -> coordinator / architecture / cross-module / high-risk / final audit
GPT-5.6 Luna  -> scoped implementation / tests / mechanical edits / documentation sync
CI + tools    -> authoritative deterministic gates
```

This is a routing policy, not a requirement to use two models for every task.

## Repository map

- `AGENTS.md` - compact cross-agent engineering policy.
- `CLAUDE.md` - thin Claude-specific adapter.
- `.agents/skills/` - on-demand reusable workflows.
- `docs/ARCHITECTURE.md` - target architecture and boundaries.
- `docs/PRODUCT_SPEC.md` - product scope and non-goals.
- `docs/ROADMAP.md` - implementation sequence and gates.
- `docs/DETACHMENT_CONTRACT.md` - formal no-lock-in contract.
- `methodology/` - canonical engineering guidance compiled into generated repositories.
- `schemas/` - machine-readable contracts for future metadata and audit artifacts.
- `scripts/generate_codebase_map.py` - deterministic repository navigation map.
- `START_SOL_COORDINATOR.md` - kickoff prompt for the coordinator.

## Local baseline

```bash
uv sync --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run python scripts/generate_codebase_map.py --check
```

## Public release rule

Do not publish V0.1 as "stable" until the detachment test proves:

```text
generate -> verify -> detach -> remove AgentReady metadata/tool -> verify again
```

See `docs/ROADMAP.md`.
