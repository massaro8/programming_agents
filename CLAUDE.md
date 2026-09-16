# CLAUDE.md

Use `AGENTS.md` as the authoritative shared repository engineering policy.

Claude-specific guidance:

- Keep active context task-focused.
- Prefer search and targeted reads over broad repository loading.
- Use skills for repeatable multi-step workflows.
- Use subagents mainly to isolate verbose read-only exploration, logs, validation, or independent review.
- Start a fresh session for unrelated work instead of carrying stale task history.
- When compacting, preserve objective, acceptance criteria, decisions, changed files, validation state,
  unresolved risks, and the next step; discard obsolete hypotheses and raw logs.
