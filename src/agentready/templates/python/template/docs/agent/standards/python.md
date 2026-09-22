# Python standard

- Use `pathlib` instead of manual path concatenation.
- Prefer typed, explicit APIs and small modules with one clear owner.
- Avoid hidden global mutable state; pass state and configuration explicitly.
- Keep I/O and other side effects at boundaries.
- Reuse an existing pattern before introducing an abstraction.
- Add no dependency without a concrete, documented justification.
- Do not create generic `utils` or `helpers` dumping grounds.
- Preserve the import direction documented for the selected profile.

Application code remains independent of AgentReady and framework-specific assumptions.
