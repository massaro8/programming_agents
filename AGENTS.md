# AGENTS.md

## Mission

Build AgentReady as the smallest coherent, vendor-neutral, detachable repository engineering layer.
Preserve user ownership of generated repositories. Prefer deterministic mechanisms over prompt text.

## Start here

1. Read `docs/generated/CODEBASE_MAP.md`.
2. Search before reading broadly.
3. Read only the implementation, tests, contract, and ADR relevant to the current task.
4. Use a repository skill when the task matches one.
5. For non-trivial work, define verification before editing.

Do not recursively read the whole repository by default.

## Product invariants

- Generated applications MUST NOT import AgentReady at runtime.
- Normal development MUST NOT require an AgentReady account, backend, or remote service.
- `AGENTS.md` is the canonical public instruction entry point in generated repositories.
- Agent-specific files are thin adapters or generated views, not independent policy sources.
- `.agentready/` contains optional maintenance metadata only and must be removable.
- `detach` must preserve source, tests, CI, useful instructions, and normal agent workflows.
- User/project-owned files are never silently overwritten by update/adoption logic.
- V0.1 must not execute arbitrary remote template hooks or community skills.
- No destructive Git operation without explicit user intent.

## Architecture rules

- Keep CLI/orchestration separate from repository detection, rendering, doctor checks, ownership,
  audit evidence, and update logic.
- Core logic should be deterministic and testable without network access.
- Keep provider/agent adapters behind explicit interfaces.
- Keep template/methodology content separate from CLI implementation.
- Avoid generic `utils.py`; put behavior under the owning capability.
- Avoid framework abstractions before two real consumers justify them.

## Change policy

- Implement the minimum coherent diff.
- Reuse an existing pattern before creating a parallel abstraction.
- Do not add a production dependency without a concrete requirement and justification.
- Do not combine unrelated refactors with feature/bug work.
- For bugs: reproduce -> root cause -> regression test -> minimal fix.
- For behavior-preserving refactors: establish baseline -> small transformation -> verify equivalence.

## Context and model routing

Classify complexity and risk independently; use the higher class.

- TRIVIAL: one focused builder is enough.
- LOCAL: Luna or equivalent builder; micro-plan; targeted checks.
- CROSS-MODULE: Sol coordinator produces compact handoff; Luna may build scoped steps.
- ARCHITECTURAL: Sol plans and reviews; builder works from approved scope.
- HIGH-RISK: Sol from the start; explicit failure/rollback considerations and broader validation.

Do NOT automatically use Sol -> Luna -> Sol for every task. Multi-model routing is justified only
when planning/review reduces ambiguity, risk, or likely rework.

## Handoff contract

Coordinator-to-builder handoffs must contain only:

```text
OBJECTIVE
SCOPE
EVIDENCE (paths/symbols)
INVARIANTS
PLAN
ACCEPTANCE
VERIFY
DO NOT CHANGE
OPEN RISKS
```

Do not pass the full reasoning transcript.

## Validation

Run the narrowest relevant checks first, then escalate by impact.

Baseline:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run python scripts/generate_codebase_map.py --check
```

A task is not complete unless every claimed check was actually executed.
CI is authoritative.

## Definition of Done

- Acceptance criteria are satisfied.
- Relevant tests exist and pass.
- Required lint/format/type checks pass.
- Generated repository artifacts remain detachable.
- No accidental runtime dependency on AgentReady is introduced.
- No unrelated modifications remain in the diff.
- Documentation/contracts are updated only when their source concept changed.
- Final report states `Changed / Checks / Residual risks`.

## Permanent knowledge routing

- Product behavior/acceptance -> `docs/PRODUCT_SPEC.md` or feature spec.
- Architecture/rationale -> `docs/ARCHITECTURE.md` + ADR when significant.
- Repeatable procedure -> skill/workflow.
- Verifiable invariant -> test/static check/CI.
- Repository navigation -> generated `CODEBASE_MAP.md`.
- Temporary task state -> session only.
