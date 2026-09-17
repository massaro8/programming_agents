# Operational Roadmap

The roadmap is deliberately sequenced to prove the differentiating property first: detachability.

## Phase 0 - Green public scaffold

Goal: establish a contributor- and agent-ready repository before product implementation.

Deliverables:
- concise `AGENTS.md` and `CLAUDE.md`;
- product spec, architecture, detachment contract;
- feature/ADR templates;
- initial four skills;
- Ruff + mypy + pytest + CI;
- deterministic codebase-map generator;
- public contribution/security/review templates;
- coordinator kickoff prompt.

Gate:
- repository baseline is green;
- generated `CODEBASE_MAP.md` is reproducible;
- no speculative product modules are created.

## Phase 1 - V0.1 vertical slice

Build only three user-visible capabilities:

### 1A - `init`
- trusted bundled Python starter;
- safe empty-directory checks;
- project naming validation;
- canonical `AGENTS.md` + `docs/agent/**`;
- optional Claude adapter;
- `.agentready/manifest.toml` metadata;
- successful generated-project smoke test.

### 1B - `doctor`
V0.1 implements deterministic structural checks only:
- supported manifest/profile identity and ownership coherence;
- expected repository and instruction files;
- broken repository-local guidance references;
- static AgentReady dependency independence;
- detachability preconditions;
- human and schema-1 JSON output.

Git state, duplicate/conflicting guidance, adapter-drift compilation, instruction budgets, and
executable quality auditing remain later evidence-based doctor/audit work.

### 1C - `detach`
- fixed-boundary metadata-only deletion;
- conservative path allowlist;
- fail-closed preflight with no force path;
- no source/test/CI deletion;
- detachment E2E test.

The V0.1 boundary is unambiguously `.agentready/`, so `detach` applies that removal directly.
Preview/update semantics remain post-V0.1 work.

Phase 1 release gate:

```text
generate -> doctor PASS -> fixture checks PASS -> detach -> fixture checks PASS
```

No V0.1 release without this gate.

The automated Phase 1 gate is complete. The repository is a V0.1 practical-validation candidate;
the scenarios in `docs/PRACTICAL_VALIDATION_PLAN.md` are the next phase, not completed evidence.

## Phase 2 - Existing repositories and evidence

Add only after V0.1 is stable:

- `adopt --dry-run` first, `--apply` second;
- adapter `sync` from canonical guidance;
- evidence-based `audit` with Markdown + JSON;
- ownership manifest validation;
- more robust instruction conflict/drift checks.

Gate:
- adoption never silently overwrites existing user-owned guidance;
- audit records commands actually executed and exit status;
- sync is deterministic.

## Phase 3 - Safe updates

- integrate Copier for managed template/guidance update semantics;
- clean-working-tree preflight;
- `update --check`, `--dry-run`, then `--apply`;
- three-way merge for shared guidance;
- generated adapters can be regenerated;
- project-owned files are never silently updated.

Gate:
- conflicts are surfaced, not hidden;
- detach still works after an update history;
- user can stop using AgentReady permanently.

## Phase 4 - Evaluation and expansion

Only after real usage:
- benchmark repository tasks with/without the harness;
- measure task success, retries, files-read/files-changed, cost/task accepted;
- calibrate instruction-budget warnings;
- add TypeScript/Go/Rust profiles only with real demand;
- consider model-routing helpers only after telemetry/evidence.

## Issue sequence for the first implementation session

1. `BOOT-001` Establish baseline tooling and package entry point.
2. `BOOT-002` Implement internal project/ownership primitives.
3. `INIT-001` Implement trusted bundled Python template generation.
4. `INIT-002` Add generated-project smoke fixture and tests.
5. `DOC-001` Implement first deterministic doctor checks.
6. `DOC-002` Add JSON doctor schema/output.
7. `DET-001` Implement fixed-boundary fail-closed detach.
8. `DET-002` Add full detachment E2E test.
9. `REL-001` Public V0.1 readiness audit.

Do not start `adopt`, `update`, telemetry, remote plugins, or multi-language profiles before `DET-002` is green.
