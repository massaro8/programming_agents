# FLOW-001 audit — Generated Project Feature Registry & Work Intake

## OBJECTIVE

Give every generated Python project a small repository-native ledger that captures what to build,
selects one ready feature at a time, and remains fully usable after AgentReady is detached.

## PROBLEM FIXED

AgentReady's own repository had a feature-specification concept, but generated repositories lost
it. Generated projects now separate engineering procedure under `docs/agent/` from project work
under `docs/features/`; the user's prompt no longer has to carry the engineering system.

## FEATURE SOURCE-OF-TRUTH MODEL

Individual `docs/features/F*.md` files are authoritative. `docs/features/index.md` is an exact,
deterministically regenerated view and is marked do-not-edit. A fresh project has the template,
empty index, and utility but no fabricated feature. Later specifications are ordinary project-owned
files and are not added to AgentReady maintenance metadata.

## FEATURE FORMAT

A specification starts with `# FNNN — Title`, a blank line, and `Status: STATUS`. Its deterministic
filename is `FNNN-ascii-title-slug.md`. The compact body records objective, requirements,
scope/non-goals, acceptance criteria, verification, implementation result, files, dependencies,
verification result, important design decision, deviations, follow-up candidates, and blocker/next
action.

## STATUS MODEL

The only statuses are `BACKLOG`, `READY`, `IN_PROGRESS`, `BLOCKED`, and `DONE`. Generated guidance
requires `DONE` only after acceptance criteria and gates pass. Blocked work records the external
decision/dependency and stops.

## FEATURE ID MODEL

IDs are positive, canonically padded, monotonically allocated values (`F001`, `F002`, ...). The
next ID is one greater than the highest existing numeric ID; gaps are never silently reused.
Filename ID, header ID, and deterministic title slug must agree. Duplicate numeric IDs fail.

## REGISTRY UTILITY

`scripts/feature_registry.py` is a Python-standard-library-only project file with no Git, AgentReady,
Copier, Jinja, network, database, or remote-service dependency.

### sync

Parses and validates specifications, sorts them by numeric ID, and atomically rewrites the exact
index. Repeated sync is byte-identical.

### check

Read-only validation of IDs, status, metadata, filename/header/slug agreement, duplicates, and exact
index content. Drift or malformed specifications return non-zero.

### next-id

Prints max-existing-ID plus one, or `F001` for an empty registry.

### next-ready

Prints the first `READY` ID in numeric order. It prints `NO_READY_FEATURE` successfully when no work
is ready and never selects BACKLOG or BLOCKED work.

### optional new command decision

`new TITLE [--status BACKLOG|READY]` was included because it removes safe mechanical work without
inventing requirements. It exclusively creates the next canonical file, populates only template
prompts and metadata, and synchronizes the index. BACKLOG is the default.

## GENERATED INDEX

The generated index contains a warning and an ID-ordered table linking each specification. The
fresh representation says `No features registered.`. Its content is derived solely from specs.

## AGENT ROUTING CHANGES

`AGENTS.md` adds only a short routing rule. `docs/agent/index.md` explains HOW versus WHAT, includes
the two minimal prompt forms, routes through the registry, and warns agents not to read every spec.

## FEATURE WORKFLOW CHANGES

Direct requests are captured faithfully, clarified or blocked when essential information is
missing, then marked READY. Existing work uses `next-ready`. The workflow performs understand,
localize, impact, verification planning, IN_PROGRESS, minimum implementation, targeted and full
gates, diff review, implementation record, DONE, sync, check, and stop. It never starts a second
feature or implements follow-up candidates opportunistically.

## OWNERSHIP

- SHARED: `docs/features/template.md`, `scripts/feature_registry.py`.
- GENERATED: `docs/features/index.md`.
- PROJECT_OWNED: later `Fxxx-*.md` specifications, outside the static manifest.

The existing taxonomy is unchanged, and GENERATED still does not mean delete-on-detach.

## MANIFEST IMPACT

The three common initial artifacts are recorded in every profile's deterministic initial manifest.
No dynamic manifest update is required when project work creates feature specifications.

## DOCTOR IMPACT

Doctor adds one `features.registry` finding to the existing human/JSON path. A trusted internal
minimal equivalent parser validates specs and exact index content without importing, invoking, or
synchronizing the project-local script. Inspection remains read-only and schema-1 compatible.

## DETACH SURVIVAL

Detach semantics are unchanged: only `.agentready/` is removed. The template, utility, generated
index, and project feature files remain. `check`, `sync`, `next-id`, and `next-ready` continue using
only repository-local files and the Python standard library.

## ALL PROFILE QUALIFICATION

The feature foundation is common to `minimal`, `application`, and `service`. Existing packaged-wheel
and formal detach harnesses run registry `check` before and after detachment for each profile, in
addition to normal sync, Ruff, mypy, pytest, build, doctor, and independence checks.

## TESTS

Focused tests cover the empty registry, max-plus-one allocation, deterministic/idempotent sync,
READY selection, no-work output, `new`, lifecycle transitions and record updates, malformed status
and metadata, duplicates, filename/header/slug disagreement, index drift, no-Git operation, doctor
parity, and detach survival. Exact-tree and ownership fixtures include the foundation.

## BACKWARD COMPATIBILITY

CLI generation/profile syntax, default `minimal` behavior, greeting behavior, doctor JSON schema,
and detach deletion boundary are unchanged. Newly generated repositories gain three common files
and one doctor finding. Existing pre-FLOW generated repositories require regeneration/adoption of
the foundation before the new doctor contract can report healthy; automatic migration is out of
scope.

## KNOWN LIMITATIONS

- Utility and doctor intentionally contain small parallel parsers; shared valid/invalid fixtures
  and full qualification guard against drift.
- No cross-process registry lock is introduced; exclusive feature creation and atomic index replace
  prevent silent overwrite, but concurrent commands should still be avoided.
- The ledger does not prioritize, schedule, or assign work.

## DEFERRED

- Jira, GitHub Issues, Notion, and other remote integrations
- databases, SQLite, server state, telemetry, and multi-user project management
- prioritization algorithms and automatic product-requirement generation
- LLM calls or Git-backed feature state

## VERIFICATION STATUS

Coordinator review and gates completed on 2026-09-22:

- `uv sync --all-groups` — passed;
- `uv run ruff format --check .` — 70 files already formatted;
- `uv run ruff check .` — passed;
- `uv run mypy src` — passed for 14 source files;
- targeted registry/init/doctor/doctor-JSON/detach suite — 68 passed, 4 Windows
  privilege-dependent symlink skips;
- packaged independent generation qualification — passed for `minimal`, `application`, and
  `service`, including registry check;
- formal pre/post-detach qualification — passed for all three profiles, including registry check;
- `uv run pytest` — 88 passed, 4 Windows privilege-dependent symlink skips;
- `uv build` — sdist and wheel built successfully;
- `uv run python scripts/generate_codebase_map.py --check` — current;
- `git diff --check` — passed.

The OpenRouter feature is prepared only as the UC-01 prompt. No product-repository F001 was created
and the practical feature was not executed.

Final readiness state:

```text
READY_FOR_REPOSITORY_DRIVEN_UC01
```

FLOW-001_COMPLETE
