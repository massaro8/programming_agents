# CFN_STANDARDIZATION_001

Date: 2026-10-15
Work: W007 — CloudFormation catalog standardization

Verdict: **READY — WITH DOCUMENTED LIMITATIONS**

## 1. Source patterns reviewed

Read-only comparison with `asia-infrastructure`: `stacks/catalog.conf`, domain template
locations, `scripts/deploy.sh`, `cfn_lib.sh`, `bootstrap.sh`, `validate.sh`,
`bitbucket-pipelines.yml`, IAM boundary/role structure, W018 and
`docs/infrastructure/DECISION_ANALYSIS_IT.md`. Compared AgentReady family contracts,
rendering/composition, doctor/map/continuity, standalone verification, canonical skills,
fixtures, environment inspection contracts and existing regression tests. No reference
repository files were written, no AWS APIs were contacted and no deployments were performed.
All generated qualification projects live under this repository's ignored build directory.

## 2. Current implementation versus historical report

The report explicitly describes an earlier baseline. Current local ASIA catalog has five
columns, with `auto`/`manual` triggers; W018 separates compute from ordinary branch pushes,
enables storage, and adds workload-boundary wiring. The current workload role template
contains PermissionsBoundary, contrary to the report's earlier missing-boundary finding.
W018 remains IN_PROGRESS in the inspected record; source presence is not evidence of live
application, complete policy correctness or deployed account security. These changes were
inspected and not modified. No claim is made about current AWS state.

## 3–5. Pattern classification

| Pattern | Classification | Treatment |
| --- | --- | --- |
| Domain ownership, ordered catalog, yaml/yml | GENERIC | Canonical generated structure |
| Unique prior output contracts; native defaults/SSM | GENERIC | Small Bash resolver, no secret retrieval |
| Local lint/Guard/security fixtures | GENERIC | Preserved and composed with governance |
| LF shell files and CRLF AWS output handling | GENERIC | Attributes, normalization and native Windows temp paths |
| Bash/AWS CLI deployment and OIDC | OPTIONAL | Unconfigured, explicit inspect/plan/execute workflow |
| Pre-push hook | OPTIONAL | Per-clone opt-in; CI remains authoritative |
| W018 auto/manual compute split | PROJECT-SPECIFIC | No automatic deploy in the generated default |
| Account bootstrap and actual IAM policies | PROJECT-SPECIFIC | Operator owned; no generic privileged template |
| ASIA names, accounts, workstation, GPU, VPC and data prefixes | PROJECT-SPECIFIC | Excluded |
| Prior Python deployment planner and custom placeholders | DEPRECATED | Not recreated; Python remains local governance only |
| Historic deployment on every branch push | DEPRECATED as a default | Validation-only CI retained |
| Historical boundary claim and unfinished W018/live state | INCOMPLETE evidence | No copied security attestation |
| Unconditional Modify execution and output-value logging | INCOMPLETE safety pattern | Separate exact-ARN authorization; no value logs |

## 6. New generator behavior

CloudFormation generates `stacks/storage/artifacts.yaml`, registered but disabled in
`stacks/catalog.conf`. Other domains are created only when useful. The original S3 logical
resources, encryption, versioning, public access blocking, retention and TLS deny remain.
EnvironmentName replaces the synthetic Environment parameter; no real identifiers are added.
The shell workflow, optional pipeline fragment, tests, hook and attributes are bundled in
wheel/sdist. Python minimal remains independent. Existing real projects are not migrated.

## 7. Catalog and parameter contract

Four fields: `NN-domain stack-id stacks/domain/file.yaml env1,env2` or `-`.
Lexical stage order and row order within a stage are deterministic. IDs and template paths
must be unique; malformed rows, traversal, symlinks, missing templates, duplicate environments
and oversized inline templates fail. Both YAML extensions are supported. Prerequisites must
precede consumers; this is not a deployment graph.

EnvironmentName comes from explicit selection. Other inputs use uniquely matching outputs
from earlier same-account/region/namespace catalog stacks, then native defaults. Disabled
upstreams can supply existing healthy outputs. Missing stacks are diagnosed, unhealthy stacks
fail, and output/access errors are not absence. Ambiguity and missing required inputs fail
before change-set creation. NoEcho inputs cannot use Outputs; secret output contracts are
forbidden. SSM keys/defaults and supported resource-property dynamic references stay native.
No cross-account imports or legacy placeholder syntax are added.

## 8. Execution architecture and safety

Standalone Bash/coreutils/AWS CLI: local catalog; read-only inspection; authorized one-stack
change-set creation; separate exact-ARN execution. The workflow never implicitly deploys
prerequisites or consumers. CLI connect/read timeouts and bounded polling apply. Empty plans
succeed without execution. Add/Modify/Remove are distinguished; removals, imports, nested
changes and replacement risk are blocked. Modify/security changes always require review.
Execution rechecks identity, membership, availability, current stack ExecutionRole and risks;
rollback stays enabled. Stack and change-set execution status must complete. Failures stop.
A sequence is not transactional and earlier completed stacks are not rolled back together.

