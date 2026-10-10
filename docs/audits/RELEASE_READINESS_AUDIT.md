# Release readiness audit

## Executive verdict

**READY — PUBLIC RELEASE AFTER REMOTE CI**.

Local quality, independent wheel/sdist onboarding and detachable three-profile qualification pass.
No remaining proven P0/P1 issue warrants reopening the architecture. Commit the reviewed scope,
require the actual GitHub matrix green for that SHA and enable/verify private security reporting
before publishing. No remote publication was authorized or performed.

Baseline commit: `ea2d0bd7366bbcb96f01fd6ccdfad99b73868993`, branch `main`.
The working tree was understood rather than clean: it held the reviewed final productization
changes, including its audit and regression tests. Those changes were preserved. Opening fast gates
passed before release edits: Ruff, format (108 files), mypy (22 files), map freshness and 16 routing
tests. Architecture remains frozen; no new runtime capability or dependency was introduced.

## Packaging

`pyproject.toml` declares `agentready` 0.1.0, Python >=3.12, MIT, Markdown README, Hatchling,
the `agentready.cli:main` console entry point and Copier >=9.18.2,<10. Runtime version comes from
installed metadata. Copier/Jinja belong to the generator environment, not generated application
dependencies. Dev requirements remain separate. Project URLs now identify repository/issues/docs;
development status reflects an early public beta.

The initial sdist included internal prompts, audits, tests and development metadata. Its inclusion
is now limited to package source, build configuration, README, MIT license and release history.
Rebuilt wheel: 124 files; sdist: 125 files; both contain all 97 bundled template files, including
hidden agent/CI assets. Neither contains bytecode/cache artifacts. Hatchling adds its normal
sdist `.gitignore` and PKG-INFO. Content hash comparison confirmed all 97 template files identical
between wheel and sdist. No production dependency was added.
`uvx --from twine twine check` passed for both exact 0.1.0 artifacts.
Archive inspection evidence: `C:/z_personale/agentready_use_cases/release_packaging.json`.

## Clean-user onboarding

A fresh worker with no conversation history received only the public repository and an isolated
workspace: `C:/z_personale/agentready_use_cases/release_user_test`. It was forbidden to read Python
implementation and used public docs/help. It understood all eleven requested topics without reading
implementation: zero source-reading defects. It selected all three profiles from README alone.
Initial DONE records exposed placeholder/enum discoverability friction; diagnostics and generated
public guidance resolved it. The new user guide now states NONE/NOT_REQUIRED explicitly.
Failed attempts remain in logs; the final wheel matrix reached DONE directly.
Detailed report: `release_user_test/ONBOARDING_REPORT.md` in the evaluation directory.

## Profile selection

README maps A (lightweight, own folders) to minimal, B (standard application/domain) to application,
and C (opinionated adapters/resources) to service. Minimal still preserves the Python scaffold;
application/service customization preserves checked boundaries. Contracts were not weakened.

## Generated-project qualification

Wheel and sdist installed independently in fresh environments; both help/version passed. Local-wheel
`uvx --refresh --from EXACT_WHEEL agentready --version` passed. The rebuilt wheel generated all three
profiles; each passed bootstrap, doctor, help, verify/build/package-check, accepted work lifecycle to
DONE, routes, skill check/lexical eval, hooks list/dry-run, checkpoint/resume, detach and verify plus
package-check afterward. Actual interception is outside the hook contract. An additional detached
sdist project check enabled safe-shell, preflighted `python --version` (allowed, not executed), then
disabled it and confirmed enabled count zero. Known global Git/Codex/Claude/PowerShell config hashes
were unchanged; this is scoped evidence, not exhaustive filesystem write tracing.
Minimal leaves folder choice open; application enforces application/domain imports; service adds
adapter/resource guidance. Application environments contain none of AgentReady/Copier/Jinja;
static runtime import screening returned no matches, complemented by installed application execution.
This does not prove absence of arbitrary future dynamic imports. The independently installed final
sdist also generated a separate minimal project, passing the entire work/route/skill/hook/continuity
and detach/verify/package-check lifecycle. Its scripts/logs are under `release_user_test/sdist-matrix/`.

Qualified artifact SHA256 values:

- wheel: `7808a31e378cf04572ad6cda3ef610a18ee6cdbe9ba7cc08bc1c90f1c867e2be`
- sdist: `57b724c0f8c9bfc40bf08b989d501098ffe40e554b0d6336913087642005d08a`

Exact command scripts and transcripts are retained under `release_user_test/final-matrix/` and
`final-install.log`. Skill eval success means lexical fixtures, not externally measured agent behavior;
missing behavioral observations remain MISSING.

## CLI discoverability

Root help exposes init, doctor, detach and repository-local skills/hooks/continuity. Generated
project help exposes work, route, skills, hooks, checkpoint/resume and project gates. Help delegates
to existing capabilities rather than duplicating implementations. Packaged root and all three generated
help commands passed; the worker navigated every requested capability without source inspection.

## CI readiness

