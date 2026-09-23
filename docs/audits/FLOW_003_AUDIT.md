# FLOW-003 audit — Unified work lifecycle

## OBJECTIVE

Replace generated-project feature-only governance with a unified repository-native work lifecycle,
deterministic changelog, and documentation impact evaluation.

## WHY FEATURE REGISTRY WAS GENERALIZED

The prior F-prefixed registry represented only feature work. A single W sequence now represents
features, bugs, refactors, maintenance, documentation, and security work with a shared lifecycle.

## WORK ITEM MODEL

Specifications live in `docs/work/Wxxx-safe-title.md`. Humans own normative requirements; the
implementing agent owns status execution and the implementation record. An unmet requirement is
recorded as a blocker and stops implementation.

## WORK TYPES

- FEATURE — new capability
- BUGFIX — established behavior correction
- REFACTOR — internal structure with behavior preserved
- MAINTENANCE — tooling, dependencies, CI, packaging, or repository operations
- DOCS — documentation work
- SECURITY — defensive security work, treated as high risk

## ID MODEL

IDs are global, monotonically allocated W001, W002, and so on. They are independent of type.

## STATUS MODEL

BACKLOG, READY, IN_PROGRESS, BLOCKED, and DONE remain the complete status set. The local utility
supports READY → IN_PROGRESS, IN_PROGRESS → DONE/BLOCKED, and BLOCKED → IN_PROGRESS. Human approval
of READY remains a manual action.

## HUMAN / AGENT OWNERSHIP BOUNDARY

Normative sections are project-owned. The agent updates implementation evidence, documentation
impact, and changelog fields without rewriting requirements. `.agentready/` remains removable.

## TYPE-SPECIFIC TEMPLATES

Six concise templates provide type-specific normative sections, a common implementation record,
documentation impact fields, and changelog fields. BUGFIX additionally records confirmed root cause
and regression test.

## REGISTRY CLI

`scripts/work_registry.py` is stdlib-only and independent of AgentReady, Copier, and Jinja at runtime.
It provides sync, check, next-id, next-ready, list, new, and transition operations. Work index and
changelog are deterministically generated; invalid DONE records are rejected.

## CHANGELOG MODEL

Completed work items are the source of truth. `docs/changelog/index.md` lists DONE items in reverse
ID order with type, title, summary, and a breaking marker. No timestamps or machine paths are
generated.

## DOCUMENTATION IMPACT MODEL

Every item evaluates README, architecture, ADR, and other documentation impact. Registry validation
requires evaluated values before DONE; it does not write user documentation.

## README POLICY

Generated README provides developer navigation. Ongoing README changes are semantic and occur only
when the work item warrants them.

## ARCHITECTURE POLICY

Update architecture documentation for material boundary, dependency direction, runtime, integration,
persistence, entrypoint, or cross-cutting changes.

## ADR POLICY

`docs/adr/0000-template.md` is shared. Subsequent ADRs are project-owned and reserved for
architecturally significant, difficult-to-reverse decisions.

## AGENT ROUTING

Compact AGENTS.md points to `docs/agent/index.md`. That routing index selects one workflow by Type
and links standards progressively by relevance.

## WORKFLOWS

Feature, bugfix, refactor, maintenance, documentation, and security workflows define the required
phase sequence. Security requires strong review before and after implementation.

## DOCTOR IMPACT

The read-only `work.registry` diagnostic validates paths, templates, metadata, DONE requirements,
and exact work/changelog index content using an internal parser. Doctor never executes the generated
project utility.

## OWNERSHIP

SHARED: work templates, registry utility, agent guidance, and ADR template. GENERATED: work and
changelog indexes. PROJECT_OWNED: work items, later ADRs, README, and architecture document.

## DETACH SURVIVAL

Detach removes only AgentReady maintenance metadata. Work items, indexes, changelog, templates,
guidance, ADRs, and local utility remain available after detach.

## MAIN-REPO DOGFOODING

Product scope and practical validation references use the unified work model. Historical FLOW-001/002
audits are retained as historical evidence. No AgentReady product W001 item was created.

## BACKWARD COMPATIBILITY

The pre-validation product intentionally removes `feature_registry.py` and `docs/features/`; previous
generated projects do not receive automatic migration or compatibility shims. Copier remains the
internal rendering engine.

## TESTS

Focused tests cover empty registry, all six templates, mixed IDs, filtering/list output, generated
indexes, invalid/duplicate metadata, both index drifts, DONE validation and no-write-on-invalid-DONE,
doctor findings, and detached utility survival. Existing generated profile, doctor, detach, and
packaged-wheel tests are updated for the new contract. On 2026-09-23, `uv run pytest -q` completed
with 97 passed and 4 skipped; the skipped cases require symlink privileges unavailable on this
Windows host.

## PACKAGED QUALIFICATION

The packaged-wheel qualification installed AgentReady in an isolated tool environment and generated
all three profiles (`minimal`, `application`, `service`). Each profile passed doctor, project gates,
build, mixed work creation, registry operations, detach, and post-detach registry checks without an
AgentReady runtime dependency. The separate `uv build` produced both sdist and wheel successfully.

## VERIFICATION STATUS

The required milestone gates completed on 2026-09-23:

- `uv sync --all-groups` — passed;
- `uv run ruff format --check .` — passed;
- `uv run ruff check .` — passed;
- `uv run mypy src` — passed for 14 source files;
- `uv run pytest -q` — 97 passed, 4 Windows symlink-privilege skips;
- `uv build` — sdist and wheel built;
- `uv run python scripts/generate_codebase_map.py --check` — current;
- `git diff --check` — passed (Windows LF→CRLF notices only).

## KNOWN LIMITATIONS

The registry checks structural completion, not the semantic quality of requirements or verification.
Human approval identity is not recorded. Older generated projects are not automatically migrated.

## DEFERRED

OpenRouter UC-01 implementation, update/adopt commands, external issue tracking, databases, telemetry,
and historical audit rewrites remain out of scope.
