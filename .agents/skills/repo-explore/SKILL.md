---
name: repo-explore
description: Use for unfamiliar repositories, unclear ownership, cross-module tasks, or broad localization. Read-only.
---

# Repo Explore

## Procedure
Search before read. Inspect instructions and the map, locate owning symbols and relevant tests, then return the scoped findings.

## Output contract

Return only:

```text
FINDINGS
FILES / SYMBOLS
DEPENDENCIES / CONTRACTS
RELEVANT TESTS
RISKS
RECOMMENDED NEXT STEP
```

Do not edit code.

## Purpose
Use for unfamiliar repositories, unclear ownership, cross-module tasks, or broad localization. Read-only.

## Positive triggers
Use for unfamiliar repositories, unclear ownership, cross-module tasks, or broad localization. Read-only.

## Exclusions
Do not use for a one-step edit or a task outside this skill’s declared scope.

## Scope
Own only the repeatable procedure above; preserve repository ownership and task boundaries.

## Verification
Support conclusions with repository paths and actually executed relevant checks.

## Failure / escalation
Report missing context or conflicting contracts before dependent implementation.
