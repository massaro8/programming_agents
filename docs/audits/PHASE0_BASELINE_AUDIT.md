# Phase 0 Baseline Audit

## Scope

This audit covers the public Phase-0 scaffold described by `docs/ROADMAP.md`. The review was
limited to restoring the coordinator kickoff reference, making the existing checks green,
making the generated codebase map reproducible in a fresh uncommitted checkout, and correcting
invalid GitHub issue-form metadata. No product command or Phase-1 capability was started.

## Pre-fix evidence

The untouched scaffold had the following baseline results:

- `uv sync --all-groups`: PASS.
- `uv run ruff format --check .`: PASS (35 files).
- `uv run ruff check .`: FAIL, `E501` in `src/agentready/cli.py:4`.
- `uv run mypy src`: PASS.
- `uv run pytest`: PASS (2 tests).
- `uv run python scripts/generate_codebase_map.py --check`: FAIL because the generator used only
  `git ls-files`, which omitted the mostly untracked copied scaffold.
- `START_SOL_COORDINATOR.md` was referenced by public documentation but missing.
- The issue forms used `about`, which is Markdown-template metadata rather than the required
  issue-form `description` key.

## Changes made

- Wrapped the long CLI module docstring in `src/agentready/cli.py`.
- Updated `scripts/generate_codebase_map.py` to combine cached and untracked, non-ignored Git
  files through `git ls-files --cached --others --exclude-standard`, while retaining the
  filesystem fallback for non-Git contexts.
- Restored `START_SOL_COORDINATOR.md` from the supplied kickoff content.
- Changed only the top-level metadata key from `about` to `description` in both issue forms.
- Regenerated `docs/generated/CODEBASE_MAP.md`; it now includes the untracked scaffold and
  `uv.lock` while excluding ignored runtime/cache noise.
- Added this audit.

## Final checks

All checks below were executed after the changes:

- `uv sync --all-groups`: PASS (14 packages audited).
- `uv run ruff format --check .`: PASS (37 files).
- `uv run ruff check .`: PASS.
- `uv run mypy src`: PASS (2 source files).
- `uv run pytest`: PASS (2 tests).
- `uv run python scripts/generate_codebase_map.py --check`: PASS.
- `git diff --check`: PASS (Git emitted only expected line-ending warnings for pre-existing
  modified `.gitignore` and `README.md`).
- `git status --short`: reviewed; pre-existing modifications to `.gitignore` and `README.md` were
  preserved, and the copied scaffold plus `uv.lock` remain untracked as supplied.

## Unresolved setup assumptions

- The scaffold is mostly untracked in this checkout; repository review must therefore use both
  `git status` and direct file inspection until the intended initial commit is created.
- The map generator relies on Git's standard ignore rules when Git is available. Its fallback
  remains filesystem-based and excludes known runtime/cache directories, but cannot reproduce
  arbitrary Git ignore rules outside a Git checkout.
- GitHub issue-form metadata was validated against the issue-form convention requiring top-level
  `name`, `description`, and `body`; no remote submission was attempted.

## Recommendation

Phase 0 is internally consistent and green. Start `BOOT-001` (baseline package and entry point)
as the next implementation task. `BOOT-001` has not been started in this audit.
