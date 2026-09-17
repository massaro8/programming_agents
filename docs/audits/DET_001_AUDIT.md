# DET-001 Detachment Audit

## Objective

Implement `agentready detach [PATH]` as a fail-closed removal of AgentReady-only maintenance
metadata while preserving every useful repository artifact.

## Initial state

DOC-002 completed deterministic human and JSON repository diagnostics. Generated repositories
contained the optional `.agentready/manifest.toml` maintenance metadata but no detach service.

## Preflight

Detach normalizes the caller target through `Project` and requires:

- an existing non-symlink project directory;
- the fixed `.agentready/` boundary as a real directory;
- a real, UTF-8, parseable `.agentready/manifest.toml`;
- schema `1`, generator `agentready`, profile `python`, and a nonempty generator version;
- a complete sorted inventory containing only regular files and real directories;
- no symlink or special entry anywhere in the removal boundary.

Preflight requires detach-safe identity, not full doctor health. Missing unrelated application files
do not prevent a user from removing maintenance ownership.

## Exact removal boundary

The only removable path is the fixed repository-relative `.agentready/` directory. Manifest
ownership entries are never used as deletion targets, and `GENERATED` is not interpreted as a
lifecycle policy.

The service inventories the boundary before mutation, validates every entry, then rechecks the
boundary and every path component immediately before each explicit file `unlink` or bottom-up
directory `rmdir`. It does not use globs, `shutil.rmtree`, Git operations, shell deletion, or a
`--force` option.

## Files preserved

The complete directory/type/content snapshot outside `.agentready/` remains identical. Tests also
assert the continued presence of:

- application source and tests;
- `pyproject.toml` and CI;
- `README.md` and architecture documentation;
- `AGENTS.md` and `CLAUDE.md`;
- `docs/agent/standards/testing.md` and `docs/agent/workflows/feature.md`.

## Negative controls

| Corruption or unsafe state | Expected behavior | Result |
|---|---|---|
| ordinary/unrecognized repository | refuse without mutation | PASS |
| missing manifest | refuse without mutation | PASS |
| malformed manifest | refuse without mutation | PASS |
| unsupported schema | refuse without mutation | PASS |
| missing unrelated `README.md` | detach metadata successfully | PASS |
| `.agentready` symlink | fail closed where platform permits specimen | PASS/privilege skip |
| nested metadata symlink | fail closed where platform permits specimen | PASS/privilege skip |

## Idempotency behavior

The first detach succeeds with exit `0`. A second invocation returns exit `1` with the deterministic
message `project is not AgentReady-managed or is already detached`; it does not recreate metadata
or modify the detached tree.

## CWD independence

Absolute and relative target paths both detach correctly when invoked from an unrelated working
directory. The CLI path argument defaults to `.`.

## No-dependency check

After detach, static TOML inspection finds no AgentReady runtime dependency, and AST inspection of
generated source finds no `agentready` import. DET-002 performs the formal isolated tooling proof.

## Safety analysis

- The fixed boundary prevents manifest-controlled arbitrary deletion.
- Symlinks and non-regular filesystem objects fail before mutation.
- Rechecks reduce path-substitution exposure before each mutation.
- Portable `pathlib` cannot eliminate all concurrent filesystem races.
- An operating-system failure after an unlink can leave maintenance metadata partially removed;
  rollback is deliberately not attempted and no ordinary repository artifact is touched.

## Files changed

- `src/agentready/detach/__init__.py`
- `src/agentready/detach/service.py`
- `src/agentready/cli.py`
- `tests/test_detach.py`
- `docs/audits/DET_001_AUDIT.md`
- `docs/generated/CODEBASE_MAP.md`

## Verification

| Check | Result |
|---|---|
| targeted detach tests | PASS — 10 passed, 2 privilege-dependent skips |
| preservation snapshot | PASS |
| negative controls | PASS |
| first/second explicit CLI detach | PASS — exits 0/1 |
| `uv sync --all-groups` | PASS |
| `uv run ruff format --check .` | PASS |
| `uv run ruff check .` | PASS |
| `uv run mypy src` | PASS |
| `uv run pytest` | PASS — 65 passed, 4 privilege-dependent skips |
| `uv run agentready --help` | PASS |
| `uv run agentready --version` | PASS |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git diff --check` | PASS |

## Dependencies

New production dependencies:

- none

## Deferred work

- formal isolated generate/qualify/detach/remove-tool/requalify proof (DET-002);
- transactional rollback for partial metadata-removal failure;
- dry-run and force modes, which are not required for the unambiguous V0.1 fixed boundary.

## Recommendation

DET-001_COMPLETE
