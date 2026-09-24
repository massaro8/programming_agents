# HARDEN-001 audit — Python architecture and agent workflow hardening

## OBJECTIVE

Make generated Python repositories structurally clear, easy to prepare, economical for coding
agents to navigate, and independently useful after AgentReady is detached. UC-01 implementation is
outside this milestone.

## RESEARCH/ARCHITECTURE RATIONALE

The existing product still uses bundled Copier for trusted rendering, with hooks disabled. The
hardening adds no proprietary renderer or runtime framework. The current
[Codex skill documentation](https://learn.chatgpt.com/docs/build-skills) and
[Claude skill documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
support repository-local `SKILL.md` files with frontmatter; the generated project uses
provider-specific discovery locations but keeps normative policy in `docs/agent/`.

Import Linter [supports static layered import contracts](https://import-linter.readthedocs.io/en/v2.9/contract_types/layers/).
For this version, the optional, dynamically
named capability modules and the limited known inversion rules do not justify another development
dependency or a fixed contract for every future module. A stdlib AST checker enforces safe, direct
inversions and structural constraints. This is a scoped inference, not a claim that the checker
proves arbitrary transitive dependency direction.

## MODULE PLACEMENT MODEL

`docs/agent/standards/module-placement.md` is the generated decision tree. Capability code belongs
under `modules/<capability>/`; domain, application, and adapter subdirectories are added only as
needed. Thin driving interfaces belong in `entrypoints/`, composition in `bootstrap.py`, configuration
in `config.py`, genuinely cross-module technical infrastructure in `platform/`, and stable
domain-neutral primitives in the deliberately small `shared/`. Work IDs do not define modules.

## PROFILE DIFFERENCES

`minimal` keeps a small root package and an explicit trigger for migrating when unrelated
capabilities accumulate. `application` and `service` use the module-first pattern. `service` adds an
example external adapter without adding a web, database, messaging, or telemetry framework.

## DEPENDENCY DIRECTION

Domain logic must not import application orchestration, adapters, entrypoints, composition,
configuration, or platform code. Application orchestration must not import adapters, entrypoints,
composition, configuration, or platform code. Adapters and entrypoints may depend inward; the
checker examines direct imports only. Tests mirror useful capability boundaries without generating
empty category trees.

## ARCHITECTURE ENFORCEMENT

Generated `scripts/architecture_check.py` rejects unexpected Python files at the package root,
global services/models/repositories/utils/helpers buckets, and known inward import inversions for
application/service. The minimal profile is deliberately exempt from module-first placement. The
checker does not reject domain-local filenames such as `models.py`.

## CODEBASE MAP

Generated `docs/generated/CODEBASE_MAP.md` summarizes entrypoints, capability modules, adapters,
tests, and commands. `scripts/generate_codebase_map.py` regenerates it or checks exact freshness
without AgentReady or its manifest. The product's read-only doctor independently checks the
material module/adapter inventory; project verification checks the full generated file.

## BOOTSTRAP MODE

Normal `agentready init` remains generation-only. Explicit `--bootstrap` checks for `uv`, performs
`uv sync --all-groups`, requires `uv.lock`, checks the work registry and architecture, and runs the
read-only doctor. A named failure returns nonzero and leaves the generated repository available for
inspection and repair. No template hook or remote script is executed by AgentReady.

## PROJECT-LOCAL TASK RUNNER

The stdlib `scripts/project.py` offers `bootstrap`, `check`, and `verify`. It delegates package
management to `uv`; check runs registry, architecture, format, lint, typing, and tests; verify adds
build and codebase-map freshness. The runner is repository-local and survives detach.

## TOKEN/CONTEXT POLICY

The canonical context waterfall starts with the work item and `AGENTS.md`, then the routing index,
selected specification and workflow, codebase map, search localization, affected implementation,
and neighboring tests. Search precedes broad reading. Compaction retains decisions, boundaries,
files, validation state, and open risks, not verbose exploration history.

## SUBAGENT POLICY

Direct work is preferred for local tasks. Read-only exploration or independent review may be
delegated when useful; bounded mechanical work may use a faster builder; cross-module/high-risk
work receives stronger coordination. Repeated failures escalate rather than producing patch loops.
Concurrent write-heavy work needs isolated ownership, and handoffs use the nine-field contract.

## SKILL MODEL

Eight small capabilities route repeatable workflows: repo-explore, module-placement,
feature-builder, bug-investigation, refactoring, maintenance, documentation, and security-review.
Each skill has a trigger, stable input, canonical-doc pointer, and verifiable completion condition.

## CODEX SKILLS

Project-local `.agents/skills/<name>/SKILL.md` files provide Codex discovery and thin control
planes. The generated root `AGENTS.md` remains the public instruction entry point.

## CLAUDE SKILLS

Project-local `.claude/skills/<name>/SKILL.md` files expose equivalent routing without duplicating
the methodology. Optional Claude subagents were deferred: they would add provider-specific
definitions before a demonstrated need and are not necessary for skill discovery.

## FALLBACK WORKFLOWS

Agents without native skill loading can follow the type-matched `docs/agent/workflows/` document.
Skills do not alter normative intent or make the repository dependent on a provider.

## WORK-ITEM ROUTING

FEATURE, BUGFIX, REFACTOR, MAINTENANCE, DOCS, and SECURITY map to their corresponding skills and
workflows. Unfamiliar ownership invokes repo-explore; new or moved modules invoke module-placement.
Only a human may author/approve normative requirements and mark BACKLOG as READY. Agents execute
the existing READY → IN_PROGRESS → DONE/BLOCKED lifecycle and synchronize records.

## DOCTOR IMPACT

Doctor remains local, deterministic, read-only, and non-executing. Profile ownership checks cover
the generated tooling and guidance. Its map check detects missing/stale module and adapter entries
without importing or running generated code; full byte freshness belongs to project verification.

## DETACH SURVIVAL

Only `.agentready/` maintenance metadata is removed. The source, tests, guidance, skills, map,
work registry, architecture checker, project runner, lockfile, CI, and normal commands remain
independent of AgentReady.

## OWNERSHIP

Source, tests, README, architecture, work specifications, and later ADRs are PROJECT_OWNED.
Guidance, skill adapters, work templates, and project scripts are SHARED. The codebase map, work
index, and changelog index are GENERATED. No new ownership class was introduced.

## PROFILE QUALIFICATION

Each of minimal, application, and service passed isolated wheel generation and generated-project
qualification (`tests/test_generated_project.py`: 3 passed). All three also passed real opt-in
bootstrap with lockfile, healthy doctor, and project verification (`tests/test_bootstrap.py`: 8
passed, including failure controls). Normal generation/manifest tests passed (20 passed, one
Windows symlink test skipped). Formal post-detach qualification passed on all three profiles
(`tests/test_detached_project.py`: 3 passed), including project-local bootstrap, check, and verify
without the AgentReady tool environment.

## NEGATIVE CONTROLS

Architecture tests reject package-root feature code, global dumping grounds, and forbidden direct
imports while accepting a correctly placed capability. Doctor tests detect stale map inventory and
confirm inspection does not mutate the project. Bootstrap tests cover missing/failing `uv` and
repository preservation.

## PACKAGED QUALIFICATION

The isolated wheel qualification passed for minimal, application, and service. It builds a wheel,
installs it outside the source checkout, generates two byte-identical projects per profile, checks
ownership and skills, and runs the generated CI command through `project.py verify`.

## FULL REGRESSION

`uv run pytest -q` passed: 111 passed, 4 skipped in 24m12s. The four skips are Windows
symlink-privilege limitations, not test failures. The final `uv sync --all-groups`, Ruff format
and lint, `mypy src`, `uv build`, product codebase-map `--check`, and `git diff --check` gates all
passed. The 16 generated skill folders passed the skill validator.

## KNOWN LIMITATIONS

The AST checker is intentionally structural and direct-import based; it does not prove transitive
layering or semantic ownership. Doctor's independent map inspection covers material module/adapter
inventory, while exact content freshness is enforced by `project.py verify`. Bootstrap may access
the network through normal `uv` dependency resolution only when explicitly requested.

## DEFERRED

UC-01/OpenRouter implementation, additional framework profiles, adopt/update, backends, telemetry,
and provider-specific subagent definitions are outside HARDEN-001.
