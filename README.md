# AgentReady

> Bootstrap once. Own the repository forever.

AgentReady bootstraps Python and CloudFormation repositories that coding agents can understand, modify and verify
predictably. It is a small, vendor-neutral engineering layer: generated applications do not import
AgentReady, and normal development requires no AgentReady account, backend or remote service.

It generates family-specific source/templates, checks, CI, AGENTS.md, a codebase map and local
work/skill/continuity tools. The workflow is `init → work → route/skill → implement → verify → detach optional`.

## Quick start

Python 3.12+ and uv are required. From this source checkout (PyPI publication is not assumed):

```bash
uv sync --all-groups
uv run agentready init ../my-project --profile minimal --bootstrap
uv run agentready doctor ../my-project
```

In the generated project:

```bash
python scripts/project.py --help
python scripts/project.py verify
```

Omit `--bootstrap` to generate files without preparing an environment; run
`python scripts/project.py bootstrap` later. Bootstrap failure leaves the repository for repair.
For CloudFormation and Hybrid, bootstrap installs missing cfn-lint 1.57.2 in
`.tools/.venv` and Guard 3.2.1 in `.tools/bin`, using official release archives with
pinned SHA-256 checksums. This opt-in preparation needs network access; subsequent
checks remain offline and find local tools without changing your shell PATH.
Existing tools on PATH are reused; no global installation is performed.
Retry an already initialized project from this checkout with:

```powershell
uv run agentready bootstrap "C:\a_workspace\asia\aws\asia-infrastructure"
```

