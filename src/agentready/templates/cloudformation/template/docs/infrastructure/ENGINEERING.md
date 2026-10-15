# Infrastructure engineering contract

## Defaults and ownership

`stacks/<domain>/` groups resources by responsibility. Only storage is generated;
create IAM, network or compute domains when a real responsibility needs them.
`stacks/catalog.conf` determines order, independently of folder names. In Hybrid,
these assets live beneath `infrastructure/`; scripts and governance stay at the
repository root. `parameters/` and JSON declarations remain optional local inspection
examples; they are not a second deployment input source.

Default CI runs offline verification. No OIDC credential, automatic deploy, IAM
bootstrap or AWS query is part of initialization, tool bootstrap or verification.
`python scripts/project.py bootstrap` prepares local validation tools only.

## Catalog and stack contracts

Each non-comment row has exactly four whitespace-separated fields:

```text
03-storage artifact-storage stacks/storage/artifacts.yaml -
```

Fields: stage, unique stack identifier, unique relative `.yaml` or `.yml` template,
comma-separated enabled environments or `-` (disabled everywhere). Stages use
`NN-domain`, ordered lexically; row order breaks ties. Multiple stacks per stage
are supported. List prerequisites before consumers, including within one stage.
No graph inference or reordering occurs. Duplicate entries, malformed rows,
traversal, symlinks, missing templates and inline bodies above 51,200 bytes fail.
Catalog entries are infrastructure-relative even in Hybrid.

Run `bash scripts/deploy.sh catalog` to check locally without AWS. `verify` runs
this check, shell syntax, fake-AWS engine regressions, cfn-lint, Guard and the
existing positive/negative fixtures. All templates under stacks are linted,
including disabled templates. Missing tools fail with installation guidance.
Use Bash 4+ (Git Bash on Windows); shell files and hooks use LF via `.gitattributes`.

For one selected stack, the optional runner resolves each parameter from:

1. `EnvironmentName` = explicitly selected environment.
2. A uniquely named output from an earlier catalog stack in the same account,
   region and namespace, which exists and is healthy.
3. The template's CloudFormation default (the parameter is omitted from the API input).

Missing required inputs and duplicate output keys fail before change-set creation.
Disabled upstream stacks can supply existing outputs but are never created or
updated implicitly. Missing upstream stacks are diagnosed and skipped; unhealthy
stacks and output access errors fail closed. AccessDenied is never stack absence.
`NoEcho` inputs cannot use Outputs. Never place secrets in Outputs or nonsensitive
parameters. The runner logs resource/key diagnostics, never parameter or output
values; temporary parameter/token files use restrictive permissions and are removed.
Do not enable shell tracing in credential-bearing jobs.

Use Ref/GetAtt/Sub and pseudo-parameters inside a template. Use parameter/output
names as stable inter-stack contracts. AWS-managed SSM parameter types receive
parameter *keys*, typically through template defaults; CloudFormation resolves
them. Supported Secrets Manager/SSM secure dynamic references remain in supported
resource properties and are resolved by CloudFormation, never by this runner.
No custom placeholders, secret retrieval or arbitrary cross-account imports.
Default inputs are applied afresh on UPDATE; existing values are not silently
preserved with UsePreviousValue. Review this in the change set.

## Optional deployment configuration

`deployment/environments.conf` ships with comments only. Every operation except
catalog checking refuses to run until configured. Each row has seven fields:

```text
sandbox sandbox SANDBOX_ACCOUNT eu-west-1 SANDBOX_DEPLOYMENT_ROLE SANDBOX_EXECUTION_ROLE project
```

These are branch, environment, account variable name, explicit region, deployment
role variable name, execution role variable name and namespace. Configure your own
branch/account mapping (for example dev, cert, main); no environment fallback exists.
Each branch/environment must be unique. Version the mapping and catalog enablement;
keep account IDs and role ARN values in Bitbucket deployment variables. The existing
JSON environment contract serves the separate read-only inspection skill and should
be aligned explicitly when that optional workflow is used.

Required Bitbucket deployment variables: the three referenced account/role variables
and `AWS_REGION`. Enable `oidc: true`, associate the exact deployment environment,
and scope trust to issuer, audience, repository UUID and deployment-environment UUID.
The script rejects inherited static credentials/profiles, isolates AWS config files,
uses a temporary web-identity token, checks STS account and assumed role, and rejects
branch/environment/region mismatches. Branch naming alone grants no AWS permission.

