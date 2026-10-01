---
name: module-placement
description: Use before creating or moving a source module when its architectural owner, layer, or package location is uncertain.
---

# Module Placement

## Inputs and preconditions
- Proposed responsibility, dependencies, callers, and candidate source location.
- Repository architecture guidance and nearby examples.

## Procedure
1. Read the map and [module-placement workflow](../../../docs/agent/workflows/module-placement.md); search for analogous responsibilities.
2. Classify the code as entry point, adapter, application orchestration, domain behavior, or shared policy.
3. Identify allowed dependency direction and owning module; check for an existing owner.
4. Prefer established structure; avoid generic utility modules and abstractions without a second consumer.
5. Explain selected location using concrete dependencies and examples.
6. If placement is implemented, run architecture check and relevant tests.

## Context and commands
If placement serves a work item, start with `python scripts/project.py context --next`; otherwise use `AGENTS.md` and `docs/agent/index.md` directly.
Use `rg` for imports and responsibility names. Run `python scripts/architecture_check.py` when available.

## Escalate or stop
Stop when responsibility crosses ownership boundaries or guidance conflicts. Request a decision before a new layer or shared abstraction.

## Evidence of completion
Owner and path follow boundaries, nearby patterns were checked, and architecture validation passes when code moved.
