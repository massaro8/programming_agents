# Product Spec - AgentReady V0.1

## Existing Git bootstrap repositories

`init TARGET --into-existing` supports every existing family/profile combination.
Only `.git` and the documented bootstrap files are accepted; no clean-tree condition
is imposed. Git metadata, licenses and attributes remain unchanged. README and ignore
rules are integrated deterministically without dropping user content. Initialization
is staged and preflighted before publication; write failures roll back added artifacts
and restore original bootstrap bytes. The initialization manifest is published last.
Reinitialization, unexpected paths, unsafe links and linked worktrees are rejected.
The original nonempty-directory protection remains the default.

## Product statement

Explicit bootstrap prepares missing CloudFormation tools in project-local `.tools`
using pinned cfn-lint and checksum-verified official Guard archives. Initial tool
installation may use network access; ordinary checks remain offline. Existing tools
are reused and no global installation or persistent PATH change is performed.
`agentready bootstrap TARGET` retries preparation without regenerating project files.

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
- produces a valid Python starter repository (default family) or an explicitly selected
  CloudFormation infrastructure repository;
- produces compact `AGENTS.md` and selected thin agent adapters;
- creates a repository-local, type-routed work registry and changelog with stdlib-only tooling;
  normative requirements remain human-owned;
- creates optional `.agentready/` maintenance metadata;
- generated project passes its documented baseline checks.

### `agentready doctor PATH`

Read-only inspection of repository readiness.

Acceptance:
- recognizes the supported AgentReady manifest, family and compatible profile;
- validates manifest structure, ownership paths, declared artifacts, and local guidance references;
- checks the selected family's canonical structure and metadata;
- validates work item metadata and exact generated-index consistency without
  executing repository code;
- checks supported dependency tables for an AgentReady dependency;
- reports structural detach prerequisites without mutating the repository;
- provides deterministic human and schema-1 JSON output with matching exit semantics.

### `agentready detach PATH`

Removes AgentReady maintenance ownership without removing useful repository artifacts.

Acceptance:
- removes only AgentReady-specific maintenance metadata/provenance;
- leaves source/tests/CI/AGENTS/docs usable;
- leaves work specifications, registry, changelog, templates, and local utility usable;
- generated project still builds/tests/lints afterward;
- normal Codex/Claude usage does not require AgentReady.

### Repository-local skill QA, hooks and continuity

`agentready skill check [name]` validates Skill Contract v1; `skill eval <name>` validates portable
case definitions, evaluates lexical trigger fixtures and scores externally reported behavioral
observations. Neither invokes a model or agent. `--case` selects a case; `--results` ingests
repository-local results; JSON output preserves evidence and missing observations.

`agentready hooks` lists/inspects/configures named local recipes and explicitly enables/disables
them, with dry-run for every mutation. Acceptance: zero hooks enabled by init; no global agent,
Git or shell configuration changes; strict configuration; warn/block safety preflight; no command
execution; evidence excludes command arguments and output. Host/developer invocation is explicit;
no automatic agent callback or completion claim is installed.

`agentready checkpoint Wxxx` captures bounded durable work state, optionally from `--state`.
`agentready resume Wxxx` returns compact context and staleness warnings. Acceptance: reject missing
work, treat DONE work as non-actionable, require explicit checkpoint replacement, detect changed
revision/tracked contents/referenced files and stale validation, and reject recognizable secret
patterns. Current repository state always outranks checkpoint claims.

Doctor composes contract/eval/config/checkpoint checks without executing repository code. ERRORs
fail; WARNING/INFO remain advisory within the compatible schema-1 finding messages. Old manifests
may omit additive shared artifacts; missing v1 sections in legacy skills are advisory. Generated
projects ship identical stdlib implementations usable through `scripts/project.py` after detach.
Local hook config, checkpoints and evidence remain project-owned outside `.agentready/`.
See [the detailed contracts](SKILL_QA_AND_CONTINUITY.md).

### Deterministic task recommendations

Generated `project.py route` extends the existing work-type/skill mapping with explicit
TRIVIAL/LOCAL/CROSS_MODULE/ARCHITECTURAL complexity and NORMAL/HIGH risk. Supported security,
auth/permissions, money/payments, migration, concurrency, secrets, infrastructure and destructive
data signals force HIGH risk regardless of scope. Recommendations include skill, planning,
context, validation, review, sub-agent use and abstract FAST/BALANCED/STRONG model class.
The command is advisory: supplied work status is not approval evidence, no work item is modified,
and no model or worker is launched. Unknown areas may warrant one read-only explorer; parallel
explorers require explicitly independent domains. Ordinary known local work recommends none.

New accepted features start READY; resumed accepted IN_PROGRESS features remain actionable.
BACKLOG approval remains user/authorized specification authoring followed by synchronization;
the transition helper does not bypass that boundary. Generated `project.py work` forwards the
existing registry, and all capability help forwards to its owning parser.

These stdlib tools remain available after detach. Token telemetry, host execution of
recommendations and reasoning/model selection are external responsibilities.

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

Candidate follow-up doctor checks include Git state, duplicate/conflicting guidance, exact adapter
drift, and instruction-budget diagnostics. They require explicit policies and are not V0.1
capabilities.

V0.3: safe preview-first update flow backed by Copier and explicit ownership classes.

V1.0: measured benchmark showing value on repository tasks and a stable detachment contract.

### Python with CloudFormation

`init TARGET --family python --profile minimal --with cloudformation` generates
one repository with Python source and infrastructure templates, parameters, policies
and fixtures. The optional component supports application and service profiles too.
Offline environment declarations fail closed on unmapped branches and context mismatch.
AWS inspection is optional, explicitly authorized and separate from offline checks.
