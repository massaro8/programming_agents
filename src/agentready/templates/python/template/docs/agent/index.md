# Agent guidance

Start here, then read only the workflow and standards relevant to the selected work item.
Normative requirements are project-owned in `docs/work/`; the implementing agent maintains its
implementation record. Never change requirements to fit an implementation. If blocked, record the
exact blocker, transition to BLOCKED, and stop.

## Work type routing

| Type | Workflow |
| --- | --- |
| FEATURE | [Feature](workflows/feature.md) |
| BUGFIX | [Bugfix](workflows/bugfix.md) |
| REFACTOR | [Refactor](workflows/refactor.md) |
| MAINTENANCE | [Maintenance](workflows/maintenance.md) |
| DOCS | [Documentation](workflows/documentation.md) |
| SECURITY | [Security](workflows/security.md) |

Select one READY item from [the work registry](../work/index.md), inspect its Type, and follow that
workflow. Read [Python](standards/python.md) for Python changes; [architecture](standards/architecture.md)
for boundary changes; [testing](standards/testing.md) when adding or changing tests;
[dependencies](standards/dependencies.md) for dependency work; [documentation](standards/documentation.md)
for doc changes; and [security](standards/security.md) for security-sensitive work.
