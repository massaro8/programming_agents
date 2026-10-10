# AgentReady adversarial stress audit

## Executive verdict

Local adversarial testing found and corrected a Windows filesystem boundary defect (P0),
two lost-update defects and a Unicode CLI lifecycle failure (P1), and an unhandled initialization
permission error (P2).
All identified material defects are corrected. The final suite reports 248 passed and four
privilege-related symlink skips; all other local gates pass. No reproducible P0/P1 remains in the
tested surfaces. The recommendation is subject to the explicit residual limitations below.
No remote CI, push, publication, release, global hook installation or destructive Git operation
was performed. No new dependency or product feature was introduced.

## Baseline

- Date: 2026-10-09; Windows, Python 3.12.12, local uv environment.
- Baseline commit: `ea2d0bd7366bbcb96f01fd6ccdfad99b73868993`.
- The working tree already contained 26 modified tracked files and eight untracked entries,
  including release documentation and UX/routing tests. These were preserved. This audit tests
  the working tree, not an assertion about the baseline commit alone.
- Read `AGENTS.md`, generated codebase map, architecture, ownership/profile implementation,
  Detachment Contract, existing lifecycle/concurrency audit constraints and actual CLI help.
- Applied repository `bug-investigation`: reproduce, regression, minimal correction, neighboring
  checks, retest. No subagents were used.
- Fast baseline: Ruff lint/format and mypy passed. A targeted initialization run passed
  21 tests with one privilege-related symlink skip.
- An initial broad pytest invocation was invalid: its explicit basetemp parent did not exist.
  Result: 75 passed/161 setup errors, not a product baseline PASS. The workspace was created and
  subsequent tests used unique child directories. Intermediate broad runs were superseded after
  concurrency and Unicode fixes; final disjoint test groups exercise the final implementation.

Initial verification plan and expected behavior:

1. Valid ASCII project basenames under space/Unicode/nested parents and supported long paths
   succeed; reserved/invalid basenames, profiles and nonempty targets reject without overwriting.
2. Rendering, file/manifest writes, index synchronization, checkpoint and detach failures report
   failure; source/sentinels survive; partial metadata is detectable; retries follow the contract.
3. Corrupt manifests, indexes, skills, hooks and checkpoints produce deterministic read-only
   diagnostics. Valid edits to SHARED content remain user-owned and are not automatically repaired.
4. Bounded competing writes must preserve every successful checkpoint/evidence update or reject
   a conflict. Advisory work IDs are not reservations; registry mutations have a single writer.
5. Junctions/symlinks cannot redirect init or destructive detach; doctor rejects unsafe boundaries.
6. CLI mistakes return nonzero with useful diagnostics; promised successful JSON remains parseable.
7. Existing and newly built artifacts install locally; all profiles run/verify before and after
   detach without AgentReady. Offline claims are restricted to uv offline mode and cached inputs.

All destructive experiments, sentinels, environment creation and pytest temporary repositories
were confined to `C:/z_personale/agentready_use_cases/agentready_adversarial_test`.
Source edits are limited to the corrections, regression coverage, relevant documentation and map.

## Scenario matrix

The final bounded harness (`stress.py pass-two`) contains 71 cases. Counts below describe
scenario expectations, not every assertion or CLI call inside each case. Source regression tests,
fault probes and packaging qualifications are counted separately to avoid double-counting.

| Category | Cases | Expected rejection | Successful behavior | Unexpected failures after retest | Confirmed / corrected findings |
| --- | ---: | ---: | ---: | ---: | --- |
| Initialization | 17 | 11 | 6 | 0 | AS-001, AS-004, AS-005: 3/3 |
| Corrupted repository / read-only doctor | 10 | 10 | 0 | 0 | AS-001: 1/1 |
| Checkpoints | 9 | 6 | 3 | 0 | AS-002: 1/1 |
| Hooks | 9 | 6 | 3 | 0 | AS-003: 1/1 |
| Skills / lexical evaluations | 10 | 2 | 8 | 0 | 0/0 |
| Initial failure injection / retry | 3 | 3 | 0 | 0 | 0/0 |
| CLI robustness | 10 | 10 | 0 | 0 | AS-004, AS-005: 2/2 |
| Registry concurrency | 3 | 1 | 2 | 0 | 0/0 |
| **Total** | **71** | **49** | **22** | **0** | **5/5 unique findings** |

