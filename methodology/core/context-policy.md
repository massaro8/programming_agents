# Context Policy

Use progressive disclosure.

```text
L0 task + permanent instructions
L1 codebase map + search results
L2 directly affected implementation
L3 directly affected tests + analogous pattern
L4 contracts/schema/ADR when a boundary is involved
L5 neighboring modules/dependency graph if impact remains uncertain
L6 broad exploration only for complex audit/refactor/incident work
```

Always-loaded instructions should stay small. A larger available context window is not a reason to load
more repository material by default.
