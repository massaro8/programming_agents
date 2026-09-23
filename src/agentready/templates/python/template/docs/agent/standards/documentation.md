# Documentation standard

Evaluate README, architecture, ADR, and other documentation impact on every work item. Record
`NOT_REQUIRED` or the relevant update before DONE; do not change documents mechanically.

Update README when ordinary users or developers need new information about installation, setup,
CLI usage, environment variables, configuration, supported runtimes, public interfaces,
user-visible workflows, important limitations, or getting-started commands. Purely internal
refactors, test cleanup, and invisible bug fixes normally do not need a README edit.

Update `docs/ARCHITECTURE.md` for material changes to boundaries, dependency direction, runtime
components, integrations, persistence, entrypoints, or cross-cutting infrastructure—not local
implementation detail. Create an ADR only for significant, relatively hard-to-reverse decisions;
start from `docs/adr/0000-template.md`, allocate monotonically from `0001`, and keep the decision
project-owned. The local registry validates the impact decision but never writes these documents.
