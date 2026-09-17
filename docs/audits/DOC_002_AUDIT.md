# DOC-002 Machine-Readable Doctor Audit

## Objective

Expose deterministic schema-1 JSON for `agentready doctor [PATH] --format json`.

## Contract

JSON preserves inspector order and semantics with `schema`, `status`, `project`, and `checks` keys.
Finding paths remain repository-relative; absolute machine paths are never emitted.

## Schema

`schemas/doctor.schema.json` is a strict draft-2020-12 schema with lowercase health/status enums,
required fields, nullable finding paths, and no additional properties.

## Determinism and parity

Repeated serialization is byte-identical. Relative and absolute spellings of the same target emit
the same normalized project identifier. JSON and human modes inspect once and retain identical
health exit semantics: 0 healthy and 1 unhealthy; invalid format remains argparse exit 2.

## Read-only proof

Focused tests snapshot the complete generated tree and its bytes before and after the JSON CLI
invocation. The snapshot is unchanged. No dependencies, timestamps, UUIDs, network, or absolute
target paths are introduced.

## Files changed

Added serializer, doctor schema, focused JSON tests, this audit, and regenerated codebase map;
updated doctor exports and CLI format selection.

## Tests added/changed

Tests cover schema key order and authoritative schema fields, status/check order, relative paths,
absolute/relative target equivalence, deterministic bytes, healthy and unhealthy CLI exits, human
exit parity, and complete tree/content immutability.

## Verification

| Check | Result |
| --- | --- |
| focused JSON plus existing doctor tests | PASS — 24 passed, 1 privilege-dependent skip |
| `uv sync --all-groups` | PASS |
| `uv run ruff format --check .` | PASS |
| `uv run ruff check .` | PASS |
| `uv run mypy src` | PASS |
| `uv run pytest` | PASS — 55 passed, 2 privilege-dependent skips |
| `uv run agentready --help` | PASS |
| `uv run agentready --version` | PASS |
| explicit healthy JSON CLI | PASS |
| explicit unhealthy JSON CLI | PASS |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git diff --check` | PASS |
| `git status --short` | REVIEWED |

## Dependencies

No dependencies were added; serialization uses only the Python standard library.

## Deferred work

Schema validation runtime, JSON version migration, detach, repair, and other doctor capabilities
remain deferred.

## Recommendation

Accept DOC-002 as complete.

DOC-002_COMPLETE
