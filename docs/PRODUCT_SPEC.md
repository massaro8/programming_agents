# Product Spec - AgentReady V0.1

## Product statement

AgentReady is a detachable, vendor-neutral repository bootstrap and governance kit for coding agents.

## User problem

Coding agents work best when repository knowledge, workflows, boundaries, and verification are easy to
discover. Existing solutions often focus on agent runtimes, spec-driven workflows, or prompt packs.
AgentReady focuses on the repository environment itself and on making that environment removable.

## V0.1 outcome

A user can install/run the tool transiently, create an agent-ready repository, verify it, detach the
maintenance metadata, and continue development without depending on AgentReady.

## V0.1 commands

### `agentready init PATH`

Creates a new repository from a trusted bundled template.

Acceptance:
- refuses unsafe overwrite of non-empty directories;
- produces a valid Python starter repository;
- produces compact `AGENTS.md` and selected thin agent adapters;
- creates optional `.agentready/` maintenance metadata;
- generated project passes its documented baseline checks.

### `agentready doctor PATH`

Read-only inspection of repository readiness.

Acceptance:
- reports Git/readiness state;
- validates referenced instruction/workflow paths;
- reports duplicate/conflicting instructions when detectable;
- reports adapter drift when adapter generation exists;
- reports always-loaded versus on-demand instruction budget;
- reports detachability status;
- supports machine-readable JSON output.

### `agentready detach PATH`

Removes AgentReady maintenance ownership without removing useful repository artifacts.

Acceptance:
- removes only AgentReady-specific maintenance metadata/provenance;
- leaves source/tests/CI/AGENTS/docs usable;
- generated project still builds/tests/lints afterward;
- normal Codex/Claude usage does not require AgentReady.

## Explicit non-goals for V0.1

- no cloud service;
- no account system;
- no telemetry by default;
- no automatic multi-agent orchestrator;
- no generic agent runtime;
- no arbitrary remote templates/plugins;
- no automatic destructive migration of existing repositories;
- no autonomous model routing;
- no TypeScript/Go/Rust generation yet;
- no full `update` engine until ownership and detach semantics are proven.

## Follow-up scope

V0.2: `adopt`, adapter `sync`, evidence-based `audit`.

V0.3: safe preview-first update flow backed by Copier and explicit ownership classes.

V1.0: measured benchmark showing value on repository tasks and a stable detachment contract.