Account OIDC provider, operator bootstrap, CI DeploymentRole, CloudFormation
ExecutionRole and application/workload roles have separate ownership/lifecycles.
They are not ordinary catalog stacks. `scripts/bootstrap.sh` is an explanatory refusal;
it creates nothing. There is no generic secure account policy without a workload.
Operators must author least privilege, restrict CloudFormation stack names and region,
constrain `iam:PassRole` to the exact execution role and `iam:PassedToService` to
CloudFormation, and constrain `cloudformation:RoleArn` on change-set creation.
The execution role needs only reviewed resource actions; workload roles should have
an appropriate permissions boundary, including boundary enforcement on role creation.
A boundary is a ceiling, not a grant. Do not use administrator or wildcard defaults.
Offline tests cannot attest deployed trust, permissions, boundaries or account security.

## Review and authorization

The runner needs Bash/coreutils and AWS CLI v2, with no Python packages. Configure
Bitbucket custom steps only after approval; keep default validation enabled. An
operator may use the AWS CLI image for these custom steps. Merge the optional
`deployment/bitbucket-pipelines.yml.example` fragment under `pipelines.custom`,
reviewing its image version and replacing sandbox; retain default validation.
The fragment has no effect until explicitly integrated. Example step body:

```yaml
name: Inspect sandbox (read only)
oidc: true
deployment: sandbox
script:
  - bash scripts/deploy.sh inspect sandbox
```

After separate authorization to create a plan (an AWS mutation):

```bash
bash scripts/deploy.sh plan sandbox artifact-storage --authorize-plan
```

The runner creates one change set and leaves it unexecuted. Review the exact ARN,
resource/property effects, IAM/network/security changes and all Modify operations.
Set `CFN_REVIEWED_IAM=yes` only after authorizing IAM capabilities. Add is not a
security approval; Modify is not inherently safe. Remove, imports, replacement
True/Conditional/unknown, nested stacks and non-resource changes are refused.
Those changes need a separately authorized procedure outside this runner.
Empty change sets succeed without execution. Failed plans remain for manual cleanup.

After reviewing the immutable change set, authorize that exact ARN independently:

```bash
bash scripts/deploy.sh execute sandbox "$CHANGE_SET_ARN" --authorize-execution "$CHANGE_SET_ARN"
```

Execution repeats identity, enabled-catalog membership, availability and change-risk
checks. It also requires the stack's current RoleARN to match the configured
ExecutionRole; absent/different roles require separate operator investigation or
migration. DescribeChangeSet does not expose RoleARN; enforce the role at creation
through IAM as above and review CloudTrail when needed. No role migration is implicit.
Rollback remains enabled. CLI calls have connect/read timeouts; plan polling is
bounded at ten minutes and stack completion at one hour. Failures/rollbacks stop.
The execution status must complete as well as the stack. Do not rerun after a timeout
without inspecting the remote state. No sequence of stacks is transactional; inspect,
plan, review and execute prerequisites in catalog order before consumers. Downstream
stacks are never auto-executed. CloudFormation's own rollback does not undo earlier stacks.

Use provider deployment permissions and independent approval steps for execution.
Do not paste deploy commands into branch/default pipelines or treat flags as IAM
security controls. The generated default pipeline contains no active deployment.

## Local hooks, inspection and independence

Optionally activate the local pre-push hook per clone:

```bash
chmod +x .githooks/pre-push
git config --local core.hooksPath .githooks
```

It runs local verification. No global config is modified; hooks are bypassable and
are not a substitute for CI. Use `PYTHON` to select a compatible Python interpreter.
For optional read-only AWS work, reuse `.agents/skills/aws-infrastructure-inspection`;
its expected read-only role and output allowlist are separate from deployment approval.
Canonical AGENTS.md, Claude views, work/route/receipts/checkpoint/resume, doctor and
detach remain the normal engineering workflow. Removing `.agentready/` keeps all
source, scripts, tests, policies, CI and instructions; no AgentReady runtime is needed.

Authoritative API contracts:
[CreateChangeSet](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-change-set.html),
[DescribeChangeSet](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/describe-change-set.html),
[ExecuteChangeSet](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/execute-change-set.html),
[ValidateTemplate](https://docs.aws.amazon.com/cli/latest/reference/cloudformation/validate-template.html),
[Bitbucket OIDC](https://support.atlassian.com/bitbucket-cloud/docs/deploy-on-aws-using-bitbucket-pipelines-openid-connect/).
