# W006 — Feature evolution regression audit

Type: FEATURE
Status: DONE

## Normative specification

### Objective
Verify compatibility, generation, detach and quality gates; record final audit.

### Context
Strengthen engineering guarantees without runtime services or lock-in.

### Functional requirements
- Verify compatibility, generation, detach and quality gates; record final audit.

### Inputs / outputs
Repository-local files and explicit CLI actions.

### Constraints
- Preserve ownership, detach and existing CLI compatibility; stdlib only.

### Non-goals
- Agent adapters, dynamic plugins and model execution.

### Acceptance criteria
- Verify compatibility, generation, detach and quality gates; record final audit. Tests cover malformed and valid inputs.

### Manual validation
Automated targeted tests followed by repository quality gates.

## Documentation impact

README: NOT_REQUIRED
ARCHITECTURE: NOT_REQUIRED
ADR: NOT_REQUIRED
OTHER: UPDATED

## Changelog

Summary: Independent generation/detach qualification plus narrow feature regressions and full existing quality gates; no unrelated refactoring.
User impact: INTERNAL
Breaking: NO
Migration: NOT_REQUIRED

## Implementation record

### Result
COMPLETE

### Files changed
tests/test_evolution.py; tests/test_init.py; tests/test_generated_project.py; docs/audits/FEATURE_EVOLUTION_AUDIT.md; generated map/work/changelog indexes.

### Dependencies added/changed
None.

### Verification performed
uv run pytest: 212 passed, 4 Windows symlink-privilege skips; final focused skill/evolution rerun: 37 passed after protected-full-ref and native Windows exit-status fixes. Ruff lint/format, mypy src, codebase-map freshness and uv build passed. Formal detachment qualified all three profiles; source skills and generated standalone checks passed.

### Design decisions
Independent generation/detach qualification plus narrow feature regressions and full existing quality gates; no unrelated refactoring.

### Deviations or blockers
None. Completion interception remains deferred under the approved no-adapter scope because no existing host callback is available. Four symlink cases need Windows privileges unavailable here.

### Follow-up candidates
Agent host callbacks and external/model eval runners remain deferred; no extension framework is added.

### AgentReady observations
Shared stdlib source export avoids a generated-project dependency on AgentReady; existing ownership and detach boundaries suffice.

