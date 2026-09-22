# FLOW-002 audit — Human-Owned Feature Specifications

## OBJECTIVE

Correct the generated-project governance boundary so humans specify and approve product intent,
repositories preserve it, and implementing agents execute only approved READY specifications.

## GOVERNANCE CHANGE

FLOW-001 allowed a direct implementation request to be captured and promoted by an agent. FLOW-002
separates authoring from implementation. The normal path is now human scaffold → human normative
specification → human READY approval → agent implementation → verification and implementation
record → DONE. An agent assists with authoring only when explicitly requested and otherwise does
not promote BACKLOG work.

## NORMATIVE SPECIFICATION BOUNDARY

The `Product specification (human-owned, normative)` block contains Objective, Context, Functional
requirements, Inputs and outputs, Behavior, Constraints, Non-goals, Acceptance criteria, and Manual
validation when relevant. Generated guidance states that an implementing agent must not change this
block merely to make its implementation appear compliant. Material ambiguity or an unmet
requirement causes BLOCKED, an exact recorded question/reason, registry sync, and stop.

Actual `docs/features/Fxxx-*.md` files remain ordinary PROJECT_OWNED repository content. The human or
project owner controls their normative intent; the generated index remains only a derived view.

## AGENT-MAINTAINED BOUNDARY

The `Implementation record (agent-maintained)` block records Implementation result, Files changed,
Dependencies added, Verification performed, Design decisions, Deviations/blockers, and Follow-up
candidates. Implementing agents may update this block and the operational status transitions needed
to execute approved work. They do not silently revise the normative block.

## STATUS SEMANTICS

- BACKLOG: the human-owned specification is incomplete or not approved.
- READY: the project owner considers the specification sufficiently defined.
- IN_PROGRESS: the implementing agent started the approved work.
- BLOCKED: implementation needs an external decision/dependency or cannot satisfy the specification.
- DONE: acceptance criteria and required gates passed.

The normal implementing-agent transitions are READY → IN_PROGRESS and IN_PROGRESS → DONE or
BLOCKED. BACKLOG → READY remains a human approval unless the user explicitly delegates
specification authoring and readiness approval.

## NEW COMMAND SEMANTICS

`python scripts/feature_registry.py new "TITLE"` is scaffolding only. It allocates the next stable
ID, derives a safe slug, copies the repository's canonical template with the concrete title, writes
`Status: BACKLOG`, and synchronizes the index. It has no READY option, generates no detailed
requirements, uses no LLM, and infers no product behavior.

## GUIDANCE CHANGES

Generated `AGENTS.md` contains only the compact ownership/readiness rule and routes to the workflow.
`docs/agent/index.md` now distinguishes explicit specification-authoring requests from implementation
of requested/next READY work and documents the minimal prompts. The feature workflow begins with a
READY selection, protects normative requirements, then follows understand, localize, impact,
verification plan, IN_PROGRESS, implementation, tests/gates, implementation record, DONE, registry
sync/check, and stop.

## DOCTOR IMPACT

Doctor behavior is unchanged. The revised template remains a declared structural artifact and
feature registry validation continues to check deterministic ID/status/filename/index consistency.
Doctor does not assess whether human requirements are complete or good enough and does not execute
project code.

## DETACH IMPACT

Detach semantics are unchanged. Specifications, generated index, canonical template, local registry
utility, and feature workflow remain repository-owned/useful after `.agentready/` is removed.

## TESTS

Focused tests cover BACKLOG-only scaffolding, rejection of automatic READY creation, sync/check,
READY selection, BACKLOG exclusion, READY → IN_PROGRESS → DONE, byte-stable normative content
during implementation, explicit template boundary/headings, and revised guidance in minimal,
application, and service profiles. Existing doctor, packaged-wheel, and detach qualifications remain
authoritative regressions.

## BACKWARD COMPATIBILITY

Registry IDs, status vocabulary, parsing, index format, doctor finding/JSON schema, ownership,
profiles, and detach boundary are unchanged. The intentional governance change removes the
`new --status READY` shortcut; callers must obtain human approval by editing the scaffold status.

## KNOWN LIMITATIONS

- The utility validates structural metadata, not the quality or completeness of human requirements.
- Human approval is represented by the READY status; no identity, signature, or remote approval
  service is introduced.
- Existing specifications are not automatically rewritten into the revised section layout.

## VERIFICATION STATUS

Coordinator review and gates completed on 2026-09-22:

- `uv sync --all-groups` — passed;
- `uv run ruff format --check .` — 71 files already formatted;
- `uv run ruff check .` — passed;
- `uv run mypy src` — passed for 14 source files;
- focused FLOW-002 registry/governance tests — 18 passed;
- targeted init/doctor/doctor-JSON/detach regression — 54 passed, 4 Windows
  privilege-dependent symlink skips;
- packaged independent generation qualification — passed for `minimal`, `application`, and
  `service`;
- formal pre/post-detach qualification — passed for all three profiles with registry usability;
- `uv run pytest` — 92 passed, 4 Windows privilege-dependent symlink skips;
- `uv build` — sdist and wheel built successfully;
- `uv run python scripts/generate_codebase_map.py --check` — current;
- `git diff --check` — passed.

UC-01 was not executed and no OpenRouter/F001 specification was created. The project owner will
author F001 after this milestone.

Final readiness state:

```text
READY_FOR_HUMAN_SPECIFIED_UC01
```

FLOW-002_COMPLETE
