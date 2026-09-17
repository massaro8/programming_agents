# DOC-001 Repository Doctor Audit

## Objective

Implement a deterministic, local, fast, read-only `agentready doctor [PATH]` command that can
distinguish a structurally healthy generated Python repository from concrete broken states.

## Initial state

INIT-001 and INIT-002 provided and independently qualified the canonical Copier-generated Python
project. AgentReady did not yet expose repository diagnostics, structured findings, or doctor exit
semantics.

## Doctor health contract

Doctor performs eleven checks in a fixed order. A repository is healthy only when every check
passes. Inspection reads local files only: it does not write, repair, render, access the network,
invoke an LLM, or execute project tools. Unsafe repository-relative paths and symlink components
are rejected before inspection follows them.

All manifest entries are required to exist because the current generated manifest is the complete
ownership inventory emitted by the canonical Python generator.

## Implemented checks

| Check identifier | Contract |
|---|---|
| `project.root` | target exists as a non-symlink directory |
| `manifest.present` | safe `.agentready/manifest.toml` exists |
| `manifest.valid` | schema, profile, generator, version, and ownership tables are supported |
| `ownership.paths` | every ownership entry is a valid `ProjectPath` |
| `ownership.unique` | no path is duplicated within or across ownership classes |
| `ownership.artifacts` | every declared artifact is a safe regular file |
| `guidance.agents` | `AGENTS.md` is declared and present |
| `guidance.references` | local Markdown and `docs/agent/` references from declared guidance exist |
| `repository.structure` | canonical Python configuration, source, tests, CI, and architecture exist |
| `repository.independence` | supported dependency tables are valid and do not declare AgentReady |
| `detach.ready` | the preceding structural prerequisites all pass |

## Finding/status model

`FindingStatus` contains only `PASS` and `FAIL`; a warning state is not needed for the current hard
structural invariants. Frozen, slotted `DoctorFinding` values carry a stable check identifier,
status, message, and optional `ProjectPath`. A frozen, slotted `DoctorReport` carries the ordered
tuple and derives overall health from it. The representation is suitable for DOC-002 serialization
without adding JSON behavior now.

## Exit semantics

- Healthy repository: exit `0`.
- Unhealthy, unsupported, or non-AgentReady target: exit `1`.
- Invalid CLI syntax: argparse exit `2`.

## Human-readable output

The CLI prints `AgentReady Doctor`, deterministic Project/Manifest/Ownership/Agent guidance/
Repository/Detach readiness groups, one `[PASS]` or `[FAIL]` line per stable check, and a final
`RESULT` containing `HEALTHY` or `UNHEALTHY`.

## Positive control

Canonical generated project:
`demo_agentready`

Result:
`HEALTHY`, exit `0`.

## Negative controls

| Corruption | Expected finding | Result |
|---|---|---|
| missing manifest | `manifest.present` FAIL | PASS |
| malformed TOML manifest | `manifest.valid` FAIL | PASS |
| unsupported schema | `manifest.valid` FAIL | PASS |
| missing `AGENTS.md` | `guidance.agents` and declared artifact FAIL | PASS |
| missing referenced workflow | `guidance.references` FAIL with path | PASS |
| missing referenced standard | `guidance.references` FAIL with path | PASS |
| broken local link in `CLAUDE.md` | `guidance.references` FAIL with path | PASS |
| ownership path containing `..` | `ownership.paths` FAIL | PASS |
| duplicate ownership entry | `ownership.unique` FAIL | PASS |
| ownership overlap across classes | `ownership.unique` FAIL | PASS |
| missing declared artifact | `ownership.artifacts` FAIL with path | PASS |
| AgentReady dependency with extras | `repository.independence` FAIL | PASS |
| malformed dependency container/requirement | `repository.independence` FAIL | PASS |
| symlinked path component | artifact/reference checks FAIL | PASS where privilege permits |

## Read-only proof

The focused suite snapshots every directory, file byte sequence, and symlink entry immediately
before inspection and compares the complete tree immediately afterward. The snapshot is unchanged.
Absolute and relative targets also pass when the caller runs from an unrelated directory.

## Files changed

- `src/agentready/cli.py`
- `src/agentready/doctor/__init__.py`
- `src/agentready/doctor/inspector.py`
- `tests/test_doctor.py`
- `docs/audits/DOC_001_AUDIT.md`
- `docs/generated/CODEBASE_MAP.md`

## Tests added/changed

`tests/test_doctor.py` adds the canonical positive control, fixed ordering and repeatability,
human-output and exit-code checks, every mandatory negative control, strict dependency inspection,
complete tree/content immutability, unrelated-CWD coverage, and privilege-aware symlink coverage.

## Verification

| Check | Result |
|---|---|
| targeted doctor tests | PASS — 19 passed, 1 privilege-dependent skip |
| healthy canonical project | PASS — HEALTHY / exit 0 |
| negative controls | PASS — expected stable findings / non-zero |
| read-only verification | PASS |
| uv sync --all-groups | PASS |
| ruff format | PASS |
| ruff check | PASS |
| mypy | PASS |
| pytest full suite | PASS — 50 passed, 2 privilege-dependent skips |
| CLI help/version | PASS |
| CODEBASE_MAP | PASS |
| git diff --check | PASS |

## Dependencies

New production dependencies:

- none

Doctor uses the standard library and the existing BOOT-002 project/ownership primitives.

## Deferred doctor capabilities

- JSON output / DOC-002
- executable quality audit and evidence collection
- detach and repair behavior
- duplicate/conflicting prose diagnostics
- context-budget scoring
- exact generated-adapter policy drift
- Git-state diagnostics
- source-code import scanning

These require later contracts or belong to later roadmap milestones; adding them now would make the
first doctor speculative.

## Relationship to detach

Doctor verifies that the manifest is recognizable, ownership metadata is parseable and coherent,
declared artifacts exist, and the `.agentready/` maintenance boundary can be identified. It does
not infer deletion policy from ownership, simulate detach, or modify any repository state.

## Residual risks / assumptions

- Local guidance extraction deliberately supports ordinary Markdown links and the current
  backtick-form `docs/agent/` references; it is not a full Markdown parser.
- Windows without Developer Mode may skip symlink-creation tests; the safety branch remains active
  and is exercised where the platform permits creating the specimen.
- Dependency inspection covers the supported PEP-style string lists in the canonical
  `project.dependencies`, `project.optional-dependencies`, and `dependency-groups` tables. It does
  not resolve dependency graphs.

## Recommendation

DOC-001_COMPLETE
