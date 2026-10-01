# HARDEN-002 — Boundary Contracts, Architecture Enforcement & Final Readiness

## OBJECTIVE

Close the high-value engineering gaps identified by AUDIT-001 without turning AgentReady into an
application framework. The output is a detachable, vendor-neutral generated repository that can
be validated independently before a fresh practical use case.

## INPUT AUDIT

The AUDIT-001 generated-application assessment was **MATERIAL HARDENING / PAUSE FOR HARDENING**
in its `docs/audits/GENERATED_REPO_READINESS_AUDIT.md`.
It found sound discovery, module placement, work lifecycle, and detach foundations, but missing
external-boundary rules, incomplete architecture enforcement, weak bootstrap semantics, hard-coded
map content, and unverified profile parity. The audited repository is evidence only; UC-01 is not
implemented during this milestone.

## EXTERNAL I/O CONTRACT

Generated architecture guidance owns HTTP, filesystem, database, queue, SDK, and vendor I/O at the
capability's adapter or outer boundary. Blocking operations need finite bounds where supported;
network calls require finite timeouts. A single owner may retry only plausibly transient and safe
operations. Vendor failures are translated when this provides a stable inward-facing meaning,
preserving the cause. Files, clients, connections, transactions, and streams have explicit cleanup
ownership. No retry or I/O dependency is imposed by default.

## CONFIGURATION CONTRACT

For application and service profiles, `config.py` represents typed settings/loading and
`bootstrap.py` is the composition root. The outer boundary validates required settings and
injects them inward; domain, application, and adapters do not read the process environment
opportunistically. Environment variable names must be documented. Real secret defaults,
committed secrets, machine-specific tracked settings, and secret logging are forbidden. Tests use
explicit settings. The minimal profile does not receive a speculative configuration layer.

## ERROR / LOGGING CONTRACT

Domain errors describe business rejection, adapters translate technical/vendor failures when
useful, application-facing errors express stable use-case semantics, and entrypoints map those to
user/protocol output. Exceptions are caught only for recovery, translation, or meaningful context;
causes are preserved. Modules do not configure logging globally. Report failures once at the
appropriate outer boundary, with safe context and no credentials or raw sensitive payloads.

## TEST BOUNDARY POLICY

Normal tests do not use live internet, cloud accounts, credentials, or developer-local state.
Application tests prefer owned fake collaborators over private-function mocks. Filesystem tests use
temporary paths; adapter tests exercise controlled serialization, parsing, error, and configuration
mapping where relevant. Database integration tests require a real database boundary; E2E tests
cover only critical assembled paths. Multi-capability tests mirror capability ownership without
precreating unused test trees.

## ARCHITECTURE CHECKER MATRIX

The generated AST checker applies modular rules to application and service profiles only. It
rejects unknown package-root implementation buckets. Domain remains inward (own domain,
stdlib, tiny shared primitives); application can use its own domain/application and explicit
public application contracts; adapters can use inward owning-module contracts and technical
libraries; entrypoints cannot reach domain or concrete adapter internals; platform cannot import
business modules; shared remains project-neutral. The minimal profile is intentionally exempt.
Static import/layout checks are deterministic safeguards, not a proof of runtime behavior or
entrypoint thinness.

## CROSS-MODULE CONTRACT

The public surface is the owning capability's `application/__init__.py` exports. Other modules
use those exports, not another capability's domain, adapter, or private implementation modules.
Direct synchronous calls are the default. Events and `shared/` are not workarounds for ordinary
cross-module calls; each needs a concrete independent reason.

## PUBLIC CONTRACT / COMPATIBILITY

Public contracts include documented CLI behavior/options/exits, exported APIs, persisted formats,
schemas, HTTP/event contracts, and documented integrations. A work item changing such a contract
must evaluate breaking impact, migration/compatibility path, README/user documentation, and
tests. No semantic-version or release-automation machinery is added.

## BREAKING / MIGRATION VALIDATION

The generated registry and product Doctor both reject a DONE item with `Breaking: YES` and
placeholder or `NOT_REQUIRED` migration content. A substantive migration/compatibility note is
required. `Breaking: NO` with `Migration: NOT_REQUIRED` remains valid. Validation is syntactic and
does not claim to detect whether the code change is truly breaking.

