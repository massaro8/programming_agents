# MULTI-PROJECT-001 — Final productization audit

Date: 2026-10-12 (Europe/Rome). Work resumed from 2026-10-10.

## Executive verdict

READY — WITH DOCUMENTED LIMITATIONS

Both families are implemented and qualified from an installed wheel. Python profiles remain compatible;
CloudFormation has real offline lint/security checks and portable engineering tools. No remaining
reproduced P0/P1 is known after the fixes and regressions below. This verdict concerns the executed
local checks, not remote CI or guaranteed agent behavior.

Changed: native family selection, infrastructure content, family-aware routing, thin Claude views,
verification receipts, continuity coverage, doctor and documentation.
Checks: 270 passed / four privilege skips; static gates; 81 packaged qualification operations;
final wheel CLI generation/doctor/detach for both families.
Residual risks: selected security coverage, local evidence trust, untested Claude runtime and unavailable
isolated Codex continuation, documented below.

## Baseline and preservation

Source: C:/z_personale/programming_agents. HEAD: 4c2c3b9275a449ff81428b6d2d0dc755d8d37c2c.
The actual starting tree was clean; the request's earlier uncommitted-work warning was checked.
External preservation: C:/z_personale/agentready_use_cases/multi_project_final/preservation/baseline.zip,
status.txt and commit.txt. No reset, clean, source-file deletion, commit, tag, push or publication occurred.
Historical audits and W001–W006 records were retained. Disposable generated projects and logs remain
outside the source repository. Previous interrupted candidate projects were moved aside, not discarded.

Reviewed AGENTS, map, architecture/profile contracts, FINAL_FIX_001, CLOUDFORMATION_FEASIBILITY,
and external cloudformation_repo_spike/docs/audits/RULE_ADHERENCE_001.md. Historical 248-pass results
are not presented as this task's results. Early integration attempts and their failures are preserved.

## Architecture changes

A static family resolver selects python or cloudformation. Python retains minimal/application/service;
CloudFormation defaults to infrastructure. Copier uses bundled content only. Shared stdlib tools and
canonical registry/routing/check scripts are exported from their owning source, rather than maintained
as independent infrastructure copies. No plugin framework or dynamic discovery was added.
Schema-1 manifests without family mean Python. Incompatible pairs fail before writing. Design and
migration rationale are in ARCHITECTURE.md and ADR 0001. No production dependency was added.

## Python backward compatibility

All previous Python profile forms remain supported. Existing CLI/profile, architecture, ownership,
package, doctor, path and detach regressions were executed. Packaged minimal bootstrap/verification
and the generated-project tests for all three profiles pass. Additive receipt/config artifacts may be
omitted by old manifests. Legacy work records are not rewritten or retroactively required to have receipts.

## CloudFormation generation

The infrastructure family creates templates/storage.yaml, synthetic parameters/sandbox.json,
policies/security.guard, three positive/seven negative fixtures, CI, instructions, skills, docs and
standalone engineering commands. It creates no application src or pyproject/package build requirement.
Scripts require Python 3.12+. Generation provisions nothing and needs no AWS account.
Packaged W001 changed a real output Description in storage.yaml, preserved security controls,
failed verification for an injected invalid property, then passed real verification before DONE.

## Agent instruction loading

AGENTS.md stays canonical. CLAUDE.md contains @AGENTS.md. Claude skill views retain canonical
frontmatter and a relative instruction to read the canonical skill; they do not duplicate procedure
bodies. Explicit sync regenerates views; checks reject drift and broken imports.

These are structurally qualified files, not a runtime Claude observation. Claude was unavailable on
PATH. Official reference: https://code.claude.com/docs/en/memory and /docs/en/skills.
Passing tests does not guarantee Claude always follows instructions. Codex behavior and instruction
loading are host-dependent; no guaranteed automatic enforcement or token saving is claimed.

## Skills and routing

The shared router emits infrastructure context and cloudformation-change for CloudFormation features;
Python names and recommendations remain unchanged. DOCS, local/cross-template, IAM, network and
continuation scenarios were executed. IAM/network/security-group inputs support high-risk routing.
High-risk recommendations include explicit scope, replacement/permission/environment impact,
failure/rollback planning, security review and broader relevant gates. Paths resolve to shipped files.
FAST/BALANCED/STRONG are advisory host classes; the router launches no model or worker.

