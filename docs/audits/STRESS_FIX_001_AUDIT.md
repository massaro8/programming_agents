# STRESS-FIX-001 Audit

## Objective

Repair architectural repository knowledge coverage and bounded diagnostics identified by the
completed generic application stress campaign. No redesign or new operational policy.

## Input stress-test evidence

The supplied STRESS-FIX-001 request records A006: `platform/sqlite.py` existed while the map
reported platform absent. The campaign recommendation was APPLY_SMALL_VALIDATION_FIX; its
20 work items, 84 tests, scale exercise and post-detach development remain the evidence for
broader application behavior. This milestone does not repeat that campaign.

## Scope accepted

Normalized structural discovery; compact map rendering; independent Doctor coverage;
profile seed correctness; actionable card/record diagnostics; concise maintenance/resource
guidance; targeted regressions, fresh contexts, installed wheel and detach qualification.

## Explicitly rejected scope

Human-review/approval/autonomy policy was not changed. No new states, framework, dependency,
ORM, migration system, generic resource manager, telemetry or mandatory service.

## A006 root cause

Before implementation, the traced generator `scripts/generate_codebase_map.py.jinja`
enumerated immediate directories under platform/shared using `path.is_dir()` exclusively.
Flat Python responsibilities were discarded. Its `--check` compared the map to `render()`;
therefore a renderer omission was considered fresh. Doctor did **not** regenerate Markdown:
`doctor/codebase_map.py` independently enumerated capability directories and nested adapter
files, but had no coverage expectations for platform/shared or entrypoint responsibilities.
Thus different validators still shared a coverage gap. Architecture validation independently
walked Python sources and inspected import directions with AST; it did not consume the map.
Module knowledge independently enumerated capability directories and checked five-line cards
(a heading and four fields).
These were duplicated partial inventories, not one complete normalized model.
The architecture checker classifies business layers from directory path segments and reads
cross-module public contracts from `application/__init__.py`; technical flat files are classified
by their platform/shared/entrypoint parent bucket. This milestone preserves that enforcement
contract rather than extending business-layer import semantics.

## Repository inventory model

`core/inventory.py` owns deterministic stdlib discovery. Generation exports the same source
as `scripts/repository_inventory.py` through a bundled Jinja template. No generated project
imports AgentReady. The inventory returns paths grouped as capabilities, entrypoints,
platform/shared responsibility roots and test files. It ignores private responsibility helpers,
caches and build areas and rejects symlinks/junctions during source traversal.

SOURCE TRUTH is actual structure plus project-owned cards/contracts. NORMALIZED INVENTORY
models that structure. GENERATED KNOWLEDGE is the map/index. VALIDATION compares architectural
coverage to source truth independently of presentation. The exported inventory is shared
mechanism; Markdown generation is never the coverage oracle.

## File vs package semantics

Immediate public Python files and source-containing directories represent responsibility
roots equivalently. Namespace-style `platform/http/client.py` is represented by its `http`
root, not every file. Capabilities retain the existing `modules/<capability>/` policy.
Supported module layer files/packages remain visible. No automatic conversion is performed.

## CODEBASE_MAP fix

The renderer consumes normalized inventory for capability, responsibility, entrypoint and
test discovery. Platform/shared list architectural paths; entrypoints list their responsibility
paths. Existing capability cards, application exports and adapter representation remain.
Nested private/helper files are not expanded into a full source listing.

## Independent Doctor coverage validation

Doctor checks actual responsibility paths in their expected map sections, capability membership,
layer coverage, adapters and test root. It does not run project scripts or import project code.
The structural profile artifact check remains based on the canonical profile contract.

## Avoiding shared-renderer false confidence

The mandatory negative regression edits a generated renderer to omit the flat SQLite path,
regenerates its incomplete map and proves `--check` succeeds while Doctor fails. This models
internally consistent but factually incomplete knowledge rather than ordinary stale output.

## Profile-aware inventory

Actual optional responsibilities are discovered in every profile; no application-only bucket
is required for minimal. `ProfileContract.required_paths` remains the source of required seed
structure; Doctor also validates the profile marker. The seeded minimal profile has no
capability card or entrypoint directory. Application/service retain their existing boundaries.

## Profile seed correction

The greeting card describes the console adapter only in service, with no sibling-profile
explanation in application. Exact five-line grammar is preserved.

## Module-card diagnostics

Unexpected/missing/duplicate fields, contract ordering, empty values and malformed test references
receive specific errors and compact grammar guidance. Cards remain project-owned and are never
automatically rewritten.

## Work-record diagnostics

Strict values list actual allowed choices and the received value, pointing explanations to
the implementation record. Existing heading-level checks are preserved and covered with negative
fixtures; missing completion evidence remains invalid.

## Maintenance no-change clarification

The existing skill/workflow now explicitly permit evidence-backed inspection with no code
change; record verification, dependency/tool state and implementation outcome, then finish
the existing lifecycle. No synthetic diff is required.

## External-resource ownership guidance

