# W007 — CloudFormation catalog standardization

Type: FEATURE
Status: DONE
Verification evidence: REQUIRED

## Normative specification

### Objective
Standardize reusable ASIA conventions in new CloudFormation and Hybrid repositories.

### Context
AGENTREADY-CFN-STANDARD-001 authorizes implementation; current ASIA W018 supersedes parts of the historical report. Architectural scope, high safety impact; no AWS access.

### Functional requirements
- Domain stacks, ordered four-column catalog, explicit environments and unique upstream output contracts.
- Optional Bash/AWS CLI workflow with OIDC identity checks and separate exact change-set authorization.
- Preserve offline governance, Guard fixtures, Python/Hybrid, doctor and detach.

### Inputs / outputs
Bundled templates and generated independent repositories; catalog and explicit deployment configuration.

### Public contract and compatibility
New generated infrastructure layout uses stacks/storage; existing real repositories are untouched. Python CLI compatibility preserved. No automatic migration.

### Constraints
- No live AWS, deployment, publication, ASIA edits or new production dependencies.

### Non-goals
- Deployment graphs, generic IAM policies and account bootstrap automation.

### Acceptance criteria
- Catalog rejects invalid order, duplicates, unsafe paths, malformed rows and missing templates offline.
- Engine rejects ambiguous/missing inputs, mismatched identity and unauthorized execution using fake AWS only.
- Final wheel generates CloudFormation, Hybrid and Python minimal; verification, doctor and detach qualify successfully.

### Manual validation
Offline fake AWS tests and packaged qualification; root Ruff, formatting, mypy, pytest and map freshness; wheel/sdist build.

## Documentation impact

README: UPDATED
ARCHITECTURE: UPDATED
ADR: UPDATED
OTHER: UPDATED

## Changelog

Summary: Catalog-driven infrastructure defaults and optional reviewed Bash change sets.
User impact: USER_VISIBLE
Breaking: YES
Migration: Existing repositories remain unchanged; new scaffold paths change.

## Implementation record

### Result
COMPLETE

### Files changed
See docs/audits/CFN_STANDARDIZATION_001.md for the exact modified-file inventory.

### Dependencies added/changed
None.

### Verification performed
Ruff, format, mypy, full suite plus corrected targeted retests (44 passed, 1 skipped in 374.53s (0:06:14)), wheel/sdist and final packaged CloudFormation/Hybrid/Python lifecycle qualification. Receipt: docs/verification/W007.json.

### Design decisions
Four-column catalog; optional deployment independently configured; no generic bootstrap privileges.

### Deviations or blockers
No live AWS/deployment/IAM attestation; operator bootstrap and other limits are documented in the audit.

### Follow-up candidates
Account-specific IAM bootstrap remains operator owned.

### AgentReady observations
Preserve one governance system and detachable artifacts.
