# Final productization audit

Baseline: `ea2d0bd7366bbcb96f01fd6ccdfad99b73868993`; clean working tree before changes.

Final decision: **READY — RELEASE CANDIDATE, TOKEN METRICS DEFERRED**.

Product behavior and detachable profile qualification pass. Numerical token savings and a valid
token A/B comparison remain unproven because comparable task-level accounting is unavailable.

## Baseline decision table

| Strategy | Baseline classification | Owner / decision |
|---|---|---|
| Small permanent context | IMPLEMENTED | Generated concise AGENTS; retain |
| Search before read | DOCUMENTED ONLY | Generated guidance; host follows |
| CODEBASE_MAP navigation | IMPLEMENTED | Deterministic map/check + guidance |
| Progressive disclosure | PARTIALLY IMPLEMENTED | Context pointers plus guidance |
| Skill on demand | PARTIALLY IMPLEMENTED | Work-type routes; host loads skill |
| Context waterfall | DOCUMENTED ONLY | Generated guidance |
| Proportional planning | DOCUMENTED ONLY | Extend existing deterministic skill routes |
| Targeted tests before broad gates | DOCUMENTED ONLY | Guidance; final check is broad |
| Diff-based validation | DOCUMENTED ONLY | Host judgment; no new runner |
| Checkpoint handoff | IMPLEMENTED | Portable continuity tooling |
| Fresh-session continuation | PARTIALLY IMPLEMENTED | Resume/staleness tooling + host |
| Compact agent handoff | DOCUMENTED ONLY | Guidance; no orchestration |
| Log summarization | DOCUMENTED ONLY | Optional host behavior |
| Session reset guidance | PARTIALLY IMPLEMENTED | Compaction guidance; add checkpoint/reset advice |
| Sub-agent guidance | DOCUMENTED ONLY | Extend route recommendations; host executes |
| Complexity/risk routing | PARTIALLY IMPLEMENTED | Existing types omit effort/risk; extend same module |
| Model/reasoning routing | DOCUMENTED ONLY | Abstract advisory classes; reasoning host-owned |
| Token/efficiency telemetry | NOT IMPLEMENTED | External evaluation only |
| Automatic providers/orchestration | NOT APPROPRIATE FOR AGENTREADY | Do not implement |

This opening-audit classification bounds implementation. No new production dependency or runtime
service is required. The targeted baseline command was launched before edits but completed while
scoped work proceeded; it is not a frozen-snapshot A/B baseline.

## Executive verdict

Pending final full-suite reconciliation. The release decision will be finalized from executed gates.

## UX fixes

- `project.py --help` now discovers work new/list/check/sync/transition, skill/evals, opt-in hooks,
  checkpoint/resume and routing. Capability help forwards to existing parsers.
- BACKLOG -> authorized specification authoring of READY -> sync/check -> IN_PROGRESS is explicit.
  BACKLOG promotion remains forbidden through the transition helper; no governance bypass added.
- New accepted features require READY; accepted IN_PROGRESS features can continue. Explicit context
  resolution now marks both actionable, while next-work selection still chooses READY only.
- The generated feature skill and lexical continuation fixture reflect that contract. Tests exercise
  actual forwarding, rejected automatic promotion, authored approval and continuation.
- Final regression caught template bytecode contamination from the router test's import loader.
  The loader now uses runpy without caching the template module; Copier excludes __pycache__/pyc.
  An intentionally contaminated disposable template failed before the guard and passes afterward.
- Windows package-check completed build/import/CLI but could not delete a 260-character scratch
  filename. A shorter owned temporary prefix fixes the exercised case, preserving cleanup assertions.
  The qualification test now selects Scripts/python.exe or bin/python by platform, matching existing
  formal-detach conventions and the Ubuntu CI target. Linux execution is not claimed here.

## Profile selection

| Profile | Structure and customization |
|---|---|
| minimal | Direct src/package seed; architecture checker does not prescribe internal directories. E4 custom_layout passes verify/build/doctor/detach. Required Python scaffold/seed artifacts still apply. |
| application | Standard capabilities under modules, domain/application layers, thin entrypoints, bootstrap and public application exports. Existing architecture tests check boundaries. |
| service | Adds an adapter boundary to application structure. Inward dependencies and resource ownership remain enforced/documented; invariants were not weakened. |

The flexible choice is minimal within the generated Python scaffold, not a claim that arbitrary
packaging layouts or removal of required files are supported. No profile contract changed.

## Token-efficiency audit

Final classifications distinguish mechanisms from host-followed recommendations.