The existing architecture standard owns concise creation, transaction, release, transfer,
reuse and failure responsibilities. A small transaction-context example distinguishes exiting
a context from closing the caller-owned connection. No infrastructure abstraction was added.

## Regression fixtures

`test_stress_inventory.py` covers file/package responsibilities, nested source roots, private
helpers/caches, normal drift and the fresh-but-incomplete renderer negative case across profiles.
Focused diagnostics/guidance tests cover the bounded requirements. Existing architecture negatives
and wheel/detach suites are retained.

## Fresh-agent FEATURE result

Fresh Luna context received only workspace environment plus "Implement the next READY work
item." The final pristine fixture had a fully filled approved application FEATURE specification
and extended GreetingService with ordered batch greetings,
preserving single greetings, configured prefix and invalid-name behavior. The context found
the existing capability, updated its card, added tests, completed DONE and synchronized records.
Four behavior tests, project check and verify passed without coordinator intervention. An earlier
fixture had detected intermediate diagnostic formatting errors; template repairs and tooling
refresh qualified that earlier implementation through bootstrap, verify and package-check too.
Only the final fresh run against stable tooling is used as the formal cold-context result.

## Fresh-agent DOCS result

An initial harness used FEATURE placeholder replacements against a DOCS template, leaving its
normative fields unfilled (TEST_BUG); that run was excluded from formal qualification. The repaired
fixture contains a complete approved READY DOCS specification grounded in existing code.
A separate fresh Luna context received only environment plus the same next-READY instruction.
It documented the Hello default and actual configuration/CLI behavior, executed the custom-prefix
example (`Welcome, Ada!`), completed DONE/sync, and passed verify plus the final check. Source files
(13) and pyproject.toml were byte-equivalent to pristine generation after this documentation work.

## Packaged-wheel qualification

PASS for minimal/application/service. The full suite builds and installs AgentReady wheels in
isolated environments outside the checkout, generates all three profiles, bootstraps them and
validates ownership, reproducibility, Doctor, local gates, package smoke and absence of AgentReady
from generated runtime/development dependencies. The formal detach qualification adds flat
`platform/sqlite.py` to application/service generated from installed artifacts and verifies map
regeneration and healthy Doctor before detach. No template/package-data omission was found.

## Detach / post-detach result

PASS for all three profiles. Snapshot comparison proves detach removes only `.agentready`
metadata and preserves other files. Local bootstrap/check/verify, status, context, registry,
skills and package-check work after detach. Application/service then add synthetic flat
`platform/cache.py`: stale-map validation fails, local sync represents it, and project check
passes. The AgentReady tool environment is removed and development/build gates still pass.
Neither AgentReady dependencies nor `.agentready` recreation were introduced.

## Full gate results

Final product gates:

| Command | Result |
| --- | --- |
| `uv sync --all-groups` | PASS; 30 resolved/audited packages |
| `uv run ruff format --check .` | PASS; 89 files formatted |
| `uv run ruff check .` | PASS |
| `uv run mypy src` | PASS; 17 source files |
| `uv run pytest -q` | PASS; 181 passed, 4 skipped in 1776.62 seconds |
| `uv build` | PASS; source distribution and wheel |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git diff --check` | PASS |

Targeted final checks also passed: inventory plus no-change maintenance (8 tests), strengthened
flat/package SQLite map integration (1 test), diagnostics including prose values/test roots
(3 tests), and final resource/profile guidance (6 tests). Changes made while the full run was
active were confined to diagnostic wording/valid test-root forms and documentation/stronger
test assertions; their final forms received separate targeted runs. Core inventory and Doctor
logic were stable before the final full run.

Intermediate lint/type errors were IMPLEMENTATION_FAILURE and repaired.
Profile card rendering introduced an extra blank line: IMPLEMENTATION_FAILURE, addressed by
Jinja whitespace trimming and a generated-card regression. Generated diagnostic script formatting
and export trailing-newline issues were IMPLEMENTATION_FAILURE, repaired using the generated
project's line-length contract; subsequent maintenance bootstrap/check passed. Assertions coupled
to line wrapping and the malformed initial DOCS harness were TEST_BUG, corrected without weakening
semantic assertions. An early full run was interrupted after detecting intermediate tooling
issues; only the final completed run is a qualification gate. A collection preview pipeline
closed stdout early (ENVIRONMENT_FAILURE); it did not affect test execution. Expected negative
fixtures are not failures. No unresolved substantive failure remains.

## Architecture invariants preserved

Stdlib repository-local tooling; no runtime AgentReady dependency, account/backend requirement,
new production dependency or architecture framework. Existing ownership and detach rules remain.

## What was intentionally NOT changed

Approval/autonomy, work types/states, skill taxonomy, module/profile architecture, dependency
philosophy, context routing and detach contract.

## Known limitations

Structural coverage is deliberately architectural, not a complete semantic code index. Linux
execution is unavailable in this Windows session. Four real-symlink fixtures were skipped because
Windows returned WinError 1314 (insufficient creation privileges): two detach fixtures, one Doctor
fixture and one generation-target fixture. Junction rejection tests passed, including the new
inventory layer guard. Results are local qualification; no remote CI run was triggered.

## Recommendation

STRESS-FIX-001_COMPLETE

READY_FOR_BROADER_REAL_USE

FREEZE. A006 is fixed at the inventory abstraction and independent coverage prevents renderer
self-consistency from certifying incomplete knowledge. All bounded acceptance checks passed;
the existing campaign remains the evidence for broader application behavior. No additional
hardening cycle is justified by this evidence.

## SOL design review and final decision

The inventory treats public files and source-containing packages consistently and contains no
Markdown. Doctor independently interprets structural coverage, including literal application
exports, rather than calling render. Required profile seed paths remain owned by ProfileContract;
minimal gains no application-only requirements. Sorting makes output deterministic. Traversal is
limited to source responsibility areas and tests, excluding caches/build output and rejecting
linked boundaries; it does not scan work records or the entire repository per responsibility.
The existing 32-card determinism fixture remains the representative scale guard; no timing claim
or new benchmark threshold is made. Exported stdlib tooling works without AgentReady after detach.
The model is a small immutable inventory and source primitives, not a generic indexing framework.

1. A006 is fixed by responsibility discovery, with no SQLite-name special case.
2. Flat files and packages both represent technical/shared responsibilities.
3. The compromised-renderer regression proves Doctor rejects incomplete but fresh output.
4. The map remains compact: responsibility roots, existing capability/public surfaces and selected tests.
5. Profile rendering remains proportional; no new seed buckets are imposed.
6. Diagnostics name grammar/value problems while retaining strict validation.
7. Resource guidance adds lifecycle reasoning without infrastructure.
8. Fresh FEATURE/DOCS qualification passes; wheel/detach final results are recorded in their sections.
9. No evidence supports an automatic additional hardening cycle; freeze once qualification passes.

## Product change summary

Every changed product/template/documentation file is accounted for below. Tests are separately
classified TEST. No production dependency or unrelated implementation was changed.

| File | Classification | Purpose |
| --- | --- | --- |
| `src/agentready/core/inventory.py` | AUTOMATION | Canonical source inventory and literal public exports |
| `src/agentready/core/profiles.py` | AUTOMATION | Shared ownership of standalone inventory tooling |
| `src/agentready/render/generator.py` | AUTOMATION | Export canonical inventory source into independent projects |
| `src/agentready/doctor/codebase_map.py` | VALIDATION | Independent architectural knowledge coverage |
| `src/agentready/doctor/inspector.py` | DIAGNOSTIC | State architectural coverage and incomplete-map finding |
| `src/agentready/templates/python/template/scripts/repository_inventory.py.jinja` | AUTOMATION | Standalone inventory export without runtime dependency |
| `src/agentready/templates/python/template/scripts/generate_codebase_map.py.jinja` | AUTOMATION | Render files/packages and entrypoints from inventory |
| `src/agentready/templates/python/template/scripts/module_knowledge.py.jinja` | DIAGNOSTIC | Shared module discovery and actionable strict card grammar |
| `src/agentready/templates/python/template/scripts/work_registry.py` | DIAGNOSTIC | Actual enum choices, received values and completion locations |
| `src/agentready/templates/python/template/docs/generated/CODEBASE_MAP.md.jinja` | AUTOMATION | Seed entrypoint coverage matching the renderer |
| `src/agentready/templates/python/template/docs/modules/greeting.md.jinja` | GUIDANCE | Profile-accurate seed boundaries |
| `src/agentready/templates/python/template/docs/agent/standards/architecture.md.jinja` | GUIDANCE | Concise external-resource ownership example |
| `src/agentready/templates/python/template/docs/agent/standards/module-placement.md.jinja` | GUIDANCE | File/package choice and compact card/test-root grammar |
| `src/agentready/templates/python/template/docs/agent/workflows/maintenance.md` | GUIDANCE | Evidence-backed no-change completion |
| `src/agentready/templates/python/template/.agents/skills/maintenance/SKILL.md` | GUIDANCE | Same bounded maintenance clarification; adapter still generated |
| `docs/ARCHITECTURE.md` | GUIDANCE | Inventory/knowledge trust contract |
| `docs/generated/CODEBASE_MAP.md` | AUTOMATION | Regenerated product navigation for added files |
| `docs/audits/STRESS_FIX_001_AUDIT.md` | GUIDANCE | Evidence, qualification and scope accounting |
| `tests/test_init.py` | TEST | Ownership expectation for new shared script |
| `tests/test_generated_project.py` | TEST | Installed artifact ownership parity |
| `tests/test_detached_project.py` | TEST | Installed-wheel flat source coverage and post-detach cache/map/check |
| `tests/test_stress_inventory.py` | TEST | Normalized matrix, gaps, compromised renderer and junction guard |
| `tests/test_stress_diagnostics.py` | TEST | Malformed cards, test roots, prose enums and missing evidence |
| `tests/test_stress_guidance.py` | TEST | Profile/card freshness and stable guidance anchors |
| `tests/test_stress_maintenance.py` | TEST | Full no-code-change lifecycle and byte-preservation evidence |
