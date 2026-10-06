# AgentReady Feature Evolution Audit

## Executive verdict

PASS WITH NOTES. Local gates pass; four Windows symlink cases require unavailable privileges.
The limited preflight and external-observation boundaries below are intentional and documented.

## Baseline implementation map

- CURRENT CORE: argparse CLI; deterministic profile, project, ownership and inventory contracts.
- CURRENT SKILL MODEL: canonical `.agents/skills/*/SKILL.md`, rendered Claude views, standalone
  static skill checker and work-type routes. Existing frontmatter and procedure headings retained.
- CURRENT DOCTOR MODEL: ordered read-only PASS/FAIL findings; stable schema-1 JSON and exit parity.
- CURRENT WORK REGISTRY MODEL: stdlib Wxxx allocation, project-owned specifications, status
  transitions and generated work/changelog indexes. Root work templates existed without items.
- CURRENT OWNERSHIP MODEL: PROJECT_OWNED/SHARED/GENERATED lists in schema-1 manifests.
- CURRENT DETACH MODEL: fail-closed deletion exclusively inside `.agentready/`.
- CURRENT CLI PATTERN: argparse command dispatch; generated `scripts/project.py` is stable local
  development interface. No installed agent host lifecycle or completion callback.
- RELEVANT TEST INFRASTRUCTURE: pytest generation fixtures, standalone-script subprocess checks,
  doctor JSON/read-only checks, registry lifecycle and real wheel/install/detach qualification.

Verification was defined before editing: contract errors/advisories and reference safety; trigger
and external-result scoring; opt-in/config/preview/disable; durable checkpoints and staleness;
legacy manifests; generated commands; formal no-lock-in qualification and repository gates.
The baseline command was started before edits; its first five skill checks finished before
implementation. Its longer remaining cases overlapped development and are therefore also covered
by the final full-suite run rather than treated as an immutable baseline snapshot.

## Implemented

### Skill Contract

Existing SKILL.md format extended with purpose, positive triggers, exclusions and output headings;
existing scope/procedure/escalation/verification aliases remain supported. Source-repository and
bundled skills follow v1. Deterministic validation catches missing/empty structure, duplicates,
metadata size, invalid identity and unsafe/broken local references. Doctor composes the validator.
Individual QA issues have ERROR/WARNING/INFO; doctor retains schema-1 PASS/FAIL with explicit
severity in messages. Legacy contract omissions are advisory; invalid references remain errors.

### Skill Evals

Portable schema-1 JSON cases are shipped beside skills. CLI validates definitions, runs lexical
include/exclude fixtures, selects cases, ingests external observations with evidence and scores
criteria. With-skill/without-skill variants permit external comparisons. No provider calls or
agent runtime. Definition files are directly portable exports; no new export container.

### Hooks

Repository-local safe-shell and evidence-recorder recipes support list/inspect/configure/preview/
enable/status/disable. Every config mutation supports dry-run. Config is strict and fail-closed;
no arbitrary code or command is executed. Safety supports warn/block, named-rule exclusions and
protected branches. Evidence stores executable identity, reported status, work ID and UTC time;
arguments/output/environment are discarded and journal size is bounded.

DEFAULT ENABLED HOOKS: 0

GLOBAL USER CONFIG MODIFIED: NO

These recipes are explicitly invoked by a developer or existing host. No automatic agent callback
is installed; callers must honor preflight exit status. Completion interception is deferred because
there is no supported host callback, and agent adapters are expressly outside this scope.

### Work Continuity

Project-owned Wxxx JSON checkpoints store bounded durable summaries, current status, HEAD, file
hashes and tracked-content digest. Resume returns compact context and flags changed revision,
status/files/tracked contents, missing references and stale validation. Missing work is rejected;
DONE items are non-actionable. Replacement is explicit. Recognizable credentials are rejected;
no transcript, reasoning, raw log or shell-history capture is implemented.

### Extension Decision

EXTENSION SYSTEM: NOT JUSTIFIED

Only hooks need activation lifecycle; skills and checkpoints have distinct read/check/score or
create/resume operations. No independent versioning or outside maintained executable components
are required. Existing profile ownership, source-export rendering and doctor composition provide
the necessary seams; a component framework would add concepts without reducing actual duplication.
Revisit only for two real independently versioned capabilities sharing duplicated lifecycle logic.