## Verification-before-DONE

New configured records receive Verification evidence: REQUIRED. verify --work Wxxx executes the
family/type contract and writes docs/verification/Wxxx.json. DONE requires successful stages, matching
work identity/type, unchanged accepted specification/repository inputs, tool identity and fresh time.
Receipts record commands/exit status, timestamp, hashes and available tool versions. Writes are bounded,
atomic and protected by the existing repository write guard. DOCS runs registry/skill/map checks.

Missing/fabricated prose, failed checks, missing stages, expiry, changed inputs/contracts, mismatching
kind, concurrent writes, resumed work and legitimate completion are covered by tests and packaged probes.
An optional version-probe timeout no longer falsely reports a changed executable; a regression covers it.
Executable identity remains checked, and differing available versions still invalidate evidence.

Legacy records without the REQUIRED marker retain their previous contract; explicit migration adds the
marker and executes verification. Historical DONE receipts are checked as historical success rather than
made stale by later development. See VERIFICATION_EVIDENCE.md for bounds and migration.
Repository-local evidence improves correctness and staleness detection but does not guarantee protection
against a malicious agent that can edit all local files. There is no independent attestation or signature.

## CloudFormation security policies

Executed cfn-lint 1.57.2 and Guard 3.2.1. Real checks validate template properties/references and selected
S3 encryption, public access, versioning/retention, world-open ingress and a TLS-deny baseline.
Three positives include renamed storage and a network-only template. Seven negatives reject invalid
property (E3002), broken Ref (E1020), public S3, missing encryption, missing public-access block,
unrestricted ingress and missing TLS policy. Fixture presence is asserted: removing a required fixture
fails rather than falsely claiming success. Missing tools fail with local installation instructions.

TLS coverage is template-level: it does not prove that every bucket has the correct policy/Resource
association. Intrinsic values, every resource/security posture, permissions/quotas and deployment results
are not comprehensively assessed. New resources require deliberate policy/association review.
Official tool sources: github.com/aws-cloudformation/cfn-lint and cloudformation-guard;
AWS Guard validate documentation was consulted. No global tool installation or AWS operation occurred.

## CODEBASE_MAP

CloudFormation inventories template, parameter, policy, script, skill, work and fixture paths without
custom YAML/resource inference. Generation, sync and freshness checks work offline. Checkpoint/evidence
state is excluded from navigation. Doctor independently checks file coverage without executing project
code. A reviewed unsafe output-write defect was fixed using local paths, guarded atomic writes and
junction regressions; unsafe output/skill ancestors are rejected.

## Checkpoint/resume

Continuity includes non-ignored untracked Git files and a bounded relevant-file fallback without Git.
Explicit relevant files, content drift, work status and revision changes are checked. Fresh repositories
before their first commit are tested for Python and CloudFormation. Packaged checkpoints/resume detected
real content changes and DONE status. Checkpoints contain compact state/hashes, not transcripts or secrets.
The optional isolated Codex continuation was not executed: delegated agents exhausted workspace credits.
Primary-session/tool continuation and deterministic resume are observed; isolated agent compliance is not.

## Doctor/detach

Family-aware doctor checks manifest/ownership, structure, references, skills, evidence configuration,
work/checkpoints, map and independence read-only. Duplicate template views were removed and duplicate
normalized artifact paths now fail. Actual packaged doctor/detach hash comparisons preserve ordinary
files. Both projects verify after detach without AgentReady/Copier in their execution environments.
Existing Windows junction/path regressions ran; four unavailable symlink-privilege cases remain skips.

## Packaged installation

