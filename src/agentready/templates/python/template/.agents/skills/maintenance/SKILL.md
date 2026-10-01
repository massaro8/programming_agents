---
name: maintenance
description: Use for a READY MAINTENANCE item changing dependencies, developer tooling, CI, packaging, or supported runtime versions.
---

# Maintenance

## Inputs and preconditions
- One READY MAINTENANCE item defining component, compatibility range, and acceptance.
- Current dependency declarations, lockfile, CI, and repository policy as relevant.

## Procedure
1. Read instructions, map, and [maintenance workflow](../../../docs/agent/workflows/maintenance.md); search affected configuration.
2. Establish current behavior and versions; identify compatibility and supply-chain effects.
3. Change authoritative configuration and regenerate lock data with the approved tool.
4. Keep development local and deterministic; justify any new production dependency.
5. Verify resolution, runtime compatibility, packaging, and affected CI commands.
6. Review docs/ADR impact and record versions, commands, outcomes, and deviations.
7. Sync indexes and mark DONE only after acceptance and required checks pass.

## Context and commands
Start with `python scripts/project.py context --next` (or the explicit work ID); if tooling is unavailable, follow `AGENTS.md` and `docs/agent/index.md` manually.
Consult `docs/agent/standards/dependencies.md` and applicable CI workflow. Use project lock and verification commands.

## Escalate or stop
Stop if the requested version is unsupported, lock resolution changes unrelated packages materially, or security/compatibility choice lacks an owner decision.

## Evidence of completion
Configuration and lock data agree, compatibility checks pass, changes are recorded, and the READY item is DONE.