## Core Impact

| Area | Impact |
| --- | --- |
| init | Additional shared stdlib scripts and eval fixtures; zero hooks/config activation |
| doctor | Four composed checks, read-only; JSON schema and existing keys unchanged |
| detach | Implementation unchanged; preserves useful tools and project-owned state |
| ownership | Additive shared artifacts; old manifests may omit them; no ownership reclassification |
| work registry | Existing Wxxx lifecycle and index generator reused; checkpoints outside specification |
| generated project runtime | No application dependency/import or service requirement added |

## Compatibility

Existing init/doctor/doctor JSON/detach commands remain. New capability commands are additive.
Doctor keeps schema 1 and status pass/fail; severity is explicit within its messages. Added check IDs
are documented. Legacy skills without eval artifacts have advisory v1 omissions. Existing manifests
do not need additive file declarations. New generated skill checks enforce bundled v1 contracts.
`--path` for capability commands precedes their remaining arguments.

## New dependencies

None.

## Tests / Gates

- Baseline: `uv run pytest tests/test_skill_contract.py tests/test_doctor.py
  tests/test_doctor_json.py tests/test_work_registry.py tests/test_detach.py -q`:
  69 passed, 3 skipped (Windows symlink privilege unavailable); overlap noted above.
- `uv run pytest`: 212 passed, 4 skipped in 2044.88 seconds. Includes unit, CLI, doctor/JSON,
  generation, package, work-registry and formal detachment qualification for all three profiles.
- `uv run pytest tests/test_skill_contract.py tests/test_evolution.py -q`: final run 37 passed in 47.61 seconds,
  including the protected-full-ref and native Windows exit-status regressions. This focused rerun occurred after the
  final hook fixes. The complete-suite session started before these localized changes; the final
  focused rerun covers the changed hook behavior and standalone exports. Other capabilities did
  not change. Across these runs all 217 current cases were
  covered (213 passed, 4 skipped), with overlap between the runs.
- `uv run ruff check .`: PASS.
- `uv run ruff format --check .`: PASS.
- `uv run mypy src`: PASS, 22 source files.
- `uv run python scripts/generate_codebase_map.py --check`: PASS.
- `uv build`: PASS, wheel and source distribution.
- `uv run agentready skill check --format json`: PASS, repository canonical contracts.
- Source repository evals: all four trigger definitions passed using `evaluate(root, name)`.
- Fresh standalone export probe: generated-project `ruff format --check .`, `ruff check .`,
  `python scripts/project.py skill check`, and `skill eval feature-builder`: PASS.
- Root work registry checked through its existing `read_work/sync/check/transition` implementation;
  work and changelog indexes are generated, never edited by hand.

One integration failure was localized to an import deferred until after a runpy test removed its
temporary scripts path. Moving imports to module loading restored the existing test contract.
This was corrected before the successful focused rerun; no broad refactoring was required.
The manifest expectation initially placed additive shared files ahead of existing files;
correcting its expected order preserved the actual append-only artifact order and passed its
targeted rerun before the successful complete suite. Final safety review reproduced a protected
push with `HEAD:refs/heads/main` and an explicitly supplied unprotected current branch. An optional
`refs/heads/` prefix in the matcher fixed it; regressions also preserve unprotected branch suffixes.
Recorder review also reproduced rejection of native Windows exit status 9009. Expanding the
bounded integer range to signed/unsigned 32-bit statuses fixes portable evidence ingestion;
the final focused run verifies that case and rejection of values outside native bounds.

## Detachment

Local config, evidence and checkpoint state live outside `.agentready/` and are project-owned.
Shared scripts export the identical stdlib implementation with local imports. Existing detach
code is unchanged. New regression compares all preserved bytes and invokes new tools after detach.
The formal generate/verify/detach/verify qualification passed for minimal, application and service.
The Detachment Contract remains satisfied: project verification and installed application smoke
tests work with AgentReady absent, and every retained repository artifact remains unchanged.

## Residual Risks

