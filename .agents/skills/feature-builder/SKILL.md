---
name: feature-builder
description: Use for a non-trivial feature in an existing repository after scope and acceptance are known.
---

# Feature Builder

## Procedure
1. Read applicable instructions and codebase map.
2. Localize owning capability and analogous patterns.
3. Identify tests/contracts and impact.
4. Define verification before implementation.
5. Implement the minimum coherent change.
6. Run targeted checks and escalate only when the diff/risk justifies it.
7. Review the diff for scope creep, duplication, and accidental contract changes.
8. Report `Changed / Checks / Residual risks`.

## Purpose
Use for a non-trivial feature in an existing repository after scope and acceptance are known.

## Positive triggers
Use for a non-trivial feature in an existing repository after scope and acceptance are known.

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
