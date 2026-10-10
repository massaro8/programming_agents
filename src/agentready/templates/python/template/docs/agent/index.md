# Agent guidance

## Skill QA and durable continuity

Skill Contract v1 retains single-line name/description frontmatter and nonempty sections for
purpose, positive triggers, exclusions, scope/inputs, process/procedure, verification,
failure/escalation and output contract. Supporting links are optional and repository-local.
`python scripts/project.py skill check [name] --format json` reports ERROR/WARNING/INFO;
`python scripts/project.py skill eval <name> [--case <id>] [--results results.json]` checks
lexical include/exclude fixtures in `.agents/skills/<name>/evals/cases.json` and scores
external boolean observations with evidence. Trigger tests do not prove model routing.
External results use schema 1, skill, variant (with-skill/without-skill), and cases keyed by ID;
each criterion maps to passed (boolean) and evidence (string). Missing criteria score zero.

`python scripts/project.py checkpoint Wxxx [--state state.json] [--dry-run]` accepts exactly
objective, files, decisions, validation, risks, questions, next_step. Objective/next_step are
short strings; others are lists of summaries (files are relative paths). Store durable facts,
never reasoning, transcripts, raw logs or secrets. Resume returns compact current-work context
with warnings when HEAD, tracked contents, referenced files or work status changed. Code/tests/
config and accepted decisions always outrank checkpoints. DONE items are not actionable.
Checkpoint files live in `docs/work/checkpoints/`; explicit `--replace` is required to overwrite.

## Optional local hooks

Hooks are disabled by default and require explicit user activation. AgentReady does not change
global agent configuration. `python scripts/project.py hooks list`, `hooks inspect <name>`,
`hooks configure <name>`, `hooks enable <name> --dry-run`, `hooks enable <name>`, `hooks status`
and `hooks disable <name>` provide the local lifecycle. Every configuration mutation supports
preview. `safe-shell` supports warn/block, excluded rule IDs and protected branches. A host or
developer explicitly calls `hooks check "<command>" [--branch <name>]` and honors the exit status;
the tool never runs commands and is not a shell security sandbox. No host callbacks are installed.
`evidence-recorder` ingests an explicit `hooks record "<command>" --exit-status <n> --work Wxxx`:
only executable name, status, UTC timestamp and work ID are stored, with source external-report.
Arguments, output and environment are discarded. Records are caller assertions, not execution
proof. Completion interception is deferred until a concrete host callback is supported.
`docs/agent/hooks.json`, `docs/work/evidence/`, and checkpoints are project-owned and survive detach.

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

Select one READY item, or continue an accepted IN_PROGRESS item, from [the work registry](../work/index.md), inspect its Type, then use the
matching skill or fallback above. Load only relevant standards: [Python](standards/python.md),
[architecture](standards/architecture.md), [testing](standards/testing.md),
[dependencies](standards/dependencies.md), [documentation](standards/documentation.md), or
[security](standards/security.md). If blocked, record the blocker, transition to BLOCKED, and stop.

Use `python scripts/project.py context --next` for the deterministic next-READY route, or
`python scripts/project.py context W003` for an explicit item. The command returns paths and
metadata, not full document contents or an implementation plan. `python scripts/project.py status`
is a read-only overview. If scripts are unavailable, use this index and the work item directly.

`python scripts/project.py route <TYPE> --complexity LOCAL` extends these same routes with
explicit complexity/risk recommendations. `route --help` lists supported inputs; no worker or
provider is launched. See [context efficiency](standards/context-efficiency.md) for host guidance.
