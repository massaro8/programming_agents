# PRODUCTIZE-001 audit

## OBJECTIVE

Make generated AgentReady repositories independently navigable, maintainable, scalable, and verifiable through deterministic local tooling while retaining Copier rendering and full detachment.

## INPUT VALIDATION EVIDENCE

The prior OpenRouter practical report recorded `VALIDATED_WITH_MINOR_GAPS`: new modules lacked responsibility in the generated map and malformed DONE headings produced an unhelpful registry diagnostic. That repository was read only for evidence; this milestone uses fresh generated repositories for qualification.

## VALIDATE-FIX RESULTS

The generated map now draws responsibility from project-owned module cards. DONE heading diagnostics name the item, expected heading, and malformed heading. Regression tests cover both wrong heading levels.
The read-only security campaign exposed a Windows junction escape in generated work-registry boundary checks. A regression first failed and then passed after a minimal `Path.is_junction()` guard was added alongside symlink checks.

## SKILLS V2 DESIGN

Eight skills are operational, scoped procedures with inputs, actions, stop conditions, and completion evidence. Canonical content is under `.agents/skills/`; Copier renders Claude views from it. Skills point to local context resolution and canonical workflows rather than duplicating standards.

## SKILL CONTRACTS

`AGENTS.md` remains the public entry point. Skills are on-demand; the human-owned work specification remains normative. Review-only security work is read-only and needs no READY implementation item; implementation does.

## SKILL ROUTING

`scripts/skill_routes.py` maps all six work types to one skill, workflow, and narrow standards set. Repository exploration and module placement remain conditional auxiliary skills.

## SKILL VALIDATION

`scripts/skill_check.py` checks the expected skill set, frontmatter, unique useful descriptions, local references, routes, security modes, and exact provider parity. `project.py check` runs this gate.
`project.py` exports the routine command names; `command_check.py` validates public documentation and skill references against them, including essential bootstrap/check/verify references in README, AGENTS, and the map.

## SKILL EVAL FIXTURES

Generated `tests/fixtures/skill_routing.json` supplies deterministic work-type scenarios, not a live model evaluation or provider dependency.

## MODULE KNOWLEDGE MODEL

`docs/modules/<capability>.md` is project-owned and records responsibility, public surface, boundaries, and tests. The map derives actual layers and links from source plus cards; missing or orphan cards fail validation.

## MODULE CREATION UX

`project.py module new` delegates to `module_knowledge.py`, validates names, refuses overwrite, creates only the package root and card, and regenerates the map. Existing-module work does not create another card.

## CODEBASE_MAP SCALABILITY

Map output remains compact and deterministic; a synthetic 32-module test exercises card inventory, generation, and ordering. The map is generated, not an independent policy document.

## CONTEXT RESOLVER

`project.py context --next` or an explicit W ID returns item status, work type, skill, workflow, specification path, map path, relevant standards, verification command, and `UNKNOWN` for a module not deterministically known. It does not concatenate source documents or mutate work state.

## PROJECT STATUS/SYNC/NEXT UX

`status` summarizes profile, work counts, next READY, registry/map freshness, architecture, module, and skill health without a test-suite run. `sync` regenerates only registry indexes/changelog and map. `next` is a read-only context shortcut; no inspection auto-transition occurs.

## FINISH AUTOMATION DECISION

Deferred. The existing registry owns legal transitions and DONE validation. A second orchestration path in `project.py` would duplicate lifecycle rules and could imply semantic completion merely from passing tests. Agents complete human-owned records and invoke the registry explicitly.

## DEPENDENCY REPRODUCIBILITY

`bootstrap` performs `uv sync --all-groups` and may create/update the lock. `check`/`verify` invoke `uv run --locked`; only `verify` adds a build. There is no AgentReady runtime dependency in generated applications. Product policy remains stdlib-first and direct dependencies must be declared.

## PACKAGE ARTIFACT SMOKE

`package-check` builds a wheel offline, installs it into a temporary offline environment, imports the installed package, and exercises CLI help when present. It does not require `.agentready/` and leaves no project-local build output or lock change.

## WORK REGISTRY SCALE

A synthetic 300-item test covers parse, sync, check, next ID, and deterministic repeated output without committing hundreds of work files.

## MODULE SCALE

The synthetic module/card qualification covers 32 capabilities and map generation. No speculative layers or global buckets are added.

## BEST-PRACTICE REVIEW

