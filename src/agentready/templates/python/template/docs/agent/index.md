# Agent guidance index

Read the canonical `AGENTS.md` first. The `docs/agent/` tree explains HOW to work in this repository;
the `docs/features/` tree records WHAT the repository should deliver. Use the generated feature index
to route work and do not read every feature specification unless the selected feature requires it.
These documents are repository-local guidance and remain useful after detach.

- [Python](standards/python.md)
- [Architecture](standards/architecture.md)
- [Testing](standards/testing.md)
- [Dependencies](standards/dependencies.md)
- [Feature workflow](workflows/feature.md)
- [Bugfix workflow](workflows/bugfix.md)
- [Refactor workflow](workflows/refactor.md)

Feature registry and specifications:

- [Feature registry](../features/index.md) (generated; do not edit manually)
- [Feature template](../features/template.md)

Minimal user prompts are enough because the workflow lives here:

- New work: `Implement this as the next project feature: <requirement>`
- Existing work: `Implement the next ready feature.`

For new work, the agent creates and maintains the specification; the user does not need to edit the
registry. For existing work, use `next-ready` and read only the one returned specification.
