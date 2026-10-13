# ADR 0002: Bundled infrastructure composition

Status: accepted.

Python projects may opt into the bundled CloudFormation component. They retain
their Python family and profile; the manifest records the explicit component.

Infrastructure artifacts are mapped under `infrastructure/`, with component
guidance under `docs/infrastructure/`. One work registry, receipt store and local
command interface own the repository workflow. Canonical skills have thin agent views.

The component uses trusted bundled templates, deterministic path selection and
ownership union. Conflicting paths fail instead of overwriting existing artifacts.
No remote hooks, component marketplace or application runtime dependency is introduced.

Hybrid verification runs both domains conservatively, including documentation work.
This costs more than impact-selective verification but prevents a task label from
suppressing infrastructure checks. Both domains continue to work after detach.
