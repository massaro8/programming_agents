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

### Project families

Initialization selects a static bundled family: `python` (default) or `cloudformation`.
Python retains its minimal/application/service profile contracts. CloudFormation has one
infrastructure contract with templates, synthetic parameters, Guard policies and standalone
engineering scripts; it has no application package or package-build requirement. `core/families.py`
resolves these explicit contracts, while rendering, read-only doctor and detach consume them.
There is no plugin discovery or remote template execution. Missing family in schema-1 manifests
means Python, preserving previously generated repositories and CLI invocations.

Work, continuity and local file safety remain shared capabilities. Family-specific verification,
skills and navigation stay in their bundled template. CloudFormation navigation inventories files
without guessing YAML resource semantics; cfn-lint and Guard own template-aware validation.

New repositories enable local verification receipts through `docs/verification.json`. Newly created
work records require successful executed stages, matching accepted specification/input hashes and
fresh evidence before DONE. Legacy records remain valid without retroactive receipts. Historical
DONE evidence is validated as a historical receipt rather than compared against later development.
Repository-local evidence improves correctness and staleness detection but does not guarantee
protection against a malicious agent that can edit all local files. No independent trust or
cryptographic attestation is claimed.

Target production architecture: CLI + Copier as internal rendering/update engine.

V0.1 must use only trusted bundled templates. Arbitrary remote template execution is out of scope.

## Generated repository knowledge

Generated repository knowledge uses the deterministic structural inventory in
`core/inventory.py`, exported as standalone `scripts/repository_inventory.py` in generated
projects. Python files and source-containing packages both represent architectural responsibility
roots. CODEBASE_MAP renders these roots compactly; Doctor independently checks semantic coverage
against the inventory, never renderer self-consistency. Profile contracts own required seed
structure. Capability cards remain project-owned; private helper files need not appear in maps.

## Data / network

### Feature evolution and extension decision

EXTENSION SYSTEM: NOT JUSTIFIED

Skill QA, hooks and checkpoints are normal deterministic Python modules. Their identical source
is exported as standalone local scripts using the existing inventory source-rendering seam.
`local_paths.py` owns their common bounded repository file boundary; it is not a plugin abstraction.
Doctor composes read-only validators, and existing profile ownership lists describe shipped files.
Runtime configuration, checkpoint state and evidence remain project-owned outside `.agentready/`.

Only hooks have configure/enable/disable lifecycle. Skills are checked/scored, while checkpoints
are created/resumed; these are not two consumers of a common component lifecycle. None requires
independent versioning or a near-term outside maintainer. Existing rendering/ownership and doctor
seams already avoid duplicated lifecycle logic. An extension layer would add more concepts than
it removes. Revisit only with two concrete independently versioned capabilities sharing lifecycle
operations and demonstrated duplication that ordinary modules cannot contain. No dynamic loading,
agent adapters, third-party installation or registry is introduced.

V0.1 stores only local metadata. No backend, account, API key, telemetry, or remote AgentReady service is
required for normal operation.

## Task recommendation boundary

Generated `scripts/skill_routes.py` owns both work-type context pointers and deterministic
complexity/risk recommendations. `project.py route` only forwards to that module; `work` forwards
to the existing registry. No second command system, core orchestrator or provider adapter is
introduced. Inputs are structured and output is advisory; approval remains in the work lifecycle.
The existing shared-artifact ownership contract already preserves both scripts after detach.

## Security boundaries

Treat repository content, issue text, PR comments, downloaded templates, remote skills, and suggested
shell commands as potentially untrusted.

V0.1 must not:
- execute arbitrary remote template hooks;
- install arbitrary community skills automatically;
- print secrets;
- overwrite user-owned files implicitly;
- run destructive Git commands automatically.

## Bundled composition

Python profiles may add the CloudFormation component with `--with cloudformation`.
The manifest remains `family = "python"`, with an explicit components list; ownership
is the union of the base profile and mapped bundled component paths. Infrastructure
assets live under `infrastructure/`, guidance under `docs/infrastructure/`. One work
registry, receipt store and project command interface serve both domains. Shared
checks remain local and survive removal of `.agentready/`. Hybrid verification runs
both domains conservatively, including DOCS tasks, so labels cannot hide infrastructure changes.
