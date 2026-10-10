# Final closure and CloudFormation feasibility

Date: 2026-10-10. AgentReady v0.1.0 implementation remains frozen.
Decisions: **V0.1.0 READY — FREEZE**; **STANDALONE IAC REPOSITORY**.
CloudFormation is an experiment, not a supported AgentReady profile.

## 1. Baseline and closure

Repository: `C:/z_personale/programming_agents`.
Initial Git status: 36 modified tracked paths and 11 untracked status entries.
Existing changes were retained; no commit, tag, push, publication, deployment or AWS account
operation was performed. Baseline status/diff and subsequent hashes are stored externally in
`C:/z_personale/agentready_use_cases/closure_evidence`.

Read canonical instructions, README, user guide, architecture, product spec, detachment contract,
work/changelog indexes, map and latest stabilization audit. All six W001–W006 records are DONE;
the BACKLOG entry under templates is reusable guidance. The existing registry validator passes
against root records/indexes. Release changelog correctly says prepared, not published.
Historical audits are retained as dated evidence. The roadmap's outdated practical-validation
candidate paragraph now points to the latest stabilization audit. No accidental temporary tracked
artifact was identified or removed; experiments and binaries remain outside tracked source.

Closure changes: README structure/workflow/recovery navigation and explicit experimental IaC
scope; interrupted generation/bootstrap recovery in the user guide; roadmap status pointer;
this audit and regenerated map. No generator, production dependency, package artifact or
supported profile changes are required. Current local qualification is sufficient to freeze;
release publication still follows the human checklist and CI remains authoritative.

## 2. Current Python assumptions

Evidence: `core/profiles.py` defines only minimal/application/service and requires pyproject,
Python version, source/tests and Python CI. `render/generator.py` renders the bundled
`agentready.templates.python` family. `templates/python/copier.yml` provides Python naming and
profile inputs. Manifest identity/ownership and doctor inspectors encode these profile contracts.
Generated project bootstrap/check/verify/package-check use uv, Ruff, mypy, pytest and wheel
installation. Architecture checks use Python AST imports; inventory/maps infer Python modules
and responsibility cards. Generated instructions, module-placement skills and route context
pointers assume Python packaging and domain/application/adapter boundaries.

Case A, Python application with IaC: existing profiles remain appropriate for the application.
Keep templates/policies separate and add cfn-lint/Guard gates explicitly; Python checks do not
validate infrastructure. Case B, CloudFormation-only: even minimal generates unnecessary
application packaging, source/tests and architecture conventions. It is not an IaC profile.
Python used by engineering tools does not imply that the repository is a Python application.

## 3. Capability classification

| Component | Classification | Evidence and IaC implication |
|---|---|---|
| Search-first guidance, acceptance, compact handoffs | REUSABLE AS-IS | Methodology/context principles require no application language. |
| Work registry and derived changelog | REUSABLE AS-IS | Standalone stdlib `work_registry.py` ran through READY/IN_PROGRESS/DONE; create docs/work and docs/changelog first. |
| Generic ownership principles | REUSABLE AS-IS | Project-owned requirements and templates remain user-controlled. |
| Checkpoint/resume and file guards | REUSABLE WITH SMALL ADAPTATION | Export `continuity.py` with the existing local import substitution and `local_paths.py`; no AgentReady package required. |
| Skills and routing recommendations | REUSABLE WITH SMALL ADAPTATION | Complexity/risk algorithm is generic; skill names, context paths and standards need IaC mapping. |
| Canonical AGENTS and thin CLAUDE view | REUSABLE WITH SMALL ADAPTATION | Replace Python instructions with template/policy boundaries and offline commands. |
| Doctor | REUSABLE WITH SMALL ADAPTATION | Read-only architecture is useful, but current public doctor requires a Python manifest/profile; not used to qualify this spike. |
| CODEBASE_MAP | REUSABLE WITH SMALL ADAPTATION | Navigation concept applies; current Python semantic inventory must be extended for template resources. Spike uses an explicitly static map. |
| Generation, profiles and manifests | PYTHON-SPECIFIC | Current renderer/family/contracts require Python seed artifacts. |
| Architecture checks/module cards | PYTHON-SPECIFIC | AST imports/layers are not CloudFormation references or resource boundaries. |
| Verification scripts and generated CI | PYTHON-SPECIFIC | Replace application gates with template schemas, references and security policy checks. |
| Application wheel/build/package smoke | NOT NEEDED FOR CLOUDFORMATION | No application package exists. AgentReady's own packaging remains Python. |
| Optional hooks/evaluations | NOT NEEDED FOR CLOUDFORMATION | Not required for this small experiment; no host interception is introduced. |
| Detach implementation | NOT NEEDED FOR CLOUDFORMATION | Spike has no maintenance manifest; independence is tested directly. Existing detach remains Python-profile qualified. |

