---
name: feature-builder
description: Use for implementing a non-trivial feature from a scoped, human-owned READY FEATURE item with explicit acceptance criteria.
---

# Feature Builder

## Inputs and preconditions
- One READY FEATURE item describing scope, acceptance, constraints, and verification.
- Applicable `AGENTS.md`, codebase map, and repository instructions.
- If scope or acceptance is absent, stop implementation and report the missing decision.

## Procedure
1. Read the repository instructions and generated codebase map; search before opening broad areas.
2. Read the feature spec, owning implementation, analogous patterns, relevant contracts, and tests.
3. Identify user-visible behavior, ownership boundaries, and a narrow verification plan before editing.
4. Use the module-placement skill before creating or moving a source module.
5. Implement the smallest coherent change. Keep generated applications independent of AgentReady at runtime.
6. Add or update focused tests for the acceptance criteria and update authoritative docs only when the concept changes.
7. Run focused checks first, then the verification required by repository policy and task risk.
8. Record changed files, dependencies, decisions, verification, deviations, and documentation impact in the work item.
9. Sync generated work indexes and transition the item to DONE only after acceptance and required checks pass.

## Context and commands
Start with `python scripts/project.py context --next` (or the explicit work ID); if tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Use `uv run pytest <relevant-test>` for focused tests, then the repository's documented verification command. Consult `docs/agent/workflows/feature.md` for the work record and `docs/agent/standards/` for applicable standards.

## Escalate or stop
Stop before coding when scope, acceptance, ownership, or a required external decision is unclear. Escalate broad architectural changes, incompatible constraints, or checks that cannot be run; record the reason and evidence.

## Evidence of completion
Acceptance criteria are met, relevant checks pass, the work record is complete, indexes are synced, and the item is DONE.
