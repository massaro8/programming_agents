# BOOT-002 Implementation Audit

## Objective

Establish the minimal deterministic project, repository-relative path, and artifact ownership
vocabulary required by later bootstrap capabilities.

## Initial state

BOOT-001 provided the package and CLI foundation, but no typed project-root, relative-path, or
ownership primitives existed. The manifest schema names ownership groupings, while persistence and
lifecycle behavior remain intentionally deferred.

## Requirement interpretation

The domain needs immutable values for an absolute project root, safe repository-relative artifact
paths, three canonical ownership classes, and an explicit path/class association. Path handling is
native-platform and lexical only: no filesystem access, symlink resolution, discovery, or CWD
dependence for accepted inputs.

## Domain model

### Project

`Project` is a frozen, slotted value object holding an absolute `pathlib.Path` root. The root is
lexically normalized without requiring existence or resolving symlinks. `path_for` joins a validated
`ProjectPath`; `relative_path` converts an absolute in-project path and rejects the root and
outside paths.

### Ownership classes

`OwnershipClass` contains exactly `PROJECT_OWNED`, `SHARED`, and `GENERATED`. Classification does
not encode overwrite, merge, regeneration, or detach deletion policy.

### Artifact ownership

`ArtifactOwnership` is a frozen, slotted association of one `ProjectPath` and one `OwnershipClass`.
It has no lifecycle behavior and rejects raw strings or other wrong runtime types.

## Design decisions

Project paths must be non-empty and unanchored on the native platform, with no `..` traversal. A
non-empty native `Path.anchor` is rejected, covering absolute, rooted, UNC, and drive-relative forms
without manual foreign-path parsing. This prevents rooted paths from escaping a project on Windows.

## Files changed

- `src/agentready/core/__init__.py`: public exports for BOOT-002 primitives.
- `src/agentready/core/project.py`: immutable project and relative-path objects.
- `src/agentready/core/ownership.py`: canonical ownership enum and association object.
- `tests/test_project.py`: path validation, conversion, containment, and value semantics.
- `tests/test_ownership.py`: ownership vocabulary, association, validation, and value semantics.
- `docs/audits/BOOT_002_AUDIT.md`: this permanent audit.
- `docs/generated/CODEBASE_MAP.md`: regenerated repository map.

## Tests added/changed

Focused tests cover all ownership members, invalid path forms including native rooted paths,
deterministic conversion and CWD independence, outside-project rejection, and equality/hash behavior
for immutable values.

## Verification

| Check | Result |
| --- | --- |
| `uv run pytest tests/test_project.py tests/test_ownership.py` | PASS |
| `uv sync --all-groups` | PASS |
| `uv run ruff format --check .` | PASS |
| `uv run ruff check .` | PASS |
| `uv run mypy src` | PASS |
| `uv run pytest` | PASS |
| `uv run agentready --help` | PASS |
| `uv run agentready --version` | PASS |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git diff --check` | PASS |
| `git status --short` | REVIEWED |

## Dependencies

No production dependencies were added. The implementation uses only Python standard-library
`pathlib`, `os.path`, `dataclasses`, and `enum`.

## Deferred work

Manifest persistence, serialization, migration, repository scanning, lifecycle policy, and all
init/doctor/detach/adopt/update behavior remain deferred. Ownership classes do not imply automatic
overwrite, merge, regeneration, or deletion on detach.

## Architecture review

The change is limited to the target `core` package and focused tests. It preserves the separation
between deterministic core values and CLI/application capabilities, adds no runtime AgentReady
dependency to generated applications, and performs no I/O or mutation.

## Residual risks / assumptions

Containment is lexical by design and does not resolve symlinks; physical containment belongs at a
future filesystem-writing boundary. Existing manifest grouping names are more specific than the
canonical enum and are not guessed or mapped until persistence is designed.

## Recommendation

Accept BOOT-002 as complete and use these primitives as the vocabulary for INIT-001, without adding
INIT-001 functionality to this change.

BOOT-002_COMPLETE
