# Contributing

Start with `AGENTS.md`, `docs/ARCHITECTURE.md`, and `docs/ROADMAP.md`.

Principles:
- small scoped pull requests;
- behavior and acceptance before implementation;
- deterministic checks as evidence;
- no unrelated refactors;
- preserve no-lock-in and detachment invariants.

Install Python 3.12+ and uv, clone the repository, then run:

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
uv run python scripts/generate_codebase_map.py --check
uv build
```

Tests run serially, including generated-project and installed-wheel detach qualification.
CI covers Ubuntu/Windows on 3.12 and Ubuntu on 3.14. Windows symlink privilege skips are explicit;
junction tests retain deterministic alternate coverage. Linux jobs exercise symlink behavior.
Remote CI must actually pass before release. Support through GitHub issues is best effort.
See `docs/RELEASING.md` for version policy and the human publication procedure.
