# Project guidance

Purpose: maintain a small, independent Python project.

Commands: `uv sync --all-groups`; `uv run ruff format --check .`; `uv run ruff check .`; `uv run mypy src`; `uv run pytest`.

Invariants: keep the src layout, preserve tests, and do not add a runtime dependency on AgentReady.

Definition of done: tests, formatting, lint, and type checks pass. See `docs/agent/standards/testing.md` and `docs/agent/workflows/feature.md` for focused procedures.
