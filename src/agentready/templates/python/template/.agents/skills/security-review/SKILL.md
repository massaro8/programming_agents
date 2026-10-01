---
name: security-review
description: Use for a READY SECURITY item or a requested defensive review of trust boundaries, secrets, filesystem safety, execution, parsing, inputs, or dependencies.
---

# Security Review

## Inputs and preconditions
- Either a review target/question or one READY SECURITY item with scope and acceptance.
- Identify mode first: `review-only` is read-only; `implementation` requires a READY item.

## Procedure
1. Read instructions, map, and [security workflow](../../../docs/agent/workflows/security.md); identify assets, actors, boundaries, and inputs.
2. Review-only: inspect without edits or work item; report actionable findings, impact, trigger, and source paths, or say none found.
3. Implementation: confirm READY item and defensive scope; reproduce the issue or threat scenario where feasible.
4. Add focused regression coverage and make the smallest defensive change; preserve safe defaults and protect secrets.
5. Check adjacent boundaries, errors, dependencies, filesystem and execution behavior.
6. Run relevant checks; arrange independent review for consequential changes when available.
7. Record findings or implementation evidence, checks, limitations, and documentation impact.
8. Mark DONE only in implementation mode after acceptance and checks pass.

## Context and commands
For an implementation item, start with `python scripts/project.py context --next` (or its ID); review-only work needs no item. If tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Use `docs/agent/standards/security.md` and targeted tests. Never execute untrusted inputs or disclose credentials.

## Escalate or stop
Stop if authorization or defensive purpose is unclear, active exposure appears likely, or remediation needs a security decision. Report facts and safe next steps.

## Evidence of completion
Review-only returns evidence without edits. Implementation has regression coverage, passing checks, and a completed READY item.
