---
name: bug-investigation
description: Use for a reported defect with observable incorrect behavior that needs reproduction, root cause, and a regression fix.
---

# Bug Investigation

## Inputs and preconditions
- One READY BUGFIX item with expected and observed behavior, scope, and acceptance.
- Applicable repository instructions and a reproducible case or enough evidence to construct one.

## Procedure
1. Read instructions and the codebase map; search for behavior, owner, and relevant tests.
2. Reproduce the defect before changing code. Record command, inputs, and observed failure.
3. Trace the failure to its smallest supported root cause; distinguish evidence from hypotheses.
4. Add a regression test that fails for the defect and passes for intended behavior.
5. Make the smallest fix in the owning capability; preserve contracts and user-owned data.
6. Run the regression test, neighboring checks, and task-required verification.
7. Record root cause, regression test, changed files, checks, and documentation impact.
8. Sync indexes and mark DONE only when acceptance and checks pass.

## Context and commands
Start with `python scripts/project.py context --next` (or the explicit work ID); if tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Follow [the bugfix workflow](../../../docs/agent/workflows/bugfix.md). Start with `uv run pytest <relevant-test>` and use documented verification as risk requires.

## Escalate or stop
Do not guess expected behavior. Stop and report evidence when the issue cannot be reproduced, root cause is ambiguous, or resolution requires a scope or contract decision.

## Evidence of completion
The failure is reproduced, a regression test covers it, focused checks pass, and the READY item is recorded and DONE.