The actual AWS API schema was checked against official CLI documentation. DescribeChangeSet
has no RoleARN field: execution verifies DescribeStacks RoleARN and relies on operator IAM
constraints on the role selected at plan creation. Absent/mismatched roles fail closed;
role migrations are outside this runner. The first proposed schema correction was rejected
by automatic review because it removed role validation; the accepted correction preserved
validation using the supported stack field.

## 9. OIDC and bootstrap

Account OIDC provider, operator bootstrap, DeploymentRole, ExecutionRole and workload roles
are separate. No bootstrap stacks or administrator permissions are generated. The bootstrap
shell entry point explains responsibilities and refuses mutation. Documentation requires
scoped trust, exact PassRole/PassedToService, cloudformation:RoleArn constraints and appropriate
workload boundaries. CI rejects inherited static credentials/profiles, isolates AWS config,
uses a temporary OIDC token and verifies account/assumed role/branch/environment/region.
Neither offline tests nor role-name checks attest actual account-level IAM security.

## 10. Pipeline defaults and opt-in

Default GitHub/Bitbucket pipelines run local verification only. The inactive
`deployment/bitbucket-pipelines.yml.example` supplies separate custom inspect/plan/execute
steps with an AWS CLI image and no Python deployment packages. Operators merge only after
review/configuration, retain default validation and use provider deployment permissions.
`deployment/environments.conf` is comments only initially; all AWS operations refuse to run.
Branch names, environments, account references, explicit region, role references and namespace
are configurable; no branch or production fallback exists. Account values stay outside templates.

## 11. Local validation

The shared verification entry point checks work, synchronized skill views, map, existing
JSON inspection contracts, catalog, Bash syntax, fake-AWS engine, cfn-lint, Guard and unchanged
positive/negative fixtures. Existing compatible tools are reused. Missing tools fail.
Optional `.githooks/pre-push` runs validation; activation is repository-local and bypassable.
Git Bash is selected explicitly on Windows rather than the Windows WSL launcher.

## 12. Hybrid and detachment

Hybrid stores infrastructure assets beneath `infrastructure/`, shares scripts/work/receipts
and canonical skills with Python, and composes checks into its existing verification pipeline.
Doctor, inventory, continuity and ownership recognize stacks and the new optional assets.
Detach preserves all useful scripts, tests, templates, policies, CI and instructions. No
application imports AgentReady or requires an account/backend/service at runtime.

## 13. Actual qualification results

- Final focused regressions: **3 passed in 252.52 seconds** (`test_cfn_standard.py` and `test_composition.py`). Both generated infrastructure families run the fake-AWS engine.
- Final wheel and sdist built successfully with `uv build --out-dir build/cfn-standard/dist`.
- Final wheel SHA-256: `21318532b01438a8f5623cca523394b2f09ac8be5a9753615d12c75850661da3`.
- Isolated installation from that wheel and offline qualification: **CloudFormation, Hybrid and Python minimal PASSED**. Every family completed init, local bootstrap, explicit work lifecycle, full verification receipt, DONE, healthy managed doctor, detach and successful standalone verification after detach.
- The generated shell engine and catalog were compared byte-for-byte with the final wheel; default pipelines contain no active deployment command.
- An extra doctor probe after CloudFormation detach returns exit 1 for the missing maintenance manifest, as expected by the existing managed-repository contract. The aggregate qualification explicitly checks that result; the standalone post-detach verification passes.
- Ruff, format, mypy (29 source files) and map freshness passed after corrections. W007 has an executed, input-hashed receipt in `docs/verification/W007.json`.
- Complete suite executed: **295 passed, 4 skipped, 4 failed, 3 errors** in 7525.17 seconds. The four skips require unavailable Windows symlink privileges. The initial failures/errors were a real adoption collision on existing `.gitattributes` (two cases), an obsolete navigation-test path, and four installed-console/PATH cases.
- Corrected adoption to preserve existing owner attributes unchanged; updated the drift test to the new stack path; reran with `.venv/Scripts` on PATH. All failed/error cases and neighboring modules now pass: **44 passed, 1 skipped in 374.53s (0:06:14)**. This is a complete-suite run followed by targeted repairs/retests, not a claim that a second complete suite was run.
- Earlier checks exposed and corrected Hybrid lint/format, the Doctor directory requirement, and accidental Hybrid catalog/test path rewriting. A stale full-suite process was stopped and restarted against the final sources.
- Detailed final packaged logs: `qualification-release-cloudformation.log`, `qualification-release-others.log`, `qualification-release-summary.log`; source suite: `pytest-final.log`, all beneath the ignored log directory.

