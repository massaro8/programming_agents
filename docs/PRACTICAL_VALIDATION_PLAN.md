# AgentReady V0.1 Practical Validation Plan

## Purpose

This plan defines the next manual validation campaign for the V0.1 practical-validation candidate.
It does not execute the scenarios and does not introduce telemetry. Each run should start from a
recorded AgentReady revision and a fresh generated repository.

## Shared setup and evidence

For every use case:

1. record AgentReady version/revision, operating system, coding agent, and model;
2. create a fresh repository with `agentready init` unless the scenario says otherwise;
3. retain the exact user prompt and initial repository state;
4. record files read, files changed, commands/tests run, retries, and human interventions;
5. run the generated repository's documented gates;
6. preserve the final diff and concise outcome notes.

Stop a run if it requires secrets, a destructive action outside its temporary repository, a
capability deferred beyond V0.1, or an unbounded task expansion.

## UC-01 — Greenfield feature

### Objective

Evaluate whether generated guidance turns a plain OpenRouter requirement into a persistent feature
specification, then steers a coding agent toward explicit boundaries, deterministic tests, justified
dependencies, and a focused diff.

### Setup

Run `agentready init practical-app --profile application`, verify its baseline tests, and open it in
a fresh coding-agent session only after the project owner has:

1. run `python scripts/feature_registry.py new "OpenRouter model catalog"`;
2. written the detailed normative product specification in the resulting BACKLOG file;
3. marked it `READY`, synchronized the registry, and verified `feature_registry.py check` passes.

The human-authored F001 is the fixed input to the implementation session.

### Prompt

> Implement the next READY feature.

### Procedure and evidence

- Observe whether the agent reads `AGENTS.md`, uses `next-ready`, and reads only the human-authored
  F001 specification rather than creating or rewriting product requirements.
- Record its plan, files read/changed, tests added, and verification commands.
- Require the agent to transition `F001` through `IN_PROGRESS` to `DONE`, record the implementation
  result and verification in the spec, and run `python scripts/feature_registry.py check`.
- Compare the normative specification before and after implementation and require it to remain
  unchanged. Material ambiguity must produce BLOCKED plus an exact question, not an assumption.
- Require Ruff format/check, mypy, and pytest to pass.
- Review for unnecessary abstractions, dependency additions, unrelated edits, and missing tests.
- Confirm no `F001` is created in the AgentReady product repository and no issue-tracker, backend,
  telemetry, or unrelated project-management machinery is introduced.

Success means the feature and behavior tests pass on the first accepted implementation or after a
small recorded repair, with no out-of-scope edits.

## UC-02 — Bug investigation

### Objective

Evaluate whether repository guidance produces reproduce → root cause → regression test → minimal
fix → verification behavior.

### Setup

Generate `uc02_bug`, introduce a deterministic defect in `greet` (for example, strip the supplied
name unexpectedly), and add or record a failing reproduction without explaining the root cause to
the agent.

### Prompt

> A reproducible greeting behavior regression has been reported. Investigate it, demonstrate the
> failure, identify the root cause, add a regression test, implement the smallest correct fix, and
> run the repository gates. Avoid unrelated refactoring.

### Procedure and evidence

- Record whether the agent reproduces before editing and whether its diagnosis matches the defect.
- Check that the regression test fails before and passes after the fix.
- Record changed files, retry count, and any speculative edits reverted.
- Require all documented gates to pass.

Success means the minimal fix is supported by a regression test and no unrelated behavior changes.

## UC-03 — Cross-agent parity

### Objective

Compare practical instruction adherence between Codex and Claude Code without treating the result
as a scientific benchmark.

### Setup

Create two byte-identical repositories from the same AgentReady version. Use the same bounded UC-01
feature or UC-02 bug prompt in fresh Codex and Claude Code sessions with no shared conversation
history.

### Procedure and evidence

For each agent record:

- files read and changed;
- whether canonical and on-demand guidance was consulted;
- scope discipline and unnecessary abstractions;
- tests added and commands executed;
- first-pass gate result and retry count;
- human intervention and approximate model usage when available.

Compare outcomes side by side. Success does not require identical diffs; both results must satisfy
the same behavior, scope, and gate criteria.

## UC-04 — Detach and continue

### Objective

Validate the central no-lock-in promise during ordinary agent development, not only in the formal
qualification harness.

### Setup and procedure

1. Generate `uc04_detach_continue` and complete one small feature in a coding-agent session.
2. Run `agentready doctor` and require HEALTHY.
3. Record the repository snapshot and run `agentready detach`.
4. Remove the AgentReady tool environment and confirm `.agentready/` is absent.
5. Start a fresh coding-agent session with no AgentReady context.
6. Request a second small feature using only repository-local guidance.
7. Run sync, Ruff format/check, mypy, pytest, and build.

The second prompt should be comparable in size to UC-01, for example:

> Add a typed method that returns the most recent recorded greeting, including empty-history
> behavior tests. Follow the repository instructions, keep the change focused, and run all gates.

Success requires `AGENTS.md`, `CLAUDE.md`, `docs/agent/**`, and normal Python tooling to remain
sufficient; no AgentReady installation, framework import, or manual guidance reconstruction is
allowed.

## Run record template

```markdown
# Practical validation record — <UC-ID> / <agent>

- AgentReady revision/version:
- Date / OS:
- Agent / model:
- Task completed: yes/no
- First-pass success: yes/no
- Retry count:
- Files read:
- Files changed:
- Tests added/changed:
- Commands run:
- Final gate result:
- Out-of-scope edits:
- Human intervention required:
- Approximate agent/model usage, if available:
- Residual issues:
- Evidence links or diff location:
```

Markdown records are sufficient. V0.1 must not add telemetry or automated model-usage collection.