Finding identities span categories; their reproductions come from the additional regressions
below, not exclusively the 71-case post-fix harness. Filesystem safety adds ten real-junction
rejection cases (AS-001, corrected). Packaging adds 33 steps: 32 successes, one expected missing-
dependency rejection, no unexpected failures and no additional findings. Additional fault/ownership
probes add eight cases: seven expected failure/recovery scenarios, one valid-edit success, no
unexpected failures and no additional findings. A separate service-profile long-path variation
generated successfully (root length 148, longest generated file path 207) and doctor was healthy.

Additional evidence:

- 10 real-junction regression scenarios: four detach locations, two init locations, four doctor
  locations. Seven tests failed before correction; ten passed afterward. Root/ancestor doctor
  cases could already be unhealthy for other reasons. Their assertions were strengthened to
  require the specific failed root/manifest/work check; all four doctor cases were rerun and passed.
- One permission-error regression: failed with uncaught `PermissionError`, passed after correction.
- Two deterministic lost-update regressions: both failed before correction, both passed afterward.
- Two lock lifecycle cases: a competing subprocess is rejected; release on exception and retry
  succeed; a stale lock is preserved with an actionable error.
- One additional CLI Unicode lifecycle case forces redirected CP1252 output, initializes under
  a Japanese parent and detaches. It failed before AS-005 and passed afterward.
- Eight additional fault/ownership probes cover actual renderer file writes (AGENTS, manifest,
  registry script), second-index failure, partial checkpoint/config writes, late detach failure,
  and valid SHARED content edits. Detailed final results appear in the quality gates.
- Packaging runs cover both existing wheel/sdist and final local builds, isolated installs,
  every profile's bootstrap/verify/detach/verify/run, and missing-dependency rejection.

The first exploratory harness included an over-limit Windows path and mistakenly encoded work
fixtures using CP1252. Those failures were harness mistakes, not product defects; valid UTF-8 and
paths within supported limits passed. Concurrent index replace once returned Windows access denied;
it reported failure and a sequential sync/check recovered. A fault probe originally expected a
stale changelog even though READY items did not change it; the final probe first makes it stale.
An early artifact harness named `packaging.py` shadowed the installed Python package and was
renamed; its recursive test subprocesses were stopped. These invalid runs support no PASS claim.

## P0/P1/P2 findings

### AS-001 — P0: Windows junction traversal during detach

**Reproduction:** Generate `junction-before/project`; create `sentinel-directory/sentinel.txt`
outside it; create a Windows junction at `.agentready/junction` pointing to that directory; call
`detach_project(project)`. The initial real integration reproduction printed
`sentinel survives: False`. Variants using a junction as `.agentready`, project root or an ancestor
also passed the old guard. Initialization accepted junction targets/ancestors and wrote outside
the lexical destination. Doctor could report linked maintenance metadata as healthy.

**Expected:** Fail before deletion/writes; preserve sentinel, manifest and ordinary repository
files. Unsafe metadata is diagnosed. **Actual:** Junctions were traversed because `is_symlink()`
does not identify Windows junctions. **Contract:** filesystem boundary, conservative writes,
Detachment Contract 9. **Root cause:** missing junction and root-ancestor checks in these lifecycle
paths despite existing guards in the portable local tools.

**Correction:** Reject symlinks/junctions at init/detach/doctor roots and ancestors; reject metadata
junctions during detach inventory and per-entry rechecks; add junction checks to doctor's artifact,
work and adapter boundaries. Actual Windows integration regressions preserve external sentinels.

### AS-002 — P1: checkpoint creation can silently replace another successful creation

**Reproduction:** Block writer A immediately before `write_json`; start writer B for the same
W001 with a different objective, without `--replace`; B succeeds; release A. Both operations
succeeded, but only A's checkpoint remained. Regression:
`test_concurrent_writes_preserve_every_success[checkpoint]`.

