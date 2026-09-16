# INIT-001 Implementation Audit

## Objective

Generate a deterministic, independent Python repository from the trusted bundled Copier template.

## Initial state

BOOT-002 supplied typed project, relative-path, and ownership primitives. No init command,
template renderer, or generated-project contract existed.

## Architecture confirmation

### Rendering engine

Copier 9.18.2 is the only new direct production dependency and the sole rendering engine, invoked
through public `copier.run_copy`.

### Bundled-template strategy

Only packaged local resources under `agentready.templates.python` are used. No URL, network,
plugins, tasks, hooks, migrations, or update state are enabled; `unsafe=False`, `skip_tasks=True`,
`defaults=True`, and `overwrite=False` are explicit.

### Filesystem safety policy

The target becomes an absolute `Project`; files, symlinks, and non-empty directories are refused.
Missing and existing empty real directories are allowed, with no force path or user-content overwrite.

## Generated project contract

The template produces a Python >=3.12 src-layout project using hatchling, pytest, Ruff, and mypy.
`greet(name: str) -> str` returns `Hello, {name}!`; generated projects have no AgentReady runtime
or development dependency.

## Naming contract

Target basenames match lowercase ASCII `[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*`; hyphens map to
underscores for a valid non-keyword package identifier. Dots, uppercase, leading digits/separators,
repeated/trailing separators, and ambiguous names are rejected.

## Ownership map

### PROJECT_OWNED

`.github/workflows/ci.yml`, `.gitignore`, `.python-version`, `README.md`, `docs/ARCHITECTURE.md`,
`pyproject.toml`, `src/<package>/__init__.py`, `src/<package>/main.py`, `tests/test_main.py`.

### SHARED

`AGENTS.md`, `docs/agent/standards/testing.md`, `docs/agent/workflows/feature.md`.

### GENERATED

`CLAUDE.md`, `.agentready/manifest.toml`.

## Manifest/provenance design

Manifest TOML is deterministic: schema 1, profile `python`, generator `agentready`, the current
AgentReady version, and exact canonical ownership arrays. It contains no timestamps, UUIDs,
absolute paths, Copier answers, or detach policy.

## Files changed

`pyproject.toml`, `uv.lock`, manifest schema, CLI, render generator, bundled template files,
focused init tests, this audit, and regenerated codebase map.

## Tests added/changed

Focused tests verify the exact rendered tree, complete parsed manifest and schema alignment, safe and
invalid names (including Windows-reserved names), file/symlink/non-empty refusal, existing-empty
acceptance, caller-CWD independence, no answers file, hyphen mapping, runtime independence, and the
installed CLI path.

## Canonical generated example

Target: `demo_agentready`

```text
demo_agentready/
├── .agentready/manifest.toml
├── .github/workflows/ci.yml
├── .gitignore
├── .python-version
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── docs/ARCHITECTURE.md
├── docs/agent/standards/testing.md
├── docs/agent/workflows/feature.md
├── pyproject.toml
├── src/demo_agentready/__init__.py
├── src/demo_agentready/main.py
└── tests/test_main.py
```

## Verification

| Check | Result |
| --- | --- |
| targeted INIT-001 tests | PASS |
| sample init | PASS |
| non-empty target refusal | PASS |
| invalid name handling | PASS |
| ownership/manifest checks | PASS |
| `uv sync --all-groups` | PASS |
| ruff format | PASS |
| ruff check | PASS |
| mypy | PASS |
| repository pytest | PASS |
| agentready --help | PASS |
| agentready --version | PASS |
| CODEBASE_MAP | PASS |
| `git diff --check` | PASS |

Additional packaging verification: `uv build` and wheel resource inspection passed.
The focused run completed with 19 passed and one Windows privilege-based symlink skip; the full
repository run completed with 30 passed and the same single skip. An isolated wheel installation
also generated a project successfully from its packaged template resources.

## Dependencies

Copier `>=9.18.2,<10` is the only new direct production dependency, providing trusted local
template rendering; its transitive dependencies are resolved in `uv.lock`.

## Independence review

Generated application, build configuration, and tests contain no AgentReady dependency/import or
runtime reference. Only the provenance manifest identifies the generator; guidance remains ordinary
repository files.

## Deferred work

INIT-002 qualification, doctor, detach, adopt, sync, audit command, update lifecycle, Git
initialization, additional profiles/languages, and remote/community template execution remain
deferred.

## Residual risks / assumptions

Target checks are lexical and do not resolve parent symlinks; the target itself is rejected if
symlinked. Existing empty destinations may retain partial Copier output after a rendering failure,
while newly created destinations receive Copier cleanup. The real-symlink test was skipped locally
because this Windows account lacks symlink privileges; it remains active on hosts that permit symlink
creation. Build artifacts remain ignored.

## Recommendation

Accept INIT-001 as complete and use the generated independent repository as input to INIT-002.

INIT-001_COMPLETE
