# User guide

Generated `python scripts/project.py --help` lists every local capability; append `--help` to
work, route, skill, hooks, checkpoint or resume to see its options. None requires AgentReady
at application runtime. The root CLI additionally offers init, doctor and detach.

## Work and skills

Run `python scripts/project.py work new --type FEATURE "Add a capability"`, then fill the
created specification with scope and acceptance criteria. Once a human authorizes the scope,
author `Status: READY` in that record, run `work sync` and `work check`, then
`work transition W001 IN_PROGRESS`. The helper cannot approve BACKLOG. Accepted IN_PROGRESS
work may resume directly. Record results, verification, documentation impact and changelog before
DONE. Generated `docs/agent/workflows/feature.md` explains the complete lifecycle.
Replace all template placeholders with concrete evidence or the literal `NONE`. Evaluate README,
ARCHITECTURE and ADR impact explicitly: use `NOT_REQUIRED` when no change is needed, rather than
leaving `NOT_EVALUATED`. `work check` diagnoses incomplete records before a DONE transition.

`route FEATURE --complexity LOCAL --work-status READY` selects the existing skill and recommends
context, planning, validation and abstract FAST/BALANCED/STRONG effort. Risk signals, such as
`--risk-signal concurrency`, dominate small scope. Inputs are advisory, not proof of approval.
`skill check` validates local skill contracts; `skill eval --help` discovers lexical fixtures and
externally supplied behavioral observations. Fixture success alone is not proof of agent behavior.

## Context and sub-agents

Read AGENTS.md, follow CODEBASE_MAP, search before reading source, load relevant skills on demand,
and validate narrowly before broad gates. The design reduces unnecessary context/rework;
numerical token savings are unproven. Maps, routes and checkpoints are deterministic mechanisms;
reading discipline and model/worker choice belong to the host.

Use one read-only explorer for unfamiliar areas, parallel explorers only for independent domains,
and specialist review when risk warrants it. Avoid delegation for known local edits or typos.
Use compact handoffs rather than full transcripts. AgentReady neither launches nor controls models.

## Hooks and continuity

Hooks enabled by default: zero. `hooks list` lists local recipes; `hooks enable safe-shell --dry-run`
previews activation. Enabling a recipe does not install command interception or global configuration;
a host explicitly invokes its preflight. Generated `docs/agent/hooks/` contains the recipe contracts.

`checkpoint W001` saves bounded work state; `resume W001` returns context and staleness warnings.
Existing checkpoints require `--replace`; inspect current repository state before resuming.
See [skill QA and continuity](SKILL_QA_AND_CONTINUITY.md).

## Build, verify and detach

`python scripts/project.py build` builds the application; `verify` runs its gates and installed-wheel
package check. Doctor checks structure rather than executing tests. From the source checkout,
`uv run agentready doctor ../my-project` and `uv run agentready detach ../my-project` operate on
the generated repository. With a release wheel, use the same `uvx --from WHEEL agentready` prefix.
Detach removes only recognized `.agentready/` metadata; source, tests, CI and local tools survive.
See [detachment contract](DETACHMENT_CONTRACT.md).

## Recovery and retry

If bootstrap is interrupted, inspect the retained generated repository, resolve the reported
problem, and retry `python scripts/project.py bootstrap`. If generation itself was interrupted,
inspect the partial target and preserve any user edits; init only accepts missing/empty targets.
Generate into a separate empty directory for comparison rather than rerunning init over files.

If an update reports another writer, wait for that writer to finish and retry. After a crashed or
killed process, remove only the lock file named in the error, and only after confirming no writer
is still running. Active locks are never removed automatically. Run work registry mutations and
index synchronization sequentially; `next-id` is a suggestion, not a reserved ID.

For a malformed checkpoint, review the current work specification and state input before using
`checkpoint W001 --replace`. Restore malformed hook configuration from a trusted project backup
or correct it explicitly; commands do not silently reset it. Hook configure/enable/disable support
`--dry-run`; evidence recording does not.

If detach fails, run doctor to inspect the remaining metadata. Source, tests, CI and local tools
remain usable. When the manifest is still valid and the reported filesystem problem has been
resolved, retry detach. If a partial removal deleted the manifest, restore the original manifest
from a trusted backup before retrying; do not fabricate one or rerun init over the project.
