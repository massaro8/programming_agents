# Feature workflow

Select one READY FEATURE → read its normative specification → understand the goal and constraints → localize the owning capability → assess impact → define verification → transition IN_PROGRESS → implement the minimum coherent change → targeted tests → required gates → evaluate documentation impact → complete implementation record → complete changelog → DONE → sync registry → stop.

Create a work record with `python scripts/project.py work new --type FEATURE "Work title"`.
Fill its human-owned requirements, acceptance criteria, constraints, and verification plan.
Once the user authorizes that scope, edit the record's `Status: BACKLOG` to `Status: READY`
and run `python scripts/project.py work sync` followed by `python scripts/project.py work check`.
READY is authored in the approved record; the transition helper intentionally does not promote BACKLOG.
Begin with `python scripts/project.py work transition W001 IN_PROGRESS` (using the actual ID).
Use `python scripts/project.py work --help` to discover registry commands.

For an already accepted IN_PROGRESS FEATURE, read its implementation record and any checkpoint.
When a checkpoint exists, validate continuity with `python scripts/project.py resume W001`;
then continue the accepted scope.
Do not reset it to READY or require repeated approval for already authorized work. Escalate only
new ambiguity, a changed scope, or a required external decision.

Preserve human-owned requirements. If they cannot be met or are materially ambiguous, record the exact blocker, transition to BLOCKED, and stop.
