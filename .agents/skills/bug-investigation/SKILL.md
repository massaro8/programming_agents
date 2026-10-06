---
name: bug-investigation
description: Use for bugs, regressions, non-obvious test failures, or localized incidents.
---

# Bug Investigation

## Procedure
1. Reproduce first.
2. Localize the failure path.
3. State a root-cause hypothesis backed by evidence.
4. Add a regression test where practical.
5. Apply the smallest coherent fix.
6. Run the regression and neighboring checks.
7. If the same substantive error survives repeated attempts, stop editing and re-investigate.
8. Report `Cause / Changed / Checks / Residual risks`.

## Purpose
Use for bugs, regressions, non-obvious test failures, or localized incidents.

## Positive triggers
Use for bugs, regressions, non-obvious test failures, or localized incidents.

## Exclusions
Do not use for a one-step edit or a task outside this skill’s declared scope.

## Scope
Own only the repeatable procedure above; preserve repository ownership and task boundaries.

## Verification
Support conclusions with repository paths and actually executed relevant checks.

## Failure / escalation
Report missing context or conflicting contracts before dependent implementation.

## Output contract
Return the outcome, relevant files, verification evidence and residual risks.
