---
name: cloudformation-change
description: Implement scoped CloudFormation template, parameter and security policy changes with explicit infrastructure acceptance criteria.
---

# Feature Builder

## Inputs and preconditions
- One human-authorized READY or IN_PROGRESS FEATURE item describing scope, acceptance, constraints, and verification.
- For READY work, transition to IN_PROGRESS before implementation. For accepted IN_PROGRESS work, continue its recorded scope without resetting status or seeking duplicate approval.
- Applicable `AGENTS.md`, codebase map, and repository instructions.
- If scope or acceptance is absent, stop implementation and report the missing decision.

## Procedure
1. Read the repository instructions and generated codebase map; search before opening broad areas.
2. Read the feature spec, owning implementation, analogous patterns, relevant contracts, and tests.
3. Identify user-visible behavior, ownership boundaries, and a narrow verification plan before editing.
4. Use the module-placement skill before creating or moving an infrastructure component.
5. Implement the smallest coherent change. Keep generated infrastructure independent of AgentReady at runtime.
6. Add or update focused tests for the acceptance criteria and update authoritative docs only when the concept changes.
7. Run focused checks first, then the verification required by repository policy and task risk.
8. Record changed files, dependencies, decisions, verification, deviations, and documentation impact in the work item.
9. Sync generated work indexes and transition the item to DONE only after acceptance and required checks pass.

## Context and commands
Start with `python scripts/project.py context --next` (or the explicit work ID); if tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Use `python scripts/project.py verify` for focused tests, then the repository's documented verification command. Consult `docs/agent/workflows/feature.md` for the work record and `docs/agent/standards/` for applicable standards.

## Escalate or stop
Stop before coding when scope, acceptance, ownership, or a required external decision is unclear. Escalate broad architectural changes, incompatible constraints, or checks that cannot be run; record the reason and evidence.

## Evidence of completion
Acceptance criteria are met, relevant checks pass, the work record is complete, indexes are synced, and the item is DONE.

## Purpose
Implement or continue a non-trivial feature from a scoped, human-owned READY or IN_PROGRESS item with explicit acceptance criteria.

## Positive triggers
Use for implementing or continuing a non-trivial feature from a scoped, human-owned READY or IN_PROGRESS FEATURE item with explicit acceptance criteria.

## Exclusions
Do not use for typo-only edits, investigation without accepted scope, or bugs requiring reproduction.

## Output contract
Return a concise outcome, changed files or findings, verification evidence, and unresolved risks. Preserve the owning work item as the durable implementation record.

## CloudFormation conventions

Place resources by responsibility under stacks/<domain>/ (infrastructure/stacks in Hybrid).
Register every deployable template in stacks/catalog.conf: stage, stack id, path, environments
or `-`. Order prerequisites before consumers; names of folders do not schedule deployment.
Use EnvironmentName, unique upstream output names and CloudFormation defaults/SSM parameter
keys. Do not put secrets in Outputs. Validate with scripts/project.py verify, including fake
AWS engine tests; sync maps and skill views. Read docs/infrastructure/ENGINEERING.md before
changing catalog/environment/parameter contracts. Reuse aws-infrastructure-inspection for
explicit read-only AWS work. Default CI never deploys. Optional scripts/deploy.sh requires
explicit configuration, OIDC identity checks, plan authorization and a separate exact-ARN
execution authorization. IAM bootstrap is operator owned, outside the catalog.