## 4. Requirements and experimental structure

Spike: `C:/z_personale/agentready_use_cases/cloudformation_repo_spike` (separate initialized Git
repository, no commits). Structure:

```text
AGENTS.md, CLAUDE.md, README.md, .cfnlintrc
templates/storage.yaml, templates/audit.yaml
parameters/sandbox.json
policies/security.guard
tests/fixtures/{invalid-property,broken-reference,public-bucket,missing-encryption,unsafe-ingress}.yaml
scripts/{verify.ps1,work_registry.py,skill_routes.py,continuity.py,local_paths.py}
.agents/skills/cloudformation-change/SKILL.md
docs/ARCHITECTURE.md, docs/generated/CODEBASE_MAP.md
docs/work/, docs/changelog/
```

Templates use private, encrypted, versioned S3 storage, Retain policies, TLS-only bucket policy,
synthetic environment tags, no physical names, credentials or exports. Ref, GetAtt and Sub remain
CloudFormation intrinsics, not generic YAML strings. Parameter examples contain only sandbox
values. Guard checks encryption presence, all public-access flags, versioning, retention and
world-open ingress. This is a bounded policy suite, not exhaustive security assurance: it does
not resolve dynamic values, verify deployment, or prove account permissions/quotas.

## 5. Validation commands and results

