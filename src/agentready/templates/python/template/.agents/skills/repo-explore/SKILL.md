---
name: repo-explore
description: Use to locate ownership, behavior, boundaries, or tests in an unfamiliar repository area before planning implementation.
---

# Repository Exploration

## Inputs and preconditions
- A concrete question, behavior, or proposed change to localize.
- Repository read access; this skill is read-only.

## Procedure
1. Read applicable instructions and generated codebase map.
2. Search filenames, symbols, tests, contracts, and docs before opening broadly.
3. Trace the request from entry point through owning capability and important consumers.
4. Inspect the narrowest implementation, tests, and relevant workflow or standard.
5. Separate facts from hypotheses; note missing tests, ownership ambiguity, and uncertainty.
6. Return evidence-backed paths and symbols with a concise boundary summary and next checks.

## Context and commands
If exploration serves a work item, start with `python scripts/project.py context --next`; otherwise use `AGENTS.md` and `docs/agent/index.md` directly.
Use `rg --files` and `rg -n`; follow [exploration workflow](../../../docs/agent/workflows/repo-explore.md) and context-efficiency standard.

## Escalate or stop
Do not edit files or run mutating commands. Stop when answered or evidence is insufficient; state what would resolve uncertainty.

## Evidence of completion
Report identifies owner, entry points, behavior path, tests/contracts, boundaries, and unresolved questions with source paths.
