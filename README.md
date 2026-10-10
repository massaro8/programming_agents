# AgentReady

> Bootstrap once. Own the repository forever.

AgentReady bootstraps Python repositories that coding agents can understand, modify and verify
predictably. It is a small, vendor-neutral engineering layer: generated applications do not import
AgentReady, and normal development requires no AgentReady account, backend or remote service.

It generates a Python package, tests, CI, AGENTS.md, a codebase map and local work/skill/continuity
tools. The workflow is `init → work → route/skill → build → verify → detach optional`.

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

For a GitHub release installation, download its wheel from
[Releases](https://github.com/massaro8/programming_agents/releases), then use
`uvx --from ./agentready-0.1.0-py3-none-any.whl agentready --help` and the same prefix for init,
doctor or detach. Before publication, `uv build` produces the wheel locally. PyPI is not assumed.

## Which profile should I choose?

| Your goal | Profile | Actual contract |
|---|---|---|
| Control my own package folder structure | `minimal` | Direct `src/<package>/` seed; no prescribed module/layer boundaries. Keep the Python packaging, tests and tooling scaffold. |
| Start with a standard application structure | `application` | Thin entrypoints, bootstrap/config and `modules/<capability>/domain` + `application`; checked import directions and public exports. |
| Use an opinionated service architecture | `service` | Application structure plus an adapter boundary; inward dependencies and resource ownership guidance. |

Choose `minimal` for flexible organization inside the generated Python scaffold. This does not
promise arbitrary build systems or removal of required seed artifacts. Application/service
customization must preserve their checked boundaries; moving code arbitrarily is not supported.

## Generated repository at a glance

| Path | Purpose |
|---|---|
| `AGENTS.md`, `CLAUDE.md` | Canonical starting instructions and thin Claude adapter. |
| `src/`, `tests/`, `pyproject.toml`, `.github/workflows/ci.yml` | Project-owned Python application, tests, dependencies and CI. |
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

## Detach / no lock-in

From the source checkout, `uv run agentready detach ../my-project` removes only recognized `.agentready/` maintenance
metadata. Source, tests, CI, instructions, local routing, work/skill/hook/checkpoint tools and
useful docs remain. Generated projects require neither AgentReady nor Copier/Jinja for normal
development. See [the detachment contract](docs/DETACHMENT_CONTRACT.md).

## Commands and limits

`agentready --help` discovers init, read-only doctor, detach, skill, hooks, checkpoint and resume.
Generated `project.py --help` discovers work, route, context, status, module, skill/evals, hooks,
checkpoint/resume, bootstrap, sync, check, verify and installed-wheel package-check.
Use `<command> --help` for details.

V0.1 supports bundled Python profiles and missing/empty init targets. Adoption, updates, remote
templates, provider orchestration, plugins and token telemetry are not implemented. Doctor checks
structure/contracts; it does not execute project tests. CI remains authoritative. Windows may
skip symlink tests when link privileges are unavailable.

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

See [recovery and retry](docs/USER_GUIDE.md#recovery-and-retry) for stale locks, interrupted
operations, malformed checkpoints/hooks and partial detach. Doctor diagnoses structure; project
checks execute validation. A passing doctor does not establish passing tests.

## CloudFormation feasibility

CloudFormation alongside a Python application can use its Python profile with separate IaC
checks. CloudFormation-only generation is experimental and is **not a supported profile**.
See [the feasibility experiment](docs/audits/CLOUDFORMATION_FEASIBILITY.md) for the standalone
repository approach and local validation evidence.
