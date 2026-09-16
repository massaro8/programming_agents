# Detachment Contract

A generated repository is considered detachable only when all conditions below hold.

1. Removing AgentReady maintenance metadata does not alter application behavior.
2. Uninstalling/not having AgentReady does not break build, test, lint, type check, or run commands.
3. No application module imports AgentReady code.
4. Agent instructions remain usable as ordinary repository files.
5. No AgentReady account, backend, or network endpoint is required for normal development.
6. The project owner can rewrite or delete generated guidance at any time.
7. Git history belongs to the generated repository.
8. Optional update capability can be permanently removed.
9. `detach` never removes project source, tests, CI, architecture docs, or useful agent guidance.
10. The framework test suite proves detachment with a real generate -> verify -> detach -> verify cycle.

## Required V0.1 acceptance test

```text
A. generate a fixture project
B. run fixture baseline checks
C. run detach
D. assert AgentReady metadata is removed
E. assert no runtime import/reference requires AgentReady
F. run fixture baseline checks again
G. assert AGENTS.md/selected agent adapter remains usable
```

This contract is a product invariant, not a documentation promise.
