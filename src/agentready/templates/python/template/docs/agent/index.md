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

Normative product requirements are project-owned. Implementing agents must not rewrite them merely
to fit an implementation. Requirement authoring and implementation are separate routes:

- Author a specification only when explicitly requested: run `python scripts/feature_registry.py
  new "TITLE"` or use the template, help structure the human's requirements, and leave the feature
  `BACKLOG` unless the project owner explicitly approves `READY`.
- Implement approved work: consult the registry, select the requested or next `READY` feature, read
  only that specification, and follow the feature workflow.

Minimal user interactions:

- `Create a feature scaffold titled "<title>".`
- `Implement the next READY feature.`

The human may edit a specification directly. The generated index is never edited manually.