Packaging/src layout, CLI contracts, direct dependencies, lock discipline, boundary-focused tests, and local security guidance are strengthened by installed-wheel smoke and static checks. No global coverage threshold, web/database framework, semantic-version automation, or live-network test is warranted. Existing optional CI stays optional; no additional CI provider contract is introduced.

## SUBAGENT POLICY

Bounded independent slices used Luna for skill contracts, module knowledge, and package smoke; the coordinator owned cross-slice integration. A separate fresh Luna agent was used for the generated-project context-independence test. Small localized edits remained direct.

## OPTIONAL AUTOMATION DEFERRED

Provider hooks, mandatory pre-commit, work-item archival, `finish`, and CI-provider-specific automation remain deferred. Local deterministic commands are the canonical mechanisms.

## PROFILE MATRIX

Minimal remains direct; application and service use capability modules, with the service adapter only where needed. Automated generated-project qualification passed all three profiles, including bootstrap, local checks, installed artifact, and detach. The final product suite was `164 passed, 4 skipped` on Windows; skips require unavailable symlink privileges.

## CROSS-PLATFORM RESULT

Windows is exercised directly. Scripts use pathlib and argument-array subprocess calls; no bash, chmod, or symlink privilege is assumed. Linux qualification is pending available CI evidence.

## DETACH SURVIVAL

Detachment removes only optional `.agentready/` metadata. In the practical application, a post-detach W005 feature reached DONE with local `check` (17 tests) and `package-check` passing, and `.agentready/` stayed absent. Formal detach qualification passed for minimal, application, and service.

## PRACTICAL CAMPAIGN

A new local application repository was generated from the built AgentReady wheel, separate from the prior OpenRouter repository. W001 was implemented from a READY specification by a fresh subagent with no product-source context and completed through DONE/sync, `verify`, installed-wheel smoke, and status health. W002 extended the same counter without a new module/card; W003 added a separate labels capability/card; W004 completed a no-code dependency audit with evidence. A SECURITY review-only pass changed no files (97 hashes unchanged) and found the junction issue above. Doctor reported HEALTHY, then detach removed only `.agentready/`. W005 extended labels after detach, reached DONE/sync, passed local `check` with 17 tests and `package-check`, and left `.agentready/` absent.

## KNOWN LIMITATIONS

The bundled template is Python-only. Static routing fixtures test deterministic policy, not model-choice quality. No Linux run has yet been claimed for this milestone.
The registry's junction guard is a deterministic preflight rather than an atomic no-follow filesystem API; concurrent hostile mutation between validation and write remains outside V0.1's local-trusted-repository model.

## DEFERRED

Frameworks, remote services/accounts, mandatory Git/CI/hooks, live-network normal tests, provider-specific policy, nested agent instructions, coverage percentage, and speculative performance infrastructure are intentionally excluded. Another hardening cycle is not justified absent multi-project validation evidence.

## VERIFICATION

Final Windows run: `uv sync --all-groups`, Ruff format/check, `mypy src`, `uv run pytest -q` (164 passed, 4 privilege-dependent symlink skips), `uv build` (sdist and wheel), generated codebase-map check, and `git diff --check` all passed. Focused package smoke passed for minimal/application/service, including after removing `.agentready/`; isolated installed AgentReady wheel exposed the expected CLI. The practical detached application passed `project.py check` (17 tests) and `package-check`.

## FINAL DECISION GATE

1. Skills are more operational without duplicating whole handbooks: yes; each has a bounded procedure and links to canonical workflows/standards.
2. A fresh agent can find the correct workflow with almost no prompt: yes in the W001 observed campaign; broader providers remain for multi-project validation.
3. Relevant context can be resolved without broad reading: yes, via `context --next` and the compact map.
4. Module knowledge remains navigable with dozens of capabilities: yes in the 32-module synthetic qualification; real large-project validation remains next.
5. Deterministic tooling detects architecture/work/skill drift: yes through local checks and focused negative tests.
6. Installed artifacts are tested: yes, offline wheel smoke checks install, import, and CLI help where applicable.
7. Mutation semantics are distinct: yes; bootstrap syncs, check is locked, verify is locked plus build.
8. Detach preserves ordinary work: yes in the W005 practical continuation and formal three-profile tests.
9. Profiles remain proportionate: yes; minimal has direct src layout, application modules, and service adapter only where needed.
10. Another automatic hardening cycle is justified: no; next evidence should come from distinct fresh projects and Linux CI where available.