- Lexical fixtures do not measure model routing quality; external observations are caller assertions.
- safe-shell is a bounded preflight, not a shell parser/sandbox; host/developer must invoke it.
- Credential detection cannot recognize arbitrary opaque secrets in manually supplied summaries.
- Untracked files outside listed checkpoint paths are not covered by staleness hashes.
- Windows symlink tests require privileges unavailable on this host; junction boundaries have
  deterministic coverage, and CI remains authoritative.

## Deferred Ideas

Agent adapters, automatic host completion interception, external executable extensions, remote
registries/marketplaces, model-based eval runners and semantic/claude-mem memory integrations.

## Final Repository Status

`git diff --check`: PASS. 27 tracked files modified (448 additions, 6 deletions) and 32 new files. New files comprise the capability modules, portable exports/evals, work records/generated indexes, guide/audit and regression tests. Existing modifications are limited to capability wiring, skills, necessary contracts/docs and expected generated artifacts. No unrelated modifications, new dependencies, root commit or destructive Git operation.

`git status --short` (final snapshot; generated build/cache outputs are ignored):

```text
 M .agents/skills/bug-investigation/SKILL.md
 M .agents/skills/feature-builder/SKILL.md
 M .agents/skills/project-bootstrap/SKILL.md
 M .agents/skills/repo-explore/SKILL.md
 M README.md
 M docs/ARCHITECTURE.md
 M docs/DETACHMENT_CONTRACT.md
 M docs/PRODUCT_SPEC.md
 M docs/generated/CODEBASE_MAP.md
 M src/agentready/cli.py
 M src/agentready/core/profiles.py
 M src/agentready/doctor/inspector.py
 M src/agentready/render/generator.py
 M src/agentready/templates/python/template/.agents/skills/bug-investigation/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/documentation/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/feature-builder/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/maintenance/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/module-placement/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/refactoring/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/repo-explore/SKILL.md
 M src/agentready/templates/python/template/.agents/skills/security-review/SKILL.md
 M src/agentready/templates/python/template/README.md.jinja
 M src/agentready/templates/python/template/docs/agent/index.md
 M src/agentready/templates/python/template/scripts/project.py
 M src/agentready/templates/python/template/scripts/skill_check.py
 M tests/test_generated_project.py
 M tests/test_init.py
?? .agents/skills/bug-investigation/evals/
?? .agents/skills/feature-builder/evals/
?? .agents/skills/project-bootstrap/evals/
?? .agents/skills/repo-explore/evals/
?? docs/SKILL_QA_AND_CONTINUITY.md
?? docs/audits/FEATURE_EVOLUTION_AUDIT.md
?? docs/changelog/
?? docs/work/W001-skill-contract-and-doctor-validation.md
?? docs/work/W002-portable-skill-evaluation.md
?? docs/work/W003-opt-in-repository-hooks.md
?? docs/work/W004-work-checkpoint-and-resume.md
?? docs/work/W005-extension-architecture-decision.md
?? docs/work/W006-feature-evolution-regression-audit.md
?? docs/work/index.md
?? src/agentready/continuity.py
?? src/agentready/doctor/evolution.py
?? src/agentready/hooks.py
?? src/agentready/local_paths.py
?? src/agentready/skill_qa.py
?? src/agentready/templates/python/template/.agents/skills/bug-investigation/evals/
?? src/agentready/templates/python/template/.agents/skills/documentation/evals/
?? src/agentready/templates/python/template/.agents/skills/feature-builder/evals/
?? src/agentready/templates/python/template/.agents/skills/maintenance/evals/
?? src/agentready/templates/python/template/.agents/skills/module-placement/evals/
?? src/agentready/templates/python/template/.agents/skills/refactoring/evals/
?? src/agentready/templates/python/template/.agents/skills/repo-explore/evals/
?? src/agentready/templates/python/template/.agents/skills/security-review/evals/
?? src/agentready/templates/python/template/scripts/continuity.py.jinja
?? src/agentready/templates/python/template/scripts/hooks.py.jinja
?? src/agentready/templates/python/template/scripts/local_paths.py.jinja
?? src/agentready/templates/python/template/scripts/skill_qa.py.jinja
?? tests/test_evolution.py
```
