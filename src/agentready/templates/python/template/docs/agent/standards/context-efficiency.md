# Context efficiency

Load context in this order, stopping when the task is clear:

`task/work item -> AGENTS.md -> docs/agent/index.md -> work specification -> matching skill/workflow -> CODEBASE_MAP -> symbol/search localization -> affected implementation -> neighboring tests`

Do not read all documentation or the whole repository before coding. Search for the relevant
symbol, path, or pattern first; open only matching files and inspect their neighboring tests.
Expand the search when evidence reveals a dependency, contract, caller, or test outside the initial
area. Never infer requirements from implementation when a READY work specification exists.

## Routing effort

- Local or trivial change: work directly.
- Unknown module or verbose exploration: an optional read-only explorer may summarize evidence.
- Bounded mechanical implementation: use a faster/smaller builder when available.
- Cross-module, architectural, or uncertain work: have a stronger coordinator define scope first.
- Security, destructive, or high-risk work: use a strong coordinator and independent review.
- Repeated failure: stop patch loops, revisit the evidence, and escalate reasoning. Review only when
  risk or complexity justifies it.

Use subagents for broad exploration, verbose logs, independent test analysis, read-only review,
security review, or research with separable questions. Do not spawn agents only because they are
available. Avoid parallel writers on one module; where parallel edits are necessary, use isolated
worktree/merge boundaries when available.

## Handoff and compaction

Pass a compact handoff with exactly these headings:

`OBJECTIVE · SCOPE · EVIDENCE · INVARIANTS · PLAN · ACCEPTANCE · VERIFY · DO NOT CHANGE · OPEN RISKS`

Do not pass the conversation transcript unless essential. When compacting context, retain only the
objective, acceptance criteria, frozen decisions, relevant architecture boundary, changed files,
validation state, and unresolved blockers or risks. Drop verbose exploration history.
