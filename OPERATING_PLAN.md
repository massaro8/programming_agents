# Operational Plan for Building and Publishing AgentReady

## 1. What we are building

The public repository is not merely a Python starter. It is the source repository for a tool that creates,
adopts (later), verifies, and eventually updates agent-ready repositories without owning them.

The core public promise is:

> Bootstrap once. Own the repository forever.

## 2. Product boundary

Build:
- local CLI;
- trusted templates;
- canonical vendor-neutral instructions;
- deterministic `doctor`;
- formal `detach`;
- machine-readable evidence/contracts;
- optional thin adapters.

Do not build in V0.1:
- cloud backend;
- agent runtime;
- SDD replacement;
- model router;
- agent team orchestrator;
- arbitrary plugin marketplace;
- telemetry by default.

## 3. Recommended model operating model

### Default

Use **Luna directly** for TRIVIAL/LOCAL bounded work.

### Escalate to Sol when

- architectural/cross-module decision;
- high-risk file ownership/delete/update behavior;
- ambiguous design;
- public contract;
- security boundary;
- repeated builder failure;
- milestone/release audit.

### Good pipeline

```text
Sol: scope/decision when needed
 -> compact handoff
Luna: implementation + tests
 -> deterministic checks
Sol: only triggered review/milestone audit
```

### Bad pipeline

```text
Sol plan -> Luna build -> Sol review
```

for every typo or one-file task. That wastes repeated context bootstrap and contradicts the token-efficient
research.

## 4. First 9 implementation tickets

Use the exact sequence in `docs/ROADMAP.md`:

1. BOOT-001
2. BOOT-002
3. INIT-001
4. INIT-002
5. DOC-001
6. DOC-002
7. DET-001
8. DET-002
9. REL-001

Do not branch into secondary features before DET-002.

## 5. Release criteria for V0.1

Required:
- installable package/CLI;
- `init`, `doctor`, `detach` documented and tested;
- trusted bundled Python starter;
- no runtime framework dependency in generated app;
- doctor text + JSON;
- formal detachment E2E pass;
- Windows/Linux CI if feasible before public stable tag;
- public README, contributing, security and license finalized;
- no placeholder copyright holder;
- examples regenerated from the released version;
- clean release audit.

## 6. Public repository publication order

1. Create empty GitHub repository.
2. Copy this scaffold into it.
3. Replace `[YOUR NAME OR ORGANIZATION]` in `LICENSE`.
4. Initialize Git and commit only the scaffold.
5. Run the kickoff prompt in `START_SOL_COORDINATOR.md`.
6. Fix Phase-0 baseline until green.
7. Implement tickets one by one.
8. Keep PRs small; each ticket should have explicit acceptance and evidence.
9. Tag `v0.1.0` only after DET-002 + REL-001.
10. Only then start adoption/update functionality.

## 7. What makes the repository reusable by anyone

A user should need only:

```text
Python/uv for the tool at bootstrap time
+ their chosen coding agent
+ normal project dependencies
```

After generation/detachment they must not need:
- your source repository;
- your Git remote;
- your account;
- your server;
- your API key;
- your CLI for ordinary coding.

The generated repository must contain the durable instructions, workflows, checks, and documentation it
needs to continue independently.

## 8. Avoidable failure modes

- giant `AGENTS.md` instead of progressive disclosure;
- copying the same policy independently into every vendor file;
- building `adopt/update` before detachability is proven;
- remote template/plugin execution too early;
- creating empty architecture directories for future features;
- adding multi-agent complexity before single-agent workflows are reliable;
- optimizing token counts before measuring accepted-task outcomes;
- describing checks as passed without command evidence;
- making the framework a runtime dependency of generated projects.
