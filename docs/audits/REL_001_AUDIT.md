# REL-001 V0.1 Readiness Audit

## Objective

Prepare AgentReady 0.1.0 for practical use-case testing without publishing the package or claiming
production maturity.

## Milestone summary

The accepted V0.1 vertical slice now comprises deterministic bundled generation, independent
generated-project qualification, read-only human/JSON diagnostics, fixed-boundary detach, and a
formal installed-wheel no-lock-in proof. REL-001 aligns public documentation, package metadata, CI,
packaging evidence, and the next-phase validation plan with that implemented surface.

## CLI surface

- `agentready init PATH`
- `agentready doctor [PATH] [--format human|json]`
- `agentready detach [PATH]`
- `agentready --help`
- `agentready --version`

No adopt, update, sync, audit, repair, force, remote-template, or additional-profile command is
present or advertised.

## Package and version

`pyproject.toml` and `uv.lock` declare local version `0.1.0`. Runtime `__version__` and CLI version
derive from installed package metadata. This is local release preparation only: no tag, remote
release, or PyPI publication was created.

Copier remains the sole internal rendering engine for the trusted bundled template. Generated
projects do not depend on AgentReady, Copier, or Jinja.

## Tests and CI

The single Ubuntu/Python 3.12 CI job runs sync, format, lint, typing, the complete pytest suite,
direct package build, and codebase-map verification. Full pytest includes the installed-wheel INIT
qualification and formal detachment qualification. Ubuntu exercises the symlink tests that may be
privilege-skipped on local Windows; no redundant CI matrix or duplicate E2E job was added.

## Packaging readiness

The formal qualification builds and installs the current wheel into a dedicated environment and
proves packaged-template generation plus installed CLI help, version, init, doctor JSON, and detach.
The release gate also builds sdist and wheel directly and inspects their resources. Artifact
publication remains out of scope.

## No-lock-in proof

DET-002 proves that only `.agentready/` disappears, the AgentReady tool environment can be removed,
a fresh project environment passes sync/Ruff/mypy/pytest/build, ordinary guidance remains usable,
and neither dependencies, imports, environment modules, nor application wheel contain AgentReady
framework code.

## Known limitations

- Python 3.12+ and one bundled Python profile only.
- New missing/empty target generation only; no existing-repository adoption or update engine.
- Doctor is structural and does not run Git, tests/builds, LLM review, duplicate analysis, or context
  scoring.
- Detach supports recognized schema-1 projects and has no force, repair, dry-run, or transactional
  rollback mode.
- Concurrent filesystem replacement cannot be eliminated portably; detach rechecks and fails closed
  where observable.
- Local Windows may skip symlink creation without Developer Mode; capable Linux CI remains
  authoritative.
- Practical use-case validation has not yet been executed.

## Security boundary

V0.1 uses only a trusted local bundled template, disables unsafe Copier tasks/hooks, refuses
non-empty init targets, performs read-only local doctor checks, and constrains detach to a recognized
non-symlink `.agentready/` boundary. It executes no remote templates/plugins, repository hooks, Git
mutations, telemetry, backend calls, or account workflow.

## Documentation status

README now documents actual installation status, commands, JSON output, detach behavior, no-lock-in
evidence, Python requirement, limitations, and trust boundary. PRODUCT_SPEC and ROADMAP no longer
present deferred Git/duplicate/context-budget doctor checks or detach preview semantics as V0.1
features. Historical audits remain unchanged.

## Practical-validation readiness

`docs/PRACTICAL_VALIDATION_PLAN.md` defines UC-01 greenfield feature, UC-02 bug investigation,
UC-03 Codex/Claude parity, and UC-04 detach-and-continue, with bounded prompts, procedures, evidence,
stop conditions, and a manual metrics record. No use case or telemetry campaign was started.

## Files changed

- `README.md`
- `SECURITY.md`
- `docs/PRODUCT_SPEC.md`
- `docs/ROADMAP.md`
- `docs/PRACTICAL_VALIDATION_PLAN.md`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `uv.lock`
- `tests/test_detached_project.py`
- `docs/audits/REL_001_AUDIT.md`
- `docs/generated/CODEBASE_MAP.md`

## Verification

| Check | Result |
|---|---|
| focused installed-wheel qualification | PASS — 1 passed |
| source sync/format/lint/type/tests | PASS — 66 passed, 4 privilege-dependent skips |
| CLI help/version 0.1.0 | PASS |
| `uv build` | PASS — sdist and wheel 0.1.0 |
| wheel/sdist resource inspection | PASS — template in wheel; schemas/docs/tests in sdist |
| formal init/doctor JSON/detach proof | PASS |
| codebase map | PASS |
| `git diff --check` | PASS |
| documentation consistency review | PASS |

## Residual risks

Practical task quality and cross-agent instruction adherence remain empirical questions for the
separate validation campaign. V0.1 is not declared production-stable or publicly published.

## Recommendation

REL-001: COMPLETE

READY_FOR_PRACTICAL_USE_CASES
