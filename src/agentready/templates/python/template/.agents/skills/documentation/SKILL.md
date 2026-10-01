---
name: documentation
description: Use for a READY DOCS item that changes project guidance, reference material, examples, or user-facing documentation.
---

# Documentation

## Inputs and preconditions
- One READY DOCS item with audience, requested outcome, scope, and acceptance.
- The authoritative source files and any commands or examples being documented.

## Procedure
1. Read repository instructions, codebase map, and [documentation workflow](../../../docs/agent/workflows/documentation.md).
2. Find the authoritative source; avoid parallel copies and handbook duplication.
3. Check existing terminology, linked contracts, and examples before editing.
4. Make the narrowest canonical edit; update generated views only through their source mechanism.
5. Verify links, commands, examples, and rendered output where applicable.
6. Check README, architecture, and ADR impact; record UPDATED or NOT_REQUIRED with a reason.
7. Record changes and verification, sync indexes, and mark DONE only when acceptance is met.

## Context and commands
Start with `python scripts/project.py context --next` (or the explicit work ID); if tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Use `rg` to locate references. Run documented link or generation checks and execute examples when practical; do not claim unrun verification.

## Escalate or stop
Request a decision when sources conflict or the audience/behavior is undefined. Do not change runtime behavior under a docs-only item unless scoped.

## Evidence of completion
Canonical docs express accepted behavior, links and examples are checked, documentation impact is recorded, and the item is DONE.