Wheel/sdist archives include both families and standalone scripts. Both were installed offline in
isolated environments. The wheel performed complete Python and CloudFormation workflows; the sdist
performed CLI/init/doctor/detach for both. qualification-results.json records 81 operations with expected
statuses, including intentional failures. Final artifacts are under multi_project_final/final-artifacts.
Final wheel native uvx init/doctor/detach passed for both families. Its executable/template validation
payload matches the fully qualified candidate; the generated README minimum-Python correction and CI installer
changed (neither changes executed local validators). The nonexistent crates.io Guard 3.2.1 package was replaced with the official versioned Ubuntu binary. Its downloaded archive SHA256 and contents were checked; remote CI was not executed. Root README/package metadata was refreshed afterward. Artifact hashes are saved externally.

Local wheel-cache reuse was observed during retries. README uses --refresh-package agentready when
rebuilding the same version. That option was executed successfully; it cannot be combined with --offline.
Offline qualification instead used a distinct immutable candidate artifact path and cached dependencies.

## Complete local test results

274 current test nodes were collected. Final per-node outcomes: 270 passed, four skipped, zero failed,
zero missing. Four disjoint full-suite groups plus targeted corrected retries cover every node exactly
once in the final outcome summary (no duplicate pass counting). final-test-summary.json identifies the
XML evidence for each node. Initial failures, obsolete assertions and interrupted attempts remain in logs.

Executed: Ruff check, Ruff format --check (127 files), mypy src (25 source files), source map generation
and freshness check, wheel/sdist build and content inspection, installed qualification and final CLI smoke.
The privilege skips are not passes. Remote CI was not run and is not claimed. CI remains authoritative.

## Documentation

Root README was updated after installed family qualification. It covers both families, profiles, local
wheel installation, commands, structures, work/routing, receipts, continuity, doctor/detach, adapters,
progressive context and recovery. Generated infrastructure README explains adding resources, parameter
files, security/tooling, policy limits, offline verification and separate deployment review. AGENTS is
short; longer procedures live in skills/docs. No PyPI publication or release is claimed.

## Remaining limitations

- Claude runtime loading/behavior and isolated Codex continuation are not qualified here.
- Local receipts cannot defend against an agent that can modify every local file.
- Guard has selected template-level coverage, including the TLS association limit above.
- Four Windows symlink privilege cases are skipped; real junction checks are separate executed cases.
- Offline checks use installed tools/cached dependencies, not an OS-level network isolation guarantee.
- Local guards are not a hostile-process security boundary; killed writers can leave explicit stale locks.
- No deployment, global tool provisioning, remote CI, publishing or external service was used.

## Git diff and release state

HEAD remains the baseline commit. Changes are task-scoped and uncommitted; historical audits/work
records remain intact. No reset, clean, commit, tag, push, GitHub/PyPI publication or AWS deployment.
The final Git status/diff checks and artifact/test summaries are retained in the external workspace.

## Exact commands for starting a new Python project

From the source checkout, using an empty/missing destination:

```powershell
uv build
uvx --refresh-package agentready --from ./dist/agentready-0.1.0-py3-none-any.whl agentready init ../my-python --family python --profile minimal
cd ../my-python
python scripts/project.py bootstrap
python scripts/project.py verify
python scripts/project.py work new --type FEATURE "Add a capability"
```

Fill/accept the specification, sync, transition READY to IN_PROGRESS, implement and execute
verify --work W001 before DONE. Legacy init without --family still defaults to Python minimal.

## Exact commands for starting a new CloudFormation project

From the source checkout, using an empty/missing destination:

```powershell
uv build
uvx --refresh-package agentready --from ./dist/agentready-0.1.0-py3-none-any.whl agentready init ../my-infra --family cloudformation
uvx --refresh-package agentready --from ./dist/agentready-0.1.0-py3-none-any.whl agentready doctor ../my-infra
cd ../my-infra
python scripts/project.py work new --type FEATURE "Change infrastructure"
python scripts/project.py bootstrap
python scripts/project.py verify
```

Install the local cfn-lint/Guard tools first using the generated README. For an accepted IN_PROGRESS
item, sync and execute python scripts/project.py verify --work W001 before DONE. From the source
checkout, detach with:

```powershell
uvx --refresh-package agentready --from ./dist/agentready-0.1.0-py3-none-any.whl agentready detach ../my-infra
```

Detachment preserves the project-local verification command. None of these commands deploys resources.
