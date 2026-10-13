# READY-FOR-PROJECTS-001 qualification

Verdict: **READY — WITH MINOR LIMITATIONS**. All packaged workflows and literal README quick starts passed.
Evidence: `C:/z_personale/agentready_use_cases/ready_for_projects/`.

## 1. Baseline and preservation
HEAD at start: `4c2c3b9275a449ff81428b6d2d0dc755d8d37c2c`.
The existing dirty tree was preserved in `preservation/working-tree.zip`, with
SHA256 inventory, Git status and diff. Previous MULTI_PROJECT evidence remains intact.

## 2. Actual changes
Explicit bundled CloudFormation composition, offline environment and parameter
contracts, bounded optional AWS inspection, domain routing and validation-only CI.
No production dependency, AWS mutation, publish or global configuration change.

## 3. Three project types
Python minimal/application/service, standalone CloudFormation, Python with CloudFormation.

## 4. Hybrid composition architecture
The Python family retains its profile. Its manifest declares the optional component.
Infrastructure paths are mapped under `infrastructure/`; guidance is under
`docs/infrastructure/`. Registry, scripts, receipts and canonical skills are shared.
Conflicting additive paths fail closed. This is bundled composition, without remote hooks.

## 5. AWS inspection skill
Canonical `.agents/skills/aws-infrastructure-inspection/SKILL.md` and a thin Claude view.
Explicit authorization, profile, region, target stack, account and read-only role are
required. STS identity is checked before named-stack metadata inspection. IAM policy
is the actual security boundary. Only allowlisted nonsensitive outputs are returned.

## 6. AWS CLI / Agent Toolkit behavior
Actual local discovery: AWS CLI available; Agent Toolkit unavailable.
Only local help/version discovery was executed. No AWS account was queried.
Unsupported or unavailable toolkit capabilities fall back to local evidence.

## 7. Branch/account mapping
Versioned declarations contain explicit branch mappings and account/role reference
names. Unknown branches, missing references and account/region mismatch fail closed.
The starter declares sandbox only; users must explicitly add other environments.

## 8. Dynamic parameters and outputs
Declarations carry type, source, required, environment and sensitivity. Sensitive
inputs allow Secrets Manager/SSM SecureString dynamic-reference identifiers only.
Offline verification never resolves remote values. Engineering guidance covers
Ref/GetAtt, nested outputs, imports and explicit cross-account/region references.

## 9. GitHub/Bitbucket CI conventions
Validation-only adapters invoke shared repository scripts, install pinned cfn-lint
and verify the official pinned Guard archive digest. Hybrid CI includes Python setup.
OIDC/deployment approvals are future deployment guidance. Remote CI was not run.

## 10. Routing and skills
Explicit `--domain python|infrastructure|aws-inspection|both` routes portable canonical
skills. Python-only repositories reject infrastructure domains. Hybrid verification
conservatively checks both domains, even for DOCS work, so task labels cannot hide changes.

## 11. Work lifecycle
Qualification exercises creation, READY, IN_PROGRESS, implementation, machine receipt,
DONE and doctor. Human-owned specification and completion records remain required.

## 12. Verification evidence
Receipts include stage results, input hashes and tool identity. Changed inputs invalidate
fresh evidence. Completion prose belongs after the accepted specification; changing
specification or documentation-impact fields requires verification again.

## 13. Doctor/detach
Doctor independently checks ownership, canonical skill views and infrastructure map
coverage. All three packaged workflows passed doctor and verification after detach.
A separate three-project hash comparison preserved every ordinary file, excluding
transient caches and environments; see `detach-preservation.json`.

## 14. Packaged installation
Wheel and sdist: `artifacts-delivery/`. `qualify-delivery.py` uses an isolated offline uv
tool environment. All 40 workflow operations passed. Exact commands and logs are
in `delivery-results.json`; all 11 literal README commands passed in
`readme-proof-delivery/results.json`. Wheel SHA256: `b11f0e904407ac463398da219f68771d1a50c1057b59c4260da634adfcb072c9`.

