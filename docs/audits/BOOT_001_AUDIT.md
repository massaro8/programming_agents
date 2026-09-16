# BOOT-001 Implementation Audit

## Objective

Establish the minimal AgentReady package and CLI foundation: derive the public package version
from project metadata, expose predictable `--help`, `--version`, and invalid-input behavior, and
prove the installed console script with subprocess tests.

## Initial state

The Phase-0 scaffold declared version `0.0.0` in `pyproject.toml` and duplicated that literal in
`src/agentready/__init__.py`. The CLI embedded a separate scaffold version string and `main()` did
not accept an argument sequence. Smoke tests only constructed the parser and checked a truthy
version.

## Design decision

`importlib.metadata.version("agentready")` is the sole runtime source for `__version__`; the
project's static `[project].version` remains the single declaration. The CLI keeps stdlib
`argparse`, formats its version from `__version__`, and accepts `Sequence[str] | None` for direct
and testable invocation. Console behavior is tested through the installed executable.

## Files changed

- `src/agentready/__init__.py`: metadata-backed public version.
- `src/agentready/cli.py`: metadata-backed version output and argv support.
- `tests/test_smoke.py`: installed-console subprocess coverage.
- `docs/audits/BOOT_001_AUDIT.md`: this permanent audit.

## Behavior implemented

- `agentready --help` exits `0` and prints concise argparse help.
- `agentready --version` exits `0` and prints `agentready 0.0.0`.
- Unknown options use argparse's standard error and exit code `2`.
- No command capabilities are implemented in BOOT-001.

## Tests added/changed

The smoke suite invokes the installed `agentready` executable and covers help output, exact
metadata-derived version output, and invalid-option behavior.

## Verification

| Check | Result |
| --- | --- |
| `uv sync --all-groups` | PASS |
| `uv run pytest tests/test_smoke.py` | PASS |
| `uv run agentready --help` | PASS |
| `uv run agentready --version` | PASS |
| `uv run agentready --definitely-invalid` (exit 2) | PASS |
| `uv run ruff format --check .` | PASS |
| `uv run ruff check .` | PASS |
| `uv run mypy src` | PASS |
| `uv run pytest` | PASS |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git diff --check` | PASS |
| `git status --short` | REVIEWED |

## Dependencies

No production dependencies were added. The implementation uses only the Python standard library;
the existing development toolchain remains unchanged.

## Scope review

`init`, `doctor`, `detach`, `adopt`, `sync`, `audit`, `update`, provider adapters, templates, and
all BOOT-002 work remain deferred.

## Residual risks / assumptions

The metadata lookup requires the package to be installed, as guaranteed by the repository's
`uv sync` workflow. The executable subprocess tests therefore fail clearly if the synced console
script is absent from `PATH`. The mostly untracked scaffold is preserved as supplied.

BOOT-001_COMPLETE
