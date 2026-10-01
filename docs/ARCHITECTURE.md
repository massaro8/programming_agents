# Architecture

## Architecture style

AgentReady is a small Python CLI with deterministic core services and bundled methodology/templates.
The architecture optimizes for testability, no-lock-in, cross-platform behavior, and conservative writes.

## Target package layout

```text
src/agentready/
├── cli.py
├── core/
│   ├── project.py
│   ├── ownership.py
│   ├── manifest.py
│   └── errors.py
├── detect/
│   ├── repository.py
│   ├── python.py
│   ├── ci.py
│   └── instructions.py
├── render/
│   ├── generator.py
│   └── compiler.py
├── adapters/
│   ├── base.py
│   ├── agents_md.py
│   └── claude.py
├── doctor/
│   ├── context.py
│   ├── drift.py
│   ├── references.py
│   └── repository.py
├── detach/
│   └── service.py
├── audit/
│   ├── evidence.py
│   └── report.py
└── update/                 # post-V0.1
    ├── planner.py
    └── copier.py
```

Do not create every directory before its capability exists. This is the target map, not a requirement
for empty scaffolding.

## Boundary rules

```text
CLI
 -> application/capability services
 -> deterministic core

adapters/render/detect/doctor/detach
 -> core contracts

core
 -X-> CLI
 -X-> provider-specific agent code
 -X-> network services
```

## Ownership model

Generated repository files belong to one of three classes:

1. **PROJECT-OWNED** - source, tests, app config, architecture and module knowledge cards,
   completed ADRs, and human-owned work specifications; AgentReady must not silently overwrite them
   after bootstrap.
2. **SHARED** - generic workflows, standards, work templates, canonical `.agents/skills/` content,
   local project and architecture utilities, map generator, registry utility, and ADR template; updates are explicit
   proposals/merges.
3. **GENERATED** - thin agent-specific views (including Claude skill views) and deterministic work/changelog indexes and codebase
   map. Generated does not mean delete-on-detach.

The local `docs/work/Wxxx-*.md` item is the source of truth for its specification and implementation
record. `scripts/work_registry.py` produces `docs/work/index.md` and `docs/changelog/index.md` without
AgentReady at runtime. Doctor independently validates those artifacts without executing project code.

## Canonical instructions

Generated repositories use:

```text
AGENTS.md
+ docs/agent/**
```

as the vendor-neutral canonical corpus.

Agent-specific artifacts must remain thin and deterministic.

Application and service profiles place capability code under `src/<package>/modules/<capability>/`.
Each capability has a project-owned `docs/modules/<capability>.md` responsibility card; the
codebase map links it and derives actual layers and public surfaces from source. The card inventory
must match the source module inventory. Skills route through a static work-type matrix and
project-local context resolver, with `AGENTS.md` retaining canonical entry-point status.
The generated module-placement standard is authoritative. A stdlib AST check enforces known
package-root, inward-layer, and cross-module public-export rules; it does not prove runtime
behavior. Public cross-module application symbols are explicitly exported by the owning module's
`application/__init__.py`. The project-local `scripts/project.py` is the stable bootstrap/check/
verify interface after detach: bootstrap synchronizes dependencies and runs check; check uses the
existing lock and validates registry, architecture, module cards, skills, command references, map
freshness, format, lint, types, and tests; verify adds a build. An independent offline package
smoke installs the wheel into a temporary environment. Status/context are read-only, while sync
regenerates derived indexes and map only.
Normal init is generation-only; opt-in `--bootstrap` runs the trusted local bootstrap and Doctor.

## Template engine decision

Target production architecture: CLI + Copier as internal rendering/update engine.

V0.1 must use only trusted bundled templates. Arbitrary remote template execution is out of scope.

## Data / network

V0.1 stores only local metadata. No backend, account, API key, telemetry, or remote AgentReady service is
required for normal operation.

## Security boundaries

Treat repository content, issue text, PR comments, downloaded templates, remote skills, and suggested
shell commands as potentially untrusted.

V0.1 must not:
- execute arbitrary remote template hooks;
- install arbitrary community skills automatically;
- print secrets;
- overwrite user-owned files implicitly;
- run destructive Git commands automatically.