## DEPENDENCY LIFECYCLE

Generated standards/workflow require declared direct dependencies, coherent `uv.lock`, removal
of unused direct dependencies, compatibility-based constraints, focused compatibility tests, and
required gates. Additions/upgrades require relevant release-note and security-impact review;
unrelated broad upgrades and intentional transitive imports are discouraged. No new dependency
management tooling is added.

## SECURITY DEFAULTS

Generated guidance covers path normalization, containment at use, symlink/traversal behavior,
argument-array subprocesses, safe data-only deserialization, bounded network operations,
destination control where relevant, and redaction of credentials and sensitive fields.

## SECURITY REVIEW MODES

The security-review skill distinguishes read-only review (no READY item or lifecycle mutation)
from SECURITY implementation (READY item, regression, normal gates, independent final review).
The `.agents` and `.claude` delivery adapters remain aligned to the canonical workflow.

## DELEGATED HANDOFF

The existing canonical nine-field handoff is used when task state crosses an isolated agent or
context boundary for implementation/review. Pure localization reports may be shorter. The schema
is not copied into each skill.

## CODEBASE_MAP HARDENING

The generated map is derived from actual entrypoints, capability packages, concise package-level
responsibilities, public application exports, adapters, and test roots. A short module docstring
provides the optional one-line responsibility: no second metadata or module-map system is needed.
Output is profile-aware and deterministic; it avoids demo-function and assumed-CLI facts.

## BOOTSTRAP SEMANTICS

Project-local `bootstrap` performs `uv sync --all-groups`, verifies lockfile creation, then runs
regular `check`. Product `init --bootstrap` calls that trusted project-local command and then
Doctor. Failures report the stage/command and leave the generated repository in place. Normal
`init` remains generation-only.

## PROJECT CHECK / VERIFY SEMANTICS

`check` runs registry, architecture, map freshness, Ruff format, Ruff lint, mypy, and pytest in
that order. `verify` runs `check` and then builds the package. The map is no longer checked only
at the end of `verify`.

## PROFILE PARITY

Minimal remains direct; application and service use module-first architecture. Rendered-profile,
opt-in bootstrap, isolated generation, Doctor, and detach tests passed for all three. Service-only
concerns do not appear in application output.

## DOCTOR IMPACT

Doctor remains read-only, local, non-AI, and non-network. Its work-item validation mirrors the
generated registry's migration rule. No generated script is executed by Doctor, and JSON
diagnostic schema is unchanged.

## DETACH SURVIVAL

The generated project owns its scripts, guidance, tests, registry, changelog, and map. Formal
detach qualification passed for minimal, application, and service: bootstrap/check/verify and
ordinary work remain available without an AgentReady runtime dependency.

## PACKAGED QUALIFICATION

Isolated wheel-based generation and independent generated-project qualification passed for all
three profiles. Source-tree-only rendering was not used as the sole evidence. A separate
`uv build` produced the source distribution and wheel successfully.

## TESTS

Targeted fixtures cover boundary guidance, architecture rules, registry/Doctor migration
consistency, bootstrap stage semantics, map freshness/shape, and rendered profiles. The full
repository suite passed with **138 passed, 4 skipped**; the four skips are Windows symlink tests
unavailable without the host privilege. `uv sync --all-groups`, Ruff format/lint, mypy, `uv build`,
product map freshness, and `git diff --check` passed. The full suite includes packaged-wheel and
detached-project qualification.

## WHAT REMAINS INTENTIONALLY MINIMAL

No framework, ORM, event bus, generic result type, configuration library, retry package,
observability stack, backend, telemetry, or new work type is introduced. Root `AGENTS.md` and
skills remain compact routing surfaces. Module/test layers are created only when needed.

## KNOWN LIMITATIONS

Static checks recognize imports/layout, not dynamic imports, runtime call paths, semantic API
compatibility, actual idempotence, or secret exfiltration. Review and behavior tests remain
necessary. Live vendor integration is deliberately outside ordinary automated tests.

## DEFERRED

OpenRouter UC-01, adopt/update commands, deployment/infrastructure choices, performance and
async/concurrency handbooks, semantic-version automation, and speculative data-model guidance
remain outside HARDEN-002. The next practical validation begins with a freshly generated
application repository.