**Expected:** Preserve the explicit replacement boundary; one creation rejects. **Actual:** both
read `exists() == False` before either completed its write. **Contract:** existing checkpoints
require explicit `--replace`; no silent successful update loss. **Root cause:** check/write race.
**Correction:** A per-artifact exclusive local lock covers existence check and write.

### AS-003 — P1: evidence append loses a successful concurrent entry

**Reproduction:** Enable evidence-recorder, block A's journal write, complete B's append, release A.
Both records return success; the journal contains one entry instead of two. Regression:
`test_concurrent_writes_preserve_every_success[evidence]`.

**Expected:** Every successful append survives or conflict is explicit. **Actual:** stale journal
read/modify/write overwrote B. **Contract:** bounded evidence journal correctness. **Root cause:**
unprotected read/modify/write. **Correction:** The same local per-artifact guard protects journal
append and neighboring hook configuration updates. Competing writers fail clearly and may retry;
no distributed lock, waiting service or new dependency is introduced. Exported standalone scripts
receive the same implementation through the existing source-rendering mechanism.

### AS-004 — P2: unreadable init target produces an uncaught traceback

**Reproduction:** Inject `PermissionError` from `Path.iterdir()` for an existing empty target;
invoke CLI `main(['init', target])`. **Expected:** actionable error/exit 1 and no success or writes.
**Actual:** raw exception escaped. **Contract:** CLI robustness for ordinary filesystem errors.
**Root cause:** init CLI caught generator/type errors but not filesystem errors arising before
rendering. **Correction:** Catch `OSError` at that existing CLI boundary. Regression passes.

### AS-005 — P1: redirected Windows output breaks a successful Unicode-path lifecycle

**Reproduction:** `uv run agentready init <workspace>/pass-two/città_日本/cli_project` with redirected
Windows output. Initialization creates the project, then printing its path raises
`UnicodeEncodeError` in CP1252 and the command exits 1. The subprocess regression forces
`PYTHONIOENCODING=cp1252` and checks both init and detach under a Japanese parent.

**Expected:** Supported Unicode parents succeed through the actual CLI, including redirected
output. **Actual:** CLI failed after the mutation had completed. **Contract:** valid inputs and
supported lifecycle/exit-code correctness. **Root cause:** standard output's strict encoding error
handler cannot represent the path. **Correction:** At the root CLI boundary, native text streams
use `backslashreplace` for encoding errors, retaining the configured encoding. Unsupported
characters remain readable as escapes; machine JSON already uses ASCII escapes. The dedicated
regression and neighboring CLI/JSON tests passed (9 tests). No output encoding is forced on callers.

Confirmed/corrected findings: **P0 1/1; P1 3/3; P2 1/1**. Expected contract rejections, unsupported
registry concurrency, privilege skips and invalid harness assumptions are excluded.

## Fixes implemented

- Lifecycle junction/root-ancestor rejection and read-only unsafe-path diagnostics.
- Local exclusive guard for checkpoint creation, hook configuration and evidence append.
- Actionable init filesystem-error handling.
- Encoding-safe root CLI diagnostics and lifecycle messages for redirected Windows output.
- Regression tests and documentation of retry/stale-lock and registry single-writer behavior.

No unrelated refactor, hook activation, adapter/plugin system, backend or runtime dependency was
added. Passing product areas were left unchanged.

## Regression coverage

`tests/test_adversarial_boundaries.py` adds 16 cases covering real junction, permission, Unicode, deterministic
lost-update, subprocess exclusion and stale-lock regressions. Existing init, detach, doctor,
evolution, work registry, skill, packaging and generated-project tests provide neighboring checks.
Pre-fix failures were actually executed; final runs and results are listed below.

## Ownership / filesystem safety

Nonempty target sentinels remain unchanged. Doctor snapshots prove no repository-content changes
while detecting missing source/docs, malformed or escaping manifests, stale indexes, duplicate
work IDs, invalid statuses, malformed skills/evals/hooks and checkpoints. A valid SHARED-standard
edit remains healthy and unchanged. Malformed metadata is not silently repaired.

Junction integration was available and executed. Real file/directory symlink creation failed with
Windows error 1314; corresponding existing tests are skips, not PASS claims. Portable path checks
remain preflights and cannot eliminate malicious filesystem replacement between check and use.
No hostile concurrent link-swap guarantee is claimed.