| Strategy | Final status | Actual behavior / responsibility |
|---|---|---|
| Small permanent context | IMPLEMENTED | Concise AGENTS links deeper guidance; qualification checks under 2,000 characters, not a runtime token budget |
| Search before read | RECOMMENDED | Agent/host reading discipline |
| CODEBASE_MAP navigation | IMPLEMENTED | Generated inventory, map and freshness checks; host chooses to read it |
| Progressive disclosure | IMPLEMENTED | Context tool returns paths/metadata rather than document bodies |
| Skill on demand | RECOMMENDED | Deterministic routes identify a skill; host loads it |
| Context waterfall | RECOMMENDED | AGENTS/map/search/spec/skill/affected code/tests, stopping when sufficient |
| Proportional planning | IMPLEMENTED | Advisory deterministic effort output; host executes the plan |
| Targeted tests before broad gates | RECOMMENDED | Guidance; final project verify is intentionally broad |
| Diff-based validation | RECOMMENDED | Host selects affected contracts/checks; no speculative validation engine |
| Checkpoint handoff | IMPLEMENTED | Bounded portable continuity records and staleness checking |
| Fresh-session continuation | HOST-DEPENDENT | Portable resume supports it; host manages session boundaries |
| Compact agent handoff | RECOMMENDED | Fixed headings, no transcript transfer |
| Log summarization | RECOMMENDED | Summarize outcome/errors/paths; external evidence retains command output |
| Session reset guidance | RECOMMENDED | Checkpoint/resume before reset; no automatic reset |
| Sub-agent guidance | HOST-DEPENDENT | Router advises bounded exploration; host decides and executes |
| Complexity/risk routing | IMPLEMENTED | Explicit structured inputs; HIGH overrides scope |
| Model/reasoning routing | HOST-DEPENDENT | Abstract class recommendation; reasoning/model selection belongs to host |
| Token/efficiency telemetry | DEFERRED | External evaluation; no production telemetry dependency |

Core owns deterministic rendering, ownership, checks and continuity. Generated tooling owns local
recommendations and work/context commands. Guidance owns reading/planning discipline. Agent hosts
own execution, sessions, model choice and delegation. External evaluation owns token accounting.

## Routing

The existing `scripts/skill_routes.py` owns both work-type routes and effort/risk recommendations;
`project.py route` forwards to its parser. No parallel route registry was created. Inputs include
work type, complexity, explicit risk/signals, unknown area, number of independent domains and
advisory work status. Output includes skill/workflow/standards, plan, context, validation, review,
sub-agent recommendation and abstract FAST/BALANCED/STRONG class. It neither mutates work nor
launches providers/workers. Supplied status is not independent approval evidence.

Sixteen deterministic tests passed: typo, local feature, cross-module public contract, local auth,
migration, concurrency, architectural boundary, known local bug, resumed feature, plus independence,
approval/risk dominance, deterministic JSON and invalid structured input cases. HIGH risk always
uses failure/rollback planning, specialist review and relevant broader gates. Known local and trivial
work recommend no explorer. Unknown areas may recommend one read-only explorer; scoped parallel
explorers require at least two explicitly independent domains.

## Sub-agent evidence

SUBAGENT EXECUTION: AVAILABLE IN HOST

- E1/TRIVIAL README wording: zero sub-agents; no large plan.
- E2/LOCAL ordered batch greeting: zero sub-agents; bounded module/test changes and micro-plan route.
- E3/CROSS_MODULE unknown greeting normalization: one isolated read-only explorer, fresh worker
  without conversation history. Scope: AGENTS/map, service, CLI and neighboring test. Five distinct
  files read, no repeated full-file reads inside worker, three tool calls, no broad directory read,
  no worker edits. Lead additionally read facade and CLI signature and mechanically read service
  to apply an edit. The CLI reread was needed because the handoff omitted the function signature;
  service reread was mechanical editing. AGENTS/map were shared prerequisites. Context isolation
  helped localization, but did not eliminate overlap or prove token saving.
- E4/HIGH concurrency: one fresh read-only specialist; counter and test only, two reads, no repeats,
  one tool call, no edits or checks executed by reviewer. Review confirmed common lock ownership
  and absence of nested-lock paths. Lead ran the concurrent regression and relevant broad gates.

Implementation also used two scoped collaborators (routing vs UX), with distinct owned files and
compact handoff headings. Both implementation collaborators inherited conversation context; that orchestration
was not treated as a token-efficiency benchmark. No two workers explored the whole repository.

## Token evidence

### ACTUAL TOKEN METRICS

The exposed host tool catalogue offers account usage-limit percentages, not reliable task/worker
input, cached input, output, reasoning or total token accounting. No comparable per-task accounting
was available through the execution/delegation tools. Token counts are unavailable, not estimated.

NUMERICAL TOKEN SAVING: NOT PROVEN

### PROXY METRICS

CONTEXT-EFFICIENCY PROXY only. Evaluation roots are exclusively under
`C:/z_personale/agentready_use_cases/agentready_final_eval`; previous stress projects were untouched.
Raw command evidence and disposable harnesses remain there in `results.json`, `evaluate.py`,
`recover.py`, `qualify.py`, `docs_qualify.py` and `docs_results.json`.

| Task | Harness implementation reads | Implementation files changed, including work record | Read/changed ratio | Attempts | Validation failures | First-pass gates | Agents |
|---|---:|---:|---:|---:|---:|---|---:|
| E1 trivial | 4 | 2 | 2.00 | 1 | 0 | yes | 0 |
| E2 local | 5 | 3 | 1.67 | 1 | 0 | yes | 0 |
| E3 cross-module | 3 + 1 mechanical edit read | 3 | 1.33 within harness | 2 | 1 | no | 1 explorer |
| E4 concurrency | 3 | 4 | 0.75 within harness | 2 | 1 | no | 1 reviewer |