## 15. Local test results
The complete run executed 280 tests: 275 passed, four Windows symlink-privilege
skips, and one failure in the missing-tool guidance. The `.venv` wording was restored
and that exact failing node passed its targeted rerun. Six final targeted tests also
passed, including generated lint/format, initial hybrid map consistency, routing,
environment contracts and mocked inspection. Latest result for every collected node:
**276 passed, 4 skipped, 0 unresolved failures**. The raw full-run exit was 1; it is
not reported as an entirely green fresh run. No expensive full rerun followed this
localized message fix. XMLs and the per-node summary remain in the evidence directory.

Executed checks:

```powershell
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run python scripts/generate_codebase_map.py --check
uv run pytest -q --junitxml=C:/z_personale/agentready_use_cases/ready_for_projects/final-tests.xml
uv run pytest tests/test_cloudformation.py::test_missing_tools_fail_actionably -q --junitxml=C:/z_personale/agentready_use_cases/ready_for_projects/tool-guidance-retry.xml
uv run pytest tests/test_composition.py tests/test_environment_contracts.py tests/test_aws_inspection.py -q --junitxml=C:/z_personale/agentready_use_cases/ready_for_projects/final-targeted.xml
```

The broad run used `UV_OFFLINE=1`. Final Ruff checks passed (134 formatted files),
mypy passed (27 source files), and the generated source navigation map was current.

## 16. Residual limitations
Hybrid work verification is conservative rather than impact-selective. No live AWS,
remote CI, deployment, or actual coding-agent runtime qualification is claimed.
Guard covers selected baseline controls, not comprehensive security assurance.

## 17. Exact setup commands
The final wheel was exercised with these exact initialization commands:

```powershell
uv tool run --offline --from C:/z_personale/agentready_use_cases/ready_for_projects/artifacts-delivery/agentready-0.1.0-py3-none-any.whl agentready init C:/z_personale/agentready_use_cases/ready_for_projects/delivery-python
uv tool run --offline --from C:/z_personale/agentready_use_cases/ready_for_projects/artifacts-delivery/agentready-0.1.0-py3-none-any.whl agentready init C:/z_personale/agentready_use_cases/ready_for_projects/delivery-cloudformation --family cloudformation
uv tool run --offline --from C:/z_personale/agentready_use_cases/ready_for_projects/artifacts-delivery/agentready-0.1.0-py3-none-any.whl agentready init C:/z_personale/agentready_use_cases/ready_for_projects/delivery-hybrid --with cloudformation
```

In the Python and hybrid directories: `uv sync --all-groups`. In each directory:

```powershell
python scripts/project.py verify
python scripts/project.py work new --type FEATURE "first task"
```

The approved specification was filled and marked READY before
`python scripts/project.py work transition W001 IN_PROGRESS`. Both required domains
were changed, synced and verified with `python scripts/project.py verify --work W001`;
completion then passed the DONE transition. Full argv, working directories and exits
are preserved in `delivery-results.json`. The literal portable README commands
were separately tested without repairing or syncing their initial generated maps.

## 18. First-task examples
Python: add a typed application helper. CloudFormation: change a template description.
Hybrid: change the Python helper and infrastructure template in one accepted item,
then verify both domains with `python scripts/project.py verify --work W001`.

## 19. Git status
The final working tree has 56 status entries, including pre-existing changes.
HEAD remains `4c2c3b9275a449ff81428b6d2d0dc755d8d37c2c`. No commit, push, reset or
source cleanup was performed. The original dirty-tree archive and hashes remain intact.

## 20. Final recommendation
**READY — WITH MINOR LIMITATIONS**. Start real projects using the three verified
README workflows. Hybrid checks are deliberately conservative rather than
impact-selective. Live AWS inspection and remote CI require their own future
qualification; offline generation, work verification and detach do not depend on them.