Rendering write failures in new targets clean up the target. Partial JSON writes are bounded to
their intended file, report failure, release the write guard and remain diagnosable. Checkpoint
recovery needs explicit replacement; malformed hook configuration needs owner restoration.
No multi-file transaction or automatic rollback is promised.

## Detachment

All three profiles undergo bootstrap and full local verify before and after detach. Ordinary-file
snapshots are identical across detach. Source, tests, CI, useful guidance and portable engineering
scripts survive; no application imports or installation of AgentReady is required.

An injected first deletion failure leaves metadata unchanged and retry succeeds. An injected
failure removing the metadata directory after its manifest was removed leaves empty/incomplete
maintenance metadata; doctor detects it and repeat detach safely refuses. This is the previously
documented partial-removal limitation; ordinary files remain unchanged and no rollback is claimed.

## CLI robustness

Actual CLI help was used. Missing arguments, unknown options, invalid enum/profile/format values,
nonexistent paths, invalid work IDs, missing checkpoints, unknown skills and empty preflight input
reject with expected codes 1 or 2. No ordinary invalid-input traceback or false success was observed
after the permission fix. Doctor JSON for a missing root parses successfully and reports failure.
Hook preflights only inspect hypothetical dangerous command strings; none were executed.
Successful skill/doctor/checkpoint payloads are JSON where promised; error text is not asserted to
be JSON unless the existing interface promises it.

## Packaging/offline limitations

Existing `dist/agentready-0.1.0` wheel/sdist and final local artifacts contain trusted templates and
standalone scripts. Clean local environments install both wheels and sdists with
`uv pip install --offline`; both installed sdist entry points pass `--help`.
The final build uses `uv build --offline`, including wheel creation from the sdist.
Every current profile bootstraps/verifies with uv offline mode using cached dependencies. Detached
application probes assert AgentReady and Copier are absent, then import and run the greeting API.

This is cached offline qualification, not complete offline reproducibility or an OS-level network
block. Missing-dependency installation with `--no-deps` succeeds by request; invoking that incomplete
installation fails nonzero with `ModuleNotFoundError: copier`, rather than falsely claiming success.
The existing artifact predates the fixes; only the rebuilt artifacts qualify the corrected code.
No package was published.

Qualified final artifacts are in the disposable workspace's `final-dist/` (SHA-256):

- Wheel: `6bd533d92b6868cce8a0e7c0d0861a931cf3598e0e099cbe8cfa4add8d09602a`.
- Sdist: `d8bb92f1668cd49468c9a585248b6dfd827b223d6760cea9de9fbf1d242d9e6d`.

Any later release must rebuild from the corrected source rather than reuse the pre-audit `dist/`
artifacts; this task deliberately did not replace those existing files.

## Final quality gates

