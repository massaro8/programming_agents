# INIT-002 Generated Project Qualification Audit

## Objective

Prove that a project generated from the packaged AgentReady wheel is deterministic and operates as
an ordinary independent Python project without AgentReady, Copier, or Jinja in its environment.

## Qualification environment

- Host: Windows, Python 3.12.12.
- Project tooling: uv 0.9.29.
- Qualification root: pytest-managed temporary directory outside the AgentReady checkout.
- Harness: `tests/test_generated_project.py`, using bounded subprocesses and concise failure output.

## AgentReady packaged-artifact test

The harness builds an AgentReady wheel with `uv build --wheel`, then invokes `agentready init` via
`uv run --isolated --no-project --with <wheel>`. Generation therefore uses the installed wheel and
its packaged Copier template resources rather than the editable source checkout.

## Canonical generated specimen

The qualified specimen is `demo_agentready`, with package `demo_agentready` and observable behavior
`greet("AgentReady") == "Hello, AgentReady!"`. A second specimen with identical inputs is generated
in a separate temporary root for determinism comparison.

## Generated project qualification

| Check | Result |
|---|---|
| generation from packaged AgentReady | PASS |
| uv sync | PASS |
| ruff format | PASS |
| ruff check | PASS |
| mypy | PASS |
| pytest | PASS |
| uv build | PASS |
| AgentReady absent from project dependencies | PASS |
| independent project environment | PASS |
| manifest coherence | PASS |
| guidance references | PASS |
| deterministic double generation | PASS |
| CI coherence | PASS |

The focused qualification command, `uv run pytest tests/test_generated_project.py -v`, completed
with one passing test in 38.36 seconds.

## Independence evidence

The generated `pyproject.toml` has no AgentReady dependency. After the generated project's own
`uv sync --all-groups`, an import probe confirms that `agentready`, `copier`, and `jinja2` are not
available, while the generated package imports and greets correctly. Ruff format/lint, mypy,
pytest, and build all pass from the generated project root. Its wheel contains only
`demo_agentready/__init__.py` and `demo_agentready/main.py` as package code and no `agentready/`
framework package.

## Determinism evidence

Before any project tooling creates locks, environments, caches, or build output, the harness compares
the complete relative file map and bytes from two separate generations. All 14 files and all byte
payloads are identical. No timestamps, UUIDs, machine paths, or temporary paths differ.

## Manifest review

The three ownership arrays are pairwise non-overlapping and their union exactly equals the initial
14-file generated tree. Every entry is an existing repository-relative path accepted by
`ProjectPath`, and each path/class pair is representable as `ArtifactOwnership`. Ownership remains a
classification and does not encode detach deletion.

## Guidance review

`AGENTS.md` remains the compact canonical entry point and references the existing testing standard
and feature workflow under `docs/agent/`. `CLAUDE.md` is a one-line link to `AGENTS.md`. The detailed
guidance stays outside the always-loaded adapter.

## INIT-001 risk follow-up

### Existing empty target partial rendering

The documented V0.1 behavior remains acceptable: a pre-existing empty directory is never deleted on
failure, and `GeneratorError` makes the rendering failure explicit. Partial output may remain for
inspection and manual cleanup. A transaction or destructive rollback layer is not justified here.

### Symlink coverage

Production rejects a symlink target before rendering. The real-symlink test remains active where the
host permits symlink creation; this Windows account lacks that privilege, so capable CI hosts must
continue to exercise it.

### Future update provenance

For V0.1, `generator = "agentready"`, `generator_version`, and `profile = "python"` identify the
bundled template because it is shipped inside that AgentReady release and only one profile exists.
A distinct template version becomes necessary only if template evolution is decoupled from AgentReady
releases. No update metadata or Copier answers file is needed now.

## Repairs required during qualification

No generated-template or production-code repair was required. The new harness itself was hardened to
derive the checkout root from its file location, use the located absolute uv executable, reject Ruff's
no-files warning, and validate ownership through BOOT-002 primitives.

## AgentReady regression gates

- `uv sync --all-groups`: PASS.
- `uv run ruff format --check .`: PASS.
- `uv run ruff check .`: PASS.
- `uv run mypy src`: PASS.
- `uv run pytest`: PASS.
- `uv run agentready --help`: PASS.
- `uv run agentready --version`: PASS.
- `uv run python scripts/generate_codebase_map.py --check`: PASS.
- `git diff --check`: PASS.

The complete AgentReady suite finished with 31 passed and one Windows privilege-based symlink skip
in 46.06 seconds.

## Residual risks / assumptions

Qualification requires uv and package-index or cache access for the generated development toolchain,
matching the repository's documented workflow. The integration test is intentionally slower than the
unit suite. Real symlink coverage depends on host privileges. Formal metadata removal and post-detach
requalification remain DET-001/DET-002 work.

## Recommendation

Accept INIT-002 as complete. Proceed next to DOC-001 without starting doctor or detach work in this
change.

INIT-002_COMPLETE
