# Agent guidance

Use the [context efficiency standard](standards/context-efficiency.md): follow its context
waterfall, search before opening files, and expand only when evidence requires it. Normative
requirements live in project-owned `docs/work/`; never change them to fit an implementation.

## Work routing

| Type or need | Skill when supported | Canonical fallback |
| --- | --- | --- |
| FEATURE | `feature-builder` | [Feature workflow](workflows/feature.md) |
| BUGFIX | `bug-investigation` | [Bugfix workflow](workflows/bugfix.md) |
| REFACTOR | `refactoring` | [Refactor workflow](workflows/refactor.md) |
| MAINTENANCE | `maintenance` | [Maintenance workflow](workflows/maintenance.md) |
| DOCS | `documentation` | [Documentation workflow](workflows/documentation.md) |
| SECURITY | `security-review` | [Security workflow](workflows/security.md) |
| Unfamiliar area | `repo-explore` | [Repo exploration](workflows/repo-explore.md) |
| New or moved module | `module-placement` | [Module placement](workflows/module-placement.md) |

Select one READY item from [the work registry](../work/index.md), inspect its Type, then use the
matching skill or fallback above. Load only relevant standards: [Python](standards/python.md),
[architecture](standards/architecture.md), [testing](standards/testing.md),
[dependencies](standards/dependencies.md), [documentation](standards/documentation.md), or
[security](standards/security.md). If blocked, record the blocker, transition to BLOCKED, and stop.