Detailed transient logs: `build/cfn-standard/` (ignored).

## 14. Files modified

- `README.md`
- `docs/ARCHITECTURE.md`
- `docs/adr/0003-catalog-driven-cloudformation.md`
- `docs/audits/CFN_STANDARDIZATION_001.md`
- `docs/generated/CODEBASE_MAP.md`
- `docs/verification.json`
- `docs/verification/W007.json`
- `docs/work/W007-cloudformation-catalog-standardization.md`
- `docs/work/index.md`
- `src/agentready/continuity.py`
- `src/agentready/core/families.py`
- `src/agentready/doctor/infrastructure.py`
- `src/agentready/doctor/inspector.py`
- `src/agentready/render/existing.py`
- `src/agentready/render/generator.py`
- `src/agentready/templates/cloudformation/template/.agents/skills/cloudformation-change/SKILL.md`
- `src/agentready/templates/cloudformation/template/.claude/skills/cloudformation-change/SKILL.md.jinja`
- `src/agentready/templates/cloudformation/template/.gitattributes`
- `src/agentready/templates/cloudformation/template/.githooks/pre-push`
- `src/agentready/templates/cloudformation/template/AGENTS.md`
- `src/agentready/templates/cloudformation/template/README.md.jinja`
- `src/agentready/templates/cloudformation/template/deployment/bitbucket-pipelines.yml.example`
- `src/agentready/templates/cloudformation/template/deployment/environments.conf`
- `src/agentready/templates/cloudformation/template/docs/ARCHITECTURE.md`
- `src/agentready/templates/cloudformation/template/docs/adr/0001-catalog-driven-cloudformation.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/architecture.md.jinja`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/context-efficiency.md`
- `src/agentready/templates/cloudformation/template/docs/agent/standards/module-placement.md.jinja`
- `src/agentready/templates/cloudformation/template/docs/infrastructure/ENGINEERING.md`
- `src/agentready/templates/cloudformation/template/docs/verification.json`
- `src/agentready/templates/cloudformation/template/scripts/bootstrap.sh`
- `src/agentready/templates/cloudformation/template/scripts/cfn_lib.sh`
- `src/agentready/templates/cloudformation/template/scripts/deploy.sh`
- `src/agentready/templates/cloudformation/template/scripts/generate_codebase_map.py`
- `src/agentready/templates/cloudformation/template/scripts/infrastructure_checks.py`
- `src/agentready/templates/cloudformation/template/scripts/validate.sh`
- `src/agentready/templates/cloudformation/template/stacks/catalog.conf`
- `src/agentready/templates/cloudformation/template/stacks/storage/artifacts.yaml`
- `src/agentready/templates/cloudformation/template/templates/storage.yaml`
- `src/agentready/templates/cloudformation/template/tests/engine/aws-fake.sh`
- `src/agentready/templates/cloudformation/template/tests/engine/run.sh`
- `tests/test_cfn_standard.py`
- `tests/test_composition.py`
- `tests/test_family_lifecycle.py`

## 15. Remaining limitations

- No live deployment, OIDC login, IAM role creation or deployed policy verification was tested.
- Bootstrap is deliberately operator-owned; account policies/boundaries need workload-specific design.
- One stack per separately reviewed operation; no automatic multi-stack execution or transaction.
- Nested changes, imports, deletion/replacement, role migration and templates above the inline limit require another authorized procedure.
- Optional deployment mapping is distinct from the retained read-only inspection JSON contract; operators align both when using both workflows.
- Bash 4+/coreutils and AWS CLI v2 are required for optional deployment. Static validation proves selected controls, not complete infrastructure safety.
- Adoption preserves user-owned `.gitattributes` byte-for-byte; operators must explicitly merge any desired shell LF rules into an existing file.
- Existing repositories are unchanged; generated scripts remain usable with the tooling/version they own. No automatic template adoption/migration is performed.

## 16–17. Exact generation commands

After installing the final wheel (`python -m pip install path/to/agentready-0.1.0-py3-none-any.whl`):

```bash
agentready init my-infrastructure --family cloudformation
cd my-infrastructure
python scripts/project.py bootstrap
python scripts/project.py verify
```

```bash
agentready init my-hybrid --with cloudformation
cd my-hybrid
python scripts/project.py bootstrap
python scripts/project.py verify
```

Python minimal compatibility: `agentready init my-python --profile minimal`.
These commands prepare/validate local repositories; they do not deploy.

## Authoritative contracts

[CreateChangeSet](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-change-set.html),
[DescribeChangeSet](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/describe-change-set.html),
[ExecuteChangeSet](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/execute-change-set.html),
[ValidateTemplate](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/validate-template.html),
[Bitbucket OIDC](https://support.atlassian.com/bitbucket-cloud/docs/deploy-on-aws-using-bitbucket-pipelines-openid-connect/).
