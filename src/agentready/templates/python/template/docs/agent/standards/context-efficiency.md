# Context efficiency

Load context in this order, stopping when the task is clear:

`task/work item -> AGENTS.md -> CODEBASE_MAP -> symbol/search localization -> work specification -> matching skill/workflow and relevant standards -> affected implementation -> neighboring tests`

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

Usually use no sub-agent for typos, formatting, single-file edits, known local features or small
deterministic fixes. Consider one read-only explorer for unknown areas, noisy investigation or
large logs. Consider parallel explorers only for independent domains (API, persistence, tests),
never three agents each reading the entire repository. Recommend a reviewer/specialist only for
architectural or high-risk work. Parallelism primarily helps latency/context isolation; it is not
automatically token saving. Avoid parallel writers on one module.

`python scripts/project.py route <TYPE> --complexity <LEVEL>` recommends effort from structured
inputs. Levels are TRIVIAL, LOCAL, CROSS_MODULE and ARCHITECTURAL; HIGH risk dominates complexity.
Use `--risk HIGH` or a supported `--risk-signal` for auth, payments, migrations, concurrency,
secrets, infrastructure or destructive data changes. Unknown areas use `--unknown-area`;
`--independent-domains N` declares separable exploration scopes. Output includes primary skill,
planning, context, validation, review, sub-agent recommendation and FAST/BALANCED/STRONG class.
These are advisory; the host owns model/reasoning choice, delegation and usage accounting.

Define verification before editing. Run the narrowest relevant tests first, then broaden by the
actual diff, public contracts and risk. Final project checks remain mandatory for completion.
Summarize large logs as outcome, relevant errors, paths and next action; retain raw evidence
outside permanent instructions when needed.

## Handoff and compaction

Pass a compact handoff with exactly these headings:

`OBJECTIVE · SCOPE · EVIDENCE · INVARIANTS · PLAN · ACCEPTANCE · VERIFY · DO NOT CHANGE · OPEN RISKS`

Do not pass the conversation transcript. When compacting context, retain only the
objective, acceptance criteria, frozen decisions, relevant architecture boundary, changed files,
validation state, and unresolved blockers or risks. Drop verbose exploration history.

Use the canonical handoff whenever task state crosses an isolated agent or context boundary and
the receiver needs implementation or review state. An explorer may return a shorter evidence and
localization summary when that is all the receiver needs.

Before a fresh session or context reset, save `project.py checkpoint <id>`; continue with
`project.py resume <id>` and current work state. Verify staleness before trusting prior checks.
Reset after repeated unproductive context expansion when a compact checkpoint can preserve the
accepted scope; do not discard unresolved failures. No automatic reset or token telemetry exists.
