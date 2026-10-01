---
name: refactoring
description: Use for a READY REFACTOR item that changes internal structure while preserving observable behavior and documented contracts.
---

# Refactoring

## Inputs and preconditions
- One READY REFACTOR item naming target structure, behavior invariants, and acceptance.
- Relevant tests or other evidence describing current observable behavior.

## Procedure
1. Read instructions, map, and [refactor workflow](../../../docs/agent/workflows/refactor.md); locate owner and consumers.
2. Establish baseline behavior with focused tests or reproducible examples.
3. Define the smallest structural transformation; preserve behavior, data, and ownership.
4. Apply one cohesive change at a time; avoid unrelated cleanup and speculative abstractions.
5. Run focused tests and compare results to baseline; run architecture checks for boundary changes.
6. Review docs/ADR impact and record decisions, checks, and deviations.
7. Sync indexes and transition to DONE only when invariants and acceptance hold.

## Context and commands
Start with `python scripts/project.py context --next` (or the explicit work ID); if tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Start with `uv run pytest <relevant-test>`; follow repository checks and architecture standards as applicable.

## Escalate or stop
Stop if baseline behavior is unknown, acceptance requires behavior change, or transformation reveals broader redesign. Clarify scope.

## Evidence of completion
Observable behavior remains equivalent, checks pass, and the refactor record is complete and DONE.