These counters measure explicit harness reads during implementation, not subprocess-internal reads,
template rendering, later work finalization, all lead-source investigation or provider context.
E3 additionally has five explorer reads and two lead follow-up reads: 11 observed read events across
those scopes, seven distinct files, four overlaps (including prerequisites and mechanical editing).
E4 adds two reviewer reads. E1/E2/E4 had no exploratory scope expansion; E3 had one facade/signature
follow-up expansion. Harness implementation reads had zero repeats and broad directory reads.
Changed-file counts exclude common generated index/map refreshes and evaluation tooling refreshes;
those are validation setup, not product implementation changes.

E1/E2 each executed 28 subprocess commands through qualification. E3 executed nine initial commands
and 21 recovery/qualification commands; initial behavioral pytest passed, then verify failed on Ruff
I001 import ordering in the disposable test. E4 executed 30 commands, including the same evaluation
fixture import-ordering failure and successful correction. Both failures were evaluation authoring
errors, not suppressed checks. E1 documentation edit used direct local wording inspection and then
regular project tests; E2/E3/E4 ran focused generated tests before broad verify. Common broad gates
were intentionally retained as the quality floor.

Per-task host tool-call counts cannot be separated from the shared harness invocations; subprocess
command counts above are not relabeled as host tool calls. Explorer/reviewer tool calls are separately
observed. Parallelism and file-read ratios do not demonstrate numerical token saving.
The four task implementations use a deterministic disposable harness plus real host delegation for
E3/E4, not four independently isolated model sessions. Routing-selected skills are recorded; per-case
host skill loading is not instrumented. These proxies do not prove automatic host compliance with
every reading/planning recommendation.

## A/B result

TOKEN A/B: INSUFFICIENT TELEMETRY

A/B NOT VALIDLY MEASURABLE

Fresh isolated workers exist, but comparable provider accounting does not. No matched efficiency
claim or fabricated baseline was produced; quality was not traded for a proxy score.

## Detachment

All four task projects plus the service qualification project passed doctor before detach and verify
again afterward. Local routing remained usable; application environments had no importable AgentReady,
Copier or Jinja. All three profiles also receive a separate latest-documentation qualification.
Formal automated qualification removes the tool environment and rebuilds a fresh project environment.
Hooks remain disabled by default; no global configuration was changed.

## Documentation

Root README now explains actual installation/init, verified profile selection, authorized lifecycle,
routing, context efficiency, sub-agent policy, hooks, continuity, detach and command discovery.
Generated README identifies profile structure/customization and links to deeper guidance; generated
AGENTS/index/workflow explain new vs resumed work. Source product/architecture contracts describe the
small routing boundary. No source runtime imports or profile dependencies were added.

## Architecture decision

Orchestrator: NO. Agent adapters: NO. Plugin framework: NO. Memory database: NO.
Existing routing, ownership and rendering seams suffice; host-dependent behaviors and external
measurement do not justify adding runtime infrastructure.

## Quality

Final regression coverage: **232 passed, 4 skipped, zero failures**, covering all 236 collected cases.
Formal detach qualification was serialized to avoid the observed Windows launcher startup timeouts;
the remaining suite used four workers. Both executions completed successfully:

| Executed command | Result |
|---|---|
| `uv run pytest tests/test_detached_project.py -q --tb=short` | 3 passed in 487.21s |
| `uv run --with pytest-xdist pytest -n4 --ignore=tests/test_detached_project.py -v --tb=short` | 229 passed, 4 skipped in 607.54s |
| `uv run ruff check .` | Passed |
| `uv run ruff format --check .` | Passed; 108 files |
| `uv run mypy src` | Passed; 22 source files |
| `uv build` | Wheel and sdist built |
| `uv run python scripts/generate_codebase_map.py --check` | Passed |
| `git diff --check` | Passed |

Durable final logs and JUnit XML are in the isolated evaluation directory as `detach_final.*` and
`regression_final.*`. Earlier passing targeted checks include routing 16 tests, UX/context 8 tests,
the reproduced template-bytecode regression (five relevant init tests), three package-check profile
tests, and two evaluation-scoring tests. Source skill check and four source lexical skill evals pass;
fresh generated profiles pass all eight lexical fixtures. Lexical fixture pass alone is not behavioral
agent execution: absent externally reported observations remain MISSING. Remote CI was not run;
these are local results, and repository CI remains authoritative.

## Residual issues

Reliable numerical token accounting and a valid A/B comparison remain unavailable. The concurrency
stress test alone cannot prove every interleaving; specialist inspection complements it. Its future
result timeout does not guarantee bounded executor shutdown under a hypothetical deadlocked worker.
Four Windows symlink cases were skipped because this host lacks creation privileges; junction tests
passed. Earlier concurrent installed-launcher timeouts did not reproduce when the same executable
was rerun unchanged; final serialized formal qualification passes all profiles. This host behavior
does not establish a product root cause, and no speculative launcher refactor was added. Linux CI
execution remains external to this local qualification.
