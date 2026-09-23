# AgentReady

> Bootstrap once. Own the repository forever.

AgentReady is a small, vendor-neutral CLI that generates a Python repository with concise coding-
agent guidance, checks its structural integrity, and can remove its own maintenance metadata. The
generated application remains an ordinary repository: it does not import AgentReady or require an
AgentReady account, backend, network service, Copier, or Jinja for normal development.

## Status

Version 0.1.0 is a **practical-validation candidate**, not a production-stable release. The V0.1
surface is intentionally limited to:

- `agentready init PATH`
- `agentready doctor [PATH] [--format human|json]`
- `agentready detach [PATH]`

Adoption of existing repositories, updates, synchronization, an audit command, additional language
profiles, remote templates, plugins, telemetry, accounts, and hosted services are not implemented.

## Requirements and installation

AgentReady requires Python 3.12 or newer. This repository has not been published to PyPI; from a
source checkout, install and run it with uv:

```bash
uv sync --all-groups
uv run agentready --help
uv run agentready --version
```

Once a distribution is published, the intended transient invocation is:

```bash
uvx agentready init my-project
```

No AgentReady installation is needed inside the generated project.

## Quickstart

From the directory where the new project should be created:

```bash
uv run agentready init my-project
uv run agentready doctor my-project
uv run agentready doctor my-project --format json

cd my-project
uv sync --all-groups
uv run pytest
```

The generated repository also documents its complete Ruff, mypy, pytest, and build workflow. To
stop using AgentReady while keeping the application and its guidance:

```bash
# From the parent directory:
cd ..
uv run agentready detach my-project

# Or, with the CLI installed, from inside the generated project:
agentready detach .
```

`detach` removes only the recognized `.agentready/` maintenance boundary. It preserves source,
tests, configuration, CI, README, architecture documentation, `AGENTS.md`, `CLAUDE.md`, and
`docs/agent/**`, `docs/work/**`, `docs/changelog/**`, `docs/adr/**`, and the local
`scripts/work_registry.py` utility. A second detach returns a deterministic non-zero “not managed or
already detached” result.

Generated projects track six kinds of work under `docs/work/`. Humans approve normative specifications
as `READY`; agents follow the type-specific workflow, record verification and documentation impact,
then synchronize the deterministic work index and changelog. The local registry remains usable after
detach and has no AgentReady runtime dependency.

## What doctor checks

Doctor is read-only, deterministic, local, and non-AI. For the bundled Python profile it checks:

- AgentReady manifest identity and supported schema;
- safe, unique ownership paths and declared artifact presence;
- `AGENTS.md`, declared adapters, and repository-local guidance references;
- expected Python source/test/configuration/CI structure;
- absence of an AgentReady dependency in supported dependency tables;
- work-item metadata and consistency of the generated work index and changelog;
- structural prerequisites needed for safe detach.

It does not run project tests, builds, Git operations, network requests, or editorial/LLM review.
Human and schema-1 JSON modes use identical findings and exit `0` only for a healthy repository.

## No-lock-in evidence

The automated detachment qualification builds and installs the AgentReady wheel, generates and
diagnoses a project, runs its full toolchain, detaches it, deletes the AgentReady tool environment,
creates a fresh project environment, and repeats sync, format, lint, type checking, tests, and
build. It also proves:

- only `.agentready/` disappears;
- useful guidance remains byte-identical and locally linked;
- AgentReady, Copier, and Jinja are absent from the project environment;
- application source and artifacts contain no AgentReady framework import or package.

See [DET-002 audit](docs/audits/DET_002_AUDIT.md) and the
[detachment contract](docs/DETACHMENT_CONTRACT.md).

## Trust and security boundary

V0.1 renders only the trusted template bundled in the installed package. Copier is an internal
generation engine; AgentReady disables unsafe template execution and does not execute remote
templates, arbitrary hooks, community plugins, repository commands, or network checks. Init refuses
non-empty targets, doctor is read-only, and detach fails closed unless it recognizes the fixed local
metadata boundary. AgentReady never runs destructive Git commands.

Repository content and suggested commands should still be treated as untrusted input. See
[SECURITY.md](SECURITY.md).

## Current limitations

- Python 3.12+ and the bundled minimal, application, and service profiles only.
- Init supports new missing or empty directories, not adoption or updating.
- Doctor performs structural checks, not Git analysis or executable quality auditing.
- Detach supports recognized schema-1 AgentReady projects and has no force or repair mode.
- Symlink safety tests run on Linux CI; local Windows runs may skip them without Developer Mode.
- V0.1 is prepared for practical validation but has not completed that campaign.

## Development

```bash
uv sync --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
uv build
uv run python scripts/generate_codebase_map.py --check
```

The complete next-phase scenarios and manual metrics are in
[docs/PRACTICAL_VALIDATION_PLAN.md](docs/PRACTICAL_VALIDATION_PLAN.md). Architecture, product scope,
roadmap, and permanent milestone evidence live under `docs/`.