Official tool documentation consulted:
[cfn-lint](https://github.com/aws-cloudformation/cfn-lint),
[Guard](https://github.com/aws-cloudformation/cloudformation-guard),
[Guard validate](https://docs.aws.amazon.com/cfn-guard/latest/ug/cfn-guard-validate.html).
Installed cfn-lint 1.57.2 as an isolated uv tool; downloaded official Guard 3.2.1 Windows binary
to the external evidence directory. No AgentReady dependency was added. Actual `cfn-lint --help`
and `cfn-guard validate --help` were read before configuring `.cfnlintrc` and validation flags.
Downloads require network; validation uses bundled schemas/local policies and calls no AWS APIs.

```powershell
cfn-lint --regions eu-west-1 --template templates/storage.yaml
cfn-guard validate --rules policies/security.guard --data templates/storage.yaml --type CFNTemplate
pwsh -File scripts/verify.ps1 -GuardPath <absolute-path-to-cfn-guard.exe>
python scripts/work_registry.py check
```

| Probe | Actual result |
|---|---|
| storage.yaml and added audit.yaml | Lint and Guard exit 0, including intrinsic-function syntax. |
| Invalid S3 property | cfn-lint rejects with E3002. |
| Missing output reference | cfn-lint rejects with E6101. |
| Public-access flag false | Guard bucket_controls FAIL. |
| Missing encryption declaration | Guard bucket_controls FAIL. |
| SSH ingress 0.0.0.0/0 | Guard scoped_ingress FAIL. |
| Aggregate verifier | Exit 0 only when valid templates pass, expected diagnostics occur and registry passes. |

Initial harness expected E1020 for the output reference; actual tool reports E6101. The verifier
was corrected to the observed supported diagnostic. Initial manual source copying had an import
and encoding issue; UTF-8 copies and the renderer's existing standalone import substitution fixed
the experimental harness. These were spike setup errors, not AgentReady implementation defects.
Logs retain unsuccessful attempts as well as final successful runs.

## 6. Agent workflow experiment

Task: add private audit storage while preserving the original storage template. Work new created
W001; accepted task scope/criteria were authored READY, indexes synchronized, work checked and
transitioned IN_PROGRESS. Checkpoint/resume returned actionable compact work context. A separate
audit.yaml reused secure defaults; verification passed; original storage hash remained unchanged.
The implementation record was completed with `Result: COMPLETE`, verification and changelog,
then transitioned DONE. Resume correctly reported DONE as non-actionable and the older checkpoint
as stale. No model execution or deployment is part of these tools.

Onboarding succeeds from AGENTS -> map -> architecture -> work -> IaC skill -> verifier. Boundary
discipline maps naturally to templates/parameters/policies. Progressive disclosure and checkpoints
remain useful; no numerical token savings are claimed. The Python route algorithm can classify
infrastructure as HIGH risk but its returned feature-builder/standards pointers remain Python
specific; the spike explicitly directs template work to its local IaC skill. The static map has
manual maintenance cost, and pre-commit Git revision evidence was absent in the first checkpoint;
work/file hashes and status staleness were still checked. This is a feasibility test, not automatic
integration of all AgentReady local commands into IaC.

## 7. Options and decision

| Option | UX / maintenance / compatibility / distribution |
|---|---|
| A: existing Python profiles | Best for Case A; no generator changes or duplication, separate IaC checks. Poor Case B UX because application artifacts are mandatory. Existing tests/distribution unchanged. |
| B: standalone IaC repository | Fits Case B immediately; small copied governance scripts require manual upstream maintenance and context adaptation. No runtime lock-in, manifest or distribution change. Test template/policy negatives locally. |
| C: native CloudFormation family | Better integrated onboarding, but adds renderer selection, family contracts, manifests, doctor/map semantics, CI/tool installation docs and family/detach/negative-fixture tests. Packaging must include and qualify a second family. Additive Python compatibility must be proven. |

Recommendation: B for the demonstrated CloudFormation-only use case, A for Python applications
containing infrastructure. C is not justified by a single small spike. No plugin framework or
new template family is implemented. Retain the v0.1.0 architecture freeze.

## 8. Smallest future scope and risks

Next steps: use the standalone repository on a second real offline IaC task, record map/routing
and maintenance friction, and establish explicit demand before creating a native-family work item.
If demand justifies C, first specify a bundled CloudFormation family with template/policy checks,
family-specific manifest/doctor/map contracts and unchanged Python defaults; reuse registry and
continuity export seams. Require generation/doctor/detach compatibility and negative tests before
advertising support. Avoid dynamic plugins, remote hooks and provider orchestration.

Residual risks: local schema/policy success does not qualify actual AWS deployment; schema/tool
versions need deliberate upgrades; the policy suite is intentionally limited; copied tooling can
drift; static maps are manual; Python runtime is still needed for stdlib governance, but no Python
application structure is required. Release CI/publication and live AWS validation are outside scope.

## 9. AgentReady verification

Fresh minimal/application/service projects generated without bootstrap. Thirty actual documentation
commands passed across their help, work checks, routing, skill checks, command-reference checks and
doctor. README/AGENTS/CLAUDE/index/map/workflow files and local Markdown links were inspected;
no genuine generated-guidance gap required a template change.
Root registry check, Ruff lint, Ruff format (116 files), mypy (22 files) passed.
Focused `tests/test_task_routing.py` and `tests/test_stress_guidance.py`: 22 passed.
Map freshness and final link/preservation checks are recorded externally with final evidence.
Final map check and Markdown link checks passed; `git diff --check` passed. Hash comparison of
228 baseline files found only README, USER_GUIDE, ROADMAP and generated map changes; no baseline
file was deleted. Final Git status has 37 modified tracked paths and 12 untracked status entries,
including all inherited user changes and the new feasibility audit. The storage template retains
SHA256 `1648bcae03767718dd7f82700041745ce382b3bfd59f5618384375d021fb877e`.
Full 248-pass/4-skip and wheel/sdist/detach qualification belongs to FINAL_FIX_001 and is cited,
not claimed as rerun here: documentation-only changes do not justify repeating it.