For a GitHub release installation, download its wheel from
[Releases](https://github.com/massaro8/programming_agents/releases), then use
`uvx --from ./agentready-0.1.0-py3-none-any.whl agentready --help` and the same prefix for init,
doctor or detach. Before publication, `uv build` produces the wheel locally. PyPI is not assumed.

## Three verified project starts

Build a wheel with `uv build`, then run these commands from this checkout.
The qualification used the cached dependencies with `--offline`; omit that flag
when installing dependencies into an empty cache. Nothing here deploys to AWS.

### Python

```powershell
uv tool run --offline --from ./dist/agentready-0.1.0-py3-none-any.whl agentready init ../my-python
cd ../my-python
uv sync --all-groups
python scripts/project.py verify
python scripts/project.py work new --type FEATURE "first task"
```

Fill `docs/work/W001-first-task.md` with the accepted Python scope and acceptance
criteria, then set its status to READY. Ask an agent: “Read AGENTS.md and implement
W001. Transition to IN_PROGRESS, verify with `python scripts/project.py verify
--work W001`, complete the work record, then transition to DONE.”

### CloudFormation

From the AgentReady checkout, with local cfn-lint and Guard on PATH:

```powershell
uv tool run --offline --from ./dist/agentready-0.1.0-py3-none-any.whl agentready init ../my-infra --family cloudformation
cd ../my-infra
python scripts/project.py verify
python scripts/project.py work new --type FEATURE "first task"
```

Fill `docs/work/W001-first-task.md` with the accepted template/parameter/policy
scope, target environment and acceptance criteria; set READY. Ask an agent:
“Read AGENTS.md and the cloudformation-change skill; implement W001 offline.
Transition to IN_PROGRESS, run `python scripts/project.py verify --work W001`,
complete the record and transition to DONE.” Tool installation guidance is in the
generated README. AWS credentials are unnecessary for verification.

### Python + CloudFormation

From the AgentReady checkout, with the same local infrastructure tools:

```powershell
uv tool run --offline --from ./dist/agentready-0.1.0-py3-none-any.whl agentready init ../my-hybrid --with cloudformation
cd ../my-hybrid
uv sync --all-groups
python scripts/project.py verify
python scripts/project.py work new --type FEATURE "first task"
```

Fill `docs/work/W001-first-task.md` with both Python and infrastructure scope,
acceptance criteria and environment; set READY. Ask an agent: “Read AGENTS.md,
the Python feature-builder skill and cloudformation-change skill; implement W001
across both domains. Transition to IN_PROGRESS, run `python scripts/project.py
verify --work W001`, complete the record and transition to DONE.” Infrastructure
lives under `infrastructure/`; verification conservatively checks both domains.

Packaged qualification, exact executed paths and residual limitations are recorded
in [the preparation audit](docs/audits/READY_FOR_PROJECTS_FINAL.md).
No remote CI, publication, deployment or live AWS inspection is claimed.

## Initialize an existing empty Git repository

```powershell
git clone <repository-url>
cd <repository>
agentready init . --into-existing
```

Use `--family cloudformation` or `--with cloudformation` for the other project types;
all Python profiles remain available. From a local wheel, use the same arguments
after `uv tool run --from ./agentready-0.1.0-py3-none-any.whl agentready`.

The repository may contain `.git`, `README.md`, `.gitignore`, `LICENSE`, `LICENSE.md`,
`LICENSE.txt` and `.gitattributes`. Uncommitted bootstrap files are supported.
Git metadata and license/attributes files remain untouched. Existing UTF-8 README
content is retained verbatim, followed by one marked development section. Missing
generated ignore rules are inserted before existing user rules, preserving their
precedence. Existing marked sections, other files/directories and unsafe links are
rejected before publication, with an actionable error. Linked Git worktrees are
not supported; use a normal clone. Bootstrap files are limited to 1 MiB each.

Generation is staged before publication, with rollback on ordinary write errors.
Already initialized projects are rejected. Without `--into-existing`, the target
must still be completely empty. Initialization does not reset, clean, checkout,
commit or push Git. After initialization, synchronize dependencies and run
`python scripts/project.py verify` as described above.

## Which profile should I choose?

| Your goal | Profile | Actual contract |
|---|---|---|
| Control my own package folder structure | `minimal` | Direct `src/<package>/` seed; no prescribed module/layer boundaries. Keep the Python packaging, tests and tooling scaffold. |
| Start with a standard application structure | `application` | Thin entrypoints, bootstrap/config and `modules/<capability>/domain` + `application`; checked import directions and public exports. |
| Use an opinionated service architecture | `service` | Application structure plus an adapter boundary; inward dependencies and resource ownership guidance. |
| Generate infrastructure | `--family cloudformation` (profile `infrastructure`) | Templates, synthetic parameters, Guard policies, fixtures and portable governance; no Python application package. |

Python is the default family and retains all previous invocations. Its default profile is
`minimal`; CloudFormation defaults to `infrastructure`. Incompatible family/profile pairs fail
before generation. Only trusted bundled families are supported.

Choose `minimal` for flexible organization inside the generated Python scaffold. This does not
promise arbitrary build systems or removal of required seed artifacts. Application/service
customization must preserve their checked boundaries; moving code arbitrarily is not supported.

## Generated repository at a glance

| Path | Purpose |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | Canonical starting instructions and thin Claude adapter. |
| `src/`, `tests/`, `pyproject.toml`, `.github/workflows/ci.yml` | Project-owned Python application, tests, dependencies and CI. |
| `templates/`, `parameters/`, `policies/`, `tests/fixtures/` | CloudFormation resources, synthetic inputs and selected security checks. |
| `docs/generated/CODEBASE_MAP.md` | Derived navigation; regenerate after structural changes. |
| `docs/agent/`, `.agents/skills/` | Workflows, standards and skills loaded on demand. |
| `docs/work/`, `docs/changelog/` | Human-owned specifications and generated indexes. |
| `scripts/project.py` | Local command entry point that survives detachment. |
| `.agentready/` | Optional maintenance metadata, removable by detach. |

Use the generated agent index to select exploration, feature, bug investigation, refactoring,
documentation, maintenance or security workflows. Work types select skills; acceptance criteria
and risk determine planning and verification depth. Permanent context stays small; detailed
standards and skills are disclosed only when the task needs them.

## Work item lifecycle

Task → work item → routing/skill → implementation → validation → DONE.

```bash
python scripts/project.py work new --type FEATURE "Add a capability"
```

Fill the created specification with scope and acceptance criteria. After user authorization,
a human or authorized agent authors `Status: READY` in that record, then runs:

```bash
python scripts/project.py work sync
python scripts/project.py work check
python scripts/project.py context --next
python scripts/project.py work transition W001 IN_PROGRESS
```

The transition helper intentionally cannot promote BACKLOG to READY. Continue already accepted
IN_PROGRESS work directly; no rollback or repeated approval is needed. After implementing the
accepted scope, record verification, documentation impact and changelog, transition to DONE and
sync. See generated `docs/agent/workflows/feature.md` and `docs/work/templates/`.

New work items require executed verification evidence before DONE:

```bash
python scripts/project.py sync
python scripts/project.py verify --work W001
python scripts/project.py work transition W001 DONE
python scripts/project.py sync
```

Receipts in `docs/verification/` record commands, exit codes, timestamp, tool identity/version
and input hashes. Failed, missing, expired or stale receipts reject completion. DOCS work uses
proportional registry, skill and navigation checks; other work uses its family's full contract.
Old records without the REQUIRED marker remain compatible. Local evidence detects mistakes and
stale results; it cannot independently attest against an agent able to edit every local file.
See [the evidence contract](docs/VERIFICATION_EVIDENCE.md).

## Token-efficient workflow

Read AGENTS.md and CODEBASE_MAP, search before opening implementation, load skills on demand,
and stop at the minimum sufficient context. Start with targeted checks; broaden validation by
diff and risk. Save a checkpoint instead of replaying the conversation in a fresh session.

AgentReady implements deterministic maps, context pointers, skill checks and checkpoints. Reading
strategy, planning discipline, log summarization and sub-agent use are recommendations followed
by the host. It neither measures token savings nor controls a model's context. See the
[final evaluation](docs/audits/FINAL_PRODUCTIZATION_AUDIT.md).

## Task routing

Generated local tooling extends the existing work-type → skill mapping:

```bash
python scripts/project.py route FEATURE --complexity LOCAL --work-status READY
python scripts/project.py route BUGFIX --complexity LOCAL --risk-signal concurrency
python scripts/project.py route FEATURE --complexity CROSS_MODULE --unknown-area
```

Explicit inputs distinguish TRIVIAL, LOCAL, CROSS_MODULE and ARCHITECTURAL complexity from
NORMAL/HIGH risk. Security/auth/permissions, money/payments, migrations, concurrency, secrets,
infrastructure and destructive data signals dominate small scope. Output recommends skill,
planning, context, validation, review, sub-agent use and abstract FAST/BALANCED/STRONG model class.
`--format json` exposes deterministic data. Status inputs are advisory, not approval evidence.
No model switching, provider calls or worker launching occurs.

CloudFormation selects the `cloudformation-change` skill and infrastructure-specific context.
IAM, network and security-group signals require high-risk scope, impact assessment, rollback
considerations, security review and broader relevant validation. These remain recommendations.

## Sub-agents

Consider one read-only explorer for an unfamiliar area or noisy investigation. Consider scoped
parallel explorers only for explicitly independent domains. Architectural or high-risk work
warrants a reviewer/specialist recommendation. Use compact handoffs, not conversation transcripts.

Avoid delegation for typos, formatting, known local features and small deterministic fixes.
Parallelism can improve latency and context isolation; it does not automatically save tokens.
AgentReady recommends but neither requires nor orchestrates sub-agents.

## Hooks

**Hooks enabled by default: 0.** Activation is explicit and repository-local. No global agent,
Git or shell configuration is changed. `hooks list` inspects recipes; `hooks enable safe-shell
--dry-run` previews activation. A host/developer explicitly invokes preflight; enabling a recipe
does not install automatic command interception.

## Continuity

`python scripts/project.py checkpoint W001` saves bounded work state;
`python scripts/project.py resume W001` returns compact context and staleness warnings.
Validate current repository state before continuing; existing checkpoints require `--replace`.
See [skill QA and continuity](docs/SKILL_QA_AND_CONTINUITY.md).

New/untracked file changes are detected, including before the first Git commit. Projects without
Git use a bounded relevant-file inventory. Explicit `--state` files support scoped continuation.
Checkpoints store compact state and hashes, never transcripts.

## Detach / no lock-in

From the source checkout, `uv run agentready detach ../my-project` removes only recognized `.agentready/` maintenance
metadata. Source, tests, CI, instructions, local routing, work/skill/hook/checkpoint tools and
useful docs remain. Generated projects require neither AgentReady nor Copier/Jinja for normal
development. See [the detachment contract](docs/DETACHMENT_CONTRACT.md).

With the local wheel:

```bash
uvx --refresh-package agentready --from ./dist/agentready-0.1.0-py3-none-any.whl agentready detach ../my-infra
```

CloudFormation templates, policies, parameters, skills and offline verification survive detach.

## Commands and limits

`agentready --help` discovers init, read-only doctor, detach, skill, hooks, checkpoint and resume.
Generated `project.py --help` discovers work, route, context, status, module, skill/evals, hooks,
checkpoint/resume, bootstrap, sync, check, verify and installed-wheel package-check.
Use `<command> --help` for details.

V0.1 supports bundled Python and CloudFormation families and missing/empty init targets. Adoption, updates, remote
templates, provider orchestration, plugins and token telemetry are not implemented. Doctor checks
structure/contracts; it does not execute project tests. CI remains authoritative. Windows may
skip symlink tests when link privileges are unavailable.

Codex uses canonical `AGENTS.md`. `CLAUDE.md` imports it with `@AGENTS.md`; `.claude/skills/`
contains thin views generated from canonical `.agents/skills/` metadata and references.
Explicit `project.py sync` refreshes those views; checks detect drift. Structural qualification
does not guarantee a model follows instructions. Claude runtime loading was not tested on this host.
CloudFormation policies cover selected controls, including a template-level TLS deny baseline;
review policy association and resource coverage when adding buckets. Validation is separate from
any eventual account-aware deployment review. See [the final audit](docs/audits/MULTI_PROJECT_FINAL_AUDIT.md).

Development gates: `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`,
`uv run mypy src`, `uv build`, and `uv run python scripts/generate_codebase_map.py --check`.
See [product scope](docs/PRODUCT_SPEC.md), [architecture](docs/ARCHITECTURE.md), and
[security](SECURITY.md).

For deeper instructions see [the user guide](docs/USER_GUIDE.md). For development and publication,
see [contributing](CONTRIBUTING.md), [release history](CHANGELOG.md) and
[the release checklist](docs/RELEASING.md). Report bugs and questions through
[GitHub issues](https://github.com/massaro8/programming_agents/issues); support is best effort.
Only the latest release receives fixes.

## Recovery and troubleshooting

| Problem | Supported next step |
|---|---|
| Init refuses a target | Use a missing or empty directory; adoption is not implemented. |
| Bootstrap was interrupted | Inspect the retained project and retry `python scripts/project.py bootstrap`. |
| Work/index check fails | Complete the specification and run `work sync`, then `work check`. |
| Busy or stale lock | Confirm the writer has stopped before removing only the reported lock. |
| Malformed metadata or partial detach | Restore trusted original data and follow the recovery procedure. |
| Missing cfn-lint / Guard | Run `agentready bootstrap <project-path>` or the generated `python scripts/project.py bootstrap`; missing tools are installed locally. |
| DONE rejects evidence | Run sync and genuine `verify --work Wxxx` against current inputs; prose alone is insufficient. |

See [recovery and retry](docs/USER_GUIDE.md#recovery-and-retry) for stale locks, interrupted
operations, malformed checkpoints/hooks and partial detach. Doctor diagnoses structure; project
checks execute validation. A passing doctor does not establish passing tests.

## CloudFormation feasibility

CloudFormation alongside a Python application can use its Python profile with separate IaC
checks. CloudFormation-only generation is experimental and is **not a supported profile**.
See [the feasibility experiment](docs/audits/CLOUDFORMATION_FEASIBILITY.md) for the standalone
repository approach and local validation evidence.

## CloudFormation catalog standard

New infrastructure repositories group templates in `stacks/<domain>/`; Hybrid uses
`infrastructure/stacks/` with the same shared governance. A four-column `stacks/catalog.conf`
records lexical stage order, unique stack id, template path (`.yaml`/`.yml`) and enabled
environments (`-` disables). The retained private S3 example starts disabled. Existing
repositories are not migrated or overwritten.

`python scripts/project.py verify` checks the catalog, shell syntax, fake-AWS engine,
cfn-lint, Guard and existing fixtures, alongside normal work/skill/map checks. Python checks
remain in Hybrid. Optional `.githooks/pre-push` is activated per clone with
`chmod +x .githooks/pre-push` followed by `git config --local core.hooksPath .githooks`;
no global configuration changes.

Default pipelines validate offline. The optional Bash/AWS CLI workflow ships unconfigured:
branch/environment/account/region and separate OIDC deployment/execution roles require
explicit setup. Bootstrap IAM is operator owned and outside the catalog. Plan creation
requires authorization; execution requires separately reviewing and authorizing an exact
change-set ARN. No deletion/replacement, automatic downstream execution or secret logging.
Parameters use EnvironmentName, uniquely matching earlier outputs, or native defaults/SSM
keys; supported secure dynamic references stay native to CloudFormation. Sequences are not
transactional. See generated `docs/infrastructure/ENGINEERING.md` and
[ADR 0003](docs/adr/0003-catalog-driven-cloudformation.md) for configuration and limitations.
Detach preserves these ordinary scripts, templates, CI and instructions without an AgentReady
runtime or service.
