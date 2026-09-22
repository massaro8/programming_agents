# PYT-001 audit — Python Template Profiles & Guidance Hardening

## OBJECTIVE

Make the bundled Python starter representative enough for practical validation while preserving
determinism, independence, detachability, framework neutrality, and low permanent context.

## WHY PROFILES WERE INTRODUCED

The original starter was appropriate for a small tool but did not exercise layer ownership during
the planned greenfield application validation. Three bounded shapes now let callers select the
smallest appropriate structure without creating a catalog of duplicated templates.

## PROFILE MODEL

`src/agentready/core/profiles.py` is the deterministic contract shared by generation and doctor.
It defines the supported names, default, ownership paths, and profile-specific required files.
There is no plugin registry or dynamic discovery.

### minimal

Intended for small tools, utilities, experiments, and early prototypes. It remains the default and
preserves the original greeting behavior.

```text
src/<package>/
├── __init__.py
└── main.py
tests/
└── test_main.py
```

### application

Intended for an ordinary Python application expected to grow. `main` and `bootstrap` call the
application layer, which depends inward on domain code. Configuration is consumed at the
composition boundary rather than imported by the application service.

```text
src/<package>/
├── __init__.py
├── bootstrap.py
├── config.py
├── main.py
├── application/
│   ├── __init__.py
│   └── service.py
└── domain/
    ├── __init__.py
    └── errors.py
```

### service

Intended for a deployable but framework-neutral service. It retains the application direction and
adds one concrete console adapter. Adapters depend inward; bootstrap wires the adapter and
application service. No API, database, messaging, repository, or observability package is implied.

```text
src/<package>/
├── __init__.py
├── bootstrap.py
├── config.py
├── main.py
├── application/
│   ├── __init__.py
│   └── service.py
├── domain/
│   ├── __init__.py
│   └── errors.py
└── adapters/
    ├── __init__.py
    └── console.py
```

## TEMPLATE COMPOSITION STRATEGY

The architecture still names Copier as the internal rendering engine. PYT-001 retains one trusted
bundled Copier template. Common files exist once; Copier renders `_exclude` patterns from the
selected answer to omit profile-only directories, while Jinja varies the few files whose content
must be profile-aware. No proprietary renderer, template inheritance mechanism, hooks, remote
template, or duplicated complete template tree was added.

## GENERATED GUIDANCE

`AGENTS.md` remains the short always-loaded policy: purpose/profile, commands, search-before-read,
profile direction, minimum coherent diff, verification, Definition of Done, and routing links.
Detailed durable guidance is split without duplicating workflows:

```text
docs/agent/index.md
docs/agent/standards/python.md
docs/agent/standards/architecture.md
docs/agent/standards/testing.md
docs/agent/standards/dependencies.md
docs/agent/workflows/feature.md
docs/agent/workflows/bugfix.md
docs/agent/workflows/refactor.md
```

Architecture and feature guidance render for the selected profile. Testing distinguishes unit,
integration-on-demand, and regression coverage; dependency guidance requires coherent project and
lock updates.

## MANIFEST CHANGES

The manifest records `minimal`, `application`, or `service` deterministically. The JSON schema
constrains the field to those values. No timestamp or machine-specific value was introduced.

## DOCTOR IMPACT

Doctor resolves the selected profile through the canonical contract and validates that exact
ownership and required artifacts. It therefore neither imposes service files on smaller profiles
nor accepts a manifest whose declared tree disagrees with its selected profile. Inspection remains
local, deterministic, and read-only; human and JSON report contracts are unchanged.

## DETACH IMPACT

Detach accepts each supported manifest profile. Its safety checks and deletion boundary are
unchanged: only `.agentready/` is removed, while source, tests, CI, architecture, `AGENTS.md`,
`CLAUDE.md`, and `docs/agent/**` remain byte-for-byte intact.

## BACKWARD COMPATIBILITY

`agentready init demo_agentready` still works, selects `minimal`, and preserves the original public
greeting behavior and small source/test shape. The manifest now uses the explicit value `minimal`
and the generated guidance corpus is intentionally expanded. Explicit selection uses
`--profile minimal|application|service`; there is no questionnaire.

## TESTS

Focused tests cover default and explicit profiles, invalid selection, exact file trees, absence of
unexpected profile directories, manifest metadata, ownership, deterministic output, independence,
healthy doctor reports, and detach preservation. Existing doctor JSON and detach safety tests remain
part of the full repository suite.

## INDEPENDENT QUALIFICATION

The existing packaged-wheel qualification harness is parameterized across all three profiles. For
each it generates two byte-identical repositories in isolated contexts and runs sync, Ruff format,
Ruff lint, mypy, pytest, runtime independence probes, and build. The formal detach harness likewise
qualifies every profile before detach and repeats sync/lint/type/test/build after removing the tool
environment and `.agentready/` metadata.

## KNOWN LIMITATIONS

- Profiles are deliberate starting shapes, not automatic architecture selection.
- The service adapter is framework-neutral and intentionally does not imply an HTTP deployment.
- PYT-001 provides generation only; it does not migrate an existing generated repository between
  profiles.

## DEFERRED

- data profile
- ML profile
- framework-specific profiles
- adopt
- update

## VERIFICATION STATUS

Coordinator review and gates completed on 2026-09-18:

- `uv sync --all-groups` — passed;
- `uv run ruff format --check .` — 67 files already formatted;
- `uv run ruff check .` — passed;
- `uv run mypy src` — passed for 13 source files;
- targeted init/doctor/doctor-JSON/detach suite — 54 passed, 4 Windows privilege-dependent
  symlink skips;
- packaged independent generation qualification — passed for `minimal`, `application`, and
  `service`;
- formal pre/post-detach qualification — passed for all three profiles;
- `uv run pytest` — 74 passed, 4 Windows privilege-dependent symlink skips;
- `uv build` — sdist and wheel built successfully;
- `uv run python scripts/generate_codebase_map.py --check` — current;
- `git diff --check` — passed.

UC-01 was prepared in the practical validation plan and was not executed.

Final readiness state:

```text
READY_FOR_PRACTICAL_USE_CASE_UC01
```

PYT-001_COMPLETE