CI now runs Ubuntu/3.12, Windows/3.12 and Ubuntu/3.14. Explicit interpreter selection overrides the
checkout's 3.12 default; dependency sync is locked. Existing setup-uv caching is retained. Each job
runs Ruff, format, mypy, serial complete pytest (including generated projects and formal detach),
build and map check. No macOS-specific requirement justifies another job.
Python 3.14 is a released interpreter ([official release](https://www.python.org/downloads/release/python-3140/));
the matrix does not claim to prove every future version allowed by >=3.12.

**REMOTE CI: NOT EXECUTED**. Ubuntu/newer-interpreter behavior awaits the actual matrix. Windows
symlink privilege skips remain explicit; junction tests provide alternate coverage, while Ubuntu
tests exercise actual symlinks. Final local tests use two workers for ordinary cases and then
serialized formal detach to avoid previous launcher contention; public CI remains entirely serial.
An additional packaged-wheel smoke test on Windows CPython 3.14.2 passed help, minimal init,
doctor and detach via `uvx --python 3.14 --from ./dist/agentready-0.1.0-py3-none-any.whl agentready`.
Its disposable project is `C:/z_personale/agentready_use_cases/release_python314`; it is a limited
CLI/rendering check, not a substitute for complete newer-interpreter CI.

## Open-source repository readiness

MIT LICENSE, issue forms, PR template, architecture and Detachment Contract exist. CONTRIBUTING
now contains exact setup/gates and support expectations. CHANGELOG.md records the prepared 0.1.0
release without claiming publication. RELEASING.md defines a small version policy and checklist.
The compact conduct policy no longer calls itself a placeholder. SECURITY links private vulnerability
reporting with a safe fallback; the human must enable and verify that GitHub setting before launch.
Support is best effort through GitHub issues, with fixes for the latest release only.

## Token-efficiency claims

**NUMERICAL TOKEN SAVING CLAIM: NOT MADE**.

The documentation describes design mechanisms and recommendations for reducing context waste,
not measured token savings. No telemetry, provider execution or model orchestration was added.

## Detachment

Packaged-profile and formal automated qualification must pass normal build/verify after detach;
generated environments must lack AgentReady/Copier/Jinja imports. Final evidence follows.

## Public documentation

README remains the landing page with purpose, no lock-in, quick start, wheel invocation and compact
profile table. USER_GUIDE provides deeper work/routing/skill/hook/continuity instructions. Work DONE
guidance now explains literal NONE and NOT_REQUIRED, addressing observed placeholder friction.
Release history and the human release procedure are linked without promising a PyPI publication.
A local link check executed successfully for 13 links in README, USER_GUIDE, RELEASING,
CONTRIBUTING and this audit. Dedicated publication notes avoid publishing the changelog's
"prepared, not published" status as the GitHub release description.

## Remaining P0/P1/P2 findings

P0: none found. P1: none found. P2: initial completion-field discoverability friction was addressed
in USER_GUIDE; the stricter work contracts remain intact. Four unavailable Windows symlink cases
are explicit skips, not passing claims. Remote CI remains a publication gate, not an assumed result.

### Exact local quality results

All 236 collected tests were covered across the two final executions: **232 passed, 4 skipped,
zero failures**. The split serializes formal detach and limits ordinary parallelism.

| Executed command | Result |
|---|---|
| `uv run --with pytest-xdist pytest -n 2 --ignore=tests/test_detached_project.py -v --tb=short --junitxml=C:/z_personale/agentready_use_cases/release_regression.xml` | 229 passed, 4 skipped in 815.69s |
| `uv run pytest tests/test_detached_project.py -q --tb=short --junitxml=C:/z_personale/agentready_use_cases/release_detach.xml` | 3 passed in 229.88s |
| `uv run ruff check .` | Passed |
| `uv run ruff format --check .` | Passed; 111 files |
| `uv run mypy src` | Passed; 22 files |
| `uv run python scripts/generate_codebase_map.py --check` | Passed |
| `uv build` | Wheel and sdist built |
| `uvx --from twine twine check dist/agentready-0.1.0-py3-none-any.whl dist/agentready-0.1.0.tar.gz` | Both passed |
| `git diff --check` | Passed |

Logs accompany both JUnit files in the evaluation directory. The four skips are doctor symlinked
component, detach symlinked boundary/nested metadata link and init symlink target tests; Windows
reported WinError 1314. Deterministic junction tests passed. Packaging archive/hash comparison,
13 local documentation links and clean installed-artifact tests were also actually executed.
Only audit text changed after these gates; final map/diff checks were repeated afterward.

## Deferred non-blockers

Per-task numerical token telemetry/A-B, macOS qualification, future Python versions and optional PyPI
name ownership/publication remain outside this release. There is no guaranteed support SLA.
Dependency-index/offline reproducibility and exhaustive filesystem write tracing were not assessed.
The working tree intentionally remains uncommitted for human review; publication must use the exact
qualified artifact names/hashes and a reviewed clean commit. Architecture stays frozen.

## Exact release procedure

See [RELEASING.md](../RELEASING.md) for ordered human commands: commit reviewed scope and verify
clean status; create local annotated v0.1.0 tag; push main; require CI for that exact SHA; push tag;
create GitHub release with exact wheel/sdist. Enable private security reports before inviting users.
Optional PyPI upload requires separate authorization and package ownership. No remote action,
commit or tag was performed by this task.