| Command / evidence | Actual result |
| --- | --- |
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | PASS, 115 files already formatted |
| `uv run mypy src` | PASS, 22 source files |
| `uv run python scripts/generate_codebase_map.py --check` | PASS |
| `git -c core.safecrlf=false diff --check` | PASS |
| `uv build --offline --out-dir <workspace>/final-dist` | PASS, wheel built from sdist |
| `uv run pytest -q --basetemp <workspace>/quality-pytest` | 247 passed, 4 symlink skips; intermediate run before AS-005, superseded by final groups |
| `uv run python <workspace>/final_gates.py` | PASS: 248 passed, 4 symlink skips, 0 failures across all 252 tests |
| Final group 1: adversarial, bootstrap, map, detach, formal detachment | 39 passed, 2 symlink skips |
| Final group 2: doctor, JSON, evolution, UX | 60 passed, 1 symlink skip |
| Final group 3: generated architecture, context and project qualification | 45 passed |
| Final group 4: every remaining test file | 104 passed, 1 symlink skip |
| `uv run pytest -q tests/test_init.py --basetemp <workspace>/diagnostic-pytest` | 21 passed, 1 symlink skip |
| `uv run pytest -q tests/test_detach.py tests/test_doctor.py tests/test_doctor_json.py tests/test_project.py --basetemp <workspace>/neighbors` | 45 passed, 3 symlink skips |
| `uv run pytest -q tests/test_adversarial_boundaries.py --basetemp <workspace>/regression-after` (initial 10 junction cases) | 10 passed |
| Permission regression alone, `--basetemp <workspace>/cli-after` | 1 passed |
| `uv run pytest -q tests/test_adversarial_boundaries.py::test_concurrent_writes_preserve_every_success tests/test_evolution.py --basetemp <workspace>/concurrency-after` | 34 passed |
| Two lock lifecycle regressions, `--basetemp <workspace>/lock-tests` | 2 passed |
| `uv run pytest -q tests/test_adversarial_boundaries.py::test_doctor_rejects_junction_boundaries --basetemp <workspace>/doctor-boundary-final` (strengthened assertions) | 4 passed |
| `uv run pytest -q tests/test_adversarial_boundaries.py::test_cli_unicode_target_succeeds_with_redirected_legacy_encoding tests/test_doctor_json.py tests/test_smoke.py --basetemp <workspace>/unicode-after` | 9 passed |
| `uv run python <workspace>/stress.py pass-two` | 71/71 expected outcomes |
| `uv run python <workspace>/fault_probe.py fault-probe-final` | 8/8 expected outcomes |
| `uv run python <workspace>/artifact_probe.py artifact-probe-release` | Rebuilt after AS-005; 27/27 expected outcomes |
| `uv run python <workspace>/sdist_probe.py` | 6/6 successes: existing/final isolated sdist install and help |

`<workspace>` expands to
`C:/z_personale/agentready_use_cases/agentready_adversarial_test`. The permission regression is
`tests/test_adversarial_boundaries.py::test_init_cli_reports_unreadable_target_without_traceback`;
the lock cases are `::test_repository_write_rejects_other_process_and_recovers` and
`::test_stale_lock_is_preserved_with_actionable_error` in that same file. They were run using
`uv run pytest -q` with the basetemp values above.

The artifact harness records each actual subprocess command and exit code. Each generated profile
runs `uv run --offline python scripts/project.py bootstrap`, `verify` before detach, `verify` after
detach, and an isolated application probe. Verify includes skills, registry, architecture/module
contracts, map, format/lint/types/tests, build and installed-wheel check. The stress harness evaluates
all eight shipped skill fixture sets and snapshots read-only doctor behavior. Source pytest includes
formal no-lock-in qualifications for all profiles. No remote CI result is claimed.

The final test harness verifies that all `tests/test_*.py` files occur exactly once in its four
groups. Each invokes `uv run pytest -q` with its explicit file list and a distinct
`<workspace>/final-gate-N` basetemp. `final-gates-results.json` records the complete actual command,
file list, exit status and pytest summary for each group; no subagents are involved.

Evidence is retained under the disposable workspace: `pass-two/results.json`,
`fault-probe-final/results.json`, `artifact-probe-release/packaging-results.json`,
`final-gates-results.json`, `sdist-results.json`, quality/neighbor/regression logs and final build logs.

## Residual risks

- Real symlink integration remains unverified on this host because privileges were unavailable.
- A killed writer can leave an artifact `.lock`. Retry reports how to remove it only after
  confirming no writer remains; locks are never stolen automatically.
- Hostile path replacement and arbitrary concurrent manual edits are outside the local trusted
  repository model. Registry mutations/index sync require one writer; `next-id` does not reserve.
- Late detach failure and partial JSON writes are diagnosable but not transactional rollback.
- Offline results depend on this machine's cached dependencies. Remote CI was not requested/run.

## Git diff summary

This task changes nine implementation files: CLI, generator, detach service, three doctor modules,
continuity, hooks and local paths. It adds `tests/test_adversarial_boundaries.py` and this audit,
updates the skill/continuity operational documentation and regenerates CODEBASE_MAP. Earlier
working-tree changes are preserved and are not attributed to this audit. No commits were made.

## Release recommendation

READY — MINOR NOTES

Use the corrected source/rebuilt artifacts. The notes are unavailable real-symlink privileges,
cached offline qualification, stale-lock recovery and documented single-writer/partial-failure
limits. None is an outstanding reproduced release-blocking defect in the supported tested flow.
