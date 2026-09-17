# DET-002 Formal No-Lock-In Qualification Audit

## Objective

Automate the complete installed-wheel generation, diagnosis, qualification, detach, tool-removal,
and independent post-detach qualification required by the V0.1 detachment contract.

## Qualification sequence

The test performs this isolated flow under `tmp_path`:

1. build the current AgentReady wheel;
2. create a dedicated tool virtual environment and install that wheel;
3. invoke the installed `agentready` executable to generate `demo_agentready`;
4. invoke installed-wheel doctor JSON and require schema 1, HEALTHY, and all checks passing;
5. run sync, Ruff format/check, mypy, pytest, and build in the generated project;
6. prove AgentReady, Copier, and Jinja are absent from the project environment;
7. snapshot semantic repository paths, types, and bytes;
8. invoke installed-wheel detach;
9. prove the snapshot changed only by removal of `.agentready/` and its descendants;
10. delete the dedicated AgentReady tool environment and the project's transient environment;
11. create a fresh project environment and repeat sync, Ruff, mypy, pytest, and build;
12. re-prove framework absence, normal application behavior, guidance integrity, dependency/import
    independence, and clean application wheel contents.

Subprocess failures retain only the last 2,000 output characters and every command has a bounded
timeout.

## Before/after preservation proof

The snapshot excludes only explicitly named tool-created environments, caches, and build outputs.
Immediately after detach, the after-set must equal the before-set minus `.agentready` and its
descendants; no added path is tolerated. Every remaining type and byte sequence must match.

Source, tests, CI, `pyproject.toml`, README, architecture documentation, `AGENTS.md`, `CLAUDE.md`,
and `docs/agent/**` therefore survive detach unchanged.

## Independent post-detach qualification

After deleting the AgentReady tool environment and the generated project's pre-detach `.venv`, the
detached project passes:

- `uv sync --all-groups`;
- `uv run ruff format --check .`;
- `uv run ruff check .`;
- `uv run mypy src`;
- `uv run pytest`;
- `uv build`.

The fresh project environment cannot resolve `agentready`, `copier`, or `jinja2`, while the generated
application imports and runs normally.

## Agent-guidance survival

The test preserves and byte-compares `AGENTS.md`, `CLAUDE.md`, both referenced `docs/agent/` files,
and `docs/ARCHITECTURE.md`. It verifies that AGENTS names both existing workflow/standard paths and
that CLAUDE remains a thin link to AGENTS. AgentReady is not needed to interpret these plain files.

## Dependency and artifact proof

Runtime, optional, and development dependency declarations contain no AgentReady requirement.
Generated Python ASTs contain no `agentready` import. The post-detach application wheel contains the
expected application module and no `agentready/`, `copier/`, or `jinja2/` framework package.

## Required qualification answers

**Can the generated project function after AgentReady is gone?** Yes. It imports, tests, and builds
after the dedicated AgentReady environment is deleted.

**Can it be developed using ordinary Python tooling?** Yes. A fresh uv-managed environment passes
the complete documented Python toolchain.

**Are its agent instructions still ordinary usable files?** Yes. Guidance files and their local
references remain present and byte-identical.

**Did detach remove only AgentReady maintenance ownership?** Yes. Exact snapshot comparison permits
only `.agentready/` descendants to disappear.

**Is any runtime or development dependency on AgentReady left?** No. Static dependency/import
inspection, environment probes, and application wheel inspection all pass.

## Files changed

- `tests/test_detached_project.py`
- `docs/audits/DET_002_AUDIT.md`
- `docs/generated/CODEBASE_MAP.md`

No product, template, manifest, or dependency behavior changed.

## Verification

| Check | Result |
|---|---|
| formal detached-project qualification | PASS — 1 passed |
| installed-wheel init/doctor/detach | PASS |
| exact preservation snapshot | PASS |
| fresh post-detach toolchain | PASS |
| framework/dependency/import absence | PASS |
| guidance survival | PASS |
| `uv sync --all-groups` | PASS |
| `uv run ruff format --check .` | PASS |
| `uv run ruff check .` | PASS |
| `uv run mypy src` | PASS |
| `uv run pytest` | PASS — 66 passed, 4 privilege-dependent skips |
| `uv run agentready --help` | PASS |
| `uv run agentready --version` | PASS |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git diff --check` | PASS |

## Dependencies

New production dependencies:

- none

## Residual risks / assumptions

- Qualification requires `uv` and access to already cached or resolvable Python tooling packages.
- Filesystem concurrency and partial metadata-removal limitations remain those documented by
  DET-001.
- The qualification supports the sole V0.1 Python profile; additional profiles remain deferred.

## Recommendation

DET-002_COMPLETE
