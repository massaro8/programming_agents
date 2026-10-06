# W002 — Portable skill evaluation

Type: FEATURE
Status: DONE

## Normative specification

### Objective
Validate trigger fixtures and score externally supplied behavioral observations.

### Context
Strengthen engineering guarantees without runtime services or lock-in.

### Functional requirements
- Validate trigger fixtures and score externally supplied behavioral observations.

### Inputs / outputs
Repository-local files and explicit CLI actions.

### Constraints
- Preserve ownership, detach and existing CLI compatibility; stdlib only.

### Non-goals
- Agent adapters, dynamic plugins and model execution.

### Acceptance criteria
- Validate trigger fixtures and score externally supplied behavioral observations. Tests cover malformed and valid inputs.

### Manual validation
Automated targeted tests followed by repository quality gates.

## Documentation impact

README: UPDATED
ARCHITECTURE: UPDATED
ADR: NOT_REQUIRED
OTHER: UPDATED

## Changelog

Summary: Portable lexical trigger fixtures and external observable results with evidence; no agent/model runner or provider binding.
User impact: USER_VISIBLE
Breaking: NO
Migration: NOT_REQUIRED

## Implementation record

### Result
COMPLETE

### Files changed
src/agentready/skill_qa.py; canonical and bundled evals/cases.json; profile exports; tests/test_evolution.py; docs/SKILL_QA_AND_CONTINUITY.md.

### Dependencies added/changed
None.

### Verification performed
uv run pytest: 212 passed, 4 Windows symlink-privilege skips; final focused skill/evolution rerun: 37 passed after protected-full-ref and native Windows exit-status fixes. Ruff lint/format, mypy src, codebase-map freshness and uv build passed. Formal detachment qualified all three profiles; source skills and generated standalone checks passed.

### Design decisions
Portable lexical trigger fixtures and external observable results with evidence; no agent/model runner or provider binding.

### Deviations or blockers
None. Completion interception remains deferred under the approved no-adapter scope because no existing host callback is available. Four symlink cases need Windows privileges unavailable here.

### Follow-up candidates
Agent host callbacks and external/model eval runners remain deferred; no extension framework is added.

### AgentReady observations
Shared stdlib source export avoids a generated-project dependency on AgentReady; existing ownership and detach boundaries suffice.

